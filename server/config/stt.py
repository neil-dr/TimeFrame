import pyaudio
from urllib.parse import urlencode

FRAMES_PER_BUFFER = 800
SAMPLE_RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16

# --- Configuration ---
ASSEMBLYAI_API_KEY = "7afb17bc4d1c45f080dbf28040a6afe0"
CONNECTION_PARAMS = {
    "sample_rate": SAMPLE_RATE,
    "format_turns": False,
    "max_turn_silence": 300
}
API_ENDPOINT = f"wss://streaming.assemblyai.com/v3/ws?{urlencode(CONNECTION_PARAMS)}"
