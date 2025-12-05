"""Kyutai/Moshi adapter - Emotional TTS with preset voices.

Moshi: https://github.com/kyutai-labs/moshi
- ~4GB VRAM
- Emotion presets (happy, sad, calm, etc.)
- Multiple host failover support
"""
import logging
import os
from typing import Optional

import requests

from .base import TTSBackend

logger = logging.getLogger(__name__)

# Emotion presets (not voice cloning)
KYUTAI_VOICES = {
    "happy": "Cheerful and upbeat",
    "sad": "Thoughtful and empathetic",
    "angry": "Assertive and intense",
    "calm": "Peaceful and soothing",
    "confused": "Curious and questioning",
    "fearful": "Cautious and alert",
    "sleepy": "Relaxed and drowsy",
    "neutral": "Balanced and professional",
    "default": "Default neutral voice",
}


class KyutaiBackend(TTSBackend):
    """Kyutai/Moshi emotional TTS backend."""

    def __init__(self, hosts: list = None):
        if hosts is None:
            host_str = os.environ.get("KYUTAI_HOSTS", "http://localhost:8899")
            hosts = [{"name": "default", "url": host_str}]
        self.hosts = hosts
        self._active_host: Optional[dict] = None

    @property
    def name(self) -> str:
        return "kyutai"

    @property
    def port(self) -> int:
        return 8899

    @property
    def vram_gb(self) -> int:
        return 4

    def _find_active_host(self) -> Optional[dict]:
        for host in self.hosts:
            try:
                r = requests.get(f"{host['url']}/", timeout=2)
                if r.status_code == 200:
                    return host
            except Exception:
                continue
        return None

    def is_available(self) -> bool:
        self._active_host = self._find_active_host()
        return self._active_host is not None

    def generate(self, text: str, voice_path: str, transcript: str) -> bytes:
        if not self._active_host:
            self._active_host = self._find_active_host()
            if not self._active_host:
                raise RuntimeError("No Kyutai server available")

        # Extract emotion from voice_path
        voice_name = os.path.basename(os.path.dirname(voice_path)) if "/" in voice_path else voice_path
        emotion = voice_name.lower() if voice_name.lower() in KYUTAI_VOICES else "default"

        response = requests.post(
            f"{self._active_host['url']}/synthesize",
            json={"text": text, "voice": emotion, "return_audio": True},
            timeout=30,
        )
        response.raise_for_status()

        if response.headers.get("content-type", "").startswith("audio/"):
            return response.content

        data = response.json()
        if "audio_url" in data:
            audio_response = requests.get(f"{self._active_host['url']}{data['audio_url']}", timeout=30)
            return audio_response.content

        raise RuntimeError("Kyutai returned no audio")
