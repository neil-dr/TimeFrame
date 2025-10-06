# 🖥️ Timeframe Frontend (React + Vite)

This is the **frontend** for Timeframe, built with **React + Vite**.  
It provides the web interface for interacting with the backend.

---

## 📋 Prerequisites

- Node.js **18+**
- npm (or yarn)
- Edge Browser (for autoplay withou interaction permissions)
- Backend running locally (`http://localhost:8000`)

---

## 🌐 Edge Browser Configuration (Required)

1. Open Microsoft Edge.
2. Navigate to:
   ```
   edge://settings/privacy/sitePermissions/allPermissions/mediaAutoplay
   ```
3. Add this site:
   ```
   http://localhost:5173
   ```
4. Set **Control if audio and video play automatically on sites** → **Allow**.

---

## ⚙️ Setup and Run (Development Mode)

1. Open terminal in the `client/` directory.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
4. Open your browser:
   👉 [http://localhost:5173](http://localhost:5173)

---

## 🔌 Connecting to the Backend

By default, the frontend expects the backend API at:
```
http://localhost:8000
```

## 🧩 Folder Structure

```
client/
├── src/
│   ├── components/
│   ├── pages/
│   ├── assets/
│   └── App.jsx
├── package.json
└── vite.config.js
```

---

## 🧠 Troubleshooting

| Issue | Solution |
|-------|-----------|
| App can’t access mic/camera | Check Edge autoplay permissions |
| API calls fail | Ensure backend (`http://localhost:8000`) is running |
| Hot reload not working | Restart `npm run dev` |

---

## ✅ Summary

| Component | Description | Default Port |
|------------|--------------|---------------|
| React + Vite | Frontend UI | 5173 |
| FastAPI | Backend API | 8000 |
| MySQL | Database | 3306 |
| LM Studio | Local LLM API | 1234 |

---

## 🧾 Notes

- This frontend must run simultaneously with the backend.
- Use Edge for best unmuted autoplay support.
