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
   brew install pyenv
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
   chmod +x .venv/bin/activate
   source .venv/bin/activate
   ```

   - On Windows

   ```bash
   venv\Scripts\activate
   ```

5. If you are on Mac, you need to install PortAudio with Homebrew. This is a one time setup.
   ```bash
   brew install portaudio

6. Install all dependencies

   ```bash
   pip install mediapipe fastapi opencv-python ultralytics websocket-client omegaconf pyaudio python-dotenv vosk uvicorn openai
   ```

   If above command fails download dependencies one by one

   - `mediapipe`
   - `openai`
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

1. Frontend runs on `http://locahost:5173`
2. Hit (either reload it or open it) the url `127.0.0.1:8000/start-loop` to make the linclon start detecting for person infront of camera
3. Hit (either reload it or open it) the url `127.0.0.1:8000/stop-loop` to stop the software (usecase: closing time)
4. Hit (either reload it or open it) the url `127.0.0.1:8000/state` to see the state of the system

## Troubleshooting
What is core loop?
Core Loop is the main logic that runs the conversational ai agent.
Presence Detection <-> Speech to Text -> LLM (thinking) -> Speech to Text

Modes:
Idle, Listening, Thinking, Error (Lincoln is away)

- There is an sql-lite file `server/logs.db` that conatins all the errors and questions logs along with timestamps. Use `DB Browser for SQL lite` to see the table rows
- For the core loop to start there are condtions.
   - Python fast api server is runing
   - Websocket connection is established between frontend and backend (the websocket connection poll in case of disconnection so wait until connection {see backend terminal it prints on connection} is made or just reload the frontend to make the connection isntantly)
   - Internet is connected
   - Frontend is runing
   - Camera is acquired by the frontend
   - Loop is not already running

- Incase of wierd behaviore just stop the loop and start the loop again [SOFT REFRESH]
- HARD REFRESH
   - Backend
      Restart the backend (open terminal in server folder)
      ```
      source venv/bin/activate
      python index.py
      ```
   - Frontend 
      Restart the frontend (open terminal in client folder)
      ```
      npm run dev
      ```

- All the errors are logged into the terminal as well as the sql lite logs.db so check it
- In case no error found do check the frontend console 
