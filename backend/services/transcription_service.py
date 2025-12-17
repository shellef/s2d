"""
Transcription Service - Whisper API integration for speech-to-text.
"""

import tempfile
import logging
from typing import Optional
from openai import AsyncOpenAI
from backend.config import get_settings

logger = logging.getLogger(__name__)


class TranscriptionService:
    """
    Service for transcribing audio using OpenAI Whisper API.

    Handles audio file formatting and API communication.
    """

    def __init__(self):
        """Initialize transcription service with OpenAI client."""
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.whisper_model

    async def transcribe_audio(
        self,
        audio_data: bytes,
        audio_format: str = "webm",
        language: str = "en"
    ) -> str:
        """
        Transcribe audio using OpenAI Whisper API.

        The Whisper API requires a file input, so we write the audio data to a
        temporary file before transcribing.

        Args:
            audio_data: Raw audio bytes
            audio_format: Audio format (webm, mp3, wav, etc.)
            language: Language code (default: "en" for English)

        Returns:
            Transcribed text string

        Raises:
            Exception: If transcription fails
        """
        if not audio_data or len(audio_data) == 0:
            logger.warning("Empty audio data received")
            return ""

        # Skip very small audio chunks (likely invalid/incomplete)
        # WebM/MP4 chunks should be at least a few KB for valid audio
        if len(audio_data) < 1000:
            logger.warning(f"Audio data too small ({len(audio_data)} bytes), skipping")
            return ""

        try:
            logger.info(f"Transcribing audio: format={audio_format}, size={len(audio_data)} bytes")

            # Whisper API requires a file, so write to temp file
            with tempfile.NamedTemporaryFile(
                suffix=f".{audio_format}",
                delete=False
            ) as temp_audio:
                temp_audio.write(audio_data)
                temp_audio.flush()
                temp_audio_path = temp_audio.name

            # Transcribe using Whisper API
            # Pass file as tuple (filename, file_object, content_type) for proper multipart upload
            with open(temp_audio_path, "rb") as audio_file:
                transcript = await self.client.audio.transcriptions.create(
                    model=self.model,
                    file=(f"audio.{audio_format}", audio_file, f"audio/{audio_format}"),
                    language=language,
                    response_format="text"
                )

            # Clean up temp file
            import os
            try:
                os.unlink(temp_audio_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file {temp_audio_path}: {e}")

            # Extract text from response
            if isinstance(transcript, str):
                text = transcript
            else:
                text = transcript.text if hasattr(transcript, 'text') else str(transcript)

            logger.info(f"Transcribed {len(audio_data)} bytes → {len(text)} chars")
            return text.strip()

        except Exception as e:
            logger.error(f"Transcription failed: {e}", exc_info=True)
            raise Exception(f"Transcription failed: {str(e)}")


# Global service instance
_transcription_service: Optional[TranscriptionService] = None


def get_transcription_service() -> TranscriptionService:
    """
    Get the global transcription service instance.

    Returns:
        TranscriptionService instance
    """
    global _transcription_service

    if _transcription_service is None:
        _transcription_service = TranscriptionService()

    return _transcription_service
