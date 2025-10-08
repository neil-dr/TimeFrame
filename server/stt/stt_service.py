import threading
import websocket
import json
from utils.mic_manager import open_mic, close_mic, listen_to_audio
from config.stt import API_ENDPOINT, ASSEMBLYAI_API_KEY, SILENCE_LIMIT
from presence_detection.detect_person import detect_person
from utils.websocket_manager import manager
import time
from threading import Event
from thinking.index import think
from utils.logs_manager import LogManager


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
        self.exception: Exception | None = None
        self.stt_start_time = None
        self.muted = False
        self.stop_event: Event | None = None
        self.user_speak = False  # whether we've received any transcription yet

    @classmethod
    def get_instance(cls):
        """Global access point to the single STTService."""
        return cls()

    def reset(self):
        self.muted = False
        self.user_speak = False
        self.stt_start_time = time.time()

    def on_open(self, ws):
        def stream_audio():
            open_mic()
            manager.broadcast("listening")
            print("STT started")
            self.stt_start_time = time.time()

            try:
                while self.connected and not self.stop_event.is_set():
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
                    print(f'chunk')
                    ws.send(chunk, websocket.ABNF.OPCODE_BINARY)
                print(
                    f"audio streaming stop {self.connected} {not self.stop_event.is_set()}")
            except Exception as e:
                self.exception = e
                print(f"audio exception: {self.exception}")
                self.stop()
            finally:
                close_mic()

        self.audio_thread = threading.Thread(target=stream_audio, daemon=True)
        self.connected = True
        self.audio_thread.start()

    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            print(data)
            if 'transcript' in data:
                self.user_speak = True
                if data.get('end_of_turn', False):
                    print(data['transcript'])
                    self.muted = True
                    print("Shifting to Thinking mode. Mic is now muted.")
                    log = LogManager()
                    log.insert_question(
                        question=f"[ONLINE]:{data['transcript']}")
                    think(data['transcript'])  # start thinking mode
                else:
                    # send data['transcript'] as in event
                    manager.broadcast(event="stt-transcription",
                                      data=data['transcript'])
        except Exception as e:
            self.exception = e
            self.stop()

    def on_error(self, ws, error):
        print(error)
        self.exception = error

    def on_close(self, ws, code, reason):
        self.connected = False
        print("STT stopped")

    def start(self, stop_event: Event):
        self.stop_event = stop_event
        self.ws_app = websocket.WebSocketApp(
            API_ENDPOINT,
            header={'Authorization': ASSEMBLYAI_API_KEY},
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        wst = threading.Thread(target=self.ws_app.run_forever, daemon=True)
        wst.start()

        while not stop_event.is_set() and wst.is_alive():
            time.sleep(0.1)

        self.stop()
        if self.audio_thread:
            self.audio_thread.join()
        if self.exception:
            self.stop()
            raise self.exception

    def stop(self):
        self.connected = False
        if self.ws_app:
            self.ws_app.close()
            manager.broadcast(event="stop-video-connection")
