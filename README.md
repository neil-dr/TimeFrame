# 🧠 Timeframe – Full Stack Setup (Docker + LM Studio)
---

## 📦 What’s Included

| Service | Description | Port |
|----------|--------------|------|
| 🧩 Backend | FastAPI (Python 3.10) server with YOLO + Vosk | 8000 |
| 💾 Database | MySQL 8.0 | 3306 |
| 💻 Frontend | React + Vite | 5173 |
| 🧠 LM Studio | Local AI inference server | 1234 |

---

## 🧰 Prerequisites

Before running Docker Compose, ensure you have:

1. **Docker Desktop** installed  
   👉 [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)

2. **LM Studio** (optional, for local LLM inference)  
   👉 [https://lmstudio.ai](https://lmstudio.ai)

## ⚙️ Setting Up LM Studio

If you want to use **local LLM inference**:

1. **Install LM Studio** from [https://lmstudio.ai](https://lmstudio.ai)
2. **Open LM Studio**
   - Go to the **Server** tab
   - Click **Start Local Server**
3. Note the API URL (usually):
   ```
   http://localhost:1234/v1
   ```
4. Add `.env` file to server
Copy `example.env` and rename to `.env` inside `server/`. Than replace values of variables with valid corresponding values
---

## 🚀 Run with Docker Compose

Once Docker and LM Studio are ready:

1. Open a terminal in the **project root**.
2. Build and start all services:
   ```bash
   docker compose up --build
   ```
3. Wait for setup — the backend will download the required models automatically.

Once running:

| Service | URL |
|----------|-----|
| Frontend | http://localhost:5173 |
| Backend API Docs | http://localhost:8000/docs |
| MySQL DB | localhost:3306 |
| LM Studio (optional) | http://localhost:1234/v1 |

---

## 🧪 Testing

1. Open **Postman** or browser:
   - Visit: [http://localhost:8000/docs](http://localhost:8000/docs)
2. Test endpoints:
   - `GET /get_state`
   - `POST /start_loop`
   - `POST /stop_loop`
3. Ensure webcam/microphone permissions are granted in Edge (see `client/README.md`).

---

## 🧱 Project Structure

```
Timeframe/
├── client/               # React frontend
│   └── README.md
├── server/               # FastAPI backend
│   └── README.md
├── docker-compose.yml    # Defines frontend, backend, db services
└── README.md             # (This file)
```

---

## 🧹 Stopping and Cleaning Up

To stop all services:
```bash
docker compose down
```

To rebuild fresh:
```bash
docker compose build --no-cache
docker compose up
```

---

## ✅ Summary

✅ One command to run everything:  
```bash
docker compose up --build
```

✅ Optional LM Studio integration for local LLMs  
✅ Fully containerized frontend, backend, and database  
✅ Uses YOLOv8 + Vosk for vision and speech processing  

---

**Author:** Your Team  
**Version:** 1.0  
**License:** MIT  
