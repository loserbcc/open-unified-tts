"""Abstract base class for TTS backend adapters.

Implement this interface to add support for any TTS backend.
"""
from abc import ABC, abstractmethod


class TTSBackend(ABC):
    """Abstract interface for TTS backends.

    To create a new adapter:
    1. Inherit from TTSBackend
    2. Implement all abstract methods/properties
    3. Add to router.py backend list

    Example:
        class MyTTSBackend(TTSBackend):
            @property
            def name(self) -> str:
                return "mytts"

            @property
            def port(self) -> int:
                return 8000

            @property
            def vram_gb(self) -> int:
                return 4

            def is_available(self) -> bool:
                # Check if your backend is running
                ...

            def generate(self, text, voice_path, transcript) -> bytes:
                # Call your TTS API and return WAV bytes
                ...
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique backend identifier (e.g., 'openaudio', 'voxcpm')."""
        ...

    @property
    @abstractmethod
    def port(self) -> int:
        """Default port (0 for cloud services)."""
        ...

    @property
    @abstractmethod
    def vram_gb(self) -> int:
        """Approximate VRAM usage in GB (0 for cloud)."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check if backend is running and healthy."""
        ...

    @abstractmethod
    def generate(self, text: str, voice_path: str, transcript: str) -> bytes:
        """Generate TTS audio.

        Args:
            text: Text to synthesize
            voice_path: Reference audio path (cloning) or voice name (presets)
            transcript: Transcript of reference audio (if applicable)

        Returns:
            WAV audio bytes

        Raises:
            RuntimeError: If generation fails
        """
        ...

    def list_voices(self) -> list[str]:
        """List available voices for this backend.

        Returns:
            List of voice names/identifiers.
        """
        return []  # Default: no voices (override in subclasses)
