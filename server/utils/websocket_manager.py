from fastapi import WebSocket
import threading
import asyncio
import json


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

    def broadcast(self, event: str, data: str = None):
        with self.lock:
            targets = list(self.active_connections)

        for ws in targets:
            asyncio.run_coroutine_threadsafe(
                ws.send_text(json.dumps({
                    "event": event,
                    "data": data
                })),
                self.loop
            )


manager = ConnectionManager()
