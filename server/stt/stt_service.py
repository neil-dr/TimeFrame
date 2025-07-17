import threading
import websocket
import json
from utils.mic_manager import open_mic, close_mic, listen_to_audio
from config.stt import API_ENDPOINT, ASSEMBLYAI_API_KEY


class STTService:
    def __init__(self, on_transcript, stop_event):
        self.on_transcript = on_transcript
        self.stop_event = stop_event
        self.ws_app = None
        self.audio_thread = None
        self._audio_exception: Exception | None = None

    def on_open(self, ws):
        def stream_audio():
            try:
                open_mic()
                print("STT started")
                while not self.stop_event.is_set():
                    data = listen_to_audio()
                    ws.send(data, websocket.ABNF.OPCODE_BINARY)
            except Exception as e:
                self.stop()
                self._audio_exception = e
            finally:
                close_mic()

        self.audio_thread = threading.Thread(target=stream_audio, daemon=True)
        self.audio_thread.start()

    def on_message(self, ws, message):
        data = json.loads(message)
        if 'transcript' in data:
            self.on_transcript(data)

    def on_error(self, ws, error):
        self.stop_event.set()

    def on_close(self, ws, code, reason):
        print("STT stop")
        self.stop_event.set()

    def start(self):
        self.stop_event.clear()
        self.ws_app = websocket.WebSocketApp(
            API_ENDPOINT,
            header={'Authorization': ASSEMBLYAI_API_KEY},
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        self.ws_app.run_forever()

        if self.audio_thread:
            self.audio_thread.join()

        if self._audio_exception:
            raise self._audio_exception

    def stop(self):
        self.stop_event.set()
        if self.ws_app:
            self.ws_app.close()
