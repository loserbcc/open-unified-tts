"""VoxCPM 1.5 adapter - High-quality voice cloning via OpenAI-compatible API.

VoxCPM 1.5 runs on Mother's RTX PRO 6000 Blackwell GPU:
- 44.1kHz sample rate (2x improvement over VoxCPM)
- ~8GB VRAM (lighter than original VoxCPM)
- 88+ character voices pre-loaded
- OpenAI-compatible API endpoint
"""
import logging
import os
from pathlib import Path

import httpx

from .base import TTSBackend

logger = logging.getLogger(__name__)


class VoxCPM15Backend(TTSBackend):
    """VoxCPM 1.5 (Tokenizer-free Voice Cloning) via OpenAI-compatible API."""

    def __init__(self, host: str = None):
        self.host = (host or os.environ.get("VOXCPM15_HOST", "http://mother:7870")).rstrip("/")
        self._voices = None

    @property
    def name(self) -> str:
        return "voxcpm15"

    @property
    def port(self) -> int:
        return 7870

    @property
    def vram_gb(self) -> int:
        return 8  # Much lighter on Blackwell

    def is_available(self) -> bool:
        """Check if VoxCPM 1.5 endpoint is responding."""
        try:
            r = httpx.get(f"{self.host}/health", timeout=3)
            return r.status_code == 200
        except Exception:
            return False

    def get_voices(self) -> list[str]:
        """Get list of available voices from server."""
        if self._voices is None:
            try:
                r = httpx.get(f"{self.host}/v1/voices", timeout=5)
                if r.status_code == 200:
                    self._voices = r.json().get("voices", ["default"])
                else:
                    self._voices = ["default"]
            except Exception:
                self._voices = ["default"]
        return self._voices

    def generate(self, text: str, voice_path: str = "", transcript: str = "") -> bytes:
        """Generate TTS using VoxCPM 1.5 OpenAI-compatible API.

        Args:
            text: Text to synthesize
            voice_path: Path to voice reference (extracts voice name from path)
                        e.g., "/path/to/voice_clones/yoda/reference.wav" -> "yoda"
            transcript: Ignored (VoxCPM 1.5 uses pre-stored transcripts)

        Returns:
            WAV audio bytes (44.1kHz)
        """
        # Extract voice name from path like "/path/voice_clones/yoda/reference.wav"
        if voice_path:
            voice = Path(voice_path).parent.name
        else:
            voice = "default"

        logger.info(f"VoxCPM 1.5 generating: {len(text)} chars with voice '{voice}'")

        try:
            response = httpx.post(
                f"{self.host}/v1/audio/speech",
                json={
                    "input": text,
                    "voice": voice,
                    "model": "voxcpm-1.5",
                    "response_format": "wav",
                },
                timeout=60,
            )

            if response.status_code != 200:
                error_detail = response.text
                raise RuntimeError(f"VoxCPM 1.5 error: {response.status_code} - {error_detail}")

            return response.content

        except httpx.TimeoutException:
            raise RuntimeError("VoxCPM 1.5 request timed out")
        except Exception as e:
            raise RuntimeError(f"VoxCPM 1.5 request failed: {e}")

    def generate_with_reference(
        self,
        text: str,
        voice_path: str,
        transcript: str
    ) -> bytes:
        """Generate with explicit reference audio (for new voice cloning).

        This uploads reference audio to create a temporary voice clone.
        For permanent voices, add files to voice_refs/ on the server.
        """
        logger.info(f"VoxCPM 1.5 cloning: {len(text)} chars from {voice_path}")

        try:
            with open(voice_path, "rb") as f:
                files = {"reference_audio": ("reference.wav", f, "audio/wav")}
                data = {
                    "text": text,
                    "voice_name": "temp_clone",
                    "reference_text": transcript,
                }
                response = httpx.post(
                    f"{self.host}/v1/clone",
                    files=files,
                    data=data,
                    timeout=90,
                )

            if response.status_code != 200:
                raise RuntimeError(f"VoxCPM 1.5 clone error: {response.text}")

            return response.content

        except Exception as e:
            raise RuntimeError(f"VoxCPM 1.5 clone failed: {e}")
