import { useEffect, useRef, useState } from "react";
import { startCoreLoopApiCall, stopCoreLoopApiCall } from "./apis";
import useLogic from "./hooks/useLogic";
import { getSocket } from "./apis/socket";

type WSStatus = "Connected" | "Disconnected" | "Error";
type DIDStatus = "Disconnected" | "Connecting" | "Connected" | "Error";

export default function App() {
  const [wsStatus, setWsStatus] = useState<WSStatus>("Disconnected");
  const [mode, setMode] = useState<Modes>("idle");
  const [loopRunning, setLoopRunning] = useState(false);
  const [loading, setLoading] = useState(false);

  const [didStatus, setDidStatus] = useState<DIDStatus>("Disconnected");
  const videoRef = useRef<HTMLVideoElement>(null);
  const { connectD_ID } = useLogic(videoRef);

  useEffect(() => {
    const ws = getSocket();
    ws.onopen = () => setWsStatus("Connected");
    ws.onclose = () => {
      setWsStatus("Disconnected");
      setLoopRunning(false);
      setMode("idle");
    };
    ws.onerror = () => setWsStatus("Error");
    ws.onmessage = async (event: MessageEvent<SocketEvents>) => {
      if (event.data === "start-video-connection") {
        setDidStatus("Connecting");
        try {
          await connectD_ID();
          setDidStatus("Connected");
        } catch (e) {
          console.error("D‑ID error", e);
          setDidStatus("Error");
        }
      } else {
        setMode(event.data as Modes);
      }
    };
    return () => ws.close();
  }, []);

  const handleCoreLoop = async () => {
    setLoading(true);
    try {
      if (!loopRunning) {
        await startCoreLoopApiCall();
        setLoopRunning(true);
        setMode("idle");
      } else {
        await stopCoreLoopApiCall();
        setLoopRunning(false);
        setMode("idle");
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const didStyles = {
    Disconnected: "bg-gray-100 text-gray-700",
    Connecting: "bg-yellow-100 text-yellow-700",
    Connected: "bg-green-100 text-green-700",
    Error: "bg-red-100 text-red-700",
  } as const;

  const wsStyles = {
    Connected: "bg-green-100 text-green-700",
    Disconnected: "bg-gray-100 text-gray-600",
    Error: "bg-red-100 text-red-700",
  } as const;

  const modeStyles = {
    idle: "bg-gray-200 text-gray-800",
    listening: "bg-blue-200 text-blue-800",
    thinking: "bg-yellow-200 text-yellow-800",
  } as const;

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <div className="bg-white rounded-lg shadow-md w-full max-w-lg p-6 space-y-6">
        <h1 className="text-3xl font-bold text-center">Timeframe Dashboard</h1>

        <div className="grid grid-cols-2 gap-4">
          {/* WS Status */}
          <div className="flex flex-col">
            <span className="font-medium mb-1">WebSocket</span>
            <span
              className={`inline-block px-3 py-1 rounded-full text-sm ${wsStyles[wsStatus]}`}
            >
              {wsStatus}
            </span>
          </div>

          {/* D‑ID Status */}
          <div className="flex flex-col">
            <span className="font-medium mb-1">D‑ID Connection</span>
            <span
              className={`inline-block px-3 py-1 rounded-full text-sm ${didStyles[didStatus]}`}
            >
              {didStatus}
            </span>
          </div>
        </div>

        {/* Video Preview */}
        <div className="w-full aspect-square bg-black rounded overflow-hidden">
          <video
            ref={videoRef}
            className="w-full h-full object-cover"
            src={didStatus === "Connected" ? undefined : "./idle.mp4"}
            muted
            loop
            autoPlay
          />
        </div>

        {/* Mode */}
        <div className="flex justify-between items-center">
          <span className="font-medium">Mode:</span>
          <span
            className={`px-3 py-1 rounded-full text-sm font-medium ${modeStyles[mode]}`}
          >
            {mode.charAt(0).toUpperCase() + mode.slice(1)}
          </span>
        </div>

        {/* Controls */}
        <button
          onClick={handleCoreLoop}
          disabled={loading || wsStatus !== "Connected"}
          className={`py-2 rounded-md w-full font-medium transition ${loopRunning
            ? "bg-red-500 hover:bg-red-600 text-white"
            : "bg-blue-500 hover:bg-blue-600 text-white"
            } ${loading || wsStatus !== "Connected" ? "opacity-50 cursor-not-allowed" : ""}`}
        >
          {loading
            ? "..."
            : loopRunning
              ? "Stop Core Loop"
              : "Start Core Loop"}
        </button>
      </div>
    </div>
  );
}
