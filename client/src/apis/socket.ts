let _ws: WebSocket | null = null;

export function getSocket(): WebSocket {
  if (!_ws || _ws.readyState === WebSocket.CLOSED || _ws.readyState === WebSocket.CLOSING) {
    _ws = new WebSocket("ws://127.0.0.1:8000/ws");
  }
  return _ws;
}
