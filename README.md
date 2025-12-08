# Open Unified TTS

One API to rule them all - unlimited-length TTS with automatic chunking.

## The Problem

Most TTS models have strict length limits:

```
┌────────────────────────────────────────────────────────────┐
│                   RAW MODEL LIMITATIONS                    │
├────────────────────────────────────────────────────────────┤
│  Model Type          │  Max Words  │  Max Chars  │        │
├──────────────────────┼─────────────┼─────────────┤        │
│  Voice Clones        │  ~75        │  ~400       │        │
│  (VoxCPM, OpenAudio) │             │             │        │
├──────────────────────┼─────────────┼─────────────┤        │
│  Neural TTS          │  ~200       │  ~1200      │        │
│  (Kokoro)            │             │             │        │
├──────────────────────┼─────────────┼─────────────┤        │
│  Emotion Models      │  ~40        │  ~250       │        │
│  (Kyutai/Moshi)      │             │             │        │
├──────────────────────┼─────────────┼─────────────┤        │
│  Generative          │  ~100       │  ~600       │        │
│  (Higgs)             │             │             │        │
├──────────────────────┼─────────────┼─────────────┤        │
│  Cloud APIs          │  ~2500      │  ~15000     │        │
│  (ElevenLabs)        │             │             │        │
└────────────────────────────────────────────────────────────┘

Beyond these limits: quality degrades, audio cuts off, or errors.
```

**The Community Has Been Asking**

This isn't a solution looking for a problem. A quick search across Reddit shows hundreds of posts from people hitting these exact limitations:

| Community | What They're Asking |
|-----------|---------------------|
| r/LocalLLaMA | *"any opensource TTS without limit on character and can clone voice?"* (14+ upvotes) |
| r/elevenlabs | 50+ posts about character limits and workarounds |
| r/TextToSpeech | Multiple threads on long-form audio generation |
| r/SillyTavern | TTS cutting off mid-sentence in roleplay |
| r/selfhosted | Requests for unlimited local TTS solutions |

Common pain points:
- **"Text too long"** errors when generating audiobooks or articles
- **Voice clone quality degrading** after ~75 words
- **No seamless way** to stitch multiple generations together
- **Wanting one API** that works with multiple backends

## The Solution

**Open Unified TTS solves this** by chunking text intelligently at natural boundaries (sentences, paragraphs), generating each chunk within model limits, and stitching results seamlessly with crossfade. The result: unlimited-length audio in any voice, with consistent quality throughout.

**Key Features:**
- **Smart Chunking** - Splits at sentence/paragraph boundaries, never mid-word
- **Crossfade Stitching** - 30-50ms overlap eliminates audio seams
- **OpenAI-Compatible** - Drop-in replacement for OpenAI TTS API
- **Multi-Backend** - Route different voices to different engines automatically

## Choose Your Path

| I want to... | Use this |
|--------------|----------|
| Just try it (no setup) | [Hosted demo](https://lessfortts.loser.com) - Free during alpha |
| Simple web UI + API | [Open TTS Studio](https://github.com/loserbcc/open-tts-studio) - Most users start here |
| Raw API with multi-backend | This repo (instructions below) |
| Terminal UI | `./tui_client.py` after setup |

## Quick Start (Kokoro Backend)

**New to this project?** Start with Kokoro - 67 built-in voices, runs on CPU, no reference audio needed.

### 1. Start Kokoro Backend

```bash
# CPU version (works anywhere)
docker run -d --name kokoro-tts -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-cpu:latest

# GPU version (faster, requires NVIDIA GPU)
docker run -d --name kokoro-tts --gpus all -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-gpu:latest
```

### 2. Start Open Unified TTS

```bash
git clone https://github.com/loserbcc/open-unified-tts.git
cd open-unified-tts
pip install -r requirements.txt
python server.py
```

### 3. Verify It's Working

```bash
# Check health endpoint
curl http://localhost:8765/health

# Should return: {"status":"ok","backend":"kokoro",...}
```

### 4. Generate Speech

```bash
# Short text - direct to MP3 (fast)
curl -X POST http://localhost:8765/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model":"tts-1","voice":"bf_emma","input":"Hello, this is a test."}' \
  --output test.mp3

# Long text - auto-chunked and stitched
curl -X POST http://localhost:8765/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model":"tts-1","voice":"am_adam","input":"Your 2000 word article here..."}' \
  --output audiobook.mp3
```

**[Full Kokoro Setup Guide →](docs/kokoro_setup_guide.md)** | **[Listen to Sample Output](demo/kokoro_audiobook_demo.mp3)**

## Demos

- **[Watch the Intro (30 sec)](demo/intro.mp4)** - Quick overview
- **[Live Demo (4 min)](demo/live_demo.mp4)** - Chunking and stitching in action
- **[Kokoro Audiobook Sample](demo/kokoro_audiobook_demo.mp3)** - 73 seconds of seamless audio ([details](demo/kokoro_demo_info.md))
- **[VoxCPM 1.5 Demo](demo/voxcpm15_intro_morgan.mp3)** - Morgan Freeman voice at 44.1kHz
- **[Project Explanation (audio)](demo/project_explanation.mp3)** - Generated using this system

## How It Works

```
INPUT: 2000-word article + "morgan" voice
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│  1. SMART CHUNKING                                          │
│                                                             │
│  Full text split at natural boundaries:                     │
│  • Sentence endings                                         │
│  • Paragraph breaks                                         │
│  • Never mid-word                                           │
│                                                             │
│  Chunk size based on backend profile (optimal < max)        │
│                                                             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │ Chunk 1 │ │ Chunk 2 │ │ Chunk 3 │ │ Chunk N │           │
│  │ ~50 wds │ │ ~50 wds │ │ ~50 wds │ │ ~50 wds │           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
└─────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│  2. GENERATE EACH CHUNK                                     │
│                                                             │
│  Each chunk sent to backend (within its limits)             │
│                                                             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │ Audio 1 │ │ Audio 2 │ │ Audio 3 │ │ Audio N │           │
│  │  ~5 sec │ │  ~5 sec │ │  ~5 sec │ │  ~5 sec │           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
└─────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│  3. STITCH WITH CROSSFADE                                   │
│                                                             │
│  Audio chunks joined with crossfade to eliminate seams:     │
│                                                             │
│  ──────┐                                                    │
│        ╲  ← crossfade (30-50ms)                             │
│         ╲──────┐                                            │
│                ╲                                            │
│                 ╲──────                                     │
│                                                             │
│  Result: Seamless audio, indistinguishable from single gen  │
└─────────────────────────────────────────────────────────────┘
                    │
                    ▼
OUTPUT: Single audio file, unlimited length, consistent voice
```

### Why Crossfade?

```
Without crossfade:          With crossfade:
─────┐ ┌─────               ─────╲ ╱─────
     │ │      ← click!           ╳      ← smooth
─────┘ └─────               ─────╱ ╲─────
```

The 30-50ms crossfade eliminates audible clicks between chunks while preserving natural speech rhythm.

## API Reference

### Core Endpoints

```bash
# Generate speech (OpenAI-compatible)
POST /v1/audio/speech
{
  "model": "tts-1",
  "voice": "bf_emma",
  "input": "Your text here",
  "response_format": "mp3"  # Optional: mp3, wav, flac, opus
}

# List available voices
GET /v1/voices

# Check health and active backend
GET /health

# List available models (OpenAI-compatible)
GET /v1/models
```

### Backend Management

```bash
# List backends and status
GET /v1/backends

# Set preferred backend
POST /v1/backends/switch
{"backend": "kokoro"}

# Get voice preferences (which voice uses which backend)
GET /v1/voice-prefs

# Set backend preference for specific voice
POST /v1/voice-prefs/morgan
{"backend": "voxcpm"}
```

### Kokoro Voice Options

| Category | Voices |
|----------|--------|
| **American Female** | `af_alloy`, `af_bella`, `af_heart`, `af_nova`, `af_sky`, `af_sarah`, `af_jessica`, `af_nicole`, `af_river` |
| **American Male** | `am_adam`, `am_echo`, `am_eric`, `am_onyx`, `am_michael`, `am_liam`, `am_fenrir`, `am_puck` |
| **British Female** | `bf_alice`, `bf_emma`, `bf_lily` |
| **British Male** | `bm_daniel`, `bm_fable`, `bm_george`, `bm_lewis` |
| **OpenAI Compatible** | `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer` |

## Backends

### Which Backend Should I Use?

**Just starting?** → Kokoro (easiest setup, 67 voices, CPU-friendly)

**Need voice cloning?** → See [BACKENDS.md](docs/BACKENDS.md) for VoxCPM and other options

**Want everything?** → Run multiple backends and let the router choose automatically

### Supported Backends

| Backend | Type | Voices | Best For | Setup |
|---------|------|--------|----------|-------|
| **Kokoro** | Neural TTS | 67 built-in | Quick start, high quality, no GPU | [Guide](docs/kokoro_setup_guide.md) |
| `openaudio` | Voice Clone | Custom | Cloning specific voices | Requires separate setup |
| `voxcpm` | Voice Clone | Custom | High-quality voice cloning | Requires GPU |
| `voxcpm15` | Voice Clone | 88+ pre-loaded | 44.1kHz output, lighter VRAM | Requires GPU |
| `fishtts` | Voice Clone | Custom | Fish Speech synthesis | Requires separate setup |
| `chatterbox` | Voice Clone | Custom | Emotion control | Requires separate setup |
| `kyutai` | Emotion | 8 emotions | Emotional expression | Requires separate setup |
| `higgs` | Generative | Scene-based | Creative voice generation | Requires GPU |
| `vibevoice` | Streaming | Microsoft | Real-time TTS | Requires separate setup |
| `minimax` | Cloud | Professional | Production voices | API key required |
| `acestep` | Musical | Singing | Music/vocals | Requires GPU |
| `elevenlabs` | Cloud | Many | Fallback/variety | API key required |

**Note:** Only Kokoro has an easy Docker setup. Other backends require manual installation. See [BACKENDS.md](docs/BACKENDS.md) for details.

### Backend Profiles

Each backend has a profile defining its capabilities and optimal chunking strategy:

```python
# backend_profiles.py
"kokoro": {
    "max_words": 200,      # Hard limit
    "max_chars": 1200,
    "optimal_words": 150,  # Target for chunking
    "needs_chunking": True,
    "crossfade_ms": 30,    # Stitch overlap
},
"voxcpm": {
    "max_words": 75,
    "max_chars": 400,
    "optimal_words": 50,
    "needs_chunking": True,
    "crossfade_ms": 50,
},
"voxcpm15": {
    "max_words": 150,       # Handles longer chunks
    "max_chars": 800,
    "optimal_words": 100,
    "needs_chunking": True,
    "crossfade_ms": 50,
    "sample_rate": 44100,   # 2x quality of VoxCPM
}
```

## Configuration

All configuration via environment variables:

```bash
# Backend URLs
KOKORO_HOST=http://localhost:8880
OPENAUDIO_URL=http://localhost:8080
VOXCPM_URL=http://localhost:7860
VOXCPM15_HOST=http://mother:7870  # VoxCPM 1.5 (44.1kHz)
FISHTTS_URL=http://localhost:7861
KYUTAI_URL=http://localhost:8086
HIGGS_URL=http://localhost:8085
VIBEVOICE_URL=http://localhost:8087

# Cloud API keys
MINIMAX_API_KEY=your_minimax_key
ELEVENLABS_API_KEY=sk_...

# Server settings
UNIFIED_TTS_PORT=8765
UNIFIED_TTS_HOST=0.0.0.0

# Voice directory (for voice clones)
UNIFIED_TTS_VOICE_DIR=~/.unified-tts/voices
```

## Web Interfaces

### Option 1: Open TTS Studio (Recommended)

Full-featured Gradio web interface with voice organization, batch processing, and export options.

**[github.com/loserbcc/open-tts-studio](https://github.com/loserbcc/open-tts-studio)**

### Option 2: Audiobook Production Studio (This Repo)

Simpler Gradio interface for document-to-audiobook conversion:

```bash
# Install additional dependencies
pip install gradio pypdf python-docx

# Start the web interface (after server.py is running)
python gradio_studio.py --port 7865
```

**Features:**
- Upload PDF, DOCX, or TXT files
- Edit extracted text before generation
- 67+ voices organized by category
- Multiple output formats (MP3, WAV, FLAC, Opus)
- Real-time API status monitoring

### Option 3: Terminal UI

A modern terminal-based interface built with Textual:

```bash
# Install TUI dependencies
pip install textual httpx rich

# Start the server first, then run TUI
python tui_client.py
```

**Controls:**
- `Ctrl+G` - Generate speech from text input
- `Ctrl+R` - Refresh API status and voices
- `Ctrl+Q` - Quit

**[Full TUI Documentation →](TUI_CLIENT_README.md)**

## Hosted SaaS Option

**Don't want to self-host?** Use our hosted API at [lessfortts.loser.com](https://lessfortts.loser.com):

- **67+ Kokoro voices** + character clones (Morgan Freeman, Rick & Morty, Yoda, etc.)
- **OpenAI-compatible API** - drop-in replacement
- **Free during alpha** - no credit card required

```bash
# Just point at the hosted API instead of localhost
curl -X POST https://lessfortts.loser.com/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"voice":"bf_emma","input":"Hello from the cloud!"}' \
  -o test.mp3
```

> **Coming Soon:** API keys and MCP access tokens. Currently in dev/testing - free access while we build out authentication. Want early access? Email buddy@loser.com.

### MCP Integration (AI-Native Interface)

Use TTS directly from Claude, Cline, Cursor, or any MCP-compatible AI:

```bash
# See the simple studio version for the MCP server
git clone https://github.com/loserbcc/open-tts-studio.git
cd open-tts-studio/mcp-server
uv sync
claude mcp add unified-tts-simple uv run python server.py
```

Then just ask your AI: *"Read this article aloud with Emma's voice"* - no API calls needed.

**[Full MCP documentation →](https://github.com/loserbcc/open-tts-studio#-mcp-server---the-ai-native-interface)**

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     YOUR APPLICATION                        │
│              (Any OpenAI TTS compatible client)             │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ POST /v1/audio/speech
                          │ {"voice": "morgan", "input": "..."}
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   OPEN UNIFIED TTS                          │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Router    │  │   Chunker   │  │  Stitcher   │         │
│  │             │  │             │  │             │         │
│  │ • Backend   │  │ • Smart     │  │ • Crossfade │         │
│  │   selection │  │   splitting │  │ • Normalize │         │
│  │ • Failover  │  │ • Profile-  │  │ • Format    │         │
│  │ • Voice     │  │   aware     │  │   convert   │         │
│  │   prefs     │  │             │  │             │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Backend 1  │  │  Backend 2  │  │  Backend N  │
│  (Kokoro)   │  │  (VoxCPM)   │  │ (ElevenLabs)│
│             │  │             │  │             │
│  67 Neural  │  │  Voice      │  │  Cloud      │
│  Voices     │  │  Clones     │  │  Fallback   │
└─────────────┘  └─────────────┘  └─────────────┘
```

## Smart Format Handling

The server optimizes format conversion based on text length:

| Scenario | Processing | Why |
|----------|------------|-----|
| **Short text** (<200 words) | Request final format (MP3) directly from backend | Efficient - no conversion needed |
| **Long text** (>200 words) | Generate WAV chunks → stitch → convert to final | WAV required for lossless crossfade stitching |

This means short requests are fast and efficient, while long requests maintain quality through proper audio processing.

## Performance

Tested benchmarks (Kokoro on CPU):

| Input | Output | Time | Hardware |
|-------|--------|------|----------|
| 230 words | 73s audio (630KB MP3) | ~30s | AMD Ryzen + RTX 4070 (GPU unused) |
| 50 words | 15s audio | ~5s | Same |

Kokoro GPU mode is significantly faster for batch generation.

## Voice Preferences

Route specific voices to specific backends for optimal quality:

```bash
# Set morgan to always use voxcpm (best quality for this clone)
curl -X POST http://localhost:8765/v1/voice-prefs/morgan \
  -H "Content-Type: application/json" \
  -d '{"backend": "voxcpm"}'
```

Preferences are stored in `~/.unified-tts/voice_prefs.json`.

## Extensibility

> Any TTS or audio generation model with an API can plug in as a backend. Voice cloning, emotion synthesis, even musical TTS. If it has an endpoint, it can join the party.

> Because this is OpenAI TTS-compatible, it plugs directly into tools you already use - [OpenWebUI](https://github.com/open-webui/open-webui), [SillyTavern](https://github.com/SillyTavern/SillyTavern), or any app with OpenAI TTS support. Point them at this API, connect your backends, and you've got a production audio studio. No code changes needed.

## Directory Structure

```
open-unified-tts/
├── server.py           # FastAPI application
├── router.py           # Backend selection & failover
├── chunker.py          # Smart text splitting
├── stitcher.py         # Audio concatenation with crossfade
├── voices.py           # Voice clone discovery
├── voice_prefs.py      # Per-voice backend routing
├── backend_profiles.py # Backend capabilities
├── config.py           # Environment configuration
├── gradio_studio.py    # Simple web interface
├── tui_client.py       # Terminal UI
├── adapters/
│   ├── base.py         # Abstract backend interface
│   ├── kokoro.py       # Kokoro neural TTS (67+ voices)
│   ├── openaudio.py    # OpenAudio/Fish Speech S1-mini
│   ├── voxcpm.py       # VoxCPM voice cloning
│   ├── voxcpm15.py     # VoxCPM 1.5 (44.1kHz, 88+ voices)
│   ├── fishtts.py      # FishTTS
│   ├── kyutai.py       # Kyutai/Moshi emotions
│   ├── higgs.py        # Higgs Audio generative
│   ├── vibevoice.py    # Microsoft VibeVoice
│   ├── minimax.py      # MiniMax TTS cloud
│   ├── acestep.py      # ACE-Step musical TTS
│   └── elevenlabs.py   # ElevenLabs cloud
├── docs/
│   ├── kokoro_setup_guide.md  # Kokoro setup documentation
│   └── BACKENDS.md            # Backend selection and setup guide
└── demo/
    ├── kokoro_audiobook_demo.mp3  # Kokoro sample output
    ├── kokoro_demo_info.md        # Demo details
    └── voxcpm15_intro_morgan.mp3  # VoxCPM 1.5 Morgan demo
```

## License

Apache License 2.0 - See LICENSE file.
