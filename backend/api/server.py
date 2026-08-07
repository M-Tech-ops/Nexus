from __future__ import annotations

import asyncio
import logging
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from ai.ai_manager import AIManager
from ai.tool_router import ToolRouter
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

ai = AIManager(
    model_path=MODEL_PATH,
    n_ctx=4096,
    n_gpu_layers=0,
)

router = ToolRouter()

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

            full_response = ""

            #
            # Stream tokens
            #
            final_prompt = router.process_prompt(prompt)
            print("\n========== FINAL PROMPT ==========")
            print(final_prompt)
            print("==================================\n")
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