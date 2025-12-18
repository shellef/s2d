"""
HTTP Routes - REST API endpoints for session management.
"""

import logging
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel
from backend.services.session_manager import get_session_manager
from backend.services.connection_manager import get_connection_manager
from backend.services.llm_service import get_llm_service
from backend.config import get_settings
from backend.models.message import create_transcription_message, create_document_patch_message
from core.patch_generator import apply_patch

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["sessions"])


class TranscriptionInput(BaseModel):
    """Input model for transcription endpoint."""
    text: str


@router.get("/sessions")
async def list_sessions() -> Dict[str, Any]:
    """
    List all sessions with their summaries.

    Returns:
        Dictionary with session summaries and counts
    """
    session_manager = get_session_manager()
    sessions = session_manager.list_sessions()

    return {
        "total_sessions": session_manager.get_total_session_count(),
        "active_sessions": session_manager.get_active_session_count(),
        "sessions": sessions
    }


@router.post("/sessions")
async def create_session() -> Dict[str, Any]:
    """
    Create a new session.

    Returns:
        Session information including session_id
    """
    try:
        session_manager = get_session_manager()
        session = session_manager.create_session()

        logger.info(f"Created new session via HTTP: {session.session_id}")

        return {
            "session_id": session.session_id,
            "status": "created",
            "websocket_url": f"/ws?session_id={session.session_id}"
        }
    except ValueError as e:
        raise HTTPException(status_code=429, detail=str(e))


@router.get("/sessions/{session_id}")
async def get_session(session_id: str) -> Dict[str, Any]:
    """
    Get session details by ID.

    Args:
        session_id: Session identifier

    Returns:
        Complete session information

    Raises:
        HTTPException: If session not found
    """
    session_manager = get_session_manager()
    session = session_manager.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return session.to_dict()


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str) -> Dict[str, str]:
    """
    Delete a session.

    Args:
        session_id: Session identifier

    Returns:
        Deletion confirmation

    Raises:
        HTTPException: If session not found
    """
    session_manager = get_session_manager()
    deleted = session_manager.delete_session(session_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")

    logger.info(f"Deleted session via HTTP: {session_id}")

    return {
        "session_id": session_id,
        "status": "deleted"
    }


@router.post("/sessions/{session_id}/export")
async def export_session(
    session_id: str,
    format: str = "json"
) -> Dict[str, Any]:
    """
    Export session document.

    Args:
        session_id: Session identifier
        format: Export format (currently only 'json' supported)

    Returns:
        Exported document

    Raises:
        HTTPException: If session not found or format unsupported
    """
    session_manager = get_session_manager()
    session = session_manager.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if format != "json":
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format: {format}. Currently only 'json' is supported."
        )

    return {
        "session_id": session_id,
        "format": format,
        "document": session.document,
        "transcription": session.get_full_transcription(),
        "word_count": session.transcription_buffer.word_count()
    }


@router.post("/sessions/{session_id}/transcription")
async def add_transcription(
    session_id: str,
    transcription_input: TranscriptionInput
) -> Dict[str, str]:
    """
    Add transcription text to a session and broadcast to connected clients.

    This endpoint is used by the LiveKit agent to send transcriptions.
    The backend will process the transcription with LLM and broadcast
    both the transcription and document patches to all WebSocket clients.

    Args:
        session_id: Session identifier
        transcription_input: Transcription text input

    Returns:
        Confirmation of transcription processing

    Raises:
        HTTPException: If session not found
    """
    session_manager = get_session_manager()
    connection_manager = get_connection_manager()
    llm_service = get_llm_service()

    # Get session
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    text = transcription_input.text
    logger.info(f"Session {session_id}: Received transcription via API: {text[:50]}...")

    # Broadcast transcription to all connected WebSocket clients
    await connection_manager.broadcast_to_session(
        session_id,
        create_transcription_message(text)
    )

    # Process transcription with LLM
    try:
        # Add to session buffer
        has_new_text = session.add_transcription(text)

        if has_new_text:
            # Get transcription tail for LLM processing
            tail = session.get_transcription_tail()

            # Get patch history from session
            patch_history = session.patch_history

            # Get max count from settings
            settings = get_settings()
            max_history_count = settings.patch_history_count

            # Generate document patches
            patch_ops = await llm_service.process_transcription(
                tail,
                session.document,
                patch_history
            )

            # Apply patches to session document
            if patch_ops:
                try:
                    updated_document = apply_patch(patch_ops, session.document)
                    session.update_document(updated_document)

                    # Add patches to history
                    session.add_patch_to_history(patch_ops, max_history_count)

                    # Broadcast patches to all connected WebSocket clients
                    await connection_manager.broadcast_to_session(
                        session_id,
                        create_document_patch_message(patch_ops)
                    )

                    logger.info(f"Session {session_id}: Applied and broadcasted {len(patch_ops)} patches")
                except Exception as e:
                    logger.error(f"Failed to apply patches: {e}")
    except Exception as e:
        logger.error(f"Failed to process transcription: {e}", exc_info=True)
        # Don't raise exception - graceful degradation

    return {
        "status": "success",
        "session_id": session_id,
        "message": "Transcription processed and broadcasted"
    }
