"""ModelsLab adapter - Cloud TTS with competitive pricing.

ModelsLab: https://modelslab.com
- Competitive pricing for TTS
- Multiple voice models
- No GPU required (cloud service)
- Supports voice cloning
"""
import logging
import os
import requests
from .base import TTSBackend

logger = logging.getLogger(__name__)

MODELSLAB_API_URL = "https://modelslab.com/api/v6/text-to-speech"

MODELSLAB_VOICES = {
    "male_1": "male_1",
    "male_2": "male_2", 
    "female_1": "female_1",
    "female_2": "female_2",
    "male_narration": "male_narration_1",
    "female_narration": "female_narration_1",
    "custom": "custom_voice",
}

DEFAULT_VOICE = "male_1"


class ModelsLabBackend(TTSBackend):
    """ModelsLab cloud TTS - competitive pricing."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("MODELSLAB_API_KEY", "")

    @property
    def name(self) -> str:
        return "modelslab"

    @property
    def port(self) -> int:
        return 0  # Cloud service

    @property
    def vram_gb(self) -> int:
        return 0  # Cloud service

    def is_available(self) -> bool:
        if not self.api_key:
            return False
        try:
            # Test with a simple API call
            r = requests.post(
                MODELSLAB_API_URL,
                json={
                    "key": self.api_key,
                    "prompt": "test",
                    "voice": DEFAULT_VOICE,
                },
                timeout=10
            )
            return r.status_code in (200, 400)  # 400 means valid but no input
        except Exception as e:
            logger.warning(f"ModelsLab availability check failed: {e}")
            return False

    def resolve_voice_id(self, voice: str) -> str:
        voice_lower = voice.lower()
        if voice_lower in MODELSLAB_VOICES:
            return MODELSLAB_VOICES[voice_lower]
        return DEFAULT_VOICE

    def generate(self, text: str, voice_path: str = "", transcript: str = "", speed: float = 1.0) -> str:
        """Generate speech from text."""
        voice = self.resolve_voice_id(voice_path or DEFAULT_VOICE)
        
        payload = {
            "key": self.api_key,
            "prompt": text,
            "voice": voice,
            "speed": speed,
            "output": "mp3",
        }

        logger.info(f"Generating speech with ModelsLab, voice: {voice}")

        try:
            response = requests.post(MODELSLAB_API_URL, json=payload, timeout=60)
            
            if response.status_code != 200:
                raise Exception(f"API error: {response.status_code} - {response.text}")
            
            data = response.json()
            
            # Check for async generation
            if "id" in data:
                return self._poll_for_result(data["id"])
            
            # Direct URL returned
            if "output" in data:
                audio_url = data["output"]
                # Download and return the file
                audio_response = requests.get(audio_url, timeout=60)
                with open("/tmp/modelslab_output.mp3", "wb") as f:
                    f.write(audio_response.content)
                return "/tmp/modelslab_output.mp3"
            
            raise Exception(f"Unexpected response: {data}")
            
        except Exception as e:
            logger.error(f"ModelsLab generation failed: {e}")
            raise

    def _poll_for_result(self, job_id: str, max_attempts: int = 30) -> str:
        """Poll for async generation result."""
        fetch_url = "https://modelslab.com/api/v6/text-to-speech/fetch"
        
        for i in range(max_attempts):
            try:
                response = requests.post(
                    fetch_url,
                    json={"key": self.api_key, "id": job_id},
                    timeout=10
                )
                
                data = response.json()
                
                if data.get("status") == "success":
                    audio_url = data["output"]
                    # Download the file
                    audio_response = requests.get(audio_url, timeout=60)
                    with open("/tmp/modelslab_output.mp3", "wb") as f:
                        f.write(audio_response.content)
                    return "/tmp/modelslab_output.mp3"
                
                if data.get("status") == "failed":
                    raise Exception("TTS generation failed")
                    
            except Exception as e:
                logger.warning(f"Poll attempt {i+1} failed: {e}")
                
            import time
            time.sleep(2)
            
        raise Exception("Timeout waiting for TTS generation")
