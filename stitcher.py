"""Audio stitching for multi-chunk TTS generation.

Combines multiple audio chunks with seamless crossfades
to eliminate audible cuts between chunks.
"""
import io
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import List

import numpy as np
from scipy.io import wavfile

logger = logging.getLogger(__name__)


def stitch_audio(chunks: List[bytes], crossfade_ms: int = 50) -> bytes:
    """Stitch multiple audio chunks into seamless output.

    Args:
        chunks: List of WAV file bytes
        crossfade_ms: Crossfade duration in milliseconds

    Returns:
        Combined WAV file as bytes
    """
    if not chunks:
        return b""

    if len(chunks) == 1:
        return normalize_audio(chunks[0])

    logger.info(f"Stitching {len(chunks)} chunks with {crossfade_ms}ms crossfade")

    normalized = [normalize_audio(chunk) for chunk in chunks]
    result_audio = _load_wav_bytes(normalized[0])
    sample_rate = result_audio['rate']

    for chunk_bytes in normalized[1:]:
        next_audio = _load_wav_bytes(chunk_bytes)

        if next_audio['rate'] != sample_rate:
            next_audio = _resample_audio(next_audio, sample_rate)

        result_audio = _crossfade_audio(result_audio, next_audio, crossfade_ms)

    return _audio_to_wav_bytes(result_audio)


def normalize_audio(wav_bytes: bytes) -> bytes:
    """Normalize audio levels to prevent volume inconsistencies."""
    audio = _load_wav_bytes(wav_bytes)

    max_val = np.max(np.abs(audio['data']))
    if max_val == 0:
        return wav_bytes

    target_peak = 0.9 * 32767 if audio['data'].dtype == np.int16 else 0.9
    normalization_factor = target_peak / max_val
    normalized_data = audio['data'] * normalization_factor

    if audio['data'].dtype == np.int16:
        normalized_data = np.clip(normalized_data, -32768, 32767).astype(np.int16)

    audio['data'] = normalized_data
    return _audio_to_wav_bytes(audio)


def stitch_with_gaps(chunks: List[bytes], gap_ms: int = 200) -> bytes:
    """Stitch audio chunks with silent gaps (for dialogue)."""
    if not chunks:
        return b""

    if len(chunks) == 1:
        return normalize_audio(chunks[0])

    normalized = [normalize_audio(chunk) for chunk in chunks]
    result_audio = _load_wav_bytes(normalized[0])
    sample_rate = result_audio['rate']

    gap_samples = int((gap_ms / 1000.0) * sample_rate)
    silence = np.zeros(gap_samples, dtype=result_audio['data'].dtype)

    for chunk_bytes in normalized[1:]:
        next_audio = _load_wav_bytes(chunk_bytes)
        if next_audio['rate'] != sample_rate:
            next_audio = _resample_audio(next_audio, sample_rate)

        result_audio['data'] = np.concatenate([
            result_audio['data'], silence, next_audio['data']
        ])

    return _audio_to_wav_bytes(result_audio)


def _load_wav_bytes(wav_bytes: bytes) -> dict:
    with io.BytesIO(wav_bytes) as f:
        rate, data = wavfile.read(f)
    return {'rate': rate, 'data': data, 'channels': 1 if len(data.shape) == 1 else data.shape[1]}


def _audio_to_wav_bytes(audio: dict) -> bytes:
    buffer = io.BytesIO()
    wavfile.write(buffer, audio['rate'], audio['data'])
    return buffer.getvalue()


def _crossfade_audio(audio1: dict, audio2: dict, crossfade_ms: int) -> dict:
    rate = audio1['rate']
    crossfade_samples = min(
        int((crossfade_ms / 1000.0) * rate),
        len(audio1['data']),
        len(audio2['data'])
    )

    if crossfade_samples <= 0:
        combined = np.concatenate([audio1['data'], audio2['data']])
        return {'rate': rate, 'data': combined, 'channels': audio1['channels']}

    fade_out = np.linspace(1.0, 0.0, crossfade_samples)
    fade_in = np.linspace(0.0, 1.0, crossfade_samples)

    if len(audio1['data'].shape) > 1:
        fade_out = fade_out[:, np.newaxis]
        fade_in = fade_in[:, np.newaxis]

    pre_fade1 = audio1['data'][:-crossfade_samples]
    fade_section1 = audio1['data'][-crossfade_samples:]
    fade_section2 = audio2['data'][:crossfade_samples]
    post_fade2 = audio2['data'][crossfade_samples:]

    crossfaded = fade_section1 * fade_out + fade_section2 * fade_in

    if audio1['data'].dtype == np.int16:
        crossfaded = np.clip(crossfaded, -32768, 32767).astype(np.int16)

    combined = np.concatenate([pre_fade1, crossfaded, post_fade2])
    return {'rate': rate, 'data': combined, 'channels': audio1['channels']}


def _resample_audio(audio: dict, target_rate: int) -> dict:
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        wavfile.write(f, audio['rate'], audio['data'])
        input_path = f.name

    output_path = input_path.replace('.wav', '_resampled.wav')

    try:
        subprocess.run([
            'ffmpeg', '-y', '-i', input_path,
            '-ar', str(target_rate), '-ac', '1', '-acodec', 'pcm_s16le',
            output_path
        ], capture_output=True)

        with open(output_path, 'rb') as f:
            return _load_wav_bytes(f.read())
    finally:
        Path(input_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True)
