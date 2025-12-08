"""VibeVoice adapter - Real-time streaming TTS.

Microsoft's streaming TTS model:
- ~2GB VRAM (can run alongside other models!)
- 300ms first-audio latency
- 7 voice presets
- Fleet discovery via fleet_config.py (if present)
"""
import logging
import os
from pathlib import Path

import requests

from .base import TTSBackend

logger = logging.getLogger(__name__)

# Try to import fleet config, fall back to single default
try:
    from fleet_config import VIBEVOICE_HOSTS as FLEET_HOSTS
except ImportError:
    FLEET_HOSTS = ["http://localhost:8086"]

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
    """VibeVoice real-time streaming TTS with fleet auto-discovery."""

    def __init__(self, host: str = None):
        self._explicit_host = host or os.environ.get("VIBEVOICE_HOST")
        self._discovered_host = None

    @property
    def name(self) -> str:
        return "vibevoice"

    @property
    def port(self) -> int:
        return 8086

    @property
    def vram_gb(self) -> int:
        return 2

    @property
    def host(self) -> str:
        """Return the active host (explicit, discovered, or triggers discovery)."""
        if self._explicit_host:
            return self._explicit_host
        if self._discovered_host:
            return self._discovered_host
        # Auto-discover on first access
        self._discovered_host = self._discover_host()
        return self._discovered_host or FLEET_HOSTS[0]

    def _check_host(self, host: str) -> bool:
        """Check if a specific host has VibeVoice available."""
        try:
            r = requests.get(f"{host}/health", timeout=2)
            if r.status_code == 200:
                return r.json().get("model_loaded", False)
            return False
        except Exception:
            return False

    def _discover_host(self) -> str | None:
        """Find first available VibeVoice host in fleet."""
        for host in FLEET_HOSTS:
            if self._check_host(host):
                logger.info(f"VibeVoice discovered at {host}")
                return host
        return None

    def is_available(self) -> bool:
        # If explicit host set, only check that
        if self._explicit_host:
            return self._check_host(self._explicit_host)

        # Try cached discovered host first
        if self._discovered_host and self._check_host(self._discovered_host):
            return True

        # Discover across fleet
        self._discovered_host = self._discover_host()
        return self._discovered_host is not None

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
