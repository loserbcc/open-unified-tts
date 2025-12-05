"""Voice-to-backend preference management.

Stores per-voice backend routing preferences for optimal quality.
Example: "morty" always uses "openaudio" because it sounds better there.
"""
import json
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Default preferences (override with your own discoveries)
DEFAULT_PREFS = {
    # Example: "morty": "openaudio",
}


class VoicePreferences:
    """Manages per-voice backend preferences for quality routing.

    Preferences are saved to a JSON file for persistence.
    """

    def __init__(self, prefs_file: Path = None):
        if prefs_file is None:
            prefs_file = Path(os.environ.get(
                "UNIFIED_TTS_PREFS_FILE",
                os.path.expanduser("~/.unified-tts/voice_preferences.json")
            ))

        self.prefs_file = Path(prefs_file)
        self._prefs: dict[str, str] = {}
        self.load()

    def load(self):
        """Load preferences from file."""
        self._prefs = DEFAULT_PREFS.copy()

        if self.prefs_file.exists():
            try:
                with open(self.prefs_file) as f:
                    saved = json.load(f)
                self._prefs.update(saved)
                logger.info(f"Loaded {len(saved)} voice preferences")
            except Exception as e:
                logger.warning(f"Failed to load preferences: {e}")

    def save(self):
        """Save preferences to file."""
        try:
            self.prefs_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.prefs_file, "w") as f:
                json.dump(self._prefs, f, indent=2)
            logger.info(f"Saved {len(self._prefs)} voice preferences")
        except Exception as e:
            logger.error(f"Failed to save preferences: {e}")

    def get(self, voice: str) -> Optional[str]:
        """Get preferred backend for a voice."""
        return self._prefs.get(voice.lower())

    def set(self, voice: str, backend: str):
        """Set preferred backend for a voice."""
        self._prefs[voice.lower()] = backend
        self.save()

    def remove(self, voice: str) -> bool:
        """Remove preference for a voice."""
        voice_lower = voice.lower()
        if voice_lower in self._prefs:
            del self._prefs[voice_lower]
            self.save()
            return True
        return False

    def list_all(self) -> dict[str, str]:
        """Return all voice preferences."""
        return self._prefs.copy()
