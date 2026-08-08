from __future__ import annotations

import asyncio
import logging
import re
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from ai.ai_manager import AIManager
from ai.tool_router import ToolRouter
from tasks.service import TaskService

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
# Load AI once
# -------------------------------------------------------

MODEL_PATH = "models/llama-3.2-3b-instruct.gguf"

logger.info("Loading AI model...")

ai = AIManager(model_path=MODEL_PATH, n_ctx=4096, n_gpu_layers=0)

router = ToolRouter()
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

# -------------------------------------------------------
# Task checklist
# -------------------------------------------------------

# Matches "checklist for TASK-001", "checklist TASK-001", case-insensitive.
# This is a placeholder trigger living in the transport layer because
# ToolRouter's actual prompt-detection conventions aren't available yet —
# see the note on process_prompt() below. It belongs there, not here.
CHECKLIST_REQUEST = re.compile(r"checklist\s+(?:for\s+)?(TASK-\d+)", re.IGNORECASE)


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

            await websocket.send_json({
                "type": "checklist",
                "title": "AI Task Progress",
                "items": progress_items,
            })

            full_response = ""

            progress_items[1]["status"] = "complete"
            progress_items[2]["status"] = "in_progress"

            await websocket.send_json({
                "type": "checklist",
                "title": "AI Task Progress",
                "items": progress_items,
            })

            #
            # Stream tokens
            #
            final_prompt = router.process_prompt(prompt)
            print("\n========== FINAL PROMPT ==========")
            print(final_prompt)
            print("==================================\n")

            progress_items[2]["status"] = "in_progress"

            await websocket.send_json({
                "type": "checklist",
                "title": "AI Task Progress",
                "items": progress_items,
            })

            for token in ai.generate_stream(final_prompt):

                full_response += token

                await websocket.send_json({
                    "type": "token",
                    "text": token
                })

                #
                # Give control back to FastAPI
                #
                await asyncio.sleep(0)

            await websocket.send_json({
                "type": "response",
                "text": full_response
            })

            progress_items[2]["status"] = "complete"
            progress_items[3]["status"] = "complete"

            await websocket.send_json({
                "type": "checklist",
                "title": "AI Task Progress",
                "items": progress_items,
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