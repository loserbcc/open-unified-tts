"""VibeVoice adapter - Real-time streaming TTS.

Microsoft's streaming TTS model:
- ~2GB VRAM (can run alongside other models!)
- 300ms first-audio latency
- 7 voice presets
"""
import logging
import os
from pathlib import Path

import requests

from .base import TTSBackend

logger = logging.getLogger(__name__)

VIBEVOICE_VOICES = {
    "emma": "en-Emma_woman",
    "carter": "en-Carter_man",
    "davis": "en-Davis_man",
    "frank": "en-Frank_man",
    "grace": "en-Grace_woman",
    "mike": "en-Mike_man",
    "samuel": "in-Samuel_man",  # Indian accent
}


class VibeVoiceBackend(TTSBackend):
    """VibeVoice real-time streaming TTS."""

    def __init__(self, host: str = None):
        self.host = host or os.environ.get("VIBEVOICE_HOST", "http://localhost:8086")

    @property
    def name(self) -> str:
        return "vibevoice"

    @property
    def port(self) -> int:
        return 8086

    @property
    def vram_gb(self) -> int:
        return 2

    def is_available(self) -> bool:
        try:
            r = requests.get(f"{self.host}/health", timeout=2)
            if r.status_code == 200:
                return r.json().get("model_loaded", False)
            return False
        except Exception:
            return False

    def generate(self, text: str, voice_path: str, transcript: str) -> bytes:
        voice_name = voice_path
        if "/" in voice_path:
            voice_name = Path(voice_path).parent.name

        voice_lower = voice_name.lower()
        if voice_lower in VIBEVOICE_VOICES:
            voice_name = voice_lower.capitalize()

        response = requests.post(
            f"{self.host}/v1/audio/speech",
            json={
                "input": text,
                "voice": voice_name,
                "model": "vibevoice-realtime-0.5b",
                "response_format": "wav",
            },
            timeout=120,
        )
        response.raise_for_status()
        return response.content
