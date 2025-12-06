# Kokoro Backend Setup Guide

How to add Kokoro TTS as a backend for Open Unified TTS.

## Prerequisites

- Docker installed
- Python 3.10+ with uv or pip
- ~6GB disk space for Docker image

## 1. Start Kokoro-FastAPI

### CPU Version (lighter, works anywhere)
```bash
docker run -d --name kokoro-tts \
  -p 8880:8880 \
  ghcr.io/remsky/kokoro-fastapi-cpu:latest
```

### GPU Version (faster, requires NVIDIA GPU)
```bash
docker run -d --name kokoro-tts \
  --gpus all \
  -p 8880:8880 \
  ghcr.io/remsky/kokoro-fastapi-gpu:latest
```

### Verify it's running
```bash
curl http://localhost:8880/v1/models
# Should return list of available models
```

## 2. Install Open Unified TTS

```bash
git clone https://github.com/loserbcc/open-unified-tts.git
cd open-unified-tts

# Create virtual environment
uv venv .venv
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

## 3. Start the Server

```bash
python server.py
# Starts on port 8765 by default
```

## 4. Test Kokoro Integration

### Short text (direct generation)
```bash
curl -X POST http://localhost:8765/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model":"tts-1","voice":"bf_emma","input":"Hello, this is a test."}' \
  --output test_short.mp3
```

### Long text (chunked + stitched)
```bash
curl -X POST http://localhost:8765/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model":"tts-1","voice":"am_adam","input":"Your long text here..."}' \
  --output test_long.mp3
```

## Available Kokoro Voices

### American Female
`af_alloy`, `af_bella`, `af_heart`, `af_nova`, `af_sky`, `af_sarah`, `af_jessica`, `af_nicole`, `af_river`, `af_kore`, `af_aoede`, `af_jadzia`

### American Male
`am_adam`, `am_echo`, `am_eric`, `am_onyx`, `am_michael`, `am_liam`, `am_fenrir`, `am_puck`, `am_santa`

### British Female
`bf_alice`, `bf_emma`, `bf_lily`

### British Male
`bm_daniel`, `bm_fable`, `bm_george`, `bm_lewis`

### OpenAI Compatible Names
`alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer` (mapped to Kokoro equivalents)

### Other Languages
- Spanish: `ef_dora`, `em_alex`
- French: `ff_siwis`
- Hindi: `hf_alpha`, `hf_beta`, `hm_omega`, `hm_psi`
- Italian: `if_sara`, `im_nicola`
- Japanese: `jf_alpha`, `jf_gongitsune`, `jf_nezumi`, `jf_tebukuro`, `jm_kumo`
- Portuguese: `pf_dora`, `pm_alex`

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `KOKORO_HOST` | `http://localhost:8880` | Kokoro API URL |
| `UNIFIED_TTS_PORT` | `8765` | Server port |
| `UNIFIED_TTS_HOST` | `0.0.0.0` | Server bind address |

### Backend Profile (backend_profiles.py)

```python
"kokoro": {
    "max_words": 200,      # Chunk if text exceeds this
    "max_chars": 1200,
    "optimal_words": 150,  # Target chunk size
    "needs_chunking": True,
    "crossfade_ms": 30,    # Smooth transitions
}
```

## How Format Handling Works

### Short Text (<200 words)
1. Request goes directly to Kokoro
2. Final format (mp3/wav) requested from backend
3. No intermediate conversion - efficient!

### Long Text (>200 words)
1. Text split at sentence boundaries
2. Each chunk generated as WAV (lossless)
3. Chunks stitched with 30ms crossfade
4. Final audio converted to requested format

## Troubleshooting

### "Voice not found" error
Make sure you're using a valid Kokoro voice name (see list above). The server routes Kokoro voices automatically.

### Audio cuts off or sounds choppy
Increase `crossfade_ms` in backend_profiles.py (try 50ms).

### Slow generation
- Use GPU Docker image if you have NVIDIA GPU
- Reduce text length or chunk size
- Check Docker container isn't memory-constrained

### Docker container won't start
```bash
# Check logs
docker logs kokoro-tts

# Ensure port isn't in use
lsof -i :8880
```

## Performance Notes

Tested on AMD Ryzen + RTX 4070 Laptop (CPU mode):
- 230 words → 73 seconds audio
- Generation time: ~30 seconds
- ~4 chunks with 30ms crossfade
- Output: 630KB MP3
