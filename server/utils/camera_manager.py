import cv2

cap = None


def open_camera():
    global cap
    if cap is None:
        cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        cap.release()
        cap = None
        print("Failed to open camera")
        raise IOError("Could not open video capture device")
    print("Camera open")


def capture_frames():
    global cap
    if cap:
        ret, frame = cap.read()
        return ret, frame
    else:
        print('No camera is open')
        raise


def close_camera():
    global cap
    if cap:
        cap.release()
        cv2.destroyAllWindows()
        print("Camera closed")
