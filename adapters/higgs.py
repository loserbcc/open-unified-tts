"""Higgs Audio adapter - Generative voice creation from descriptions.

Higgs Audio creates voices from scene descriptions, not reference audio.
- ~15GB VRAM
- Seed-based reproducibility
- Saved characters
"""
import logging
import os
from pathlib import Path
from typing import Optional, Dict

import requests

from .base import TTSBackend

logger = logging.getLogger(__name__)


class HiggsBackend(TTSBackend):
    """Higgs Audio generative voice backend."""

    def __init__(self, host: str = None):
        self.host = host or os.environ.get("HIGGS_HOST", "http://localhost:8085")
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

    def is_available(self) -> bool:
        try:
            r = requests.get(f"{self.host}/health", timeout=2)
            if r.status_code == 200:
                return r.json().get("model_loaded", False)
            return False
        except Exception:
            return False

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
