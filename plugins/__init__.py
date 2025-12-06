"""Plugin system for Open Unified TTS TUI client.

This module provides a plugin architecture for extending the TUI client.
Plugins can transform text input, add UI components, and enhance functionality.
"""
from .base import Plugin

__all__ = ["Plugin"]
