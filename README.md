# Open Unified TTS

An OpenAI-compatible TTS API that unifies multiple text-to-speech backends with smart chunking for unlimited-length generation.

**Tested Backends:** Kokoro, VibeVoice, OpenAudio S1-mini, FishTTS, VoxCPM, VoxCPM 1.5, MiniMax TTS, Chatterbox, Higgs Audio, Kyutai/Moshi, ACE-Step (singing/musical TTS)

**[Watch the Intro](demo/intro.mp4)** - 30-second overview of what this does.

**[Live Demo (4 min)](demo/live_demo.mp4)** - Screen recording showing the chunking and stitching in action with multi-voice narration.

**[Kokoro Audiobook Demo](demo/kokoro_audiobook_demo.mp3)** - 73-second audiobook sample generated with Kokoro (`bf_emma` voice), demonstrating chunked generation and seamless stitching. [Details](demo/kokoro_demo_info.md)

**[VoxCPM 1.5 Demo](demo/voxcpm15_intro_morgan.mp3)** - Morgan Freeman voice explaining VoxCPM 1.5's 44.1kHz high-quality output.

**[Rough Demo Audio (bad voice samples)](demo/demo_rough_samples.mp3)** - Audio-only version. Uses hastily-grabbed voice samples - your results will be better with proper reference audio.

**[Project Explanation (audio)](demo/project_explanation.mp3)** - What is this? How does it work? This audio was generated using the unified TTS system itself. Have questions or a specific use case? [Open an issue](https://github.com/loserbcc/open-unified-tts/issues) - tell me what you need and we'll figure it out together!

## 🚀 Start Here: Kokoro (Easiest Setup)

**New to this project?** Start with Kokoro - 50+ built-in voices, runs on CPU, no reference audio needed.

1. `docker run -d -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-cpu:latest`
2. `pip install -r requirements.txt && python server.py`
3. Generate: `curl -X POST http://localhost:8765/v1/audio/speech -d '{"voice":"bf_emma","input":"Hello world"}' -o test.mp3`

**[📖 Full Kokoro Setup Guide](docs/kokoro_setup_guide.md)** | **[🎧 Listen to Sample Output](demo/kokoro_audiobook_demo.mp3)**

---

> **Extensibility:** Any TTS or audio generation model with an API can plug in as a backend. Voice cloning, emotion synthesis, even musical TTS (yes, rapping AI is a thing). If it has an endpoint, it can join the party.

> **Instant Integration:** Because this is OpenAI TTS-compatible, it plugs directly into tools you already use - [OpenWebUI](https://github.com/open-webui/open-webui), [SillyTavern](https://github.com/SillyTavern/SillyTavern), or any app with OpenAI TTS support. Point them at this API, connect your backends (Higgs Audio, VoxCPM, ElevenLabs, whatever), and you've got a production audio studio. No code changes needed.

## 🌐 Zero-Setup Option: Hosted SaaS

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

---

## Why This Exists

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

**Open Unified TTS solves this** by chunking text intelligently, generating each chunk within model limits, and stitching the results seamlessly.

### The Community Has Been Asking

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

If you've hit any of these walls, you're in the right place.

## Quick Start with Kokoro (Easiest)

Kokoro is the fastest way to get started - 50+ built-in voices, no reference audio needed, runs on CPU.

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

### 3. Generate Speech

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

### Kokoro Voice Options

| Category | Voices |
|----------|--------|
| **American Female** | `af_alloy`, `af_bella`, `af_heart`, `af_nova`, `af_sky`, `af_sarah`, `af_jessica`, `af_nicole`, `af_river` |
| **American Male** | `am_adam`, `am_echo`, `am_eric`, `am_onyx`, `am_michael`, `am_liam`, `am_fenrir`, `am_puck` |
| **British Female** | `bf_alice`, `bf_emma`, `bf_lily` |
| **British Male** | `bm_daniel`, `bm_fable`, `bm_george`, `bm_lewis` |
| **OpenAI Compatible** | `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer` |

**[Full Kokoro Setup Guide →](docs/kokoro_setup_guide.md)**

## Web Interface (Optional)

Prefer a GUI over command line? The **Audiobook Production Studio** provides a Gradio web interface for document-to-audiobook conversion.

```bash
# Install additional dependencies
pip install gradio pypdf python-docx

# Start the web interface (after server.py is running)
python gradio_studio.py --port 7865
```

**Features:**
- Upload PDF, DOCX, or TXT files
- Edit extracted text before generation
- 50+ voices organized by category
- Multiple output formats (MP3, WAV, FLAC, Opus)
- Real-time API status monitoring

**Coming soon:** OCR support for scanned documents (modular plugin architecture)

## TUI Client (Experimental)

A terminal-based interface for text-to-speech generation using the Textual framework.

> **⚠️ Status:** Work-in-progress concept. Core TTS generation works, but some features (like file import) need testing/development.

```bash
# Install TUI dependencies
pip install textual httpx rich

# Start the server first, then run TUI
python tui_client.py
```

**Controls:**
- `Ctrl+G` - Generate speech from text input
- `Ctrl+R` - Refresh API status and voices
- `Ctrl+O` - Import file (experimental - requires zenity)
- `Ctrl+Q` - Quit

**Features:**
- Voice selection grouped by category
- Output format selection (MP3, WAV, FLAC, Opus)
- Auto-play toggle for generated audio
- Real-time API health monitoring

**Known Limitations:**
- File import feature is in development (PDF/DOCX support requires additional packages)
- Designed for Kokoro backend - other backends may need testing

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

### Smart Format Handling

The server optimizes format conversion based on text length:

| Scenario | Processing | Why |
|----------|------------|-----|
| **Short text** (<200 words) | Request final format (MP3) directly from backend | Efficient - no conversion needed |
| **Long text** (>200 words) | Generate WAV chunks → stitch → convert to final | WAV required for lossless crossfade stitching |

This means short requests are fast and efficient, while long requests maintain quality through proper audio processing.

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
│  50+ Neural │  │  Voice      │  │  Cloud      │
│  Voices     │  │  Clones     │  │  Fallback   │
└─────────────┘  └─────────────┘  └─────────────┘
```

## Supported Backends

| Backend | Type | Voices | Best For |
|---------|------|--------|----------|
| **Kokoro** | Neural TTS | 50+ built-in | Quick start, no setup, high quality |
| `openaudio` | Voice Clone | Custom | Cloning specific voices |
| `voxcpm` | Voice Clone | Custom | High-quality voice cloning |
| `voxcpm15` | Voice Clone | 88+ pre-loaded | 44.1kHz output, lighter VRAM (~8GB) |
| `fishtts` | Voice Clone | Custom | Fish Speech synthesis |
| `chatterbox` | Voice Clone | Custom | Emotion control |
| `kyutai` | Emotion | 8 emotions | Emotional expression |
| `higgs` | Generative | Scene-based | Creative voice generation |
| `vibevoice` | Streaming | Microsoft | Real-time TTS |
| `minimax` | Cloud | Professional | Production voices |
| `acestep` | Musical | Singing | Music/vocals |
| `elevenlabs` | Cloud | Many | Fallback/variety |

### Backend Setup Guides

- **[Kokoro Setup](docs/kokoro_setup_guide.md)** - Recommended starting point

## Backend Profiles

Each backend has a profile defining its capabilities:

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

The chunker uses these profiles to split text appropriately for each backend.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/audio/speech` | POST | Generate speech (OpenAI-compatible) |
| `/v1/voices` | GET | List available voices |
| `/v1/backends` | GET | List backends and status |
| `/v1/backends/switch` | POST | Set preferred backend |
| `/v1/voice-prefs` | GET | Get voice→backend preferences |
| `/v1/voice-prefs/{voice}` | POST | Set backend preference for voice |
| `/v1/models` | GET | List models (OpenAI-compatible) |
| `/health` | GET | Health check |

## Voice Preferences

Route specific voices to specific backends for optimal quality:

```bash
# Set morgan to always use voxcpm (best quality for this clone)
curl -X POST http://localhost:8765/v1/voice-prefs/morgan \
  -H "Content-Type: application/json" \
  -d '{"backend": "voxcpm"}'
```

Preferences are stored in `~/.unified-tts/voice_prefs.json`.

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
├── adapters/
│   ├── base.py         # Abstract backend interface
│   ├── kokoro.py       # Kokoro neural TTS (50+ voices)
│   ├── openaudio.py    # OpenAudio/Fish Speech S1-mini
│   ├── voxcpm.py       # VoxCPM voice cloning
│   ├── voxcpm15.py     # VoxCPM 1.5 (44.1kHz, 88+ voices)
│   ├── fishtts.py      # FishTTS
│   ├── kyutai.py       # Kyutai/Moshi emotions
│   ├── higgs.py        # Higgs Audio generative
│   ├── vibevoice.py    # Microsoft VibeVoice
│   ├── minimax.py      # MiniMax TTS cloud
│   └── elevenlabs.py   # ElevenLabs cloud
├── docs/
│   └── kokoro_setup_guide.md  # Kokoro setup documentation
└── demo/
    ├── kokoro_audiobook_demo.mp3  # Kokoro sample output
    ├── kokoro_demo_info.md        # Demo details
    └── voxcpm15_intro_morgan.mp3  # VoxCPM 1.5 Morgan demo
```

## Performance

Tested benchmarks (Kokoro on CPU):

| Input | Output | Time | Hardware |
|-------|--------|------|----------|
| 230 words | 73s audio (630KB MP3) | ~30s | AMD Ryzen + RTX 4070 (GPU unused) |
| 50 words | 15s audio | ~5s | Same |

Kokoro GPU mode is significantly faster for batch generation.

## Why Chunking + Stitching?

**The Problem:**
```
You: "Read me this 2000-word article in Morgan Freeman's voice"
Raw Model: "I can only do 75 words at a time" 💥
```

**The Solution:**
```
Open Unified TTS:
1. Splits into 40 chunks of ~50 words each
2. Generates each chunk (within model limits)
3. Crossfades chunks together (eliminates seams)
4. Returns single seamless audio file

You get: 15-minute narration, consistent voice, no quality loss
```

**Why Crossfade?**
```
Without crossfade:          With crossfade:
─────┐ ┌─────               ─────╲ ╱─────
     │ │      ← click!           ╳      ← smooth
─────┘ └─────               ─────╱ ╲─────
```

The 30-50ms crossfade eliminates audible clicks between chunks while preserving natural speech rhythm.

## License

Apache License 2.0 - See LICENSE file.
