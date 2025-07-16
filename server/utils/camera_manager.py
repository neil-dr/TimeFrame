import cv2

cap = None


def open_camera():
    global cap
    if cap is None:
        cap = cv2.VideoCapture(0)
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
