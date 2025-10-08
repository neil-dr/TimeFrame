from utils.camera_manager import capture_frames
from presence_detection.detect_frontal_face import detect_faces
from config.presence_detection import MAX_CAM_FAILURES
import cv2


def detect_person():
    failures = 0
    ret, frame = capture_frames()
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

        if ret:
            return detect_faces(frame)

        # cv2.imshow("YOLO + MediaPipe Frontal Detection", frame)
