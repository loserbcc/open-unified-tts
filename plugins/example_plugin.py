"""Example Plugin - Template for creating custom plugins.

This is a working example plugin that demonstrates the plugin API.
It's fully functional and can be enabled to see how plugins work.

Use this as a starting point for your own custom plugins.
"""
from typing import List
from .base import Plugin


class ExamplePlugin(Plugin):
    """Example plugin that demonstrates the plugin interface.

    This plugin shows how to:
    - Transform text
    - Implement enable/disable
    - Provide hooks for generation events
    - Document plugin functionality

    What it does:
    - Removes extra whitespace from text
    - Logs generation events (if enabled)
    - Demonstrates the plugin lifecycle
    """

    def __init__(self):
        """Initialize the example plugin."""
        self._enabled = False  # Disabled by default

    @property
    def name(self) -> str:
        """Plugin name shown in UI."""
        return "Example Plugin"

    @property
    def enabled(self) -> bool:
        """Check if plugin is active."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Enable or disable the plugin."""
        self._enabled = value

    def process_text(self, text: str) -> str:
        """Clean up whitespace in the text.

        Args:
            text: Input text

        Returns:
            Text with normalized whitespace
        """
        if not self._enabled:
            return text

        # Remove extra whitespace
        lines = text.split('\n')
        cleaned_lines = [' '.join(line.split()) for line in lines]
        return '\n'.join(cleaned_lines)

    def get_ui_components(self) -> List:
        """No custom UI components for this example.

        Returns:
            Empty list
        """
        return []

    def on_before_generate(self, text: str, voice: str, format: str) -> None:
        """Log before generation starts.

        Args:
            text: The processed text
            voice: Selected voice
            format: Output format
        """
        if self._enabled:
            word_count = len(text.split())
            print(f"[Example Plugin] Generating {word_count} words with {voice} as {format}")

    def on_after_generate(self, output_path: str, success: bool) -> None:
        """Log after generation completes.

        Args:
            output_path: Path to generated file
            success: Whether generation succeeded
        """
        if self._enabled:
            if success:
                print(f"[Example Plugin] Successfully saved to {output_path}")
            else:
                print(f"[Example Plugin] Generation failed")

    def get_description(self) -> str:
        """Provide plugin description.

        Returns:
            Description string
        """
        return (
            "Example plugin that demonstrates the plugin API. "
            "Normalizes whitespace and logs generation events. "
            "Enable this to see how plugins work!"
        )

    def validate_config(self) -> None:
        """Validate plugin configuration.

        Returns:
            None if valid (no config needed for this example)
        """
        return None


# Another example: Simple text transformation plugin
class UppercasePlugin(Plugin):
    """Simple plugin that converts text to uppercase.

    Demonstrates a minimal plugin implementation.
    """

    def __init__(self):
        self._enabled = False

    @property
    def name(self) -> str:
        return "Uppercase"

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value

    def process_text(self, text: str) -> str:
        """Convert text to uppercase."""
        return text.upper() if self._enabled else text

    def get_description(self) -> str:
        return "Converts all text to UPPERCASE before generation."
