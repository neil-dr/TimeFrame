import time
from utils.camera_manager import capture_frames, close_camera
from presence_detection.detect_frontal_face import detect_faces

SILENCE_LIMIT = 5


def watch_silence(on_timeout):
    last_silence_time = time.time()

    def reset():
        nonlocal last_silence_time
        last_silence_time = time.time()

    watch_silence.reset = reset

    MAX_CAM_FAILURES = 2
    failures = 0
    while True:
        if time.time() - last_silence_time > SILENCE_LIMIT:
            ret, frame = capture_frames()
            print(ret)
            if not ret:
                if failures >= MAX_CAM_FAILURES:
                    close_camera()
                    raise IOError("Could not open video capture device")
                else:
                    failures = failures+1
            else:
                failures = 0

            if ret and not detect_faces(frame):
                on_timeout()
                return
            reset()
        time.sleep(0.5)
