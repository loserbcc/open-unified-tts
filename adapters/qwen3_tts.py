"""Qwen3-TTS adapter - Multilingual TTS via OpenAI-compatible API.

Qwen3-TTS (malaysia-ai/Qwen3-1.7B-Multilingual-TTS) runs on Mother:
- 24kHz sample rate
- ~6-8GB VRAM (1.7B parameter model)
- 7 languages: English, Chinese, Vietnamese, Japanese, Korean, French, Tamil
- OpenAI-compatible API endpoint
"""
import logging
import os
from pathlib import Path

import httpx

from .base import TTSBackend

logger = logging.getLogger(__name__)


class Qwen3TTSBackend(TTSBackend):
    """Qwen3-TTS (Multilingual Text-to-Speech) via OpenAI-compatible API."""

    def __init__(self, host: str = None):
        self.host = (host or os.environ.get("QWEN3_TTS_HOST", "http://mother:7871")).rstrip("/")
        self._voices = None

    @property
    def name(self) -> str:
        return "qwen3_tts"

    @property
    def port(self) -> int:
        return 7871

    @property
    def vram_gb(self) -> int:
        return 8  # 1.7B model + neucodec

    def is_available(self) -> bool:
        """Check if Qwen3-TTS endpoint is responding."""
        try:
            r = httpx.get(f"{self.host}/health", timeout=3)
            return r.status_code == 200
        except Exception:
            return False

    def list_voices(self) -> list[str]:
        """Get list of available voices from server."""
        if self._voices is None:
            try:
                r = httpx.get(f"{self.host}/v1/voices", timeout=5)
                if r.status_code == 200:
                    self._voices = r.json().get("voices", ["jenny", "default"])
                else:
                    self._voices = ["jenny", "default"]
            except Exception:
                self._voices = ["jenny", "default"]
        return self._voices

    def generate(self, text: str, voice_path: str = "", transcript: str = "") -> bytes:
        """Generate TTS using Qwen3-TTS OpenAI-compatible API.

        Args:
            text: Text to synthesize
            voice_path: Path to voice reference (extracts voice name from path)
                        e.g., "/path/to/voice_clones/jenny/reference.wav" -> "jenny"
            transcript: Ignored (Qwen3-TTS uses preset voices)

        Returns:
            WAV audio bytes (24kHz)
        """
        # Extract voice name from path like "/path/voice_clones/jenny/reference.wav"
        if voice_path:
            voice = Path(voice_path).parent.name
        else:
            voice = "jenny"  # Default voice

        logger.info(f"Qwen3-TTS generating: {len(text)} chars with voice '{voice}'")

        try:
            response = httpx.post(
                f"{self.host}/v1/audio/speech",
                json={
                    "input": text,
                    "voice": voice,
                    "model": "qwen3-tts",
                    "response_format": "wav",
                },
                timeout=60,
            )

            if response.status_code != 200:
                error_detail = response.text
                raise RuntimeError(f"Qwen3-TTS error: {response.status_code} - {error_detail}")

            return response.content

        except httpx.TimeoutException:
            raise RuntimeError("Qwen3-TTS request timed out")
        except Exception as e:
            raise RuntimeError(f"Qwen3-TTS request failed: {e}")
