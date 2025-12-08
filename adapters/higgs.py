"""Higgs Audio adapter - Generative voice creation from descriptions.

Higgs Audio creates voices from scene descriptions, not reference audio.
- ~15GB VRAM
- Seed-based reproducibility
- Saved characters
- Fleet discovery via fleet_config.py (if present)
"""
import logging
import os
from pathlib import Path
from typing import Optional, Dict

import requests

from .base import TTSBackend

logger = logging.getLogger(__name__)

# Try to import fleet config, fall back to single default
try:
    from fleet_config import HIGGS_HOSTS as FLEET_HOSTS
except ImportError:
    FLEET_HOSTS = ["http://localhost:8085"]


class HiggsBackend(TTSBackend):
    """Higgs Audio generative voice backend with fleet auto-discovery."""

    def __init__(self, host: str = None):
        self._explicit_host = host or os.environ.get("HIGGS_HOST")
        self._discovered_host = None
        self._characters_cache: Optional[Dict] = None
        self._cache_time: float = 0

    @property
    def name(self) -> str:
        return "higgs"

    @property
    def port(self) -> int:
        return 8085

    @property
    def vram_gb(self) -> int:
        return 15

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
        """Check if a specific host has Higgs available."""
        try:
            r = requests.get(f"{host}/health", timeout=2)
            if r.status_code == 200:
                return r.json().get("model_loaded", False)
            return False
        except Exception:
            return False

    def _discover_host(self) -> str | None:
        """Find first available Higgs host in fleet."""
        for host in FLEET_HOSTS:
            if self._check_host(host):
                logger.info(f"Higgs discovered at {host}")
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

    def get_characters(self) -> Dict:
        import time
        if self._characters_cache and (time.time() - self._cache_time) < 30:
            return self._characters_cache

        try:
            r = requests.get(f"{self.host}/v1/characters", timeout=5)
            if r.status_code == 200:
                self._characters_cache = {c["name"]: c for c in r.json().get("characters", [])}
                self._cache_time = time.time()
                return self._characters_cache
        except Exception:
            pass
        return {}

    def generate(self, text: str, voice_path: str, transcript: str) -> bytes:
        voice_name = voice_path
        if "/" in voice_path:
            voice_name = Path(voice_path).parent.name

        response = requests.post(
            f"{self.host}/v1/audio/speech",
            json={"input": text, "voice": voice_name},
            timeout=120,
        )
        response.raise_for_status()
        return response.content

    def create_character(self, name: str, scene_description: str, seed: int = None) -> dict:
        """Create a new generative character."""
        payload = {"name": name, "scene_description": scene_description, "generate_sample": True}
        if seed:
            payload["seed"] = seed

        response = requests.post(f"{self.host}/v1/characters", json=payload, timeout=180)
        response.raise_for_status()
        self._characters_cache = None
        return response.json()
