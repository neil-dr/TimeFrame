import pyaudio
from urllib.parse import urlencode
import os
from dotenv import load_dotenv

load_dotenv()

FRAMES_PER_BUFFER = 800
SAMPLE_RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16

# --- Configuration ---
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
CONNECTION_PARAMS = {
    "sample_rate": SAMPLE_RATE,
    "format_turns": False,
    "max_turn_silence": 2400
}
API_ENDPOINT = f"wss://streaming.assemblyai.com/v3/ws?{urlencode(CONNECTION_PARAMS)}"
