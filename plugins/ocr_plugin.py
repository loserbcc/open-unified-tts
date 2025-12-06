"""OCR Plugin - Extract text from images (Future Implementation).

This plugin will enable optical character recognition to extract text
from images, making it easy to generate TTS from screenshots, photos
of documents, etc.

Status: PLACEHOLDER - Not yet implemented
Dependencies (when implemented): pytesseract, PIL
"""
from typing import List
from .base import Plugin


class OCRPlugin(Plugin):
    """Extract text from images using OCR.

    Future functionality:
    - Drag & drop image support
    - Clipboard image paste
    - Automatic text extraction
    - Language detection
    - Multi-column text handling

    Implementation Notes:
    - Will use pytesseract for OCR
    - Support common formats: PNG, JPG, PDF
    - Consider GPU acceleration for large batches
    - Add confidence threshold settings
    """

    def __init__(self):
        self._enabled = False  # Disabled until implemented

    @property
    def name(self) -> str:
        return "OCR (Image to Text)"

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        # Can't enable until implemented
        if value:
            raise NotImplementedError(
                "OCR plugin not yet implemented. "
                "Planned features: image paste, screenshot OCR, PDF extraction"
            )
        self._enabled = False

    def process_text(self, text: str) -> str:
        """Currently a pass-through.

        Future: If image path detected in text, extract text from image.
        """
        return text

    def get_ui_components(self) -> List:
        """Future: Add image paste button, file picker."""
        return []

    def get_description(self) -> str:
        return (
            "Extract text from images using OCR. "
            "Status: PLANNED - Not yet implemented. "
            "Will support image paste, screenshots, and PDF text extraction."
        )

    # Future methods to implement:
    # - extract_from_image(image_path: str) -> str
    # - extract_from_clipboard() -> str
    # - extract_from_pdf(pdf_path: str, page: int) -> str
    # - set_language(lang: str) -> None
