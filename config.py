import os
from pathlib import Path

# Helper to read a path from environment variables with a fallback

def _path(env, default):
    return Path(os.getenv(env, default))

VIDEO_PATH = _path('CRICCG_VIDEO_PATH', 'video.mp4')
AUDIO_PATH = _path('CRICCG_AUDIO_PATH', 'audio.wav')
TSV_PATH = _path('CRICCG_TSV_PATH', 'audio.tsv')
CSV_PATH = _path('CRICCG_CSV_PATH', 'transcript.csv')
WHISPER_JSON = _path('CRICCG_WHISPER_JSON', 'audio.json')
CLEAN_TRANSCRIPT = _path('CRICCG_CLEAN_TRANSCRIPT', 'transcript_clean.json')
LABELED_TRANSCRIPT = _path('CRICCG_LABELED_TRANSCRIPT', 'transcript_labeled.json')
CLIPS_DIR = _path('CRICCG_CLIPS_DIR', 'clips_temp')
OUTPUT_VIDEO = _path('CRICCG_OUTPUT_VIDEO', 'output.mp4')

FFMPEG_PATH = os.getenv('CRICCG_FFMPEG_PATH', 'ffmpeg')
OLLAMA_URL = os.getenv('CRICCG_OLLAMA_URL', 'http://localhost:11434/api/generate')
OLLAMA_MODEL = os.getenv('CRICCG_OLLAMA_MODEL', 'llama3.3:latest')
