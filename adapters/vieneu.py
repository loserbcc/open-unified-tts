"""VieNeu adapter - Vietnamese TTS.

VieNeu-TTS: https://github.com/pnnbao97/VieNeu-TTS
- CPU-based (works on Mac M-series)
- 10 Vietnamese voices (Northern & Southern accents)
- Runs via Docker at localhost:7860
"""
import logging
import os
import subprocess
import tempfile
from pathlib import Path

import requests

from .base import TTSBackend

logger = logging.getLogger(__name__)

# VieNeu runs on Docker (or host configured via env)
VIENEU_HOST = os.environ.get("VIENEU_HOST", "localhost")
VIENEU_PORT = int(os.environ.get("VIENEU_PORT", "7860"))
VIENEU_URL = f"http://{VIENEU_HOST}:{VIENEU_PORT}"

# Vietnamese voice presets
VIENEU_VOICES = {
    # Northern accents
    "tuyen": "miền bắc nam 1",
    "binh": "miền bắc nam 2",
    "huong": "miền bắc nữ 1",
    "ly": "miền bắc nữ 2",
    "ngoc": "miền bắc nữ 3",
    # Southern accents
    "vinh": "miền nam nam 1",
    "nguyen": "miền nam nam 2",
    "son": "miền nam nam 3",
    "doan": "miền nam nữ 1",
    "dung": "miền nam nữ 2",
    # Aliases
    "male_north": "miền bắc nam 1",
    "male_north_02": "miền bắc nam 2",
    "female_north": "miền bắc nữ 1",
    "female_north_02": "miền bắc nữ 2",
    "male_south": "miền nam nam 1",
    "male_south_02": "miền nam nam 2",
    "female_south": "miền nam nữ 1",
    "female_south_02": "miền nam nữ 2",
}


class VieNeuBackend(TTSBackend):
    """Vietnamese TTS via VieNeu Docker container."""

    @property
    def name(self) -> str:
        return "vieneu"

    @property
    def port(self) -> int:
        return VIENEU_PORT

    @property
    def vram_gb(self) -> int:
        return 0  # CPU-only

    def is_available(self) -> bool:
        """Check if VieNeu container is running."""
        try:
            resp = requests.get(f"{VIENEU_URL}/", timeout=3)
            return resp.status_code == 200
        except Exception:
            return False

    def get_voices(self) -> list[str]:
        """Return available Vietnamese voices."""
        return list(VIENEU_VOICES.keys())

    def synthesize(self, text: str, voice: str = "huong") -> bytes:
        """Generate Vietnamese speech via Gradio API.

        Args:
            text: Vietnamese text to synthesize
            voice: Voice name (huong, tuyen, doan, vinh, etc.)

        Returns:
            WAV audio bytes
        """
        # Map voice name to internal VieNeu format
        internal_voice = VIENEU_VOICES.get(voice.lower(), "miền bắc nữ 1")

        try:
            from gradio_client import Client

            client = Client(VIENEU_URL)
            result = client.predict(
                text=text,
                speaker=internal_voice,
                speed=1.0,
                api_name="/synthesize"
            )

            # Result is path to generated audio file
            if result and Path(result).exists():
                with open(result, "rb") as f:
                    audio_data = f.read()
                # Clean up temp file
                Path(result).unlink(missing_ok=True)
                return audio_data

            raise RuntimeError("VieNeu returned no audio")

        except ImportError:
            # Fallback: direct HTTP API call
            logger.warning("gradio_client not installed, using HTTP fallback")
            return self._synthesize_http(text, internal_voice)

    def _synthesize_http(self, text: str, voice: str) -> bytes:
        """HTTP fallback for synthesis."""
        # VieNeu Gradio API endpoint
        resp = requests.post(
            f"{VIENEU_URL}/api/predict",
            json={
                "data": [text, voice, 1.0],
                "fn_index": 0,
            },
            timeout=60,
        )
        resp.raise_for_status()

        data = resp.json()
        if "data" in data and data["data"]:
            audio_path = data["data"][0]
            # Fetch the audio file
            audio_resp = requests.get(f"{VIENEU_URL}/file={audio_path}", timeout=30)
            return audio_resp.content

        raise RuntimeError("VieNeu HTTP API returned no audio")
