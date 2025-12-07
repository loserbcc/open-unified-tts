# Vietnamese TTS Docker - Proof of Concept

**Status:** POC / Experimental
**Platform:** Mac M-series (ARM64) - tested on M4
**Engine:** [VieNeu-TTS](https://github.com/pnnbao97/VieNeu-TTS)

## What This Is

A Docker-based setup for Vietnamese text-to-speech that:
- Runs entirely on CPU (no GPU required)
- Works on Mac M1/M2/M3/M4
- Provides OpenAI-compatible API at `http://localhost:8765`
- Includes 10 Vietnamese voices (Northern & Southern accents)

## What This Is NOT

- Not a full production deployment
- Not tested on Linux (should work, but unverified)
- Not supporting other TTS backends in Docker (just Vietnamese)

## Quick Start

```bash
# Clone this branch
git clone -b docker-vietnamese-poc https://github.com/loserbcc/open-unified-tts.git
cd open-unified-tts

# Run setup (builds containers, starts services)
./setup-vietnamese-tts.sh

# Test it
curl -X POST http://localhost:8765/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input":"Xin chào, tôi là trợ lý ảo","voice":"huong"}' \
  -o test.wav

# Play on Mac
afplay test.wav
```

## Available Voices

| Voice | Gender | Accent |
|-------|--------|--------|
| `huong` | Female | Northern |
| `tuyen` | Male | Northern |
| `ly` | Female | Northern |
| `binh` | Male | Northern |
| `ngoc` | Female | Northern |
| `doan` | Female | Southern |
| `vinh` | Male | Southern |
| `dung` | Female | Southern |
| `nguyen` | Male | Southern |
| `son` | Male | Southern |

## Requirements

- Docker Desktop
- ~4GB disk space (for models)
- ~2GB RAM

## Troubleshooting

**Container won't start:**
```bash
docker logs vieneu-tts
```

**TTS returns empty audio:**
```bash
# Check if VieNeu is responding
curl http://localhost:7860/
```

**Stop everything:**
```bash
docker stop vieneu-tts unified-tts-proxy
docker rm vieneu-tts unified-tts-proxy
```

## Known Limitations

1. **Gradio share=True hack** - Required to bypass Docker localhost check
2. **First run is slow** - Downloads ~2GB of models
3. **CPU only** - Fast enough for conversational use, not real-time streaming

## Architecture

```
┌─────────────────┐     ┌─────────────────┐
│  Your App       │────▶│  unified-tts    │
│                 │     │  :8765          │
└─────────────────┘     └────────┬────────┘
                                 │
                        ┌────────▼────────┐
                        │  vieneu-tts     │
                        │  :7860          │
                        └─────────────────┘
```
