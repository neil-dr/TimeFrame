from stt.stt_service import STTService
from utils.websocket_manager import manager


def start_stt():
    print("Listening mode is started")
    # Start the video streaming service connection
    manager.broadcast("start-video-connection")
    stt = STTService.get_instance()
    stt.start()
