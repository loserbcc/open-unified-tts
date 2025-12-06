"""Open Unified TTS - Audiobook Production Studio

A Gradio web interface for converting documents to audiobooks.
Supports: PDF, DOCX, TXT, and direct text input.

Future: OCR for images (modular API - swap in any OCR model)
"""

import gradio as gr
import requests
import tempfile
import os
from pathlib import Path
from typing import Optional, Tuple

# =============================================================================
# CONFIGURATION
# =============================================================================

API_URL = os.environ.get("TTS_API_URL", "http://localhost:8765")

# Kokoro voices organized by category
VOICES = {
    "American Female": [
        "af_alloy", "af_bella", "af_heart", "af_nova", "af_sky",
        "af_sarah", "af_jessica", "af_nicole", "af_river", "af_kore"
    ],
    "American Male": [
        "am_adam", "am_echo", "am_eric", "am_onyx", "am_michael",
        "am_liam", "am_fenrir", "am_puck"
    ],
    "British Female": ["bf_alice", "bf_emma", "bf_lily"],
    "British Male": ["bm_daniel", "bm_fable", "bm_george", "bm_lewis"],
    "OpenAI Compatible": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
}

# Flatten for dropdown
ALL_VOICES = []
for category, voices in VOICES.items():
    for voice in voices:
        ALL_VOICES.append(f"{voice} ({category})")

DEFAULT_VOICE = "bf_emma (British Female)"


# =============================================================================
# DOCUMENT EXTRACTION
# =============================================================================

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF using pypdf."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        text = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
        return "\n\n".join(text)
    except ImportError:
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                text = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
                return "\n\n".join(text)
        except ImportError:
            raise ImportError("Install pypdf: pip install pypdf")


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX using python-docx."""
    try:
        from docx import Document
        doc = Document(file_path)
        text = []
        for para in doc.paragraphs:
            if para.text.strip():
                text.append(para.text)
        return "\n\n".join(text)
    except ImportError:
        raise ImportError("Install python-docx: pip install python-docx")


def extract_text(file_path: str) -> Tuple[str, str]:
    """Extract text from supported file types.

    Returns:
        Tuple of (extracted_text, status_message)
    """
    if not file_path:
        return "", "No file provided"

    path = Path(file_path)
    suffix = path.suffix.lower()

    try:
        if suffix == ".pdf":
            text = extract_text_from_pdf(file_path)
            word_count = len(text.split())
            return text, f"✓ Extracted {word_count} words from PDF ({path.name})"

        elif suffix in [".docx", ".doc"]:
            text = extract_text_from_docx(file_path)
            word_count = len(text.split())
            return text, f"✓ Extracted {word_count} words from DOCX ({path.name})"

        elif suffix == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            word_count = len(text.split())
            return text, f"✓ Loaded {word_count} words from TXT ({path.name})"

        elif suffix in [".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif"]:
            return "", f"⏳ OCR coming soon! Image support will be added with modular OCR API."

        else:
            # Try reading as plain text
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                word_count = len(text.split())
                return text, f"✓ Read {word_count} words as text ({path.name})"
            except:
                return "", f"✗ Unsupported file type: {suffix}"

    except Exception as e:
        return "", f"✗ Error: {str(e)}"


# =============================================================================
# TTS GENERATION
# =============================================================================

def generate_audio(
    text: str,
    voice: str,
    output_format: str = "mp3"
) -> Tuple[Optional[str], str]:
    """Generate audio from text using the TTS API."""
    if not text or not text.strip():
        return None, "✗ No text to generate"

    # Extract voice name from dropdown format "voice (category)"
    voice_name = voice.split(" (")[0] if " (" in voice else voice
    word_count = len(text.split())

    try:
        response = requests.post(
            f"{API_URL}/v1/audio/speech",
            json={
                "model": "tts-1",
                "voice": voice_name,
                "input": text,
                "response_format": output_format,
            },
            timeout=600,  # 10 minutes for long documents
        )

        if response.status_code != 200:
            return None, f"✗ API Error: {response.status_code} - {response.text[:200]}"

        # Save to temp file
        with tempfile.NamedTemporaryFile(
            suffix=f".{output_format}",
            delete=False
        ) as f:
            f.write(response.content)
            audio_path = f.name

        size_mb = len(response.content) / (1024 * 1024)
        return audio_path, f"✓ Generated: {word_count} words → {size_mb:.2f}MB {output_format.upper()}"

    except requests.exceptions.Timeout:
        return None, "✗ Request timed out (document may be too long)"
    except requests.exceptions.ConnectionError:
        return None, f"✗ Cannot connect to API at {API_URL}"
    except Exception as e:
        return None, f"✗ Error: {str(e)}"


def check_api_status() -> str:
    """Check if the TTS API is available."""
    try:
        r = requests.get(f"{API_URL}/health", timeout=5)
        if r.status_code == 200:
            data = r.json()
            return f"✓ API Online - Backend: {data.get('backend', 'unknown')}"
        return f"⚠ API returned status {r.status_code}"
    except:
        return f"✗ API Offline ({API_URL})"


# =============================================================================
# GRADIO INTERFACE
# =============================================================================

def process_document(file) -> Tuple[str, str]:
    """Process uploaded document and extract text."""
    if file is None:
        return "", "Upload a document to extract text"
    return extract_text(file.name)


with gr.Blocks(
    title="Audiobook Production Studio",
    
) as demo:
    gr.Markdown("""
    # 🎙️ Audiobook Production Studio

    Convert documents to high-quality audiobooks using **Open Unified TTS**.

    **Supported:** PDF, DOCX, TXT | **Coming Soon:** Images with OCR
    """)

    # API Status
    with gr.Row():
        api_status = gr.Textbox(
            label="API Status",
            value=check_api_status(),
            interactive=False,
            scale=3
        )
        refresh_btn = gr.Button("🔄 Refresh", scale=1)
        refresh_btn.click(check_api_status, outputs=api_status)

    with gr.Tabs():
        # Tab 1: Document Upload
        with gr.Tab("📄 Upload Document"):
            with gr.Row():
                with gr.Column(scale=1):
                    file_input = gr.File(
                        label="Upload Document",
                        file_types=[".pdf", ".docx", ".doc", ".txt"],
                        type="filepath"
                    )
                    extract_btn = gr.Button("📖 Extract Text", variant="primary")

                with gr.Column(scale=2):
                    extracted_text = gr.Textbox(
                        label="Extracted Text (editable)",
                        lines=12,
                        placeholder="Text will appear here after extraction. You can edit it before generating audio.",
                        interactive=True
                    )
                    extract_status = gr.Textbox(label="Status", interactive=False)

            extract_btn.click(
                process_document,
                inputs=[file_input],
                outputs=[extracted_text, extract_status]
            )

        # Tab 2: Direct Text Input
        with gr.Tab("✏️ Paste Text"):
            direct_text = gr.Textbox(
                label="Enter or paste text directly",
                lines=12,
                placeholder="Type or paste your text here...",
                interactive=True
            )

    gr.Markdown("---")

    # Generation Controls
    with gr.Row():
        voice_select = gr.Dropdown(
            choices=ALL_VOICES,
            value=DEFAULT_VOICE,
            label="🎭 Voice",
            scale=2
        )
        format_select = gr.Dropdown(
            choices=["mp3", "wav", "flac", "opus"],
            value="mp3",
            label="📁 Format",
            scale=1
        )
        generate_btn = gr.Button("🎙️ Generate Audiobook", variant="primary", scale=2)

    # Output
    audio_output = gr.Audio(
        label="Generated Audio",
        type="filepath",
        interactive=False
    )
    generation_status = gr.Textbox(label="Generation Status", interactive=False)

    # Wire up generation
    def generate_combined(extracted, direct, voice, fmt):
        """Use extracted text if available, otherwise direct text."""
        text = extracted.strip() if extracted and extracted.strip() else direct
        return generate_audio(text, voice, fmt)

    generate_btn.click(
        generate_combined,
        inputs=[extracted_text, direct_text, voice_select, format_select],
        outputs=[audio_output, generation_status]
    )

    # Voice guide
    with gr.Accordion("🎭 Voice Guide", open=False):
        gr.Markdown("""
        | Category | Voices | Best For |
        |----------|--------|----------|
        | **British Male** | `bm_george`, `bm_lewis`, `bm_daniel`, `bm_fable` | Audiobooks, narration |
        | **British Female** | `bf_emma`, `bf_alice`, `bf_lily` | Audiobooks, narration |
        | **American Male** | `am_adam`, `am_echo`, `am_onyx` | General TTS |
        | **American Female** | `af_bella`, `af_nova`, `af_sky` | General TTS |

        **Recommended for audiobooks:** `bm_george`, `bf_emma`
        """)

    # Roadmap
    with gr.Accordion("🗺️ Roadmap", open=False):
        gr.Markdown("""
        **Current Features:**
        - ✅ PDF text extraction
        - ✅ DOCX text extraction
        - ✅ TXT file loading
        - ✅ 50+ Kokoro voices
        - ✅ Unlimited length (auto-chunking)
        - ✅ Multiple output formats

        **Coming Soon:**
        - ⏳ OCR for images (modular API - HuggingFace, Tesseract, or custom)
        - ⏳ Batch processing (multiple files)
        - ⏳ Chapter detection
        - ⏳ Voice mixing (different voices for dialogue)
        """)

    gr.Markdown("""
    ---
    **[GitHub](https://github.com/loserbcc/open-unified-tts)** |
    **[Kokoro Setup Guide](https://github.com/loserbcc/open-unified-tts/blob/main/docs/kokoro_setup_guide.md)** |
    **[Sample Audio](https://github.com/loserbcc/open-unified-tts/blob/main/demo/kokoro_audiobook_demo.mp3)**
    """)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Audiobook Production Studio")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=7865, help="Port to bind to")
    parser.add_argument("--api-url", default=None, help="TTS API URL")
    parser.add_argument("--share", action="store_true", help="Create public Gradio link")

    args = parser.parse_args()

    if args.api_url:
        API_URL = args.api_url

    print(f"🎙️ Audiobook Production Studio")
    print(f"   Web UI: http://{args.host}:{args.port}")
    print(f"   TTS API: {API_URL}")

    demo.launch(
        server_name=args.host,
        server_port=args.port,
        share=args.share
    )
