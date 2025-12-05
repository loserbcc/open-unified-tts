"""OpenAudio (Fish Speech) adapter - Zero-shot voice cloning.

Fish Speech: https://github.com/fishaudio/fish-speech
- ~5GB VRAM
- Fast inference
- Reference audio + transcript for cloning
"""
import base64
import logging
import os

import requests

from .base import TTSBackend

logger = logging.getLogger(__name__)


class OpenAudioBackend(TTSBackend):
    """OpenAudio S1-Mini (Fish Speech) backend."""

    def __init__(self, host: str = None):
        self.host = host or os.environ.get("OPENAUDIO_HOST", "http://localhost:9877")

    @property
    def name(self) -> str:
        return "openaudio"

    @property
    def port(self) -> int:
        return 9877

    @property
    def vram_gb(self) -> int:
        return 5

    def is_available(self) -> bool:
        try:
            r = requests.get(f"{self.host}/v1/health", timeout=2)
            return r.status_code == 200
        except Exception:
            return False

    def generate(self, text: str, voice_path: str, transcript: str) -> bytes:
        with open(voice_path, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode()

        response = requests.post(
            f"{self.host}/v1/tts",
            json={
                "text": text,
                "format": "wav",
                "references": [{"audio": audio_b64, "text": transcript}],
            },
            timeout=120,
        )
        response.raise_for_status()
        return response.content
