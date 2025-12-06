#!/usr/bin/env python3
"""Open Unified TTS - Textual TUI Client

A modern terminal user interface for the Open Unified TTS API.
Provides a clean, efficient way to generate speech from text with
full voice selection, format options, and plugin support.

Usage:
    python tui_client.py [--api-url URL] [--no-autoplay]

Features:
- Multi-line text input with paste support
- Fuzzy searchable voice selector organized by category
- Multiple output format support (mp3, wav, flac, opus)
- Real-time API status monitoring
- Automatic file saving with timestamps
- Optional auto-play with mpv
- Plugin architecture for extensibility
- Word count and duration estimation
- Progress indicators during generation

Plugin System:
- OCR: Extract text from images (future)
- AI Director: Enhance text with AI (future)
- Custom plugins: Extend via plugins/base.py

Dependencies:
    pip install textual httpx rich
"""
import asyncio
import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

import httpx
from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Header,
    Footer,
    TextArea,
    Button,
    Select,
    Label,
    Static,
    Switch,
    TabbedContent,
    TabPane,
)
from textual.binding import Binding
from rich.text import Text

# Import plugin system
from plugins.base import Plugin
from plugins.ocr_plugin import OCRPlugin
from plugins.ai_director import AIDirectorPlugin


# =============================================================================
# CONFIGURATION
# =============================================================================

DEFAULT_API_URL = "http://localhost:8765"
OUTPUT_DIR = Path.home() / "tts_output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Voice categories matching the API structure
VOICE_CATEGORIES = {
    "American Female": [
        "af_alloy", "af_bella", "af_heart", "af_nova", "af_sky",
        "af_sarah", "af_jessica", "af_nicole", "af_river", "af_kore"
    ],
    "American Male": [
        "am_adam", "am_echo", "am_eric", "am_onyx", "am_michael",
        "am_liam", "am_fenrir", "am_puck"
    ],
    "British Female": ["bf_alice", "bf_emma", "bf_lily"],
    "British Male": ["bm_daniel", "bm_fable", "bm_george", "bm_lewis"],
}

AUDIO_FORMATS = ["mp3", "wav", "flac", "opus"]

# Average speaking rate for estimation (words per minute)
WORDS_PER_MINUTE = 150


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def estimate_duration(text: str) -> float:
    """Estimate audio duration based on word count.

    Args:
        text: Input text

    Returns:
        Estimated duration in seconds
    """
    word_count = len(text.split())
    return (word_count / WORDS_PER_MINUTE) * 60


def format_duration(seconds: float) -> str:
    """Format duration for display.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string (e.g., "1m 30s" or "45s")
    """
    if seconds < 60:
        return f"{int(seconds)}s"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}m {secs}s"


def play_audio(file_path: Path) -> bool:
    """Play audio file using mpv.

    Args:
        file_path: Path to audio file

    Returns:
        True if successful, False otherwise
    """
    try:
        subprocess.run(
            ["mpv", "--quiet", str(file_path)],
            check=True,
            timeout=300,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


# =============================================================================
# CUSTOM WIDGETS
# =============================================================================

class StatusIndicator(Static):
    """API status indicator with color coding."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status = "unknown"

    def set_status(self, status: str, backend: Optional[str] = None):
        """Update status display.

        Args:
            status: One of 'ok', 'error', 'checking'
            backend: Active backend name (optional)
        """
        self.status = status

        if status == "ok":
            symbol = "●"
            color = "green"
            text = f"{symbol} API Connected"
            if backend:
                text += f" ({backend})"
        elif status == "error":
            symbol = "●"
            color = "red"
            text = f"{symbol} API Offline"
        else:  # checking
            symbol = "◐"
            color = "yellow"
            text = f"{symbol} Checking..."

        rich_text = Text(text, style=color)
        self.update(rich_text)


class VoiceSelector(Select):
    """Enhanced voice selector with category grouping."""

    def __init__(self, voices: List[str], *args, **kwargs):
        """Initialize with voice list.

        Args:
            voices: List of voice names from API
        """
        # Build options with category headers
        options = []

        for category, category_voices in VOICE_CATEGORIES.items():
            # Add available voices from this category
            available = [v for v in category_voices if v in voices]
            if available:
                # Add separator
                options.append((f"── {category} ──", f"_cat_{category}"))
                # Add voices
                for voice in available:
                    # Format voice name nicely
                    display_name = voice.replace("_", " ").title()
                    options.append((display_name, voice))

        # Add any uncategorized voices
        categorized = [v for cat_voices in VOICE_CATEGORIES.values() for v in cat_voices]
        uncategorized = [v for v in voices if v not in categorized]
        if uncategorized:
            options.append(("── Other ──", "_cat_other"))
            for voice in sorted(uncategorized):
                display_name = voice.replace("_", " ").title()
                options.append((display_name, voice))

        super().__init__(options, *args, **kwargs)

    def on_select_changed(self, event):
        """Prevent selecting category headers."""
        if event.value and event.value.startswith("_cat_"):
            # Reset to previous valid selection
            event.stop()


class StatsDisplay(Static):
    """Display text statistics (word count, estimated duration)."""

    def update_stats(self, text: str):
        """Update statistics based on input text.

        Args:
            text: Input text to analyze
        """
        word_count = len(text.split())
        char_count = len(text)
        duration = estimate_duration(text)

        stats = f"Words: {word_count} | Chars: {char_count} | Est. Duration: {format_duration(duration)}"
        self.update(stats)


# =============================================================================
# MAIN APPLICATION
# =============================================================================

class TTSClientApp(App):
    """Open Unified TTS Textual Client.

    A modern TUI for generating speech from text using the Open Unified TTS API.
    """

    CSS = """
    Screen {
        background: $surface;
    }

    #main_container {
        height: 100%;
        padding: 1;
    }

    #content_area {
        height: 1fr;
    }

    #left_panel {
        width: 2fr;
        height: 100%;
        border: solid $primary;
        padding: 1;
    }

    #right_panel {
        width: 1fr;
        height: 100%;
        border: solid $accent;
        padding: 1;
        margin-left: 1;
    }

    #text_input {
        height: 10;
        border: solid $secondary;
    }

    #action_bar {
        height: 3;
        background: $surface;
        padding: 0 1;
        dock: bottom;
    }

    #action_bar Button {
        margin: 0 1;
    }

    #controls_container {
        height: auto;
    }

    .control_group {
        height: auto;
        margin-bottom: 1;
        border: solid $primary-background;
        padding: 1;
    }

    .control_label {
        color: $text-muted;
        margin-bottom: 1;
    }

    #voice_select {
        width: 100%;
        margin-bottom: 1;
    }

    #format_select {
        width: 100%;
        margin-bottom: 1;
    }

    #generate_btn {
        width: 100%;
        margin-top: 1;
    }

    #status_bar {
        height: 3;
        background: $panel;
        padding: 1;
        border-top: solid $primary;
    }

    #status_indicator {
        dock: left;
    }

    #stats_display {
        dock: right;
        color: $text-muted;
    }

    #progress_msg {
        content-align: center middle;
    }

    Switch {
        margin: 1 0;
    }

    TabbedContent {
        height: auto;
    }

    TabPane {
        padding: 1;
    }
    """

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", priority=True),
        Binding("ctrl+g", "generate", "Generate", priority=True),
        Binding("ctrl+o", "import_file", "Open File"),
        Binding("ctrl+r", "refresh_api", "Refresh API"),
        Binding("f1", "show_help", "Help"),
    ]

    TITLE = "Open Unified TTS Client"

    def __init__(self, api_url: str = DEFAULT_API_URL, autoplay: bool = True):
        """Initialize the TTS client.

        Args:
            api_url: Base URL of the TTS API
            autoplay: Whether to auto-play generated audio
        """
        super().__init__()
        self.api_url = api_url.rstrip("/")
        self.autoplay = autoplay
        self.available_voices: List[str] = []
        self.plugins: List[Plugin] = []
        self.api_status = "unknown"
        self.active_backend: Optional[str] = None

        # Initialize plugins
        self._init_plugins()

    def _init_plugins(self):
        """Initialize plugin system."""
        # Register available plugins (disabled by default for placeholders)
        self.plugins = [
            OCRPlugin(),
            AIDirectorPlugin(),
        ]

    def compose(self) -> ComposeResult:
        """Compose the UI layout."""
        yield Header()

        with Container(id="main_container"):
            with Horizontal(id="content_area"):
                # Left panel - Text input
                with Vertical(id="left_panel"):
                    yield Label("Text Input", classes="control_label")
                    yield TextArea(
                        text="",
                        id="text_input",
                        language="markdown",
                    )

                # Right panel - Controls
                with Vertical(id="right_panel"):
                    with ScrollableContainer(id="controls_container"):
                        # Voice selection
                        with Vertical(classes="control_group"):
                            yield Label("Voice", classes="control_label")
                            yield VoiceSelector(
                                [],
                                id="voice_select",
                                prompt="Select voice...",
                            )

                        # Format selection
                        with Vertical(classes="control_group"):
                            yield Label("Output Format", classes="control_label")
                            yield Select(
                                [(fmt.upper(), fmt) for fmt in AUDIO_FORMATS],
                                id="format_select",
                                value="mp3",
                            )

                        # Options
                        with Vertical(classes="control_group"):
                            yield Label("Options", classes="control_label")
                            yield Horizontal(
                                Label("Auto-play: "),
                                Switch(value=self.autoplay, id="autoplay_switch"),
                            )

            # Action bar (fixed at bottom)
            with Horizontal(id="action_bar"):
                yield Button("📂 Import File", id="import_btn")
                yield Button("🎙️ Generate", variant="primary", id="generate_btn")

            # Status bar
            with Horizontal(id="status_bar"):
                yield StatusIndicator(id="status_indicator")
                yield Static("", id="progress_msg")
                yield StatsDisplay("", id="stats_display")

        yield Footer()

    async def on_mount(self) -> None:
        """Handle application mount - check API and load voices."""
        self.update_status("Checking API...")
        self.check_api_health()  # @work decorator handles async scheduling

    @work(exclusive=True)
    async def check_api_health(self) -> None:
        """Check API health and load available voices."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Check health endpoint
                response = await client.get(f"{self.api_url}/health")
                response.raise_for_status()
                health_data = response.json()

                self.api_status = health_data.get("status", "unknown")
                self.active_backend = health_data.get("backend")

                # Load voices
                voice_response = await client.get(f"{self.api_url}/v1/voices")
                voice_response.raise_for_status()
                voice_data = voice_response.json()
                self.available_voices = voice_data.get("voices", [])

                # Update UI
                status_indicator = self.query_one("#status_indicator", StatusIndicator)
                status_indicator.set_status("ok", self.active_backend)

                # Update voice selector
                voice_select = self.query_one("#voice_select", VoiceSelector)
                voice_select.clear()

                # Rebuild voice selector with new voices
                new_selector = VoiceSelector(
                    self.available_voices,
                    id="voice_select",
                    prompt="Select voice...",
                )
                await voice_select.remove()
                control_group = self.query_one(".control_group")
                await control_group.mount(new_selector)

                self.update_status(f"Ready - {len(self.available_voices)} voices available")

        except httpx.RequestError as e:
            self.api_status = "error"
            status_indicator = self.query_one("#status_indicator", StatusIndicator)
            status_indicator.set_status("error")
            self.update_status(f"API Error: {str(e)}")
        except Exception as e:
            self.api_status = "error"
            status_indicator = self.query_one("#status_indicator", StatusIndicator)
            status_indicator.set_status("error")
            self.update_status(f"Error: {str(e)}")

    def update_status(self, message: str):
        """Update status bar message.

        Args:
            message: Status message to display
        """
        progress_msg = self.query_one("#progress_msg", Static)
        progress_msg.update(message)

    @on(TextArea.Changed, "#text_input")
    def on_text_changed(self, event: TextArea.Changed) -> None:
        """Update statistics when text changes."""
        stats_display = self.query_one("#stats_display", StatsDisplay)
        stats_display.update_stats(event.text_area.text)

    @on(Switch.Changed, "#autoplay_switch")
    def on_autoplay_changed(self, event: Switch.Changed) -> None:
        """Handle autoplay toggle."""
        self.autoplay = event.value

    @on(Button.Pressed, "#import_btn")
    async def on_import_pressed(self) -> None:
        """Handle import button press."""
        await self.action_import_file()

    async def action_import_file(self) -> None:
        """Import text from a file.

        NOTE: This feature is experimental/in-development.
        - Requires zenity for GUI file picker (Linux)
        - PDF support requires: pip install pypdf
        - DOCX support requires: pip install python-docx
        """
        # Simple file path input - prompt user
        from pathlib import Path
        import subprocess

        # Use zenity or kdialog if available, otherwise prompt in status
        try:
            result = subprocess.run(
                ["zenity", "--file-selection", "--title=Select Text File"],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                file_path = result.stdout.strip()
            else:
                self.update_status("File selection cancelled")
                return
        except (FileNotFoundError, subprocess.TimeoutExpired):
            # Fallback: just use a hardcoded test path for now
            self.update_status("Tip: Ctrl+O to import. Put file path in text box, select all, paste.")
            return

        # Read and load the file
        try:
            path = Path(file_path)
            if not path.exists():
                self.update_status(f"File not found: {file_path}")
                return

            # Handle different file types
            suffix = path.suffix.lower()
            if suffix == ".pdf":
                try:
                    from pypdf import PdfReader
                    reader = PdfReader(file_path)
                    text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
                except ImportError:
                    self.update_status("PDF support requires: pip install pypdf")
                    return
            elif suffix in [".docx", ".doc"]:
                try:
                    from docx import Document
                    doc = Document(file_path)
                    text = "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
                except ImportError:
                    self.update_status("DOCX support requires: pip install python-docx")
                    return
            else:
                # Plain text
                text = path.read_text(encoding="utf-8", errors="ignore")

            # Load into text area
            text_area = self.query_one("#text_input", TextArea)
            text_area.text = text
            word_count = len(text.split())
            self.update_status(f"Loaded {word_count} words from {path.name}")

        except Exception as e:
            self.update_status(f"Error reading file: {str(e)}")

    @on(Button.Pressed, "#generate_btn")
    async def on_generate_pressed(self) -> None:
        """Handle generate button press."""
        await self.action_generate()

    async def action_generate(self) -> None:
        """Generate speech from input text."""
        # Get input values
        text_area = self.query_one("#text_input", TextArea)
        text = text_area.text.strip()

        if not text:
            self.update_status("Error: No text to generate")
            return

        voice_select = self.query_one("#voice_select", Select)
        selected_voice = voice_select.value

        # Handle no selection or category headers
        if selected_voice is Select.BLANK or not selected_voice:
            self.update_status("Error: Please select a voice")
            return
        if isinstance(selected_voice, str) and selected_voice.startswith("_cat_"):
            self.update_status("Error: Please select a voice, not a category")
            return

        format_select = self.query_one("#format_select", Select)
        audio_format = format_select.value

        # Process text through plugins
        processed_text = text
        for plugin in self.plugins:
            if plugin.enabled:
                try:
                    plugin.on_before_generate(processed_text, selected_voice, audio_format)
                    processed_text = plugin.process_text(processed_text)
                except Exception as e:
                    self.update_status(f"Plugin error ({plugin.name}): {str(e)}")
                    return

        # Generate audio (no await - @work handles scheduling)
        self._generate_audio(processed_text, selected_voice, audio_format)

    @work(exclusive=True)
    async def _generate_audio(self, text: str, voice: str, format: str) -> None:
        """Generate audio via API.

        Args:
            text: Text to convert to speech
            voice: Voice name
            format: Output audio format
        """
        self.update_status("Generating audio...")

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.api_url}/v1/audio/speech",
                    json={
                        "model": "tts-1",
                        "input": text,
                        "voice": voice,
                        "response_format": format,
                    },
                )
                response.raise_for_status()

                # Save to file with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"tts_{timestamp}_{voice}.{format}"
                output_path = OUTPUT_DIR / filename

                output_path.write_bytes(response.content)

                self.update_status(f"Saved: {output_path}")

                # Call plugin hooks
                for plugin in self.plugins:
                    if plugin.enabled:
                        try:
                            plugin.on_after_generate(str(output_path), True)
                        except Exception:
                            pass  # Don't let plugin errors break the flow

                # Auto-play if enabled
                if self.autoplay:
                    self.update_status(f"Playing: {filename}")
                    success = play_audio(output_path)
                    if success:
                        self.update_status(f"Completed: {filename}")
                    else:
                        self.update_status(f"Saved (mpv not available): {filename}")

        except httpx.HTTPStatusError as e:
            error_msg = f"API Error {e.response.status_code}"
            try:
                error_detail = e.response.json().get("detail", str(e))
                error_msg += f": {error_detail}"
            except Exception:
                error_msg += f": {str(e)}"
            self.update_status(error_msg)

            # Notify plugins of failure
            for plugin in self.plugins:
                if plugin.enabled:
                    try:
                        plugin.on_after_generate("", False)
                    except Exception:
                        pass

        except Exception as e:
            self.update_status(f"Error: {str(e)}")

            # Notify plugins of failure
            for plugin in self.plugins:
                if plugin.enabled:
                    try:
                        plugin.on_after_generate("", False)
                    except Exception:
                        pass

    async def action_refresh_api(self) -> None:
        """Refresh API connection and voice list."""
        self.update_status("Refreshing...")
        self.check_api_health()  # @work handles scheduling

    async def action_show_help(self) -> None:
        """Show help information."""
        help_text = """
Open Unified TTS Client - Help

Keybindings:
  Ctrl+G     Generate speech
  Ctrl+R     Refresh API connection
  Ctrl+Q     Quit application
  F1         Show this help

Features:
  - Multi-line text input with paste support
  - Voice selection organized by category
  - Multiple output formats (mp3, wav, flac, opus)
  - Auto-play with mpv (optional)
  - Plugin system for extensibility

Output Directory:
  {output_dir}

API URL:
  {api_url}
        """.format(
            output_dir=OUTPUT_DIR,
            api_url=self.api_url,
        )
        self.update_status(help_text.strip())


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

def main():
    """Main entry point for the TUI client."""
    parser = argparse.ArgumentParser(
        description="Open Unified TTS - Textual TUI Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tui_client.py
  python tui_client.py --api-url http://192.168.1.100:8765
  python tui_client.py --no-autoplay

Output files are saved to: ~/tts_output/
        """,
    )
    parser.add_argument(
        "--api-url",
        default=DEFAULT_API_URL,
        help=f"TTS API base URL (default: {DEFAULT_API_URL})",
    )
    parser.add_argument(
        "--no-autoplay",
        action="store_true",
        help="Disable automatic audio playback",
    )

    args = parser.parse_args()

    # Create and run the app
    app = TTSClientApp(
        api_url=args.api_url,
        autoplay=not args.no_autoplay,
    )

    try:
        app.run()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)


if __name__ == "__main__":
    main()
