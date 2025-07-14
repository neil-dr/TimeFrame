import cv2
from ultralytics import YOLO
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import threading
import uvicorn
from presence_detection import detection_loop

# --- CONFIGURABLE PARAMETERS ---
# Minimum area of face bounding box to be considered 'close' (adjust as needed)
DISTANCE_THRESHOLD_AREA = 5000
# Seconds the face must be continuously detected to start session
STARE_TIME_LIMIT = 2
SESSION_END_TIME = 5             # Seconds with no face to end session
# Path to YOLOv8-face model (user must provide this file)
YOLO_MODEL_PATH = "./yolov8n-face.pt"

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

# --- Detection loop in a thread ---
session_active = False
stare_start_time = None
last_face_time = None

# dowload it from https://github.com/akanametov/yolo-face
model = YOLO(YOLO_MODEL_PATH)

cap = cv2.VideoCapture(0)  # this will capture video from the webcam


def presence_detection_loop():
    def onSessionStart():
        manager.broadcast("session_started")

    def onSessionEnd():
        manager.broadcast("session_ended")

    detection_loop(
        onSessionStart=onSessionStart,
        onSessionEnd=onSessionEnd,
    )


def start_detection_thread():
    t = threading.Thread(target=presence_detection_loop, daemon=True)
    t.start()

# Start detection loop in background when server starts


@app.on_event("startup")
def on_startup():
    start_detection_thread()


if __name__ == "__main__":
    uvicorn.run("index:app", host="127.0.0.1", port=8000, reload=False)
