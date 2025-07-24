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
    "min_end_of_turn_silence_when_confident": 1000, # 1s
    "max_turn_silence": 3000 # 3s
}
API_ENDPOINT = f"wss://streaming.assemblyai.com/v3/ws?{urlencode(CONNECTION_PARAMS)}"

SILENCE_LIMIT = 5 # in seconds