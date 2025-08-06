from fastapi import FastAPI, WebSocket,  HTTPException, status
import threading
import asyncio
import uvicorn
from presence_detection.index import detection_loop
from stt.index import start_stt
from utils.camera_manager import open_camera, close_camera
from utils.mic_manager import close_mic
from utils.websocket_manager import manager
from utils.state_manager import get_mode

app = FastAPI()

# — Thread & control event —
core_thread: threading.Thread | None = None
stop_event = threading.Event()
thread_lock = threading.Lock()


def core_loop():
    open_camera()
    try:
        while not stop_event.is_set():
            detection_loop(stop_event)
            start_stt(stop_event)
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
    manager.broadcast("idle")
    close_camera()
    close_mic()
    return {"status": "stopping"}


@app.get("/state")
def get_state():
    mode = get_mode()
    web_socket_connected = manager.connected
    core_loop_running = core_thread.is_alive() if core_thread else False
    data = {"mode": mode, "web_socket_connected": web_socket_connected,
            "core_loop_running": core_loop_running}
    return data


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    await manager.handle_events(ws, stop_event)


@app.on_event("startup")
async def on_ws_startup():
    manager.loop = asyncio.get_running_loop()

if __name__ == "__main__":
    uvicorn.run("index:app", host="127.0.0.1", port=8000)
