# 🕒 Timeframe

## 📋 Prerequisites

- Download the YOLOv8n face detection model:
  [yolov8n-face.pt](https://github.com/akanametov/yolo-face/releases/download/v0.0.0/yolov8n-face.pt)
  - Place the downloaded file inside the `server` directory.
- Download the vosk small en us model for offline STT:
  - [vosk-model-small-en-us-0.15](https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip)
  - Place the extracted folder from downloaded zip inside the `server` directory and make sure the folder name is `vosk-model-small-en-us-0.15`
- Python **3.7 to 3.10** is required (due to MediaPipe compatibility).
- Use Edge Browser
- Open Edge and goto `edge://settings/privacy/sitePermissions/allPermissions/mediaAutoplay`. Add Site `http://localhost:5173` and set `Control if audio and video play automatically on sites` to `Allow`
- Import [Timeframe.postman_collection.json](https://github.com/neil-dr/TimeFrame/blob/main/Timeframe.postman_collection.json) in postman

---

## 🚀 How to Run the Server

1. Open a terminal in the `server` directory.

2. Install Python 3.10
   a. Download and install Python 3.10 on a fresh machine
   b. On a machine with other Python version installed (MacOS):

   - Install pyenv and build deps

   ```bash
   brew update
   brew install pyenv openssl readline sqlite3 xz zlib tcl-tk
   ```

   - Initialize pyenv for bash

   ```bash
   echo 'eval "$(pyenv init -)"' >> ~/.bash_profile
   source ~/.bash_profile
   ```

   - Install Python 3.10 and set it for this project only (ensure you are in the `server` directory)

   ```bash
   pyenv install 3.10.14
   pyenv local 3.10.14
   ```

3. Create a virtual environment (make sure Python 3.10 is used):
   ```bash
   python -m venv .venv
   ```
4. Activate the virtual environment:

   - On MacOS

   ```bash
   source .venv/bin/activate
   ```

   - On Windows

   ```bash
   venv\Scripts\activate
   ```

5. If you are on Mac, you need to install PortAudio with Homebrew. This is a one time setup.
   a. Install Xcode CLT (compiler)

   ```bash
   xcode-select --install
   ```

   b. Install PortAudio with Homebrew

   - Apple Silicon (arm64):

   ```bash
   /opt/homebrew/bin/brew install portaudio
   ```

   - Intel Mac (x86_64) or Rosetta Homebrew:

   ```bash
   /usr/local/bin/brew install portaudio
   ```

   c. Install PyAudio inside your virtualenv

   ```bash
   pip install --no-cache-dir pyaudio
   ```

6. Install all dependencies

   ```bash
   pip install mediapipe fastapi opencv-python ultralytics websocket-client omegaconf pyaudio python-dotenv vosk uvicorn
   ```

   - `mediapipe`
   - `fastapi`
   - `opencv-python`
   - `ultralytics`
   - `websocket-client`
   - `omegaconf`
   - `pyaudio`
   - `dotenv`
   - `vosk`
   - `uvicorn`

## 🚀 How to Use

1. Use Get State API in postman and make sure the websocket connected
2. Use Start loop api to start the core loop (On first start the presence detection take some time as the camera is taking permission to wait a while)
3. Use stop loop api to stop the core loop
4. Create `.env` in server folder refer `server/example.env`
5. Start the FastAPI server:
   ```bash
   python index.py
   ```
