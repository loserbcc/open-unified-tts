# TTS Backend Guide

## What is a TTS Backend?

A **TTS backend** is the actual text-to-speech engine that generates audio. Think of Open Unified TTS as a smart router that:
1. Takes your text and voice request
2. Chooses the best backend for that voice
3. Chunks the text if needed
4. Sends chunks to the backend
5. Stitches the results together seamlessly

Each backend has different strengths, voice capabilities, and hardware requirements.

## Quick Decision Guide

**I want to...**
- **Just get started quickly** → Kokoro (CPU-friendly, Docker ready, 67 voices)
- **Clone a specific voice** → VoxCPM or OpenAudio (requires GPU and manual setup)
- **Use cloud/hosted solution** → ElevenLabs or MiniMax (API key required)
- **Generate singing/music** → ACE-Step (requires GPU)
- **Creative voice generation** → Higgs Audio (GPU, scene-based voices)

## Backend Comparison

### Kokoro (Recommended Starting Point)

**Type:** Neural TTS
**Voices:** 67 built-in voices
**Hardware:** CPU or GPU (CPU works great!)
**Setup Difficulty:** Easy (Docker one-liner)
**Quality:** Excellent natural speech

**Best For:**
- Getting started quickly
- Audiobook narration
- General-purpose TTS
- Running on machines without GPU

**Setup:**
```bash
# CPU version (works anywhere)
docker run -d --name kokoro-tts -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-cpu:latest

# GPU version (faster)
docker run -d --name kokoro-tts --gpus all -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-gpu:latest
```

**[Full Kokoro Setup Guide →](kokoro_setup_guide.md)**

**Voice Categories:**
- American Female (9 voices): `af_alloy`, `af_bella`, `af_heart`, `af_nova`, `af_sky`, etc.
- American Male (8 voices): `am_adam`, `am_echo`, `am_eric`, `am_onyx`, etc.
- British Female (3 voices): `bf_alice`, `bf_emma`, `bf_lily`
- British Male (4 voices): `bm_daniel`, `bm_fable`, `bm_george`, `bm_lewis`

### VoxCPM (Voice Cloning)

**Type:** Voice Cloning
**Voices:** Custom (clone any voice with reference audio)
**Hardware:** GPU required (12-16GB VRAM)
**Setup Difficulty:** Hard (manual installation)
**Quality:** Excellent clone quality

**Best For:**
- Cloning specific celebrity/character voices
- Matching a brand voice exactly
- Creating custom voice personas

**Limitations:**
- ~75 words per generation (handled by chunking)
- Requires 5-30 seconds of reference audio
- GPU-intensive

**Setup:**
Requires manual installation of VoxCPM from GitHub. Not covered in this guide.

### VoxCPM 1.5 (High-Quality Voice Cloning)

**Type:** Voice Cloning (improved version)
**Voices:** 88+ pre-loaded voices
**Hardware:** GPU required (8GB+ VRAM)
**Setup Difficulty:** Hard (manual installation)
**Quality:** 44.1kHz output (2x quality of original VoxCPM)

**Best For:**
- High-quality production work
- When you need better audio fidelity
- Lighter VRAM usage than original VoxCPM

**Improvements over VoxCPM:**
- Higher sample rate (44.1kHz vs 22.05kHz)
- More efficient VRAM usage (~8GB vs ~16GB)
- 88+ pre-loaded character voices
- Better handling of longer texts (~150 words vs ~75)

### OpenAudio S1-mini (Voice Cloning)

**Type:** Voice Cloning (Fish Speech based)
**Voices:** Custom clones
**Hardware:** GPU required
**Setup Difficulty:** Hard (manual installation)
**Quality:** Good clone quality

**Best For:**
- Alternative to VoxCPM
- Fish Speech ecosystem users

### FishTTS (Voice Synthesis)

**Type:** Voice Cloning
**Voices:** Custom
**Hardware:** GPU required
**Setup Difficulty:** Hard
**Quality:** Good

**Best For:**
- Fish Speech ecosystem integration
- Alternative voice cloning approach

### Higgs Audio (Generative/Creative)

**Type:** Generative TTS
**Voices:** Unlimited (scene-based generation)
**Hardware:** GPU required
**Setup Difficulty:** Hard
**Quality:** Variable (creative, not clone-accurate)

**Best For:**
- Creating NEW unique voices on the fly
- Experimental/creative projects
- Scene-based character voices ("gruff pirate", "ethereal spirit", etc.)

**How it works:**
Instead of cloning existing voices, Higgs generates voices based on scene descriptions:
- "nervous alien diplomat speaking through translator"
- "1920s radio announcer, tinny and enthusiastic"
- "ancient stone golem, grinding and rumbling"

**Not recommended for:** Cloning specific people/characters (use VoxCPM instead)

### Kyutai/Moshi (Emotion TTS)

**Type:** Emotional Expression
**Voices:** 8 emotion modes
**Hardware:** GPU required
**Setup Difficulty:** Hard
**Quality:** Good emotional range

**Best For:**
- Adding emotional expression to speech
- When you need happy/sad/angry variations
- Interactive applications

**Emotions:** neutral, happy, sad, angry, surprised, disgusted, fearful, contemptuous

### Chatterbox (Emotion Voice Cloning)

**Type:** Voice Clone + Emotion
**Voices:** Custom with emotion control
**Hardware:** GPU required
**Setup Difficulty:** Hard
**Quality:** Good

**Best For:**
- Voice clones with emotional variation
- Character dialogue with mood shifts

### VibeVoice (Streaming TTS)

**Type:** Microsoft-based streaming TTS
**Voices:** Microsoft voice set
**Hardware:** GPU required
**Setup Difficulty:** Hard
**Quality:** Good

**Best For:**
- Real-time streaming applications
- Low-latency requirements

### ACE-Step (Musical/Singing TTS)

**Type:** Musical TTS (singing!)
**Voices:** Custom
**Hardware:** GPU required
**Setup Difficulty:** Hard
**Quality:** Unique (singing, not speech)

**Best For:**
- Generating singing vocals
- Musical applications
- Creative audio projects

**Note:** This is for SINGING, not speech. Use other backends for spoken word.

### MiniMax TTS (Cloud)

**Type:** Cloud API
**Voices:** 7 professional voices
**Hardware:** None (cloud-based)
**Setup Difficulty:** Easy (API key only)
**Quality:** Excellent professional voices

**Best For:**
- No local GPU available
- Professional narration voices
- Production-quality output

**Voices:**
- English_expressive_narrator (British narrator)
- English_magnetic_voiced_man (Deep American)
- English_Aussie_Bloke (Australian)
- English_Comedian (Comedic American)
- English_radiant_girl (Energetic female)
- English_compelling_lady1 (Professional British female)
- English_CalmWoman (Meditation voice)

**Setup:**
Set environment variable: `MINIMAX_API_KEY=your_api_key`

### ElevenLabs (Cloud)

**Type:** Cloud API
**Voices:** Many professional voices
**Hardware:** None (cloud-based)
**Setup Difficulty:** Easy (API key only)
**Quality:** Industry-leading

**Best For:**
- Highest quality output
- When cost isn't a concern
- Fallback when local backends unavailable

**Setup:**
Set environment variable: `ELEVENLABS_API_KEY=sk_...`

**Note:** Can be expensive for long-form content. Consider Kokoro or self-hosted alternatives for audiobooks.

## Multi-Backend Strategy

You don't have to choose just one! Run multiple backends and use:

### Voice Preferences

Route specific voices to specific backends:

```bash
# Set "morgan" to always use VoxCPM (your best clone)
curl -X POST http://localhost:8765/v1/voice-prefs/morgan \
  -H "Content-Type: application/json" \
  -d '{"backend": "voxcpm"}'

# Set default voices to Kokoro (fast and free)
curl -X POST http://localhost:8765/v1/backends/switch \
  -H "Content-Type: application/json" \
  -d '{"backend": "kokoro"}'
```

### Automatic Failover

If a backend is unavailable, the router automatically tries alternatives. Example flow:

1. Request "morgan" voice → checks voice preference → VoxCPM
2. VoxCPM unavailable → falls back to Kokoro
3. Kokoro unavailable → tries ElevenLabs (if configured)

## Hardware Requirements Summary

| Backend | CPU Only | GPU (8GB) | GPU (12GB+) | Cloud |
|---------|----------|-----------|-------------|-------|
| Kokoro | ✓ | ✓ | ✓ | - |
| VoxCPM | - | - | ✓ | - |
| VoxCPM 1.5 | - | ✓ | ✓ | - |
| OpenAudio | - | ✓ | ✓ | - |
| Higgs | - | ✓ | ✓ | - |
| ACE-Step | - | ✓ | ✓ | - |
| MiniMax | - | - | - | ✓ |
| ElevenLabs | - | - | - | ✓ |

## Setup Recommendations

### Beginner Path
1. Start with Kokoro (Docker, CPU-friendly)
2. Learn the API with simple voices
3. Generate your first audiobook

### Intermediate Path
1. Kokoro for general use
2. Add MiniMax cloud for professional voices (easy API key setup)
3. Experiment with voice routing

### Advanced Path
1. Kokoro for fallback
2. VoxCPM 1.5 for voice cloning (GPU required)
3. ACE-Step for musical applications
4. ElevenLabs as cloud backup
5. Complex voice routing and preferences

### Production Path
1. Multiple Kokoro instances (load balancing)
2. Dedicated VoxCPM GPU server for brand voices
3. MiniMax for professional narration
4. Comprehensive monitoring and failover

## Backend Profiles (Technical)

Each backend has a profile that defines its capabilities:

```python
"kokoro": {
    "max_words": 200,        # Hard limit before errors
    "max_chars": 1200,
    "optimal_words": 150,    # Target chunk size
    "needs_chunking": True,
    "crossfade_ms": 30,      # Stitching overlap
},
"voxcpm": {
    "max_words": 75,         # Stricter limit
    "max_chars": 400,
    "optimal_words": 50,     # Smaller chunks
    "needs_chunking": True,
    "crossfade_ms": 50,      # Longer crossfade
},
"voxcpm15": {
    "max_words": 150,
    "max_chars": 800,
    "optimal_words": 100,
    "needs_chunking": True,
    "crossfade_ms": 50,
    "sample_rate": 44100,    # Higher quality
}
```

The chunker uses these profiles to automatically split your text appropriately for each backend.

## Common Questions

### Q: Can I use multiple backends at once?
**A:** Yes! Run multiple backends and route different voices to different engines. The router handles selection automatically.

### Q: Which backend is fastest?
**A:** Kokoro on GPU is fastest for general TTS. Cloud APIs (MiniMax, ElevenLabs) are fast but have network latency.

### Q: Which has the best quality?
**A:** For cloning: VoxCPM 1.5 (44.1kHz). For neural TTS: Kokoro or ElevenLabs. For music: ACE-Step.

### Q: Can I run this without a GPU?
**A:** Yes! Kokoro CPU mode works great for most uses. Cloud APIs (MiniMax, ElevenLabs) also require no GPU.

### Q: How do I add a new backend?
**A:** Create an adapter in `adapters/` that implements the `TTSBackend` interface. See `adapters/kokoro.py` for reference.

### Q: What if my preferred backend goes down?
**A:** The router automatically fails over to available alternatives. You can also set a fallback chain in preferences.

## Next Steps

1. **Start simple:** Set up Kokoro using the [Kokoro Setup Guide](kokoro_setup_guide.md)
2. **Test it:** Generate some audio with different voices
3. **Expand:** Add more backends as needed
4. **Route voices:** Configure preferences for optimal quality

For implementation details, see the main [README](../README.md).
