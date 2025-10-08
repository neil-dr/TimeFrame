from fastapi import WebSocket, WebSocketDisconnect
from utils.state_manager import set_mode
import threading
import asyncio
import json
import numpy as np
from threading import Event
import cv2
from utils.frame_buffer import set_latest_frame

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.connected = False
        self.lock = threading.Lock()
        self.loop = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        with self.lock:
            self.active_connections.append(websocket)
            self.connected = True

    def disconnect(self, websocket: WebSocket):
        with self.lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
                self.connected = False

    async def handle_events(self, websocket: WebSocket, stop_event: Event):
        try:
            while True:
                try:
                    raw = await websocket.receive()
                    if "bytes" in raw:
                        data = raw["bytes"]
                        nparr = np.frombuffer(data, np.uint8)
                        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        set_latest_frame(frame)
                    else:
                        payload = json.loads(raw)
                        event, data = payload.get("event"), payload.get("data")
                        if self.connected and not stop_event.is_set():

                            if event == "back-to-listening":
                                from stt.index import get_stt_instance
                                stt = get_stt_instance()
                                stt.reset()
                                print("🔊  Mic un-muted, back to listening")
                            elif event == "speaking":
                                set_mode("speaking")
                except (ValueError, KeyError):
                    print("bad payload")

        except WebSocketDisconnect:
            print("client disconnected")
            self.disconnect(websocket)

    def broadcast(self, event: str, data: str = None):
        with self.lock:
            print(event)
            targets = list(self.active_connections)

        for ws in targets:
            asyncio.run_coroutine_threadsafe(
                ws.send_text(json.dumps({
                    "event": event,
                    "data": data
                })),
                self.loop
            )
        set_mode(event)


manager = ConnectionManager()
