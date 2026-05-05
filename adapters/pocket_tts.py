"""Pocket-TTS adapter — lightweight local TTS via OpenAI-compatible API.

Pocket-TTS is a small footprint TTS engine designed for laptop-class GPUs.
Returns 24 kHz mono WAV. Supports both built-in voices and voice clones.

Endpoint shape (verified against engine v1):
    GET  /health           → {"status": "ok", "engine": "pocket-tts", ...}
    GET  /v1/voices        → {"voices": [{"name": "...", "type": "builtin"|"clone"}]}
    POST /v1/audio/speech  → WAV bytes
        body: {"input": str, "voice": str, "response_format": "wav"}

Default host points at the local engine port; override with POCKET_TTS_HOST.
"""
import logging
import os
from pathlib import Path

import httpx

from .base import TTSBackend

logger = logging.getLogger(__name__)


class PocketTTSBackend(TTSBackend):
    """Pocket-TTS via OpenAI-compatible API."""

    def __init__(self, host: str = None):
        self.host = (host or os.environ.get("POCKET_TTS_HOST", "http://localhost:8209")).rstrip("/")
        self._voices = None
        self._default_voice = None

    @property
    def name(self) -> str:
        return "pocket_tts"

    @property
    def port(self) -> int:
        return 8209

    @property
    def vram_gb(self) -> int:
        return 4  # Designed for laptop-class GPUs

    def is_available(self) -> bool:
        try:
            r = httpx.get(f"{self.host}/health", timeout=3)
            if r.status_code != 200:
                return False
            data = r.json()
            return data.get("engine") == "pocket-tts"
        except Exception:
            return False

    def list_voices(self) -> list[str]:
        if self._voices is None:
            try:
                r = httpx.get(f"{self.host}/v1/voices", timeout=5)
                if r.status_code == 200:
                    voices_data = r.json().get("voices", [])
                    self._voices = [v["name"] for v in voices_data if "name" in v]
                else:
                    self._voices = []
            except Exception as e:
                logger.warning(f"Pocket-TTS voice list failed: {e}")
                self._voices = []

            if not self._voices:
                self._voices = ["alba"]

            try:
                r = httpx.get(f"{self.host}/health", timeout=3)
                if r.status_code == 200:
                    self._default_voice = r.json().get("default")
            except Exception:
                pass

        return self._voices

    def generate(self, text: str, voice_path: str = "", transcript: str = "") -> bytes:
        """Generate TTS using Pocket-TTS OpenAI-compatible API.

        Args:
            text: Text to synthesize
            voice_path: Voice name or path containing voice name as parent dir.
                        e.g. "ryan" or "/voices/ryan/reference.wav"
            transcript: Ignored (Pocket-TTS uses preset voices and registered clones)

        Returns:
            WAV audio bytes (24 kHz mono)
        """
        if voice_path:
            candidate = Path(voice_path)
            voice = candidate.parent.name if candidate.parent.name else candidate.stem
        else:
            voice = self._default_voice or "alba"

        logger.info(f"Pocket-TTS generating: {len(text)} chars with voice '{voice}'")

        try:
            response = httpx.post(
                f"{self.host}/v1/audio/speech",
                json={
                    "input": text,
                    "voice": voice,
                    "model": "pocket-tts",
                    "response_format": "wav",
                },
                timeout=60,
            )
            if response.status_code != 200:
                raise RuntimeError(f"Pocket-TTS error: {response.status_code} - {response.text}")
            return response.content
        except httpx.TimeoutException:
            raise RuntimeError("Pocket-TTS request timed out")
        except Exception as e:
            raise RuntimeError(f"Pocket-TTS request failed: {e}")
