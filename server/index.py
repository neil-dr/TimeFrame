from fastapi import FastAPI, WebSocket,  HTTPException, status
import threading
import asyncio
import json
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
            detection_loop()
            start_stt()
    finally:
        close_camera()


@app.get("/start-loop")
def start_loop():
    if not manager.connected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No WebSocket client connected",
        )
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
    await manager.handle_events(ws)


@app.on_event("startup")
async def on_ws_startup():
    manager.loop = asyncio.get_running_loop()

if __name__ == "__main__":
    uvicorn.run("index:app", host="127.0.0.1", port=8000)
