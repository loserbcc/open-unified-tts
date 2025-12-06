# Quick Start - TUI Client

Get up and running with the Open Unified TTS TUI client in 5 minutes.

## Prerequisites

1. **TTS API Server** must be running:
   ```bash
   cd /home/brian/projects/open-unified-tts
   python server.py
   ```
   Server will start on http://localhost:8765

2. **Python 3.10+** installed

3. **Optional**: `mpv` for audio playback
   ```bash
   sudo pacman -S mpv  # Arch/CachyOS
   ```

## Installation

### Option 1: Quick Install (Recommended)

```bash
cd /home/brian/projects/open-unified-tts

# Run the install script
./install_tui.sh

# Or manually with uv (faster)
uv pip install -r requirements-tui.txt
```

### Option 2: Manual Install

```bash
pip install textual httpx rich
```

## Running the Client

```bash
# Start with default settings
./tui_client.py

# Or specify API URL
./tui_client.py --api-url http://localhost:8765

# Disable auto-play
./tui_client.py --no-autoplay
```

## Basic Usage

1. **Enter text** in the left panel (paste works!)
2. **Select a voice** from the dropdown (organized by category)
3. **Choose output format** (mp3, wav, flac, opus)
4. **Press Generate** or hit `Ctrl+G`
5. **Find your audio** in `~/tts_output/`

## Keybindings

| Key | Action |
|-----|--------|
| `Ctrl+G` | Generate speech |
| `Ctrl+R` | Refresh API |
| `Ctrl+Q` | Quit |
| `F1` | Help |

## Testing the System

```bash
# Test plugin system
python test_plugins.py

# Check API connection
curl http://localhost:8765/health

# List available voices
curl http://localhost:8765/v1/voices | python -m json.tool
```

## Troubleshooting

### "No module named 'textual'"
```bash
pip install -r requirements-tui.txt
```

### "API Offline"
Start the TTS server:
```bash
python server.py
```

### No voices showing
Check voice directory:
```bash
ls ~/.unified-tts/voices/
```

## What's Next?

- Read the full documentation: `TUI_CLIENT_README.md`
- Explore plugins: `plugins/`
- Create custom plugins: See `plugins/example_plugin.py`

## File Locations

- **Output**: `~/tts_output/tts_TIMESTAMP_VOICE.FORMAT`
- **Voices**: `~/.unified-tts/voices/` (configurable)
- **Logs**: Terminal output only

---

**Enjoy your TTS!**
