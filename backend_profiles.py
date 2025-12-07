"""Backend capability profiles - chunk limits, quality settings.

Each backend has different text length limits. This module
provides profiles used by the chunker to split long text appropriately.
"""

BACKEND_PROFILES = {
    "openaudio": {
        "max_words": 75,
        "max_chars": 400,
        "optimal_words": 50,
        "needs_chunking": True,
        "crossfade_ms": 50,
    },
    "voxcpm": {
        "max_words": 75,
        "max_chars": 400,
        "optimal_words": 50,
        "needs_chunking": True,
        "crossfade_ms": 50,
    },
    "voxcpm15": {
        "max_words": 150,
        "max_chars": 800,
        "optimal_words": 100,
        "needs_chunking": True,
        "crossfade_ms": 50,
        "sample_rate": 44100,  # Higher quality output
    },
    "kyutai": {
        "max_words": 40,
        "max_chars": 250,
        "optimal_words": 30,
        "needs_chunking": True,
        "crossfade_ms": 30,
    },
    "higgs": {
        "max_words": 100,
        "max_chars": 600,
        "optimal_words": 75,
        "needs_chunking": True,
        "crossfade_ms": 50,
    },
    "elevenlabs": {
        "max_words": 2500,
        "max_chars": 15000,
        "optimal_words": 500,
        "needs_chunking": False,  # Cloud handles it
        "crossfade_ms": 0,
    },
    "vibevoice": {
        "max_words": 100,
        "max_chars": 500,
        "optimal_words": 75,
        "needs_chunking": True,
        "crossfade_ms": 100,
    },
}


def get_profile(backend_name: str) -> dict:
    """Get backend profile by name, fallback to openaudio profile."""
    return BACKEND_PROFILES.get(backend_name, BACKEND_PROFILES["openaudio"])


def needs_chunking(backend_name: str) -> bool:
    """Check if backend requires text chunking."""
    return get_profile(backend_name).get("needs_chunking", True)

# Add Kokoro profile
BACKEND_PROFILES["kokoro"] = {
    "max_words": 200,
    "max_chars": 1200,
    "optimal_words": 150,
    "needs_chunking": True,
    "crossfade_ms": 30,
}

# Add Qwen3-TTS profile (multilingual: EN, ZH, VI, JA, KO, FR, Tamil)
BACKEND_PROFILES["qwen3_tts"] = {
    "max_words": 100,
    "max_chars": 500,
    "optimal_words": 75,
    "needs_chunking": True,
    "crossfade_ms": 50,
    "sample_rate": 24000,
}
