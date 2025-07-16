import time
from utils.camera_manager import capture_frames
from presence_detection.detect_frontal_face import detect_faces

SILENCE_LIMIT = 5


def watch_silence(stop_event, on_timeout):
    last_silence_time = time.time()

    def reset():
        nonlocal last_silence_time
        last_silence_time = time.time()

    watch_silence.reset = reset

    while True:
        if time.time() - last_silence_time > SILENCE_LIMIT:
            ret, frame = capture_frames()
            if ret and not detect_faces(frame):

                on_timeout()
                return
            reset()
        time.sleep(0.5)
