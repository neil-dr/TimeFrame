import threading
import threading
from stt.stt_service import STTService
from stt.silence_detector import watch_silence

stop_event = threading.Event()


def handle_transcript(data):
    print(data['transcript'])
    watch_silence.reset()


def start_stt():
    def handle_timeout():
        stt.stop()

    threading.Thread(
        target=watch_silence,
        args=(stop_event, handle_timeout),
        daemon=True
    ).start()

    stt = STTService(handle_transcript, stop_event)
    stt.start()
