"""Typecast adapter - Cloud TTS with emotion and prosody control.

Typecast: https://typecast.ai
- Zero GPU (cloud service)
- Emotion presets: normal, happy, sad, angry, whisper, toneup, tonedown
- Smart emotion inference (ssfm-v30)
- Requires: pip install typecast-python
"""
import logging
import os

from .base import TTSBackend

logger = logging.getLogger(__name__)

DEFAULT_VOICE_ID = ""  # Set via TYPECAST_VOICE_ID env var or voice_path arg

EMOTION_PRESETS = [
    "normal", "happy", "sad", "angry", "whisper", "toneup", "tonedown"
]


class TypecastBackend(TTSBackend):
    """Typecast cloud TTS - emotion-aware synthesis."""

    def __init__(
        self,
        api_key: str = None,
        voice_id: str = None,
        model: str = "ssfm-v30",
        emotion_preset: str = "normal",
        emotion_intensity: float = None,
    ):
        self.api_key = api_key or os.environ.get("TYPECAST_API_KEY", "")
        self.voice_id = voice_id or os.environ.get("TYPECAST_VOICE_ID", DEFAULT_VOICE_ID)
        self.model = model
        self.emotion_preset = emotion_preset
        self.emotion_intensity = emotion_intensity
        self._client = None
        self._voices_cache = None

    @property
    def name(self) -> str:
        return "typecast"

    @property
    def port(self) -> int:
        return 0  # Cloud service

    @property
    def vram_gb(self) -> int:
        return 0  # Cloud service

    def _get_client(self):
        if self._client is None:
            from typecast import Typecast
            self._client = Typecast(api_key=self.api_key)
        return self._client

    def is_available(self) -> bool:
        if not self.api_key:
            return False
        try:
            from typecast import Typecast
            client = Typecast(api_key=self.api_key)
            client.voices_v2()
            return True
        except Exception:
            return False

    def _resolve_voice_id(self, voice_path: str) -> str:
        """Resolve voice_path (name or ID) to a Typecast voice ID."""
        if not voice_path:
            return self.voice_id

        # If it looks like a raw voice ID (e.g. "tc_..."), use directly
        if voice_path.startswith("tc_") or len(voice_path) > 20:
            return voice_path

        # Try to match by name
        try:
            voices = self._get_client().voices_v2()
            for v in voices:
                if voice_path.lower() in v.voice_name.lower():
                    return v.voice_id
        except Exception:
            pass

        return voice_path  # Fallback: treat as raw ID

    def generate(self, text: str, voice_path: str = "", transcript: str = "") -> bytes:
        from typecast.models import TTSRequest, TTSModel, Output, PresetPrompt

        voice_id = self._resolve_voice_id(voice_path) or self.voice_id
        if not voice_id:
            raise RuntimeError(
                "Typecast voice_id is required. Set TYPECAST_VOICE_ID or pass voice_path."
            )

        prompt_kwargs = {"emotion_preset": self.emotion_preset}
        if self.emotion_intensity is not None:
            prompt_kwargs["emotion_intensity"] = self.emotion_intensity

        request = TTSRequest(
            text=text,
            voice_id=voice_id,
            model=TTSModel(self.model),
            prompt=PresetPrompt(**prompt_kwargs),
            output=Output(audio_format="wav"),
        )

        response = self._get_client().text_to_speech(request)
        return response.audio_data

    def list_voices(self) -> list[str]:
        try:
            voices = self._get_client().voices_v2()
            return [v.voice_id for v in voices]
        except Exception as e:
            logger.warning(f"[TypecastBackend] Could not fetch voices: {e}")
            return []
