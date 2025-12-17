"""
Session Models - Data structures for managing transcription sessions.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from core.transcription_buffer import TranscriptionBuffer
from core.prompt_builder import get_empty_document


class Session(BaseModel):
    """
    Represents a speech-to-document transcription session.

    A session tracks the state of a single user's transcription session,
    including the accumulated transcription, current document state, and metadata.
    """

    session_id: str = Field(..., description="Unique session identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Session creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    status: str = Field(default="active", description="Session status: active, stopped, or expired")

    # Transcription data
    transcription_buffer: TranscriptionBuffer = Field(
        default_factory=lambda: TranscriptionBuffer(window_size=250),
        description="Buffer managing transcription with overlapping windows"
    )

    # Document state
    document: Dict[str, Any] = Field(
        default_factory=get_empty_document,
        description="Current document state matching PROCESS_TEMPLATE schema"
    )

    # Audio buffering
    audio_chunks: List[bytes] = Field(
        default_factory=list,
        description="Buffered audio chunks waiting for transcription"
    )

    # Track if we've received the first chunk with EBML header
    has_webm_header: bool = Field(
        default=False,
        description="Whether we've received the initial WebM chunk with EBML header"
    )

    class Config:
        arbitrary_types_allowed = True  # Allow TranscriptionBuffer

    def add_transcription(self, text: str) -> bool:
        """
        Add new transcription text to the buffer.

        Args:
            text: Newly transcribed text

        Returns:
            True if new text was added (triggers GPT processing), False otherwise
        """
        self.updated_at = datetime.utcnow()
        return self.transcription_buffer.append(text)

    def get_transcription_tail(self) -> str:
        """
        Get overlapping window of recent transcription for GPT-4o processing.

        Returns:
            Last N words of transcription (overlapping window)
        """
        return self.transcription_buffer.get_tail()

    def get_full_transcription(self) -> str:
        """
        Get complete accumulated transcription.

        Returns:
            All transcription text
        """
        return self.transcription_buffer.get_full_text()

    def update_document(self, new_document: Dict[str, Any]) -> None:
        """
        Update the document state.

        Args:
            new_document: New document state after applying patches
        """
        self.document = new_document
        self.updated_at = datetime.utcnow()

    def mark_stopped(self) -> None:
        """Mark session as stopped (recording ended)."""
        self.status = "stopped"
        self.updated_at = datetime.utcnow()

    def mark_expired(self) -> None:
        """Mark session as expired (timeout)."""
        self.status = "expired"
        self.updated_at = datetime.utcnow()

    def is_active(self) -> bool:
        """Check if session is active."""
        return self.status == "active"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert session to dictionary for JSON serialization.

        Returns:
            Dictionary representation of session
        """
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "status": self.status,
            "transcription": self.get_full_transcription(),
            "word_count": self.transcription_buffer.word_count(),
            "document": self.document,
        }
