"""Backend router for automatic TTS backend selection.

The router manages multiple TTS backends and provides:
- Automatic failover to available backends
- User-preferred backend selection
- Backend health monitoring
"""
import logging
from typing import Optional

from adapters import TTSBackend

logger = logging.getLogger(__name__)


class BackendRouter:
    """Routes TTS requests to available backends.

    Priority:
    1. User-preferred backend (if set and available)
    2. First available backend in list
    """

    def __init__(self, backends: list[TTSBackend] = None):
        """Initialize router with backends.

        Args:
            backends: List of TTSBackend instances. If None, loads defaults.
        """
        if backends is None:
            backends = self._load_default_backends()

        self.backends: list[TTSBackend] = backends
        self.preferred: Optional[str] = None

    def _load_default_backends(self) -> list[TTSBackend]:
        """Load default backends based on available adapters."""
        backends = []

        # Import adapters - they handle missing dependencies gracefully
        from adapters import (
            VibeVoiceBackend, HiggsBackend, OpenAudioBackend,
            VoxCPMBackend, KyutaiBackend, ElevenLabsBackend
        )

        # Add backends in priority order
        if VibeVoiceBackend:
            backends.append(VibeVoiceBackend())
        if HiggsBackend:
            backends.append(HiggsBackend())
        if OpenAudioBackend:
            backends.append(OpenAudioBackend())
        if VoxCPMBackend:
            backends.append(VoxCPMBackend())
        if KyutaiBackend:
            backends.append(KyutaiBackend())
        if ElevenLabsBackend:
            backends.append(ElevenLabsBackend())

        return backends

    def get_backend(self, name: str) -> Optional[TTSBackend]:
        """Get a specific backend by name."""
        for backend in self.backends:
            if backend.name == name:
                return backend
        return None

    def get_active_backend(self) -> TTSBackend:
        """Get the currently active (available) backend.

        Returns:
            First available backend, preferring user preference.

        Raises:
            RuntimeError: If no backend is available.
        """
        # Try user preference first
        if self.preferred:
            backend = self.get_backend(self.preferred)
            if backend and backend.is_available():
                logger.debug(f"Using preferred backend: {self.preferred}")
                return backend
            logger.warning(f"Preferred backend '{self.preferred}' not available")

        # Find first available
        for backend in self.backends:
            if backend.is_available():
                logger.debug(f"Using available backend: {backend.name}")
                return backend

        raise RuntimeError("No TTS backend available")

    def set_preferred(self, name: Optional[str]) -> bool:
        """Set preferred backend.

        Args:
            name: Backend name, or None to clear preference.

        Returns:
            True if valid name or None.
        """
        if name is None:
            self.preferred = None
            return True

        if self.get_backend(name):
            self.preferred = name
            return True

        return False

    def list_backends(self) -> list[dict]:
        """List all backends with their status."""
        active_name = None
        try:
            active_name = self.get_active_backend().name
        except RuntimeError:
            pass

        return [
            {
                "name": backend.name,
                "available": backend.is_available(),
                "port": backend.port,
                "vram_gb": backend.vram_gb,
                "active": backend.name == active_name,
            }
            for backend in self.backends
        ]
