import cv2
import time
from ultralytics import YOLO
import mediapipe as mp
from types import *

# --- CONFIG ---
YOLO_MODEL_PATH = "./yolov8n-face.pt"
FRONTAL_FACE_THRESHOLD = 0.35
EYE_DIFFERENCE = 0.35
STARE_TIME_LIMIT = 2
SESSION_END_TIME = 5

# --- Session state ---
session_active = False
stare_start_time = None
last_face_time = None

# --- Load YOLOv8 face model ---
yolo = YOLO(YOLO_MODEL_PATH)

# --- Setup MediaPipe FaceMesh ---
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False, max_num_faces=1, refine_landmarks=True)
mp_drawing = mp.solutions.drawing_utils

# --- Webcam ---
cap = cv2.VideoCapture(0)


def is_frontal_face(landmarks):
    left_eye = landmarks[33]
    right_eye = landmarks[263]
    nose_tip = landmarks[1]
    eye_diff = abs(left_eye.x - (1 - right_eye.x))
    nose_centered = abs(nose_tip.x - 0.5)
    return nose_centered < FRONTAL_FACE_THRESHOLD and eye_diff < EYE_DIFFERENCE


def detection_loop(onSessionStart, onSessionEnd):
    global session_active, stare_start_time, last_face_time

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            if session_active:
                # detect face 
                continue

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = yolo(frame_rgb, verbose=False)[0]

            frontal_face_detected = False
            current_time = time.time()
            for box in results.boxes:
                cls = int(box.cls[0])
                if cls != 0:
                    frontal_face_detected = False
                    continue  # Only face class

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                face_roi_rgb = frame_rgb[y1:y2, x1:x2]

                if face_roi_rgb.size == 0:
                    frontal_face_detected = False
                    continue  # skip empty ROI

                mesh_results = face_mesh.process(face_roi_rgb)

                if mesh_results.multi_face_landmarks:
                    landmarks = mesh_results.multi_face_landmarks[0].landmark
                    if is_frontal_face(landmarks):
                        frontal_face_detected = True
                        cv2.rectangle(frame, (x1, y1),
                                      (x2, y2), (0, 255, 0), 2)
                        last_face_time = current_time
                        break  # prioritize first valid frontal face
                else:
                    frontal_face_detected = False

            if frontal_face_detected:
                if not session_active:
                    if stare_start_time is None:
                        stare_start_time = current_time
                    elif current_time - stare_start_time >= STARE_TIME_LIMIT:
                        session_active = True
                        print("🟢 Session started")
                        onSessionStart()
                else:
                    stare_start_time = current_time
            else:
                if session_active and last_face_time and (current_time - last_face_time >= SESSION_END_TIME):
                    session_active = False
                    print("🔴 Session ended — no person detected")
                    onSessionEnd()
                    stare_start_time = None
                    last_face_time = None
                else:
                    stare_start_time = None

            cv2.imshow("YOLO + MediaPipe Frontal Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except:
        pass
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Session ended.")


def onSessionStart():
    print('session start')


def onSessionEnd():
    print('session end')


if __name__ == "__main__":
    print(type(detection_loop))
    detection_loop(
        onSessionStart=onSessionStart,
        onSessionEnd=onSessionEnd
    )
