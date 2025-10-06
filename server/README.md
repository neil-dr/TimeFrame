# 🧠 Timeframe Backend (FastAPI + MySQL + Vosk + YOLO + LM Studio)

This is the backend server for **Timeframe**, powered by **FastAPI**, using **YOLOv8-face** for face detection, **Vosk** for offline speech recognition, and optionally **LM Studio** for local LLM responses.

---

## 📋 Prerequisites

- Python **3.10** (due to MediaPipe compatibility)
- MySQL Server **8.0+**
- LM Studio (for local LLM serving)
- Edge browser (for frontend usage)
- YOLOv8n-face model (`yolov8n-face.pt`)
- Vosk model (`vosk-model-small-en-us-0.15`)

---

## ⚙️ Environment Setup

1. **Open a terminal inside the `server` directory**

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate it**

   - On macOS / Linux:
     ```bash
     source .venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies**
   ```bash
   pip install mediapipe fastapi opencv-python ultralytics websocket-client omegaconf pyaudio python-dotenv vosk uvicorn openai mysql-connector-python
   ```

   If a dependency fails, install it individually.

---

## 🧩 Model Setup

1. **Download the YOLOv8n-face model:**
   - [yolov8n-face.pt](https://github.com/akanametov/yolo-face/releases/download/v0.0.0/yolov8n-face.pt)
   - Place it inside the `server/` directory.

2. **Download the Vosk small English model:**
   - [vosk-model-small-en-us-0.15.zip](https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip)
   - Extract it and place the folder inside `server/`:
     ```
     server/vosk-model-small-en-us-0.15/
     ```

Your structure should look like:
```
server/
├── index.py
├── yolov8n-face.pt
├── vosk-model-small-en-us-0.15/
├── config/
└── ...
```

---

## 🐬 MySQL Database Setup

1. Install MySQL 8.0 or higher.

2. Create a new schema:
   ```sql
   CREATE DATABASE timeframe_logs;
   ```

3. Update credentials in:
   ```
   server/config/db.py
   ```

4. Run migrations:
   ```bash
   cd server
   python run_migration.py
   ```

---

## 🧠 LM Studio Setup (Optional but Recommended)

### 1️⃣ Install LM Studio
Download from:
👉 [https://lmstudio.ai](https://lmstudio.ai)

### 2️⃣ Download a Local Model
Open LM Studio → **Models tab** → Download a model (e.g., `Mistral`, `Phi-3`, or `Gemma`).

### 3️⃣ Start LM Studio API Server
There are two ways:

#### **Option A: Using GUI**
1. Open LM Studio  
2. Go to **Server → Start Local Server**
3. Keep note of the API URL (usually `http://localhost:1234/v1`)

#### **Option B: Using CLI (Headless Mode)**
```bash
lmstudio server start --port 1234
```

### 4️⃣ Add `.env`
Copy `example.env` and rename to `.env` inside `server/`. Than replace values of variables with valid corresponding values
---

## 🚀 Run the Backend Server

Once MySQL and LM Studio are running:

```bash
cd server
source .venv/bin/activate   # (or venv\Scripts\activate on Windows)
python index.py
```

You’ll see something like:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Open your browser at:
👉 [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Testing

You can test the API using Postman.  
Import this collection:
👉 [Timeframe.postman_collection.json](https://github.com/neil-dr/TimeFrame/blob/main/Timeframe.postman_collection.json)

Endpoints:
- `GET /get_state` — check system status  
- `POST /start_loop` — start core detection loop  
- `POST /stop_loop` — stop core loop  

---

## ✅ Summary

| Component | Description | Default Port |
|------------|--------------|---------------|
| FastAPI | Backend server | 8000 |
| MySQL | Database | 3306 |
| LM Studio | Local LLM API | 1234 |

---

## 🧾 Notes

- Make sure your venv is in pythonv 3.10.x
- Use LM Studio only if you need AI-generated text locally.  
- Ensure your `.env` and model files exist before starting.  
