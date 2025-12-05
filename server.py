"""Open Unified TTS - OpenAI-compatible TTS API with multiple backend support.

This is the main server providing:
- POST /v1/audio/speech - OpenAI-compatible TTS endpoint
- GET /v1/voices - List available voices
- GET /v1/backends - List backend status
- Automatic backend failover
- Smart text chunking for long content
"""
import io
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Literal, Optional

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from router import BackendRouter
from voices import VoiceManager
from voice_prefs import VoicePreferences
from chunker import chunk_text, estimate_words
from stitcher import stitch_audio
from backend_profiles import get_profile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize components
router = BackendRouter()
voice_manager = VoiceManager()
voice_prefs = VoicePreferences()

# FastAPI app
app = FastAPI(
    title="Open Unified TTS",
    description="OpenAI-compatible TTS API with multiple backend support",
    version="1.0.0",
)


# =============================================================================
# REQUEST MODELS
# =============================================================================

class SpeechRequest(BaseModel):
    """OpenAI-compatible speech request."""
    model: str = "tts-1"  # Ignored, for compatibility
    input: str
    voice: str
    response_format: Literal["mp3", "opus", "aac", "flac", "wav", "pcm"] = "mp3"
    speed: float = 1.0  # Ignored for now


class BackendSwitchRequest(BaseModel):
    """Request to switch preferred backend."""
    backend: str


class VoicePrefRequest(BaseModel):
    """Request to set voice backend preference."""
    backend: str


# =============================================================================
# ROUTES
# =============================================================================

@app.get("/")
async def root():
    """Status page."""
    try:
        active = router.get_active_backend()
        active_name = active.name
    except RuntimeError:
        active_name = None

    return {
        "service": "Open Unified TTS",
        "version": "1.0.0",
        "active_backend": active_name,
        "voice_count": len(voice_manager.list_voices()),
        "endpoints": {
            "speech": "POST /v1/audio/speech",
            "voices": "GET /v1/voices",
            "backends": "GET /v1/backends",
            "health": "GET /health",
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    try:
        active = router.get_active_backend()
        return {"status": "ok", "backend": active.name}
    except RuntimeError:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "message": "No backend available"},
        )


@app.get("/v1/models")
async def list_models():
    """List available models (OpenAI-compatible)."""
    models = [
        {"id": "tts-1", "object": "model", "owned_by": "open-unified-tts"},
        {"id": "tts-1-hd", "object": "model", "owned_by": "open-unified-tts"},
    ]
    for backend in router.backends:
        models.append({
            "id": backend.name,
            "object": "model",
            "owned_by": "open-unified-tts",
        })
    return {"object": "list", "data": models}


@app.get("/v1/voices")
async def list_voices():
    """List all available voices."""
    return {
        "voices": voice_manager.list_voices(),
        "count": len(voice_manager.list_voices()),
    }


@app.post("/v1/voices/refresh")
async def refresh_voices():
    """Re-scan voice directory."""
    count = voice_manager.refresh()
    return {"status": "ok", "voice_count": count}


@app.get("/v1/backends")
async def list_backends():
    """List all backends and their status."""
    return {
        "backends": router.list_backends(),
        "active": router.preferred,
    }


@app.post("/v1/backends/switch")
async def switch_backend(request: BackendSwitchRequest):
    """Switch preferred backend."""
    if not router.set_preferred(request.backend):
        raise HTTPException(
            status_code=400,
            detail=f"Unknown backend: {request.backend}",
        )
    return {"status": "ok", "preferred": request.backend}


# =============================================================================
# VOICE PREFERENCES
# =============================================================================

@app.get("/v1/voice-prefs")
async def get_voice_prefs():
    """Get all voice-to-backend preferences."""
    return {"preferences": voice_prefs.list_all()}


@app.post("/v1/voice-prefs/{voice}")
async def set_voice_pref(voice: str, request: VoicePrefRequest):
    """Set backend preference for a voice."""
    voice_prefs.set(voice, request.backend)
    return {"status": "ok", "voice": voice, "backend": request.backend}


@app.delete("/v1/voice-prefs/{voice}")
async def delete_voice_pref(voice: str):
    """Remove backend preference for a voice."""
    removed = voice_prefs.remove(voice)
    return {"status": "ok", "removed": removed}


# =============================================================================
# MAIN TTS ENDPOINT
# =============================================================================

@app.post("/v1/audio/speech")
async def create_speech(request: SpeechRequest):
    """Generate speech from text (OpenAI-compatible endpoint)."""
    # Import voice lists for special routing
    try:
        from adapters.kyutai import KYUTAI_VOICES
    except ImportError:
        KYUTAI_VOICES = {}
    try:
        from adapters.vibevoice import VIBEVOICE_VOICES
    except ImportError:
        VIBEVOICE_VOICES = {}
    try:
        from adapters.elevenlabs import ELEVENLABS_VOICES
    except ImportError:
        ELEVENLABS_VOICES = {}

    voice_lower = request.voice.lower()

    # Route to specific backends based on voice type
    if voice_lower in KYUTAI_VOICES:
        backend = router.get_backend("kyutai")
        if not backend or not backend.is_available():
            raise HTTPException(503, f"Kyutai not available for emotion '{request.voice}'")
        voice_path = voice_lower
        transcript = ""

    elif voice_lower in VIBEVOICE_VOICES:
        backend = router.get_backend("vibevoice")
        if not backend or not backend.is_available():
            raise HTTPException(503, f"VibeVoice not available for '{request.voice}'")
        voice_path = voice_lower
        transcript = ""

    elif voice_lower in ELEVENLABS_VOICES or router.preferred == "elevenlabs":
        backend = router.get_backend("elevenlabs")
        if not backend or not backend.is_available():
            raise HTTPException(503, f"ElevenLabs not available")
        voice_path = request.voice
        transcript = ""

    else:
        # Standard voice - check preferences
        preferred_backend = voice_prefs.get(request.voice)
        try:
            if preferred_backend:
                backend = router.get_backend(preferred_backend)
                if not backend or not backend.is_available():
                    backend = router.get_active_backend()
            else:
                backend = router.get_active_backend()
        except RuntimeError as e:
            raise HTTPException(503, str(e))

        # Get voice from voice manager
        voice = voice_manager.get(request.voice)
        if not voice:
            available = voice_manager.list_voices()[:10]
            raise HTTPException(
                400,
                f"Voice '{request.voice}' not found. Available: {available}...",
            )
        voice_path = str(voice.reference_path)
        transcript = voice.transcript

    # Generate audio with smart chunking
    try:
        backend_profile = get_profile(backend.name)
        text_words = estimate_words(request.input)
        text_chars = len(request.input)

        needs_chunk = (
            backend_profile["needs_chunking"] and
            (text_words > backend_profile["max_words"] or text_chars > backend_profile["max_chars"])
        )

        if needs_chunk:
            logger.info(f"Chunking: {text_words} words for {backend.name}")
            chunks = chunk_text(request.input, backend.name)

            audio_chunks = []
            for i, chunk in enumerate(chunks):
                chunk_audio = backend.generate(
                    text=chunk,
                    voice_path=voice_path,
                    transcript=transcript,
                )
                audio_chunks.append(chunk_audio)

            crossfade_ms = backend_profile.get("crossfade_ms", 50)
            wav_bytes = stitch_audio(audio_chunks, crossfade_ms=crossfade_ms)
        else:
            logger.info(f"Generating: {len(request.input)} chars via {backend.name}")
            wav_bytes = backend.generate(
                text=request.input,
                voice_path=voice_path,
                transcript=transcript,
            )

        # Return in requested format
        if request.response_format == "wav":
            return Response(content=wav_bytes, media_type="audio/wav")

        output_bytes = convert_audio(wav_bytes, request.response_format)
        media_types = {
            "mp3": "audio/mpeg",
            "opus": "audio/opus",
            "aac": "audio/aac",
            "flac": "audio/flac",
            "pcm": "audio/pcm",
        }
        return Response(
            content=output_bytes,
            media_type=media_types.get(request.response_format, "audio/mpeg"),
        )

    except Exception as e:
        logger.exception(f"TTS generation failed: {e}")
        raise HTTPException(500, f"Generation failed: {str(e)}")


def convert_audio(wav_bytes: bytes, format: str) -> bytes:
    """Convert WAV bytes to another format using ffmpeg."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(wav_bytes)
        wav_path = f.name

    output_path = wav_path.replace(".wav", f".{format}")

    try:
        cmd = ["ffmpeg", "-y", "-i", wav_path, "-f", format]

        if format == "mp3":
            cmd.extend(["-codec:a", "libmp3lame", "-q:a", "2"])
        elif format == "opus":
            cmd.extend(["-codec:a", "libopus", "-b:a", "128k"])
        elif format == "aac":
            cmd.extend(["-codec:a", "aac", "-b:a", "128k"])
        elif format == "flac":
            cmd.extend(["-codec:a", "flac"])
        elif format == "pcm":
            cmd.extend(["-f", "s16le", "-acodec", "pcm_s16le"])

        cmd.append(output_path)

        result = subprocess.run(cmd, capture_output=True, timeout=30)
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg error: {result.stderr.decode()[:100]}")

        with open(output_path, "rb") as f:
            return f.read()

    finally:
        Path(wav_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.environ.get("UNIFIED_TTS_PORT", "8765"))
    host = os.environ.get("UNIFIED_TTS_HOST", "0.0.0.0")

    logger.info(f"Starting Open Unified TTS on {host}:{port}")
    logger.info(f"Voice directory: {voice_manager.voice_dir}")
    logger.info(f"Discovered voices: {len(voice_manager.list_voices())}")

    for backend in router.backends:
        status = "available" if backend.is_available() else "offline"
        logger.info(f"Backend {backend.name}: {status}")

    uvicorn.run(app, host=host, port=port)
