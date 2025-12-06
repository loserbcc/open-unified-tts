"""Kokoro adapter - High-quality neural TTS.

Kokoro: https://github.com/remsky/Kokoro-FastAPI
- Lightweight (runs on CPU or GPU)
- Fast inference
- OpenAI-compatible API
- 50+ built-in voices

Format Handling:
- When chunking is needed (long text): requests WAV for seamless stitching
- When no chunking needed (short text): can use MP3 directly for efficiency
"""
import logging
import os

import requests

from .base import TTSBackend

logger = logging.getLogger(__name__)

# All available Kokoro voices (for routing in server)
KOKORO_VOICES = {
    # American Female
    "af_alloy", "af_aoede", "af_bella", "af_heart", "af_jadzia",
    "af_jessica", "af_kore", "af_nicole", "af_nova", "af_river",
    "af_sarah", "af_sky", "af_v0", "af_v0bella", "af_v0irulan",
    "af_v0nicole", "af_v0sarah", "af_v0sky",
    # American Male
    "am_adam", "am_echo", "am_eric", "am_fenrir", "am_liam",
    "am_michael", "am_onyx", "am_puck", "am_santa", "am_v0adam",
    "am_v0gurney", "am_v0michael",
    # British Female
    "bf_alice", "bf_emma", "bf_lily", "bf_v0emma", "bf_v0isabella",
    # British Male
    "bm_daniel", "bm_fable", "bm_george", "bm_lewis", "bm_v0george", "bm_v0lewis",
    # Other voices
    "ef_dora", "em_alex", "em_santa", "ff_siwis",
    "hf_alpha", "hf_beta", "hm_omega", "hm_psi",
    "if_sara", "im_nicola",
    "jf_alpha", "jf_gongitsune", "jf_nezumi", "jf_tebukuro", "jm_kumo",
    "pf_dora", "pm_alex",
    # OpenAI voice name mappings
    "alloy", "echo", "fable", "onyx", "nova", "shimmer",
}


class KokoroBackend(TTSBackend):
    """Kokoro neural TTS backend.

    Supports configurable audio format:
    - 'wav': Best for chunking/stitching (lossless, required for crossfade)
    - 'mp3': Best for direct output (smaller files, no quality loss for single chunks)
    """

    # Map OpenAI voice names to Kokoro voices
    VOICE_MAP = {
        "alloy": "af_alloy",
        "echo": "am_echo",
        "fable": "bm_fable",
        "onyx": "am_onyx",
        "nova": "af_nova",
        "shimmer": "af_sky",
    }

    def __init__(self, host: str = None):
        self.host = host or os.environ.get("KOKORO_HOST", "http://localhost:8880")

    @property
    def name(self) -> str:
        return "kokoro"

    @property
    def port(self) -> int:
        return 8880

    @property
    def vram_gb(self) -> int:
        return 0  # Can run on CPU

    def is_available(self) -> bool:
        try:
            r = requests.get(f"{self.host}/health", timeout=2)
            return r.status_code == 200
        except Exception:
            return False

    def _map_voice(self, voice: str) -> str:
        """Map OpenAI voice names to Kokoro voices."""
        voice_lower = voice.lower()
        # Map OpenAI standard voices
        if voice_lower in self.VOICE_MAP:
            return self.VOICE_MAP[voice_lower]
        # Already a Kokoro voice
        return voice_lower

    def generate(self, text: str, voice_path: str = "af_bella", transcript: str = "",
                 response_format: str = "wav", **kwargs) -> bytes:
        """Generate speech using Kokoro.

        Args:
            text: Text to synthesize
            voice_path: Voice name (Kokoro native or mapped)
            transcript: Ignored for Kokoro (no voice cloning needed)
            response_format: Audio format - 'wav' for chunking, 'mp3' for direct output
            **kwargs: Additional parameters

        Returns:
            Audio bytes in requested format

        Note:
            - Use 'wav' when text will be chunked and stitched (crossfade requires WAV)
            - Use 'mp3' for short text that won't be chunked (more efficient)
        """
        kokoro_voice = self._map_voice(voice_path)

        # Default to WAV for stitching compatibility
        # The server will convert to final format after stitching
        audio_format = response_format if response_format in ["wav", "mp3", "opus", "flac"] else "wav"

        response = requests.post(
            f"{self.host}/v1/audio/speech",
            json={
                "model": "kokoro",
                "voice": kokoro_voice,
                "input": text,
                "response_format": audio_format,
            },
            timeout=120,
        )
        response.raise_for_status()
        return response.content
