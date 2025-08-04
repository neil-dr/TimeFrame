import threading
import websocket
import json
from utils.mic_manager import open_mic, close_mic, listen_to_audio
from config.stt import API_ENDPOINT, ASSEMBLYAI_API_KEY, SILENCE_LIMIT
from presence_detection.detect_person import detect_person
from utils.websocket_manager import manager
import time
import random


class STTService:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        # Only create one instance ever
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # __init__ runs on every call to STTService(), so guard it
        if STTService._initialized:
            return
        STTService._initialized = True

        self.ws_app = None
        self.connected = True
        self.audio_thread = None
        self._audio_exception: Exception | None = None
        self.stt_start_time = None
        self.muted = False
        self.user_speak = False  # whether we've received any transcription yet

    @classmethod
    def get_instance(cls):
        """Global access point to the single STTService."""
        return cls()

    def on_open(self, ws):
        def stream_audio():
            open_mic()
            print("STT started")
            self.stt_start_time = time.time()

            try:
                while self.connected:
                    # silence → presence logic
                    if not self.user_speak and (time.time() - self.stt_start_time > SILENCE_LIMIT):
                        if detect_person():
                            print("person detected, resetting timer")
                            self.stt_start_time = time.time()
                        else:
                            self.stop()
                            break

                    # if muted, skip sending
                    if self.muted:
                        continue

                    chunk = listen_to_audio()
                    ws.send(chunk, websocket.ABNF.OPCODE_BINARY)
            except Exception as e:
                self._audio_exception = e
                self.stop()
            finally:
                close_mic()

        manager.broadcast("listening")
        self.audio_thread = threading.Thread(target=stream_audio, daemon=True)
        self.audio_thread.start()

    def on_message(self, ws, message):
        data = json.loads(message)
        if 'transcript' in data:
            self.user_speak = True
            if data.get('end_of_turn', False):
                print(data['transcript'])
                self.muted = True
                print("Shifting to Thinking mode. Mic is now muted.")
                manager.broadcast("thinking")
                # Get the last sentence and pass it to OpenAI - async code afterwards
                # DUMMY thinking mode start
                DUMMY_REPLIES = [
                    "Ah, a fascinating question… Give me a moment.",
                    "Let me recall the details from the archives…",
                    "Thinking… History holds many layers.",
                    "Interesting. Reflecting on that now.",
                    "One second… I’ve studied this before.",
                    "Digging through the past—just a moment.",
                    "Let me piece this together for you."
                ]
                threading.Timer(
                    1.0,
                    lambda: manager.broadcast(
                        event='speaking', data=random.choice(DUMMY_REPLIES))
                ).start()
                # DUMMY thinking mode end
                # await for speaking-end event from frontend and than restart the thinking mode
            else:
                # send data['transcript'] as in event
                manager.broadcast(event="stt-transcription",
                                  data=data['transcript'])

    def on_error(self, ws, error):
        self._audio_exception = error

    def on_close(self, ws, code, reason):
        self.connected = False
        print("STT stopped")

    def start(self):
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
        self.connected = False
        if self.ws_app:
            self.ws_app.close()
