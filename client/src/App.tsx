import { useEffect, useRef, useState } from "react";

export default function App() {
  const [status, setStatus] = useState("Disconnected");
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket("ws://127.0.0.1:8000/ws");
    wsRef.current = ws;
    ws.onopen = () => {
      setStatus("Connected");
      console.log("WebSocket connected");
    };
    ws.onclose = () => {
      setStatus("Disconnected");
      console.log("WebSocket disconnected");
    };
    ws.onerror = (err) => {
      setStatus("Error");
      console.error("WebSocket error", err);
    };
    ws.onmessage = (event) => {
      console.log("Received event:", event.data);
    };
    return () => {
      ws.close();
    };
  }, []);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded shadow text-center">
        <h1 className="text-2xl font-bold mb-4">WebSocket Client</h1>
        <p className="mb-2">Status: <span className={status === "Connected" ? "text-green-600" : status === "Error" ? "text-red-600" : "text-gray-600"}>{status}</span></p>
        <p className="text-gray-500">Check the browser console for session events.</p>
      </div>
    </div>
  );
}