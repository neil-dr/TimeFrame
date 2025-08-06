import threading
import websocket
import json
from utils.mic_manager import open_mic, close_mic, listen_to_audio
from config.stt import API_ENDPOINT, ASSEMBLYAI_API_KEY, SILENCE_LIMIT
from presence_detection.detect_person import detect_person
from utils.websocket_manager import manager
import time
from threading import Event


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
        self.stop_event: Event | None = None
        self.user_speak = False  # whether we've received any transcription yet

    @classmethod
    def get_instance(cls):
        """Global access point to the single STTService."""
        return cls()

    def on_open(self, ws):
        def stream_audio():
            open_mic()
            manager.broadcast("listening")
            print("STT started")
            self.stt_start_time = time.time()

            try:
                print(f"self.connected and not self.stop_event.is_set() {self.connected and not self.stop_event.is_set()}")
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
                    ws.send(chunk, websocket.ABNF.OPCODE_BINARY)
            except Exception as e:
                self._audio_exception = e
                print(f"audio exception: {self._audio_exception}")
                self.stop()
            finally:
                close_mic()

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

                message = """Good afternoon, everyone, and thank you for joining me on this journey through the hidden stories of everyday technology. I invite you to slow down, look around, and notice the ordinary objects that quietly shape our lives. Consider, for a moment, the humble pencil. At first glance it is a simple stick of cedar, but inside that cedar is graphite mined from ancient rock, clay from distant riverbeds, and a thread of wax that lets the graphite glide across paper. The wood itself was once part of a living tree that spent decades converting sunlight into cellulose. Hundreds of hands, scattered across continents, guided each material through forests, factories, and freight lines before the pencil finally rested in your palm. 
                Now turn your thoughts to the glass screen you may be holding right now. It began as grains of silica—sand that once formed the bed of a prehistoric ocean. Heated to more than fifteen hundred degrees Celsius, those grains melted, flowed, and cooled into a perfectly smooth sheet. Engineers coated that sheet with layers thinner than a human hair, each designed to repel fingerprints, to keep out moisture, and to bend light so precisely that color appears vivid even in bright sunlight. Beneath that glass lies a microchip smaller than a postage stamp, etched with billions of transistors that switch on and off trillions of times every second. That whisper-thin silicon brain required clean rooms, ultraviolet lasers, and the knowledge of thousands of scientists who spent decades chasing Moore’s Law.
                When we see these objects only as finished products, we miss the astonishing web of effort and imagination that brought them to us. We miss the miners in Chile, the chemists in Japan, the designers in Sweden, and the logistics coordinators who chart courses for container ships across stormy seas. We miss the teachers who inspired a child to study physics, and the communities that nurtured that curiosity. Technological progress is rarely the tale of a lone genius working in isolation. It is, instead, a vast coral reef of human collaboration, layer upon layer, generation after generation."""
                threading.Timer(
                    1.0,
                    lambda: manager.broadcast(
                        event='speaking', data=message)
                ).start()
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
        if self._audio_exception:
            raise self._audio_exception

    def stop(self):
        self.connected = False
        if self.ws_app:
            self.ws_app.close()
