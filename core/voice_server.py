import os
import sys
import json
import base64
import asyncio
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Initialize project roots for relative imports if run independently
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VoiceServer")

app = FastAPI(title="LunarTech Realtime Voice Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info("Client disconnected.")


manager = ConnectionManager()


@app.websocket("/ws/voice")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Recept raw audio bytes or JSON payloads from the frontend
            data = await websocket.receive_text()

            try:
                payload = json.loads(data)

                # If frontend sends base64 encoded audio chunks
                if "audio" in payload:
                    # TODO: Buffer audio chunks, trigger Whisper/SpeechRecognition on silence
                    # Right now we just echo back a status
                    audio_bytes = base64.b64decode(payload["audio"])

                    # Mock response for testing the socket loop
                    # Note: In production we will pipe this to LLM and TTS continuously
                    response_payload = {
                        "status": "receiving",
                        "bytes_received": len(audio_bytes),
                        "message": "Audio packet received, processing...",
                    }
                    await websocket.send_text(json.dumps(response_payload))

                elif "text_prompt" in payload:  # Fallback or metadata channel
                    pass

            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"error": "Invalid payload"}))

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket Error: {e}")
        manager.disconnect(websocket)


if __name__ == "__main__":
    logger.info(
        "Starting LunarTech Realtime Voice Server on ws://localhost:8001/ws/voice"
    )
    uvicorn.run("core.voice_server:app", host="0.0.0.0", port=8001, reload=True)
