"""VoxCPM adapter - High-quality character voice cloning via Gradio.

VoxCPM provides excellent character voice preservation.
- ~18GB VRAM
- Gradio interface
"""
import logging
import os
from pathlib import Path

from .base import TTSBackend

logger = logging.getLogger(__name__)


class VoxCPMBackend(TTSBackend):
    """VoxCPM character voice cloning via Gradio."""

    def __init__(self, host: str = None):
        self.host = host or os.environ.get("VOXCPM_HOST", "http://localhost:7860")
        self._client = None

    @property
    def name(self) -> str:
        return "voxcpm"

    @property
    def port(self) -> int:
        return 7860

    @property
    def vram_gb(self) -> int:
        return 18

    def _get_client(self):
        if self._client is None:
            from gradio_client import Client
            self._client = Client(self.host)
        return self._client

    def is_available(self) -> bool:
        try:
            import requests
            r = requests.get(self.host, timeout=2)
            return r.status_code == 200
        except Exception:
            return False

    def generate(self, text: str, voice_path: str, transcript: str) -> bytes:
        from gradio_client import handle_file

        result = self._get_client().predict(
            text_input=text,
            prompt_wav_path_input=handle_file(voice_path),
            prompt_text_input=transcript,
            cfg_value_input=2.0,
            inference_timesteps_input=10,
            do_normalize=False,
            denoise=False,
            api_name="/generate",
        )

        output_path = Path(result)
        with open(output_path, "rb") as f:
            audio_bytes = f.read()

        output_path.unlink(missing_ok=True)
        return audio_bytes
