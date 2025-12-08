"""Maya1 adapter - Open Source Emotional TTS with natural language voice design.

Maya1: https://huggingface.co/maya-research/maya1
- CPU-only (runs on host, ~1.6GB RAM)
- Emotional presets + custom voice descriptions
- Supports emotion tags: <angry>, <chuckle>, <cry>, <laugh>, <sigh>, <whisper>, etc.
- Port 8090 (Gradio interface)
- Fleet discovery via fleet_config.py (if present)
"""
import logging
import os
import tempfile
from typing import Optional

import requests
from gradio_client import Client

from .base import TTSBackend

logger = logging.getLogger(__name__)

# Try to import fleet config, fall back to single default
try:
    from fleet_config import MAYA1_HOSTS as FLEET_HOSTS
except ImportError:
    FLEET_HOSTS = [{"name": "default", "url": "http://localhost:8090"}]

# Preset characters available in Maya1
MAYA1_VOICES = {
    "male_american": {
        "preset": "Male American",
        "description": "Realistic male voice in the 20s age with a american accent. High pitch, raspy timbre, brisk pacing, neutral tone delivery at medium intensity, viral_content domain, short_form_narrator role, neutral delivery",
    },
    "female_british": {
        "preset": "Female British",
        "description": "Realistic female voice in the 30s age with a british accent. Normal pitch, throaty timbre, conversational pacing, sarcastic tone delivery at low intensity, podcast domain, interviewer role, formal delivery",
    },
    "robot": {
        "preset": "Robot",
        "description": "Creative, ai_machine_voice character. Male voice in their 30s with a american accent. High pitch, robotic timbre, slow pacing, sad tone at medium intensity.",
    },
    "singer": {
        "preset": "Singer",
        "description": "Creative, animated_cartoon character. Male voice in their 30s with a american accent. High pitch, deep timbre, slow pacing, sarcastic tone at medium intensity.",
    },
    # Custom emotions/styles (use description directly)
    "narrator": {
        "preset": None,
        "description": "Professional male narrator in their 40s with a warm, rich baritone. Measured pacing, clear diction, authoritative yet approachable tone.",
    },
    "excited": {
        "preset": None,
        "description": "Energetic young voice, high pitch, fast pacing, enthusiastic and animated delivery with natural excitement.",
    },
    "calm": {
        "preset": None,
        "description": "Soothing voice with slow pacing, soft timbre, gentle and reassuring tone perfect for meditation or relaxation.",
    },
    "dramatic": {
        "preset": None,
        "description": "Theatrical voice with dynamic range, emphatic delivery, building tension and emotion in storytelling.",
    },
}


class Maya1Backend(TTSBackend):
    """Maya1 emotional TTS backend with fleet auto-discovery."""

    def __init__(self, hosts: list = None):
        if hosts is None:
            env_hosts = os.environ.get("MAYA1_HOSTS")
            if env_hosts:
                hosts = [{"name": "env", "url": env_hosts}]
            else:
                hosts = FLEET_HOSTS
        self.hosts = hosts
        self._active_host: Optional[dict] = None
        self._client: Optional[Client] = None

    @property
    def name(self) -> str:
        return "maya1"

    @property
    def port(self) -> int:
        return 8090

    @property
    def vram_gb(self) -> int:
        return 0  # CPU-only, uses RAM not VRAM

    def _find_active_host(self) -> Optional[dict]:
        """Find first available Maya1 server."""
        for host in self.hosts:
            try:
                r = requests.get(f"{host['url']}/", timeout=3)
                if r.status_code == 200:
                    return host
            except Exception:
                continue
        return None

    def is_available(self) -> bool:
        """Check if Maya1 is running."""
        self._active_host = self._find_active_host()
        return self._active_host is not None

    def _get_client(self) -> Client:
        """Get or create Gradio client."""
        if self._client is None or self._active_host is None:
            self._active_host = self._find_active_host()
            if not self._active_host:
                raise RuntimeError("No Maya1 server available")
            self._client = Client(self._active_host["url"])
        return self._client

    def generate(self, text: str, voice_path: str, transcript: str) -> bytes:
        """Generate emotional TTS audio.

        Args:
            text: Text to synthesize (can include emotion tags like <laugh>, <sigh>)
            voice_path: Voice name from MAYA1_VOICES or custom description
            transcript: Unused for Maya1

        Returns:
            WAV audio bytes
        """
        client = self._get_client()

        # Determine preset and description from voice_path
        voice_name = os.path.basename(voice_path).lower().replace(".wav", "").replace(".mp3", "")

        if voice_name in MAYA1_VOICES:
            voice_config = MAYA1_VOICES[voice_name]
            preset_name = voice_config["preset"]
            description = voice_config["description"]
        else:
            # Treat voice_path as a custom description
            preset_name = None
            description = voice_path if len(voice_path) > 20 else MAYA1_VOICES["male_american"]["description"]

        logger.info(f"Maya1 generating: preset={preset_name}, voice={voice_name}")

        try:
            # Call Gradio API
            # fn_index for generate_speech based on app.py structure
            result = client.predict(
                preset_name or "Male American",  # preset_dropdown
                description,                      # description_input
                text,                            # text_input
                0.4,                             # temperature_slider
                1500,                            # max_tokens_slider
                api_name="/generate_speech"
            )

            # Result is (audio_path, status_message)
            audio_path = result[0] if isinstance(result, tuple) else result

            if audio_path is None:
                status = result[1] if isinstance(result, tuple) else "Unknown error"
                raise RuntimeError(f"Maya1 generation failed: {status}")

            # Read the audio file
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()

            # Clean up temp file if it's in a temp directory
            if "/tmp" in str(audio_path):
                try:
                    os.remove(audio_path)
                except Exception:
                    pass

            return audio_bytes

        except Exception as e:
            logger.error(f"Maya1 generation error: {e}")
            raise RuntimeError(f"Maya1 generation failed: {e}")

    def list_voices(self) -> list[str]:
        """List available Maya1 voices."""
        return list(MAYA1_VOICES.keys())
