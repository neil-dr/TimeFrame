from stt.stt_service import STTService


def start_stt():
    print("Listening mode is started")
    # Start the video streaming service connection
    stt = STTService.get_instance()
    stt.start()
