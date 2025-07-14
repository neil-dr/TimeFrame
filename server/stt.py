import pyaudio
import websocket
import json
import threading
from urllib.parse import urlencode

# --- Configuration ---
ASSEMBLYAI_API_KEY = "7afb17bc4d1c45f080dbf28040a6afe0"
CONNECTION_PARAMS = {
    "sample_rate": 16000,
    "format_turns": True,
}
API_ENDPOINT_BASE_URL = "wss://streaming.assemblyai.com/v3/ws"
API_ENDPOINT = f"{API_ENDPOINT_BASE_URL}?{urlencode(CONNECTION_PARAMS)}"

# Audio Configuration
FRAMES_PER_BUFFER = 800
SAMPLE_RATE = CONNECTION_PARAMS["sample_rate"]
CHANNELS = 1
FORMAT = pyaudio.paInt16

# State
audio = None
stream = None
ws_app = None
audio_thread = None
ws_thread = None
stop_event = threading.Event()

# STT session control flag (can be updated externally)
stt_session_active = False


def on_open(ws):
    def stream_audio():
        global stream
        print("🎙️ Audio stream started...")
        while not stop_event.is_set():
            try:
                audio_data = stream.read(
                    FRAMES_PER_BUFFER, exception_on_overflow=False)
                ws.send(audio_data, websocket.ABNF.OPCODE_BINARY)
            except Exception as e:
                print(f"Error streaming audio: {e}")
                break
        print("🎙️ Audio stream stopped.")

    global audio_thread
    audio_thread = threading.Thread(target=stream_audio)
    audio_thread.daemon = True
    audio_thread.start()


def on_message(ws, message):
    try:
        data = json.loads(message)
        if data.get("type") == "Turn" and data.get("transcript"):
            if (data['end_of_turn']):
                print("📝Sentence", data["transcript"])
            else:
                print("📝Partial", data["transcript"])
    except Exception as e:
        print("Error handling message:", e)


def on_error(ws, error):
    print("WebSocket Error:", error)
    stop_event.set()


def on_close(ws, code, reason):
    print(f"WebSocket closed: {code} - {reason}")
    stop_audio()


def stop_audio():
    global stream, audio
    stop_event.set()
    if stream:
        try:
            stream.stop_stream()
        except:
            pass
        stream.close()
        stream = None
    if audio:
        audio.terminate()
        audio = None
    if audio_thread and audio_thread.is_alive():
        audio_thread.join(timeout=1.0)


def start_stt_thread():
    global ws_app, ws_thread, audio, stream, stop_event

    if not stt_session_active:
        return

    stop_event.clear()
    audio = pyaudio.PyAudio()

    try:
        stream = audio.open(
            input=True,
            frames_per_buffer=FRAMES_PER_BUFFER,
            channels=CHANNELS,
            format=FORMAT,
            rate=SAMPLE_RATE,
        )
    except Exception as e:
        print("Failed to open microphone:", e)
        return

    ws_app = websocket.WebSocketApp(
        API_ENDPOINT,
        header={"Authorization": ASSEMBLYAI_API_KEY},
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )

    def run_ws():
        ws_app.run_forever()

    ws_thread = threading.Thread(target=run_ws, daemon=True)
    ws_thread.start()


def stop_stt():
    global ws_app
    stop_event.set()
    if ws_app:
        try:
            ws_app.close()
        except:
            pass
