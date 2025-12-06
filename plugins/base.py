"""Base plugin interface for TUI client extensions.

All plugins should inherit from the Plugin base class and implement
the required methods. Plugins can:
- Transform input text before generation
- Add custom UI components
- Provide pre/post-processing hooks
"""
from abc import ABC, abstractmethod
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from textual.widgets import Widget


class Plugin(ABC):
    """Abstract base class for TUI client plugins.

    Plugins extend the functionality of the TTS client by:
    1. Processing/transforming text input
    2. Adding custom UI components
    3. Hooking into the generation pipeline

    Example:
        class MyPlugin(Plugin):
            name = "My Plugin"
            enabled = True

            def process_text(self, text: str) -> str:
                # Transform the text
                return text.upper()

            def get_ui_components(self) -> List:
                # Return additional widgets
                return []
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin display name shown in the UI."""
        pass

    @property
    @abstractmethod
    def enabled(self) -> bool:
        """Whether the plugin is currently active."""
        pass

    @enabled.setter
    @abstractmethod
    def enabled(self, value: bool) -> None:
        """Enable or disable the plugin."""
        pass

    @abstractmethod
    def process_text(self, text: str) -> str:
        """Transform the input text before TTS generation.

        This is the main text processing hook. The text will be passed
        through all enabled plugins in sequence before being sent to
        the TTS API.

        Args:
            text: The original input text

        Returns:
            The transformed text

        Example:
            def process_text(self, text: str) -> str:
                # Remove all numbers
                return ''.join(c for c in text if not c.isdigit())
        """
        pass

    def get_ui_components(self) -> List:
        """Return optional UI widgets to add to the interface.

        Plugins can contribute additional UI elements that will be
        integrated into the main TUI layout. This is useful for
        plugin-specific controls, status displays, etc.

        Returns:
            List of Textual Widget objects to add to the UI

        Example:
            def get_ui_components(self) -> List:
                return [
                    Label("My Plugin Status: Active"),
                    Button("Configure", id="my_plugin_config")
                ]
        """
        return []

    def on_before_generate(self, text: str, voice: str, format: str) -> None:
        """Hook called before TTS generation starts.

        Use this for logging, validation, or preparing resources.

        Args:
            text: The processed text to be generated
            voice: The selected voice name
            format: The output audio format
        """
        pass

    def on_after_generate(self, output_path: str, success: bool) -> None:
        """Hook called after TTS generation completes.

        Use this for post-processing, notifications, or cleanup.

        Args:
            output_path: Path to the generated audio file
            success: Whether generation succeeded
        """
        pass

    def get_description(self) -> str:
        """Return a brief description of what this plugin does.

        Returns:
            Human-readable description string
        """
        return "No description available"

    def validate_config(self) -> Optional[str]:
        """Validate plugin configuration.

        Returns:
            Error message if invalid, None if valid
        """
        return None
