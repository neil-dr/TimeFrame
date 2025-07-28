from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
import threading
import asyncio
import uvicorn
from presence_detection.index import detection_loop
from stt.index import start_stt
from utils.camera_manager import open_camera, close_camera
from utils.websocket_manager import manager

app = FastAPI()

# — Thread & control event —
core_thread: threading.Thread | None = None
stop_event = threading.Event()
thread_lock = threading.Lock()


def core_loop():
    open_camera()
    try:
        while not stop_event.is_set():
            detection_loop()      # blocks until stare
            if stop_event.is_set():
                break
            # await manager.broadcast("listening")
            start_stt()           # blocks until STT ends
    finally:
        close_camera()


@app.get("/start-loop")
def start_loop():
    global core_thread
    with thread_lock:
        if core_thread and core_thread.is_alive():
            raise HTTPException(status_code=400, detail="Loop already running")
        stop_event.clear()
        core_thread = threading.Thread(target=core_loop, daemon=True)
        core_thread.start()
    return {"status": "started"}


@app.get("/stop-loop")
def stop_loop():
    stop_event.set()
    return {"status": "stopping"}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)
        # auto‑stop if no clients remain
        if not manager.active_connections:
            stop_event.set()


@app.on_event("startup")
async def on_ws_startup():
    manager.loop = asyncio.get_running_loop()

if __name__ == "__main__":
    uvicorn.run("index:app", host="127.0.0.1", port=8000)
