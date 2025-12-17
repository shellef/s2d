"""
HTTP Routes - REST API endpoints for session management.
"""

import logging
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from backend.services.session_manager import get_session_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["sessions"])


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
