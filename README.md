# 🕒 Timeframe

## 📋 Prerequisites

- Download the YOLOv8n face detection model:
  [yolov8n-face.pt](https://github.com/akanametov/yolo-face/releases/download/v0.0.0/yolov8n-face.pt)
  - Place the downloaded file inside the `server` directory.
- Python **3.7 to 3.10** is required (due to MediaPipe compatibility).
- Use Edge Browser
- Open Edge and goto `edge://settings/privacy/sitePermissions/allPermissions/mediaAutoplay`. Add Site `http://localhost:5173` and set `Control if audio and video play automatically on sites` to `Allow`

---

## 🚀 How to Run the Server

1. Open a terminal in the `server` directory.
2. Create a virtual environment (make sure Python 3.10 is used):
   ```bash
   python -m venv venv
   ```
   or
   ```bash
   py -3.10 -m venv venv
   ```
   in case of multiple installed python versions
3. Activate the virtual environment:
   ```bash
   venv\Scripts\activate
   ```
4. Install dependencies from `requirements.txt`:
   ```bash
    pip install -r requirements.txt
   ```
5. Create `.env` in server folder refer `server/example.env`
6. Start the FastAPI server:
   ```bash
   python index.py
   ```
