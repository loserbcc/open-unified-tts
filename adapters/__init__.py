"""TTS Backend Adapters for Open Unified TTS.

These adapters integrate popular TTS backends with the unified API.
Each adapter implements the TTSBackend interface.

Included adapters:
- OpenAudio (Fish Speech) - Voice cloning, ~5GB VRAM
- VoxCPM - High-quality character cloning via Gradio, ~18GB VRAM
- Kyutai (Moshi) - Emotional TTS presets, ~4GB VRAM
- Higgs - Generative voice creation from descriptions, ~15GB VRAM
- VibeVoice - Real-time streaming TTS, ~2GB VRAM
- ElevenLabs - Cloud TTS fallback, no GPU required

To add your own adapter:
1. Create a class inheriting from TTSBackend
2. Implement: name, port, vram_gb, is_available(), generate()
3. Add to the router in router.py
"""
from .base import TTSBackend

# Import all adapters - comment out any you don't need
try:
    from .openaudio import OpenAudioBackend
except ImportError:
    OpenAudioBackend = None

try:
    from .voxcpm import VoxCPMBackend
except ImportError:
    VoxCPMBackend = None

try:
    from .kyutai import KyutaiBackend, KYUTAI_VOICES
except ImportError:
    KyutaiBackend = None
    KYUTAI_VOICES = {}

try:
    from .higgs import HiggsBackend
except ImportError:
    HiggsBackend = None

try:
    from .vibevoice import VibeVoiceBackend, VIBEVOICE_VOICES
except ImportError:
    VibeVoiceBackend = None
    VIBEVOICE_VOICES = {}

try:
    from .elevenlabs import ElevenLabsBackend, ELEVENLABS_VOICES
except ImportError:
    ElevenLabsBackend = None
    ELEVENLABS_VOICES = {}

__all__ = [
    "TTSBackend",
    "OpenAudioBackend",
    "VoxCPMBackend",
    "KyutaiBackend",
    "KYUTAI_VOICES",
    "HiggsBackend",
    "VibeVoiceBackend",
    "VIBEVOICE_VOICES",
    "ElevenLabsBackend",
    "ELEVENLABS_VOICES",
]
