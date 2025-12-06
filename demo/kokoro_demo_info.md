# Kokoro Audiobook Demo

**File:** `kokoro_audiobook_demo.mp3`

## Details

- **Voice:** `bf_emma` (British female)
- **Duration:** 1:13 (73 seconds)
- **Text:** 230 words (~1,400 characters)
- **File size:** 630 KB (MP3)

## Content

Original lighthouse ghost story - "Chapter One: The Discovery"

A short atmospheric piece demonstrating chunked generation and seamless stitching.

## Generation Details

- **Backend:** Kokoro-FastAPI (Docker, CPU mode)
- **Chunking:** Text split into ~4 chunks at sentence boundaries
- **Stitching:** 30ms crossfade between chunks
- **Total generation time:** ~30 seconds
- **Hardware:** AMD Ryzen + RTX 4070 Laptop (GPU not used - Kokoro ran on CPU)

## How It Was Generated

```bash
curl -X POST http://localhost:8765/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1",
    "voice": "bf_emma",
    "input": "Chapter One: The Discovery..."
  }' --output demo.mp3
```

## Format Handling

Since the text exceeded Kokoro's optimal chunk size (200 words):
1. Server split text into ~4 chunks
2. Each chunk generated as WAV (for lossless stitching)
3. Chunks crossfaded with 30ms overlap
4. Final audio converted to MP3

For shorter text (<200 words), the server requests MP3 directly from Kokoro - more efficient, no intermediate conversion.
