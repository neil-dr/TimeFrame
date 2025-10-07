import cv2
import threading
import queue
import time
from cv2 import VideoCapture
from typing import Optional, Tuple

cap: Optional[VideoCapture] = None
camera_thread: Optional[threading.Thread] = None
frame_queue: "queue.Queue[Tuple[bool, object]]" = queue.Queue(maxsize=1)
stop_event = threading.Event()
thread_lock = threading.Lock()
opened_event = threading.Event()
INDEX = 0
BACKEND = cv2.CAP_ANY
WARMUP_SECONDS = 0.35
GET_TIMEOUT = 2.0

def camera_loop(index: int = INDEX, backend: int = BACKEND) -> None:
    global cap
    try:
        cap = cv2.VideoCapture(index, backend)
        if not cap or not cap.isOpened():
            cap = None
            opened_event.clear()
            return
        opened_event.set()
        t0 = time.time()
        while time.time() - t0 < WARMUP_SECONDS and not stop_event.is_set():
            ret, _ = cap.read()
            if not ret:
                time.sleep(0.01)
            else:
                time.sleep(0.005)
        while not stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.02)
                continue
            try:
                if frame_queue.full():
                    _ = frame_queue.get_nowait()
                frame_queue.put_nowait((ret, frame))
            except queue.Full:
                pass
            time.sleep(0.005)
    finally:
        if cap:
            try:
                cap.release()
            except Exception:
                pass
        cap = None
        opened_event.clear()

def open_camera() -> None:
    global camera_thread, cap
    with thread_lock:
        if camera_thread and camera_thread.is_alive():
            return
        stop_event.clear()
        opened_event.clear()
        try:
            while True:
                frame_queue.get_nowait()
        except queue.Empty:
            pass
        camera_thread = threading.Thread(target=camera_loop, args=(INDEX, BACKEND), daemon=True)
        camera_thread.start()
        got = opened_event.wait(WARMUP_SECONDS + 0.8)
        if not got or not (camera_thread and camera_thread.is_alive()):
            stop_event.set()
            if camera_thread:
                camera_thread.join(timeout=1.0)
            raise IOError("Could not open camera")

def capture_frames() -> Tuple[bool, object]:
    if not (camera_thread and camera_thread.is_alive() and opened_event.is_set() and cap and cap.isOpened()):
        raise IOError("Tried to capture frame while camera was not open")
    try:
        ret, frame = frame_queue.get(timeout=GET_TIMEOUT)
        return ret, frame
    except queue.Empty:
        raise IOError("No frame available — camera not producing frames")

def close_camera() -> None:
    global camera_thread, cap
    with thread_lock:
        stop_event.set()
        opened_event.clear()
        if camera_thread and camera_thread.is_alive():
            camera_thread.join(timeout=2.0)
        if cap:
            try:
                cap.release()
            except Exception:
                pass
            cap = None
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass
