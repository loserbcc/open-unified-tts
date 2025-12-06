# TUI Client Guide

## Overview

The TUI (Terminal User Interface) client for Open Unified TTS provides a full-featured terminal-based interface for users who prefer working in the terminal. It enables you to:

- Generate audio from text using multiple TTS backends
- Browse and select from available voices
- Configure output formats and save locations
- Monitor backend status and switch between providers
- Save generation history and custom presets
- All without leaving your terminal

Perfect for developers, power users, and terminal-native workflows.

## Installation

### Prerequisites

- Python 3.8 or higher
- Open Unified TTS server running (see main README.md)

### Quick Install

```bash
cd /path/to/open-unified-tts
pip install -r requirements.txt
pip install textual httpx  # TUI dependencies
```

### Full Setup

If installing in a new environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install textual httpx
```

## Quick Start

### Basic Launch

```bash
python tui_client.py
```

### With Custom API URL

```bash
python tui_client.py --api-url http://192.168.4.35:8765
```

### With Custom Config Directory

```bash
python tui_client.py --config ~/.my-tts-config
```

The TUI will connect to the Open Unified TTS API and display available voices and backends.

## Interface Overview

The TUI is organized into distinct panels for clarity and efficiency:

```
┌─────────────────────────────────────────────────────────────────┐
│ Open Unified TTS                          Backend: Kokoro | CPU │
├──────────────────────────────┬──────────────────────────────────┤
│ VOICE SELECTOR               │ TEXT INPUT AREA                  │
│ ┌────────────────────────┐   │ ┌──────────────────────────────┐ │
│ │ All Voices        (↓▲) │   │ │ Enter text to synthesize...  │ │
│ │ ─────────────────────  │   │ │                              │ │
│ │ ✓ bf_emma          [*] │   │ │ [Ctrl+G] Generate            │ │
│ │  bf_grace              │   │ │ [Ctrl+S] Save                │ │
│ │  bf_josh               │   │ │ [Tab] Next | [Shift+Tab] Prev│ │
│ │  bf_lisa               │   │ │                              │ │
│ │  ...                   │   │ │                              │ │
│ └────────────────────────┘   │ └──────────────────────────────┘ │
├──────────────────────────────┼──────────────────────────────────┤
│ SETTINGS PANEL               │ STATUS & GENERATION OUTPUT       │
│ ┌────────────────────────┐   │ ┌──────────────────────────────┐ │
│ │ Format: MP3            │   │ Status: Ready                │ │
│ │ Speed: 1.0             │   │ Last output: output.mp3      │ │
│ │ Auto-play: Off         │   │ Estimated generation: 2.3s   │ │
│ │ Save to: ~/tts_output  │   │                              │ │
│ └────────────────────────┘   │ [Ctrl+P] Play  [Ctrl+O] Open │ │
└──────────────────────────────┴──────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│ [Ctrl+Q] Quit | [Ctrl+H] Help | [Ctrl+B] Backends              │
└─────────────────────────────────────────────────────────────────┘
```

### Key Panels

**Voice Selector (Top Left)**
- List of all available voices organized by backend
- Current voice marked with checkmark (✓)
- Asterisk (*) indicates system default voice
- Search/filter capability (Ctrl+F)

**Text Input Area (Top Right)**
- Large text area for entering content
- Word count and estimated generation time
- Auto-formatting options available
- Paste support (Ctrl+V)

**Settings Panel (Bottom Left)**
- Output format selection
- Speech speed adjustment
- Auto-play toggle
- Save location configuration

**Status Panel (Bottom Right)**
- Real-time generation status
- Last output filename
- Estimated generation time
- Quick playback and file management

## Keyboard Shortcuts

### Core Operations

| Shortcut | Action |
|----------|--------|
| `Ctrl+G` | Generate audio from current text |
| `Ctrl+S` | Save current settings as default |
| `Ctrl+Q` | Quit the TUI |
| `Ctrl+H` | Show help screen |

### Navigation

| Shortcut | Action |
|----------|--------|
| `Tab` | Move to next panel |
| `Shift+Tab` | Move to previous panel |
| `Up/Down` | Navigate within lists/menus |
| `Enter` | Select highlighted item |
| `Escape` | Cancel or close dialogs |

### Voice Selection

| Shortcut | Action |
|----------|--------|
| `Ctrl+F` | Search/filter voices |
| `Ctrl+/` | Toggle voice categories |
| `Ctrl+*` | Set current voice as default |
| `Up/Down` | Browse voice list |

### Text Editing

| Shortcut | Action |
|----------|--------|
| `Ctrl+V` | Paste text |
| `Ctrl+A` | Select all text |
| `Ctrl+X` | Cut text |
| `Ctrl+C` | Copy selected text |
| `Ctrl+Z` | Undo last change |

### Playback & Output

| Shortcut | Action |
|----------|--------|
| `Ctrl+P` | Play last generated audio |
| `Ctrl+O` | Open output folder |
| `Ctrl+L` | View generation history |
| `Ctrl+E` | Export current audio |

### Advanced

| Shortcut | Action |
|----------|--------|
| `Ctrl+B` | Show backend status |
| `Ctrl+D` | Toggle debug mode |
| `Ctrl+R` | Reload configuration |
| `Ctrl+N` | Create new preset |

## Voice Selection

### Browsing Voices

Voices are organized by backend and category. Use the voice selector panel:

1. **All Voices Tab** - Every available voice
2. **By Backend Tab** - Grouped by TTS engine (Kokoro, VoxCPM, etc.)
3. **Favorites Tab** - Your saved favorite voices
4. **Recent Tab** - Recently used voices

### Searching Voices

```
Ctrl+F to open search
Type voice name or characteristics
Results update in real-time
Escape to close search
```

Search examples:
- `bf_` - Kokoro voices (all start with "bf_")
- `rick` - Voice clones of Rick
- `female` - Filter for feminine voices

### Voice Details

Hover over any voice to see:
- Full voice name
- Backend provider
- Reference audio transcript (if cloned voice)
- Tags and characteristics
- Estimated generation time for this voice

### Setting Defaults

Mark a voice as your default for quicker workflows:

```
1. Select voice in list
2. Press Ctrl+* to set as default
3. Default voice shown with asterisk (*)
4. New generations use default unless overridden
```

## Output Options

### Format Selection

Access format options in Settings panel or press `Ctrl+Shift+F`:

**Supported Formats:**
- **MP3** (default) - Universal compatibility, good compression
- **WAV** - Lossless, larger files, best for editing
- **FLAC** - Lossless compression, smaller than WAV
- **Opus** - Modern codec, smallest files, good quality
- **AAC** - Excellent quality, universal support
- **PCM** - Raw audio, maximum quality

### Speed Control

Adjust speech rate (when supported by backend):

```
Settings panel → Speed slider: 0.5x to 2.0x
Default: 1.0x (normal speed)

Note: Not all backends support speed adjustment
```

### Output Location

Configure where generated files are saved:

```
Settings panel → Save location
Default: ~/tts_output/
```

Press `Ctrl+O` to browse and change save location.

Files are auto-organized:
```
~/tts_output/
├── voice_name/          (organized by voice)
│   ├── 2024-12-06/     (organized by date)
│   │   ├── output_001.mp3
│   │   ├── output_002.mp3
│   │   └── ...
│   └── 2024-12-05/
└── ...
```

### Auto-Play

Automatically play audio after generation:

```
Settings panel → Toggle Auto-play
Default: Off
```

When enabled:
- Audio plays immediately after generation completes
- Uses system default audio player
- Generation waits for playback to finish

## Backend Management

### Viewing Backend Status

Press `Ctrl+B` to open the Backend Status panel:

```
┌────────────────────────────────────────┐
│ BACKEND STATUS                         │
├────────────────────────────────────────┤
│ Kokoro                  ✓ AVAILABLE    │
│   Port: 8880            CPU            │
│   Voices: 50+           Speed: Fast    │
│                                        │
│ VoxCPM                  ✗ UNAVAILABLE  │
│   Port: 7860            GPU            │
│   Error: Connection refused            │
│   Last checked: 2 minutes ago          │
│                                        │
│ Higgs Audio             ✓ AVAILABLE    │
│   Port: 8085            GPU            │
│   Voices: 100+          Speed: Slow    │
│                                        │
│ [Refresh] [Switch] [Help]             │
└────────────────────────────────────────┘
```

### Switching Backends

To switch preferred backend:

```
1. Press Ctrl+B to open Backend Status
2. Highlight desired backend
3. Press Enter or click [Switch]
4. TUI confirms and updates configuration
```

The router will use your preferred backend automatically, with automatic failover to alternatives if unavailable.

## Configuration

### Settings File Location

TUI configuration stored in:
```
~/.unified-tts/tui_config.json
```

### Configuration Structure

```json
{
  "api_url": "http://localhost:8765",
  "default_voice": "bf_emma",
  "default_format": "mp3",
  "default_speed": 1.0,
  "auto_play": false,
  "save_location": "/home/user/tts_output",
  "preferred_backend": "kokoro",
  "favorites": [
    "bf_emma",
    "bf_josh",
    "rick_clone"
  ],
  "recent_voices": [
    "bf_emma",
    "bf_grace"
  ],
  "window_size": {
    "width": 200,
    "height": 50
  },
  "theme": "dark"
}
```

### Manual Configuration

Edit `~/.unified-tts/tui_config.json` directly for advanced settings:

```bash
# View current config
cat ~/.unified-tts/tui_config.json

# Edit with your editor
nano ~/.unified-tts/tui_config.json

# Reload in TUI with Ctrl+R
```

### Environment Variables

Override configuration with environment variables:

```bash
# API connection
export UNIFIED_TTS_API_URL="http://192.168.4.35:8765"

# Voice directory (for voice cloning)
export UNIFIED_TTS_VOICE_DIR="/path/to/voices"

# Voice preferences file
export UNIFIED_TTS_PREFS_FILE="/path/to/prefs.json"

# Start TUI
python tui_client.py
```

## Generation History

### Viewing History

Press `Ctrl+L` to open Generation History:

```
┌──────────────────────────────────────────────┐
│ GENERATION HISTORY              [Clear All]  │
├──────────────────────────────────────────────┤
│ 2024-12-06 14:23  bf_emma  "Hello world"    │
│ 2024-12-06 14:20  bf_josh  "Sample text..."  │
│ 2024-12-06 14:15  rick     "Wubba lubba..." │
│                                              │
│ [Details] [Regenerate] [Export] [Delete]   │
└──────────────────────────────────────────────┘
```

### History Features

- Click any entry to view details (voice, duration, format, size)
- Press Enter to regenerate with same settings
- Press `E` to export with new filename
- Press `D` to delete from disk and history
- Press `Ctrl+Shift+C` to copy text to clipboard

### Clearing History

```
Ctrl+L → [Clear All] → Confirm
History file cleared, but audio files remain on disk
```

## Presets System

### Creating Presets

Save frequently-used voice and settings combinations:

```
1. Configure voice, format, speed as desired
2. Press Ctrl+N to create preset
3. Enter preset name: "Audiobook - Emma Fast"
4. Preset saved to ~/.unified-tts/presets.json
```

### Using Presets

```
Settings panel → Presets dropdown
Select preset → Settings auto-apply
OR press Ctrl+Shift+P and type preset name
```

### Preset Examples

**Audiobook Narration**
```
Voice: bf_emma
Format: MP3
Speed: 0.95x
Quality: High
```

**Quick Announcements**
```
Voice: bf_josh
Format: MP3
Speed: 1.1x
Auto-play: On
```

**Archive Quality**
```
Voice: bf_emma
Format: FLAC
Speed: 1.0x
Quality: Maximum
```

## Troubleshooting

### API Connection Issues

**Problem:** "Cannot connect to API"

```
Solution:
1. Verify server is running: python server.py
2. Check API URL: Ctrl+R → Reload config
3. Verify port (default 8765): netstat -tuln | grep 8765
4. Try explicit URL: python tui_client.py --api-url http://localhost:8765
```

### Audio Playback Issues

**Problem:** Audio doesn't play with Ctrl+P

```
Solution:
1. Verify audio file was generated (check ~/tts_output/)
2. Test playback manually: ffplay output.mp3
3. Check system audio: pavucontrol (PulseAudio) or alsamixer
4. Disable auto-play, manually play: ffplay ~/tts_output/*/latest.mp3
```

**Problem:** Audio file not found after generation

```
Solution:
1. Check save location (Ctrl+S → Settings)
2. Verify directory permissions: ls -la ~/tts_output/
3. Create directory if missing: mkdir -p ~/tts_output
4. Check generation status in status panel
```

### Voice Selection Issues

**Problem:** "Voice not found" error

```
Solution:
1. Press Ctrl+B to check available backends
2. Ensure backend is running and accessible
3. Try different voice from available list
4. Check voice name spelling (case-sensitive)
```

**Problem:** Voice list shows as empty

```
Solution:
1. Check API connection (Ctrl+R)
2. Verify backends are running
3. Check API logs: tail -f unified_tts.log
4. Try: curl http://localhost:8765/v1/voices
```

### Generation Issues

**Problem:** "Text too long" error

```
Solution:
This shouldn't happen - Unified TTS handles chunking automatically.
If error occurs:
1. Check backend logs for specific error
2. Try shorter text (< 5000 chars) to isolate issue
3. Report issue with error details
```

**Problem:** Generation takes too long

```
Solution:
1. Check backend status (Ctrl+B)
2. Try different backend: faster backends available
3. Reduce text length or use faster speed (2.0x)
4. Check system resources: GPU memory, CPU load
```

### Theme and Display Issues

**Problem:** Colors look wrong or unreadable

```
Solution:
1. Check terminal color support: echo $TERM
2. Set 256-color support: export TERM=xterm-256color
3. Try different theme: Edit config → "theme": "light"
4. Restart TUI
```

**Problem:** Layout doesn't fit terminal

```
Solution:
1. Increase terminal size
2. Minimum supported: 160x40 characters
3. Optimal: 200x50 characters
4. Use Ctrl+R to reload layout after resizing
```

## Advanced Usage

### Batch Generation

Generate multiple texts efficiently:

```bash
# Create input file: texts.txt
cat > texts.txt << 'EOF'
Hello world
This is a test
Another sentence
EOF

# Use with TUI:
# 1. Open text input
# 2. Paste all texts
# 3. Generate once (will chunk automatically)
# OR generate multiple times with different selections
```

### Scripting TUI Operations

For automated workflows, consider using the API directly:

```bash
# Direct API call
curl -X POST http://localhost:8765/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Your text here",
    "voice": "bf_emma",
    "response_format": "mp3"
  }' -o output.mp3
```

### Integration with Other Tools

**With mpv (audio player):**
```bash
# Set auto-play to on, or manually play:
mpv ~/tts_output/*/latest.mp3
```

**With ffmpeg (audio processing):**
```bash
# Convert output format
ffmpeg -i output.mp3 -acodec libopus -b:a 192k output.opus

# Speed up audio
ffmpeg -i output.mp3 -filter:a "atempo=1.5" output_fast.mp3
```

**With text editors:**
- Some editors support running external commands
- Configure TUI as external TTS for selected text

## Plugin System

The TUI supports extensible plugins for custom functionality.

### Available Plugins (Built-in)

**Statistics Plugin**
- Word count, character count
- Estimated generation time
- File size projections
- Enable: Settings → Plugins → Statistics

**Clipboard Plugin**
- Paste from clipboard (Ctrl+V)
- Copy audio filename (Ctrl+C in history)
- Auto-copy API response

### Creating Custom Plugins

Plugins extend `BasePlugin` class:

```python
from tui_client import BasePlugin

class MyPlugin(BasePlugin):
    """Custom functionality for TUI."""

    name = "My Plugin"
    version = "1.0"
    description = "Does something cool"

    def on_load(self):
        """Called when plugin is loaded."""
        print("Plugin loaded!")

    def on_text_changed(self, text):
        """Called when text input changes."""
        # Process text, update UI, etc.
        pass

    def get_ui_components(self):
        """Return custom UI widgets to add."""
        return {
            "custom_button": ("My Button", self.on_button_press)
        }

    def on_button_press(self):
        """Handle custom button press."""
        pass
```

### Installing Plugins

```bash
# Create plugin file
touch ~/.unified-tts/plugins/my_plugin.py
# Edit with your plugin class

# Or drop into plugins directory
cp my_plugin.py ~/.unified-tts/plugins/

# Reload plugins in TUI: Ctrl+R
```

### Plugin Ideas

- **OCR Plugin:** Extract text from images before TTS
- **Markdown Plugin:** Parse markdown formatting for emphasis
- **AI Enhancement:** Auto-improve text with Claude/GPT suggestions
- **Voice Cloning Helper:** Streamlined interface for creating voice clones
- **Batch Processor:** Generate audio for files/directories
- **Quality Analyzer:** Inspect audio properties before saving

## Tips & Best Practices

### Efficient Voice Selection

1. Create favorites for voices you use frequently
2. Set defaults for your most common use case
3. Use search (Ctrl+F) to quickly find specific voices
4. Organize presets by use case (narration, announcements, etc.)

### Text Preparation

1. Use proper punctuation for natural pauses
2. Break long passages into logical chunks
3. Preview with shorter similar text first
4. Copy/paste from editors for complex content

### Quality Optimization

1. Kokoro generally faster; VoxCPM for character clones
2. MP3 suitable for most uses; FLAC for archival
3. Test voice with sample text before long generation
4. Check backend status if generation seems slow

### Performance Tips

1. Disable auto-play if not needed (faster workflow)
2. Close unused applications during generation
3. Monitor backend status (Ctrl+B) for resource issues
4. Clear history periodically to keep config lean

### Troubleshooting Checklist

When issues occur, check in order:
1. API connection status (Ctrl+R)
2. Backend availability (Ctrl+B)
3. Text content (special characters, length)
4. Output directory permissions (ls -la ~/tts_output)
5. System resources (free memory, GPU status)
6. Application logs (check ~/unified_tts.log)

## Configuration Reference

### Full Config Options

```json
{
  "api_url": "http://localhost:8765",
  "default_voice": "bf_emma",
  "default_format": "mp3",
  "default_speed": 1.0,
  "auto_play": false,
  "save_location": "/home/user/tts_output",
  "preferred_backend": "kokoro",
  "
  theme": "dark",
  "favorites": [],
  "recent_voices": [],
  "window_size": {
    "width": 200,
    "height": 50
  },
  "history_enabled": true,
  "max_history_entries": 100,
  "plugins_enabled": true,
  "plugins_directory": "~/.unified-tts/plugins"
}
```

### Environment Variable Reference

```bash
UNIFIED_TTS_API_URL          # Override API URL
UNIFIED_TTS_VOICE_DIR        # Voice directory location
UNIFIED_TTS_PREFS_FILE       # Preferences file location
UNIFIED_TTS_CONFIG_DIR       # Config directory location
UNIFIED_TTS_DEBUG            # Enable debug logging
```

## API Response Reference

The TUI internally uses these endpoints:

### Generate Audio
```
POST /v1/audio/speech
Body: {
  "input": "Text to synthesize",
  "voice": "voice_name",
  "response_format": "mp3",
  "speed": 1.0
}
Returns: Audio file (MP3, WAV, etc.)
```

### List Voices
```
GET /v1/voices
Returns: {
  "voices": [
    {
      "name": "bf_emma",
      "backend": "kokoro",
      ...
    }
  ]
}
```

### Backend Status
```
GET /v1/backends
Returns: {
  "backends": [
    {
      "name": "kokoro",
      "available": true,
      "port": 8880,
      "vram_gb": 2
    }
  ]
}
```

## Getting Help

### In-App Help
- Press `Ctrl+H` for help screen
- Hover over elements for tooltips
- Check status bar for hints

### Debugging

Enable debug mode for detailed logging:
```bash
# Start with debug enabled
python tui_client.py --debug

# Or press Ctrl+D in TUI to toggle debug
# Logs saved to ~/.unified-tts/tui_debug.log
```

### Reporting Issues

Include when reporting bugs:
1. Full error message from status panel
2. Output of `curl http://localhost:8765/` (API status)
3. Backend status from `Ctrl+B`
4. Content of `~/.unified-tts/tui_debug.log`
5. Output of `python server.py` for API logs

## FAQ

**Q: Can I use TUI without the web server running?**
A: No - TUI is a client that communicates with the Unified TTS server. Start with `python server.py` first.

**Q: How do I add new voices?**
A: For voice clones, see main README.md. For new backend voices, ensure backend is running and available to the server.

**Q: Can I batch process a directory of text files?**
A: Use the direct API with a script, or manually process files through TUI one at a time. Batch plugin coming soon.

**Q: What if my backend goes down during generation?**
A: Generation fails with error message. TUI automatically attempts reconnection. Restart backend and retry.

**Q: How do I back up my settings and history?**
A: Copy `~/.unified-tts/` directory:
```bash
cp -r ~/.unified-tts ~/.unified-tts.backup
```

**Q: Can multiple TUI instances run simultaneously?**
A: Yes - they share the same server and configuration, but maintain separate history/session state.

**Q: How do I change the default backend globally?**
A: Edit `~/.unified-tts/tui_config.json` and set `"preferred_backend"` value.

**Q: Is there a dark mode?**
A: Yes - default is dark. Change in config: `"theme": "light"` or `"dark"`

## Keyboard Shortcut Quick Reference

```
=== CORE ===
Ctrl+G  Generate
Ctrl+S  Save settings
Ctrl+Q  Quit
Ctrl+H  Help

=== NAVIGATION ===
Tab     Next panel
Shift+Tab Prev panel
Up/Down Select

=== VOICE ===
Ctrl+F  Search voices
Ctrl+*  Set default

=== PLAYBACK ===
Ctrl+P  Play audio
Ctrl+O  Open folder
Ctrl+L  History

=== ADVANCED ===
Ctrl+B  Backends
Ctrl+D  Debug
Ctrl+R  Reload config
Ctrl+N  New preset
```

---

For latest updates and detailed API documentation, see the main [README.md](../README.md).
