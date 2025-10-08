from utils.camera_manager import capture_frames
from presence_detection.detect_frontal_face import detect_faces
from config.presence_detection import MAX_CAM_FAILURES
import cv2
from utils.frame_buffer import get_latest_frame


def detect_person():
    failures = 0
    frame = get_latest_frame()
    while True:
        frame = get_latest_frame()
        if frame is not None and frame.size > 0:
            return detect_faces(frame)
