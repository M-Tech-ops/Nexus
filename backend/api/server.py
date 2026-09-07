from __future__ import annotations

import asyncio
import logging
import re
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from core.config import Config
from ai.ai_manager import AIManager
from ai.tool_router import ToolRouter
from tasks.service import TaskService
from data.conversations.history import ConversationHistory

# -------------------------------------------------------
# Logging
# -------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s | %(message)s",
)

logger = logging.getLogger("NexusAI")

# -------------------------------------------------------
# FastAPI
# -------------------------------------------------------

app = FastAPI(
    title="Nexus AI Backend",
    version="0.1.0",
)

# -------------------------------------------------------
# Storage & Directories
# -------------------------------------------------------

Config.ensure_storage_directories()

logger.info(f"Persistent storage (tasks, memory): {Config.NEXUS_DATA_DIR}")
logger.info(f"Conversation history (temp): {Config.HISTORY_FILE}")

# -------------------------------------------------------
# Load AI once
# -------------------------------------------------------

MODEL_PATH = Config.MODEL_PATH

logger.info("Loading AI model...")

ai = AIManager(model_path=MODEL_PATH)

router = ToolRouter()

# -------------------------------------------------------
# Conversation History & Tasks
# -------------------------------------------------------

conversation_history = ConversationHistory(
    Config.HISTORY_FILE,
    max_messages=10,
)

logger.info("Conversation history loaded.")
tasks = TaskService()

logger.info("AI model loaded.")

# -------------------------------------------------------
# Health endpoint
# -------------------------------------------------------

@app.get("/")
async def root():
    return JSONResponse(
        {
            "status": "running",
            "service": "Nexus AI Backend"
        }
    )




def _checklist_items(task) -> list[dict]:
    return [
        {
            "requirement": item.requirement,
            "status": item.status.value,
            "source": item.source,
            "missing_reason": item.missing_reason,
        }
        for item in task.checklist
    ]


@app.get("/tasks/{task_id}/checklist")
async def get_task_checklist(task_id: str):
    try:
        task = tasks.get_task(task_id)
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=404)

    completion = task.completion

    return JSONResponse({
        "id": task.id,
        "title": task.title,
        "checklist": _checklist_items(task),
        "completion": {
            "complete": completion.complete,
            "total": completion.total,
            "percent": completion.percent,
        },
    })

# -------------------------------------------------------
# WebSocket
# -------------------------------------------------------

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()

    logger.info("Client connected.")

    try:

        await websocket.send_json({
            "type": "state",
            "value": "idle"
        })

        while True:

            message = await websocket.receive_json()

            if message.get("type") != "prompt":
                continue

            prompt = message.get("text", "").strip()

            if not prompt:
                continue

            logger.info("Prompt received.")

            await websocket.send_json({
                "type": "state",
                "value": "compact"
            })

            await asyncio.sleep(0.15)

            await websocket.send_json({
                "type": "state",
                "value": "expanded"
            })

            # -------------------------------------------------------
            # AI task progress
            # -------------------------------------------------------

            progress_items = [
                {
                    "requirement": "Understand the request",
                    "status": "complete",
                    "source": "AI",
                    "missing_reason": "",
                },
                {
                    "requirement": "Plan the response",
                    "status": "pending",
                    "source": "AI",
                    "missing_reason": "",
                },
                {
                    "requirement": "Generate the response",
                    "status": "pending",
                    "source": "AI",
                    "missing_reason": "",
                },
                {
                    "requirement": "Finalize the response",
                    "status": "pending",
                    "source": "AI",
                    "missing_reason": "",
                },
            ]

            full_response = ""

            #
            # Stream tokens
            #
            final_prompt = router.process_prompt(prompt)

            # -------------------------------------------------------
            # Conversation context
            # -------------------------------------------------------

            history = conversation_history.get_messages()

            logger.info(f"[Conversation] Using {len(history)} previous messages.")

            # Store the ORIGINAL user message.
            # Do NOT store final_prompt because it may contain
            # backend email/memory context.
            conversation_history.add_user_message(prompt)

            history = conversation_history.get_messages()[:-1]

            # -------------------------------------------------------
# Generate response
# -------------------------------------------------------

            for token in ai.generate_stream(
                final_prompt,
                history=history,
            ):

                full_response += token

                await websocket.send_json({
                    "type": "token",
                    "text": token
                })

                await asyncio.sleep(0)

            conversation_history.add_assistant_message(full_response)

            await websocket.send_json({
                "type": "response",
                "text": full_response
            })

            await websocket.send_json({
                "type": "state",
                "value": "idle"
            })

            logger.info("Response completed.")

    except WebSocketDisconnect:

        logger.info("Client disconnected.")

    except Exception as e:

        logger.exception(e)

        try:

            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })

        except Exception:
            pass