import time
from utils.camera_manager import capture_frames
from presence_detection.detect_frontal_face import detect_faces


def watch_silence(stop_event, on_timeout):
    last_time = time.time()

    def reset():
        nonlocal last_time
        last_time = time.time()

    watch_silence.reset = reset

    while not stop_event.is_set():
        if time.time() - last_time > 5:
            ret, frame = capture_frames()
            if ret and not detect_faces(frame):
                on_timeout()
                return
            reset()
        time.sleep(0.5)
