# Open Unified TTS - TUI Client

A modern, terminal-based user interface for the Open Unified TTS API built with [Textual](https://github.com/Textualize/textual).

## Features

- **Clean Terminal UI**: Modern, responsive interface that works great over SSH
- **Voice Organization**: Voices grouped by category (American Female/Male, British Female/Male)
- **Multi-line Input**: Full text editor with paste support
- **Real-time Stats**: Word count, character count, and duration estimation
- **Format Support**: Generate mp3, wav, flac, or opus audio
- **Auto-play**: Optional automatic playback with mpv
- **API Monitoring**: Real-time connection status and backend info
- **Plugin System**: Extensible architecture for future enhancements

## Installation

### Prerequisites

- Python 3.10+
- Open Unified TTS API running (default: http://localhost:8765)
- Optional: `mpv` for audio playback

### Install Dependencies

```bash
# From the project directory
pip install -r requirements-tui.txt

# Or install directly
pip install textual httpx rich
```

## Usage

### Basic Usage

```bash
# Start the TUI client
python tui_client.py

# Or make it executable and run directly
chmod +x tui_client.py
./tui_client.py
```

### Command Line Options

```bash
# Connect to remote API
python tui_client.py --api-url http://192.168.1.100:8765

# Disable auto-play
python tui_client.py --no-autoplay

# Show help
python tui_client.py --help
```

### Keybindings

| Key | Action |
|-----|--------|
| `Ctrl+G` | Generate speech |
| `Ctrl+R` | Refresh API connection and voice list |
| `Ctrl+Q` | Quit application |
| `F1` | Show help |

### Output Files

Generated audio files are saved to `~/tts_output/` with timestamped filenames:

```
~/tts_output/
  tts_20251206_143022_af_nova.mp3
  tts_20251206_143145_bm_daniel.wav
  ...
```

## UI Layout

```
┌─────────────────────────────────────────────────────┐
│ Header: Open Unified TTS Client                    │
├──────────────────────┬──────────────────────────────┤
│ Text Input           │ Controls                     │
│                      │                              │
│ [Multi-line text     │ Voice: [Dropdown]            │
│  editor with paste   │ Format: [mp3/wav/flac/opus]  │
│  support]            │ Auto-play: [Toggle]          │
│                      │                              │
│                      │ Plugins: [Tabs]              │
│                      │                              │
│                      │ [Generate Speech Button]     │
├──────────────────────┴──────────────────────────────┤
│ Status: ● Connected | Progress | Stats: 50 words   │
├─────────────────────────────────────────────────────┤
│ Footer: Keybindings                                 │
└─────────────────────────────────────────────────────┘
```

## Plugin System

The TUI client includes a plugin architecture for extensibility. Plugins can:

- Process/transform text before generation
- Add custom UI components
- Hook into the generation pipeline

### Available Plugins

#### OCR Plugin (Planned)
Extract text from images for TTS generation.

**Status**: Placeholder - not yet implemented

**Planned Features**:
- Image paste from clipboard
- Screenshot OCR
- PDF text extraction
- Multi-language support

**Future Dependencies**: `pytesseract`, `Pillow`

#### AI Director Plugin (Planned)
Enhance text with AI before TTS generation.

**Status**: Placeholder - not yet implemented

**Planned Features**:
- Text clarity enhancement
- Emotional direction
- Voice suggestions
- SSML generation
- Dialogue formatting

**Supported AI Backends**:
- Claude (Anthropic API)
- Ollama (local Dolphin model)
- OpenAI GPT

**Future Dependencies**: `anthropic`, `openai`

### Creating Custom Plugins

1. Create a new file in `plugins/` directory
2. Inherit from `plugins.base.Plugin`
3. Implement required methods:

```python
from plugins.base import Plugin
from typing import List
from textual.widgets import Widget

class MyPlugin(Plugin):
    def __init__(self):
        self._enabled = True

    @property
    def name(self) -> str:
        return "My Plugin"

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value

    def process_text(self, text: str) -> str:
        # Transform the text
        return text.upper()

    def get_ui_components(self) -> List[Widget]:
        # Optional: return UI widgets
        return []

    def get_description(self) -> str:
        return "Converts text to uppercase"
```

4. Register your plugin in `tui_client.py`:

```python
def _init_plugins(self):
    self.plugins = [
        OCRPlugin(),
        AIDirectorPlugin(),
        MyPlugin(),  # Add your plugin
    ]
```

## Architecture

### File Structure

```
open-unified-tts/
├── tui_client.py          # Main TUI application
├── plugins/
│   ├── __init__.py        # Plugin system exports
│   ├── base.py            # Abstract plugin interface
│   ├── ocr_plugin.py      # OCR plugin (placeholder)
│   └── ai_director.py     # AI enhancement plugin (placeholder)
├── requirements-tui.txt   # TUI-specific dependencies
└── TUI_CLIENT_README.md   # This file
```

### Key Components

**TTSClientApp**: Main Textual application
- Handles UI layout and event routing
- Manages API communication
- Coordinates plugin execution

**Custom Widgets**:
- `StatusIndicator`: Color-coded API status display
- `VoiceSelector`: Category-grouped voice dropdown
- `StatsDisplay`: Real-time text statistics

**Plugin System**:
- `Plugin` (base class): Abstract interface for all plugins
- Plugin hooks: `process_text`, `on_before_generate`, `on_after_generate`
- Optional UI integration via `get_ui_components`

### API Communication

The client uses `httpx` for async HTTP communication:

- `GET /health` - Check API status and active backend
- `GET /v1/voices` - Load available voices
- `POST /v1/audio/speech` - Generate TTS audio

All requests use async/await for non-blocking UI.

## Troubleshooting

### API Connection Issues

```
Error: API Offline
```

**Solution**: Ensure the TTS API server is running:
```bash
# Start the API server
cd /home/brian/projects/open-unified-tts
python server.py
```

### No Voices Available

```
Ready - 0 voices available
```

**Solution**: Check voice directory and refresh:
- Default: `~/.unified-tts/voices/`
- Set custom: `export UNIFIED_TTS_VOICE_DIR=/path/to/voices`
- Press `Ctrl+R` to refresh voice list

### Auto-play Not Working

```
Saved (mpv not available): tts_123.mp3
```

**Solution**: Install mpv:
```bash
# Arch/CachyOS
sudo pacman -S mpv

# Ubuntu/Debian
sudo apt install mpv

# Or disable auto-play
python tui_client.py --no-autoplay
```

### Plugin Errors

```
Plugin error (OCR): NotImplementedError
```

**Solution**: The OCR and AI Director plugins are placeholders. Don't enable them until implemented.

## Performance

- **Startup**: < 1 second (API check + voice loading)
- **Generation**: Depends on API backend and text length
- **Memory**: ~50-100 MB (Textual framework)
- **CPU**: Minimal (async I/O bound)

## Development

### Running in Development Mode

```bash
# Enable Textual dev mode for live reload
textual run --dev tui_client.py
```

### Testing

```bash
# Test with local API
python server.py &
python tui_client.py

# Test with remote API
python tui_client.py --api-url http://192.168.4.72:8765
```

### Debugging

```bash
# Enable Textual console for debugging
textual console

# In another terminal
python tui_client.py
```

## Future Enhancements

- [ ] Implement OCR plugin (pytesseract)
- [ ] Implement AI Director plugin (Claude/Ollama)
- [ ] Add voice favorites/recent voices
- [ ] Batch processing multiple files
- [ ] Export job history
- [ ] Custom voice mappings
- [ ] SSML support
- [ ] Audio preview before saving
- [ ] Streaming audio playback during generation
- [ ] Dark/light theme toggle
- [ ] Configurable keybindings
- [ ] Plugin marketplace/loader

## License

Same as Open Unified TTS project.

## Credits

Built with:
- [Textual](https://github.com/Textualize/textual) - Modern TUI framework
- [httpx](https://www.python-httpx.org/) - Async HTTP client
- [Rich](https://github.com/Textualize/rich) - Terminal formatting

---

**Happy TTS-ing!**
