# Open Unified TTS

An OpenAI-compatible TTS API that unifies multiple text-to-speech backends with smart chunking for unlimited-length generation.

**Tested Backends:** Kokoro, VibeVoice, OpenAudio S1-mini, FishTTS, VoxCPM, MiniMax TTS, Chatterbox, Higgs Audio, Kyutai/Moshi, ACE-Step (singing/musical TTS)

**[Watch the Intro](demo/intro.mp4)** - 30-second overview of what this does.

**[Live Demo (4 min)](demo/live_demo.mp4)** - Screen recording showing the chunking and stitching in action with multi-voice narration.

**[Rough Demo Audio (bad voice samples)](demo/demo_rough_samples.mp3)** - Audio-only version. Uses hastily-grabbed voice samples - your results will be better with proper reference audio.

> **Extensibility:** Any TTS or audio generation model with an API can plug in as a backend. Voice cloning, emotion synthesis, even musical TTS (yes, rapping AI is a thing). If it has an endpoint, it can join the party.

> **Instant Integration:** Because this is OpenAI TTS-compatible, it plugs directly into tools you already use - [OpenWebUI](https://github.com/open-webui/open-webui), [SillyTavern](https://github.com/SillyTavern/SillyTavern), or any app with OpenAI TTS support. Point them at this API, connect your backends (Higgs Audio, VoxCPM, ElevenLabs, whatever), and you've got a production audio studio. No code changes needed.

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
│        ╲  ← crossfade (50ms)                                │
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
│  (VoxCPM)   │  │  (Higgs)    │  │ (ElevenLabs)│
│             │  │             │  │             │
│  Voice      │  │  Generative │  │  Cloud      │
│  Clones     │  │  Scenes     │  │  Fallback   │
└─────────────┘  └─────────────┘  └─────────────┘
```

## Quick Start

### 1. Configure Environment

```bash
cp .env.example .env
# Edit .env with your backend URLs and API keys
```

### 2. Set Up Voice Directory

```bash
mkdir -p ~/.unified-tts/voices

# Add voice clones (reference audio + transcript)
mkdir ~/.unified-tts/voices/morgan
cp morgan_sample.wav ~/.unified-tts/voices/morgan/reference.wav
echo "The transcription of the reference audio" > ~/.unified-tts/voices/morgan/transcript.txt
```

### 3. Start Server

```bash
pip install -r requirements.txt
python server.py
```

### 4. Generate Speech

```bash
# Using curl
curl -X POST http://localhost:8765/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"voice": "morgan", "input": "Your text here, any length."}' \
  --output speech.mp3

# Using OpenAI Python client
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8765/v1", api_key="unused")

audio = client.audio.speech.create(
    model="tts-1",
    voice="morgan",
    input="Your text here, any length."
)
audio.stream_to_file("speech.mp3")
```

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

## Backend Profiles

Each backend has a profile defining its capabilities:

```python
# backend_profiles.py
"voxcpm": {
    "max_words": 75,       # Hard limit
    "max_chars": 400,
    "optimal_words": 50,   # Target for chunking
    "needs_chunking": True,
    "crossfade_ms": 50,    # Stitch overlap
}
```

The chunker uses these profiles to split text appropriately for each backend.

## Voice Preferences

Route specific voices to specific backends for optimal quality:

```bash
# Set morgan to always use voxcpm (best quality for this clone)
curl -X POST http://localhost:8765/v1/voice-prefs/morgan \
  -H "Content-Type: application/json" \
  -d '{"backend": "voxcpm"}'
```

Preferences are stored in `~/.unified-tts/voice_prefs.json`.

## Supported Backends

| Backend | Type | Description |
|---------|------|-------------|
| `openaudio` | Voice Clone | Fish Speech / OpenAudio S1-mini containers |
| `voxcpm` | Voice Clone | VoxCPM voice cloning |
| `fishtts` | Voice Clone | FishTTS voice synthesis |
| `kokoro` | Neural TTS | Kokoro high-quality neural voices |
| `chatterbox` | Voice Clone | Chatterbox TTS with emotion control |
| `kyutai` | Emotion | Kyutai/Moshi emotional voices |
| `higgs` | Generative | Higgs Audio scene-based voice generation |
| `vibevoice` | Streaming | Microsoft VibeVoice real-time TTS |
| `minimax` | Cloud | MiniMax TTS professional voices |
| `acestep` | Musical | ACE-Step singing/musical TTS |
| `elevenlabs` | Cloud | ElevenLabs API (fallback) |

### Backend Compatibility Notes

- **Kokoro**: Excellent quality neural TTS, fast inference
- **Chatterbox**: Voice cloning with emotion/exaggeration control
- **VibeVoice**: Microsoft's streaming TTS (Dec 2025), works on CPU
- **OpenAudio S1-mini**: Compact voice cloning model
- **FishTTS**: Fish Speech voice synthesis
- **VoxCPM**: High-quality voice cloning with reference audio
- **MiniMax TTS**: Cloud API with professional voice presets
- **Higgs Audio**: Generative voices via scene descriptions
- **Kyutai/Moshi**: Emotional expression synthesis
- **ACE-Step**: Singing and musical TTS generation

## Configuration

All configuration via environment variables:

```bash
# Backend URLs
OPENAUDIO_URL=http://localhost:8080
VOXCPM_URL=http://localhost:7860
FISHTTS_URL=http://localhost:7861
KOKORO_URL=http://localhost:8880
KYUTAI_URL=http://localhost:8086
HIGGS_URL=http://localhost:8085
VIBEVOICE_URL=http://localhost:8087

# Cloud API keys
MINIMAX_API_KEY=your_minimax_key
ELEVENLABS_API_KEY=sk_...

# Server settings
UNIFIED_TTS_PORT=8765
UNIFIED_TTS_HOST=0.0.0.0

# Voice directory
UNIFIED_TTS_VOICE_DIR=~/.unified-tts/voices
```

## Directory Structure

```
open-unified-tts/
├── server.py           # FastAPI application
├── router.py           # Backend selection & failover
├── chunker.py          # Smart text splitting
├── stitcher.py         # Audio concatenation
├── voices.py           # Voice clone discovery
├── voice_prefs.py      # Per-voice backend routing
├── backend_profiles.py # Backend capabilities
├── config.py           # Environment configuration
└── adapters/
    ├── base.py         # Abstract backend interface
    ├── openaudio.py    # OpenAudio/Fish Speech S1-mini
    ├── voxcpm.py       # VoxCPM voice cloning
    ├── fishtts.py      # FishTTS
    ├── kokoro.py       # Kokoro neural TTS
    ├── kyutai.py       # Kyutai/Moshi emotions
    ├── higgs.py        # Higgs Audio generative
    ├── vibevoice.py    # Microsoft VibeVoice
    ├── minimax.py      # MiniMax TTS cloud
    └── elevenlabs.py   # ElevenLabs cloud
```

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

The 50ms crossfade eliminates audible clicks between chunks while preserving natural speech rhythm.

## License

Apache License 2.0 - See LICENSE file.
