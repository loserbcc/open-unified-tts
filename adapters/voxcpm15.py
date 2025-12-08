"""VoxCPM 1.5 adapter - High-quality voice cloning via OpenAI-compatible API.

VoxCPM 1.5 features:
- 44.1kHz sample rate (2x improvement over VoxCPM)
- ~8GB VRAM (lighter than original VoxCPM)
- 88+ character voices pre-loaded
- OpenAI-compatible API endpoint
- Fleet discovery via fleet_config.py (if present)
"""
import logging
import os
from pathlib import Path

import httpx

from .base import TTSBackend

logger = logging.getLogger(__name__)

# Try to import fleet config, fall back to single default
try:
    from fleet_config import VOXCPM15_HOSTS as FLEET_HOSTS
except ImportError:
    FLEET_HOSTS = ["http://localhost:7870"]


class VoxCPM15Backend(TTSBackend):
    """VoxCPM 1.5 (Tokenizer-free Voice Cloning) via OpenAI-compatible API with fleet discovery."""

    def __init__(self, host: str = None):
        self._explicit_host = host or os.environ.get("VOXCPM15_HOST")
        self._discovered_host = None
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

    @property
    def host(self) -> str:
        """Return the active host (explicit, discovered, or triggers discovery)."""
        if self._explicit_host:
            return self._explicit_host.rstrip("/")
        if self._discovered_host:
            return self._discovered_host
        # Auto-discover on first access
        self._discovered_host = self._discover_host()
        return self._discovered_host or FLEET_HOSTS[0]

    def _check_host(self, host: str) -> bool:
        """Check if a specific host has VoxCPM 1.5 available."""
        try:
            r = httpx.get(f"{host}/health", timeout=2)
            return r.status_code == 200
        except Exception:
            return False

    def _discover_host(self) -> str | None:
        """Find first available VoxCPM 1.5 host in fleet."""
        for host in FLEET_HOSTS:
            if self._check_host(host):
                logger.info(f"VoxCPM 1.5 discovered at {host}")
                return host
        return None

    def is_available(self) -> bool:
        """Check if VoxCPM 1.5 endpoint is responding."""
        # If explicit host set, only check that
        if self._explicit_host:
            return self._check_host(self._explicit_host.rstrip("/"))

        # Try cached discovered host first
        if self._discovered_host and self._check_host(self._discovered_host):
            return True

        # Discover across fleet
        self._discovered_host = self._discover_host()
        return self._discovered_host is not None

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
