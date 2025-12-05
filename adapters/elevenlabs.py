"""ElevenLabs adapter - Cloud TTS fallback.

ElevenLabs: https://elevenlabs.io
- Zero GPU (cloud service)
- Always available as fallback
- High-quality pre-made voices
"""
import logging
import os
import subprocess
import tempfile
from pathlib import Path

import requests

from .base import TTSBackend

logger = logging.getLogger(__name__)

ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1"

# Pre-made voice IDs
ELEVENLABS_VOICES = {
    "rachel": "21m00Tcm4TlvDq8ikWAM",
    "drew": "29vD33N1CtxCmqQRPOHJ",
    "paul": "5Q0t7uMcjvnagumLfvZi",
    "dave": "CYw3kZ02Hs0563khs1Fj",
    "sarah": "EXAVITQu4vr4xnSDxMaL",
    "adam": "pNInz6obpgDQGcFmaJgB",
    "sam": "yoZ06aMxZJJ28mfd3POQ",
    # Add more from https://api.elevenlabs.io/v1/voices
}

DEFAULT_VOICE = "adam"


class ElevenLabsBackend(TTSBackend):
    """ElevenLabs cloud TTS - zero GPU fallback."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("ELEVENLABS_API_KEY", "")
        self._voices_cache = None

    @property
    def name(self) -> str:
        return "elevenlabs"

    @property
    def port(self) -> int:
        return 0  # Cloud service

    @property
    def vram_gb(self) -> int:
        return 0  # Cloud service

    def is_available(self) -> bool:
        if not self.api_key:
            return False
        try:
            r = requests.get(
                f"{ELEVENLABS_API_URL}/user",
                headers={"xi-api-key": self.api_key},
                timeout=5
            )
            return r.status_code == 200
        except Exception:
            return False

    def resolve_voice_id(self, voice: str) -> str:
        voice_lower = voice.lower()
        if len(voice) > 15 and voice.isalnum():
            return voice  # Already a voice_id
        if voice_lower in ELEVENLABS_VOICES:
            return ELEVENLABS_VOICES[voice_lower]
        return ELEVENLABS_VOICES[DEFAULT_VOICE]

    def generate(self, text: str, voice_path: str = "", transcript: str = "") -> bytes:
        voice_id = self.resolve_voice_id(voice_path or DEFAULT_VOICE)

        response = requests.post(
            f"{ELEVENLABS_API_URL}/text-to-speech/{voice_id}",
            headers={"xi-api-key": self.api_key, "Content-Type": "application/json"},
            json={
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
            },
            timeout=60,
        )
        response.raise_for_status()

        # Convert MP3 to WAV
        return self._mp3_to_wav(response.content)

    def _mp3_to_wav(self, mp3_bytes: bytes) -> bytes:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(mp3_bytes)
            mp3_path = f.name

        wav_path = mp3_path.replace(".mp3", ".wav")
        try:
            subprocess.run(
                ["ffmpeg", "-y", "-i", mp3_path, "-ar", "44100", "-ac", "1", wav_path],
                capture_output=True, timeout=30
            )
            with open(wav_path, "rb") as f:
                return f.read()
        finally:
            Path(mp3_path).unlink(missing_ok=True)
            Path(wav_path).unlink(missing_ok=True)
