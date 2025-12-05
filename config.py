"""Centralized configuration for Open Unified TTS.

All settings are configurable via environment variables.
"""
import os
from pathlib import Path

# =============================================================================
# PATHS
# =============================================================================

# Voice clones directory - where reference audio files are stored
# Structure: VOICE_CLONES_DIR/<voice_name>/reference.wav + transcript.txt
VOICE_CLONES_DIR = Path(os.environ.get(
    "UNIFIED_TTS_VOICE_DIR",
    os.path.expanduser("~/.unified-tts/voices")
))

# Voice preferences file - stores per-voice backend routing preferences
VOICE_PREFS_FILE = Path(os.environ.get(
    "UNIFIED_TTS_PREFS_FILE",
    os.path.expanduser("~/.unified-tts/voice_preferences.json")
))

# =============================================================================
# BACKEND HOSTS
# =============================================================================

# OpenAudio S1-Mini (Fish Speech) - voice cloning
OPENAUDIO_HOST = os.environ.get("OPENAUDIO_HOST", "http://localhost:9877")

# VoxCPM - character voice cloning via Gradio
VOXCPM_HOST = os.environ.get("VOXCPM_HOST", "http://localhost:7860")

# Kyutai/Moshi - emotional TTS (can specify multiple comma-separated)
# Format: "name1=url1,name2=url2" or just "url" for single host
KYUTAI_HOSTS = os.environ.get("KYUTAI_HOSTS", "http://localhost:8899")

# Higgs Audio - generative voice creation
HIGGS_HOST = os.environ.get("HIGGS_HOST", "http://localhost:8085")

# VibeVoice - real-time streaming TTS
VIBEVOICE_HOST = os.environ.get("VIBEVOICE_HOST", "http://localhost:8086")

# =============================================================================
# CLOUD API KEYS
# =============================================================================

# ElevenLabs API key (optional - for cloud TTS fallback)
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")

# =============================================================================
# SERVER SETTINGS
# =============================================================================

# Port for the unified TTS proxy server
SERVER_PORT = int(os.environ.get("UNIFIED_TTS_PORT", "8765"))

# Host to bind to
SERVER_HOST = os.environ.get("UNIFIED_TTS_HOST", "0.0.0.0")


def parse_kyutai_hosts() -> list[dict]:
    """Parse KYUTAI_HOSTS env var into list of host dicts.

    Formats supported:
    - Single URL: "http://localhost:8899"
    - Multiple: "local=http://localhost:8899,remote=http://192.168.1.100:8899"
    """
    hosts_str = KYUTAI_HOSTS

    if "=" in hosts_str:
        # Named hosts format
        hosts = []
        for part in hosts_str.split(","):
            if "=" in part:
                name, url = part.strip().split("=", 1)
                hosts.append({"name": name.strip(), "url": url.strip()})
        return hosts
    elif "," in hosts_str:
        # Multiple URLs without names
        return [
            {"name": f"host{i}", "url": url.strip()}
            for i, url in enumerate(hosts_str.split(","))
        ]
    else:
        # Single URL
        return [{"name": "default", "url": hosts_str.strip()}]


def ensure_dirs():
    """Create necessary directories if they don't exist."""
    VOICE_CLONES_DIR.mkdir(parents=True, exist_ok=True)
    VOICE_PREFS_FILE.parent.mkdir(parents=True, exist_ok=True)
