from fastapi import WebSocket
import threading
import asyncio


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.lock = threading.Lock()
        self.loop = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        with self.lock:
            self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        with self.lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

    def broadcast(self, message: str):
        with self.lock:
            targets = list(self.active_connections)

        for ws in targets:
            print(f"emit (sync): {message}")
            asyncio.run_coroutine_threadsafe(
                ws.send_text(message),
                self.loop
            )


manager = ConnectionManager()
