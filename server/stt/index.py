import threading
import threading
from stt.stt_service import STTService
from stt.silence_detector import watch_silence

stop_event = threading.Event()
silence_exception = [None]


def handle_transcript(data):
    if data['end_of_turn']:
        print(data['transcript'])
    watch_silence.reset()


def start_stt():
    def handle_timeout():
        stt.stop()
        print("Session closed")

    t = threading.Thread(
        target=watch_silence,
        args=(handle_timeout, silence_exception),
    )
    t.start()

    stt = STTService(handle_transcript, stop_event)
    stt.start()

    t.join()

    if silence_exception[0]:
        raise silence_exception[0]
