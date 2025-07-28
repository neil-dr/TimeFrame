type Modes = "idle" | "listening" | "thinking"
type SocketEvents = Modes | "start-video-connection"

interface StartLoopResponse {
  "status": "started"
}

interface StopLoopResponse {
  "status": "stop"
}
