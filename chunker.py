"""Smart text chunking for TTS backends with token limits.

Most local TTS models have text length limits (50-100 words).
This module splits long text at natural boundaries (sentences, clauses)
and the stitcher recombines the generated audio seamlessly.
"""
import re
import logging
from typing import List

from backend_profiles import get_profile

logger = logging.getLogger(__name__)


def estimate_words(text: str) -> int:
    """Estimate word count in text."""
    return len(text.split())


def chunk_text(text: str, backend: str) -> List[str]:
    """Split text into chunks appropriate for the backend.

    Args:
        text: Text to chunk
        backend: Backend name (e.g., "openaudio", "voxcpm")

    Returns:
        List of text chunks respecting backend limits
    """
    profile = get_profile(backend)

    if not profile["needs_chunking"]:
        return [text]

    max_chars = profile["max_chars"]
    max_words = profile["max_words"]

    if len(text) <= max_chars and estimate_words(text) <= max_words:
        return [text]

    logger.info(f"Chunking for {backend}: {len(text)} chars, {estimate_words(text)} words")

    chunks = []
    current_chunk = ""

    # Split by sentences
    sentences = re.split(r'([.!?]+\s+)', text)

    for i in range(0, len(sentences), 2):
        sentence = sentences[i]
        separator = sentences[i + 1] if i + 1 < len(sentences) else ""
        full_sentence = sentence + separator

        # Handle overly long sentences
        if len(full_sentence) > max_chars or estimate_words(full_sentence) > max_words:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
                current_chunk = ""
            chunks.extend(_split_long_sentence(full_sentence, max_chars, max_words))
            continue

        # Check if adding sentence exceeds limits
        test_chunk = current_chunk + full_sentence
        if len(test_chunk) > max_chars or estimate_words(test_chunk) > max_words:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = full_sentence
        else:
            current_chunk += full_sentence

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    logger.info(f"Split into {len(chunks)} chunks")
    return chunks


def _split_long_sentence(sentence: str, max_chars: int, max_words: int) -> List[str]:
    """Split a long sentence at commas or other natural breaks."""
    parts = re.split(r'(,\s+)', sentence)

    chunks = []
    current_chunk = ""

    for i in range(0, len(parts), 2):
        part = parts[i]
        separator = parts[i + 1] if i + 1 < len(parts) else ""
        full_part = part + separator

        if len(full_part) > max_chars or estimate_words(full_part) > max_words:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
                current_chunk = ""
            chunks.extend(_force_split_by_words(full_part, max_words))
            continue

        test_chunk = current_chunk + full_part
        if len(test_chunk) > max_chars or estimate_words(test_chunk) > max_words:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = full_part
        else:
            current_chunk += full_part

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def _force_split_by_words(text: str, max_words: int) -> List[str]:
    """Force split by word count when no natural breaks exist."""
    words = text.split()
    return [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]
