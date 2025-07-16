from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import threading
import uvicorn
from presence_detection.index import detection_loop
from stt.index import start_stt
from utils.camera_manager import *

# --- FastAPI app and WebSocket manager ---
app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.lock = threading.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        with self.lock:
            self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        with self.lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        with self.lock:
            connections = list(self.active_connections)
        for connection in connections:
            try:
                await connection.send_text(message)
            except Exception:
                self.disconnect(connection)


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.on_event("startup")
def on_startup():
    try:
        open_camera()
        while True:
            detection_loop()  # breaks when user stare for 2s
            start_stt()
    except Exception as e:
        close_camera()
        print(f"Error {e}")


if __name__ == "__main__":
    uvicorn.run("index:app", host="127.0.0.1", port=8000, reload=False)
