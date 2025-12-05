"""Voice clone discovery and management.

Discovers voice clones from a directory structure:
    VOICE_DIR/
        voice_name/
            reference.wav (or .mp3, .flac)
            transcript.txt
"""
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class Voice:
    """A discovered voice clone."""

    name: str
    reference_path: Path
    transcript: str

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "reference_path": str(self.reference_path),
            "transcript": self.transcript,
        }


class VoiceManager:
    """Discovers and manages voice clones.

    Voice directory structure:
        voice_dir/
            rick/
                reference.wav
                transcript.txt (contains transcript of reference.wav)
            morty/
                reference.mp3
                transcript.txt
    """

    def __init__(self, voice_dir: Path = None):
        if voice_dir is None:
            voice_dir = Path(os.environ.get(
                "UNIFIED_TTS_VOICE_DIR",
                os.path.expanduser("~/.unified-tts/voices")
            ))

        self.voice_dir = Path(voice_dir)
        self._voices: dict[str, Voice] = {}
        self.refresh()

    def refresh(self) -> int:
        """Scan voice directory and load voices.

        Returns:
            Number of voices discovered.
        """
        self._voices.clear()

        if not self.voice_dir.exists():
            logger.warning(f"Voice directory not found: {self.voice_dir}")
            logger.info(f"Create it with: mkdir -p {self.voice_dir}")
            return 0

        for voice_path in self.voice_dir.iterdir():
            if not voice_path.is_dir():
                continue

            # Look for reference audio
            ref_audio = None
            for ext in [".wav", ".mp3", ".flac"]:
                candidate = voice_path / f"reference{ext}"
                if candidate.exists():
                    ref_audio = candidate
                    break

            if not ref_audio:
                continue

            # Look for transcript
            transcript_file = voice_path / "transcript.txt"
            if not transcript_file.exists():
                continue

            try:
                transcript = transcript_file.read_text().strip()
            except Exception:
                continue

            voice_name = voice_path.name
            self._voices[voice_name] = Voice(
                name=voice_name,
                reference_path=ref_audio,
                transcript=transcript,
            )

        logger.info(f"Discovered {len(self._voices)} voices in {self.voice_dir}")
        return len(self._voices)

    def get(self, name: str) -> Optional[Voice]:
        """Get a voice by name."""
        return self._voices.get(name)

    def list_voices(self) -> list[str]:
        """List all available voice names."""
        return sorted(self._voices.keys())

    def list_voices_detailed(self) -> list[dict]:
        """List all voices with details."""
        return [v.to_dict() for v in sorted(self._voices.values(), key=lambda x: x.name)]
