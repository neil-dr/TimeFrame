import time
import cv2
from types import *
from presence_detection.detect_frontal_face import detect_faces
from utils.camera_manager import capture_frames
from config.presence_detection import *

# --- Session state ---
stare_start_time = None
last_face_time = None


def detection_loop():
    global stare_start_time, last_face_time
    failures = 0

    try:
        while True:
            ret, frame = capture_frames()
            if not ret:
                if failures >= MAX_CAM_FAILURES:
                    raise IOError(
                        "Could not open video capture device")
                else:
                    failures = failures+1
            else:
                failures = 0

            is_face_in_front_of_camera = detect_faces(frame=frame)

            if is_face_in_front_of_camera:
                current_time = time.time()
                last_face_time = current_time

                if stare_start_time is None:  # face detected
                    stare_start_time = current_time
                elif current_time - stare_start_time >= STARE_TIME_LIMIT:  # person is staring for Stare limit
                    print("🟢 Session started")
                    break
            else:
                stare_start_time = None  # reset stare

            cv2.imshow("YOLO + MediaPipe Frontal Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except:
        pass
    finally:
        cv2.destroyAllWindows()
