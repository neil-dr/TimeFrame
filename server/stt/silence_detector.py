import time
from utils.camera_manager import capture_frames, close_camera
from presence_detection.detect_frontal_face import detect_faces
from config.presence_detection import MAX_CAM_FAILURES

SILENCE_LIMIT = 5


def watch_silence(on_timeout, silence_exception):
    last_silence_time = time.time()

    def reset():
        nonlocal last_silence_time
        last_silence_time = time.time()

    watch_silence.reset = reset

    failures = 0
    while True:
        if time.time() - last_silence_time > SILENCE_LIMIT:
            ret, frame = capture_frames()
            if not ret:
                if failures >= MAX_CAM_FAILURES:
                    silence_exception[0] = IOError(
                        "Could not open video capture device")
                    break
                else:
                    failures = failures+1
            else:
                failures = 0

            if ret and not detect_faces(frame):
                on_timeout()
                return
            reset()
        time.sleep(0.5)
