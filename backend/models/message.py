"""
WebSocket Message Models - Data structures for WebSocket communication.
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


# Client → Server Messages


class AudioChunkMessage(BaseModel):
    """Audio chunk from client to server."""

    type: Literal["audio_chunk"] = "audio_chunk"
    data: str = Field(..., description="Base64-encoded audio data")
    format: str = Field(default="webm", description="Audio format (webm, mp3, wav, etc.)")


class StopRecordingMessage(BaseModel):
    """Stop recording signal from client."""

    type: Literal["stop_recording"] = "stop_recording"


class TranscriptionInputMessage(BaseModel):
    """Transcription input from LiveKit agent to server."""

    type: Literal["transcription"] = "transcription"
    text: str = Field(..., description="Transcribed text from speech recognition")


# Server → Client Messages


class TranscriptionMessage(BaseModel):
    """Transcription update from server to client."""

    type: Literal["transcription"] = "transcription"
    text: str = Field(..., description="Newly transcribed text")
    timestamp: Optional[float] = Field(None, description="Unix timestamp")


class DocumentPatchMessage(BaseModel):
    """Document patch operations from server to client."""

    type: Literal["document_patch"] = "document_patch"
    patch: List[Dict[str, Any]] = Field(..., description="JSON Patch operations (RFC 6902)")


class StatusMessage(BaseModel):
    """Status update from server to client."""

    type: Literal["status"] = "status"
    status: Literal["processing", "idle", "error"] = Field(..., description="Current status")
    message: str = Field(default="", description="Optional status message")


class ErrorMessage(BaseModel):
    """Error message from server to client."""

    type: Literal["error"] = "error"
    error: str = Field(..., description="Error description")
    code: Optional[str] = Field(None, description="Error code")


# Utility functions


def parse_client_message(data: Dict[str, Any]) -> AudioChunkMessage | StopRecordingMessage | TranscriptionInputMessage:
    """
    Parse incoming client message based on type field.

    Args:
        data: Raw message dictionary from client

    Returns:
        Parsed message model

    Raises:
        ValueError: If message type is unknown or invalid
    """
    message_type = data.get("type")

    if message_type == "audio_chunk":
        return AudioChunkMessage(**data)
    elif message_type == "stop_recording":
        return StopRecordingMessage(**data)
    elif message_type == "transcription":
        return TranscriptionInputMessage(**data)
    else:
        raise ValueError(f"Unknown message type: {message_type}")


def create_transcription_message(text: str, timestamp: Optional[float] = None) -> Dict[str, Any]:
    """
    Create a transcription message to send to client.

    Args:
        text: Transcribed text
        timestamp: Optional timestamp

    Returns:
        Dictionary ready for JSON serialization
    """
    return TranscriptionMessage(text=text, timestamp=timestamp).model_dump()


def create_document_patch_message(patch: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create a document patch message to send to client.

    Args:
        patch: JSON Patch operations

    Returns:
        Dictionary ready for JSON serialization
    """
    return DocumentPatchMessage(patch=patch).model_dump()


def create_status_message(
    status: Literal["processing", "idle", "error"],
    message: str = ""
) -> Dict[str, Any]:
    """
    Create a status message to send to client.

    Args:
        status: Current status
        message: Optional status message

    Returns:
        Dictionary ready for JSON serialization
    """
    return StatusMessage(status=status, message=message).model_dump()


def create_error_message(error: str, code: Optional[str] = None) -> Dict[str, Any]:
    """
    Create an error message to send to client.

    Args:
        error: Error description
        code: Optional error code

    Returns:
        Dictionary ready for JSON serialization
    """
    return ErrorMessage(error=error, code=code).model_dump()
