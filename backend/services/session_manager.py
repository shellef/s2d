"""
Session Manager - Manages transcription sessions.
"""

import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from backend.models.session import Session
from backend.config import get_settings

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages active transcription sessions.

    Sessions are stored in-memory for MVP. For production, consider using Redis
    or a database for persistence and scalability.
    """

    def __init__(self):
        """Initialize session manager with empty session store."""
        self.sessions: Dict[str, Session] = {}
        settings = get_settings()
        self.session_timeout_minutes = settings.session_timeout_minutes
        self.max_sessions = settings.max_sessions

    def create_session(self, session_id: Optional[str] = None) -> Session:
        """
        Create a new session.

        Args:
            session_id: Optional session ID. If not provided, generates a UUID.

        Returns:
            Newly created Session instance

        Raises:
            ValueError: If max sessions limit is reached
        """
        # Check session limit
        if len(self.sessions) >= self.max_sessions:
            # Clean up expired sessions first
            self._cleanup_expired_sessions()

            # Check again after cleanup
            if len(self.sessions) >= self.max_sessions:
                raise ValueError(f"Maximum session limit ({self.max_sessions}) reached")

        # Generate session ID if not provided
        if session_id is None:
            session_id = str(uuid.uuid4())

        # Create new session
        session = Session(session_id=session_id)
        self.sessions[session_id] = session

        logger.info(f"Created session: {session_id}")
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get an existing session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session instance if found, None otherwise
        """
        session = self.sessions.get(session_id)

        if session:
            # Check if session is expired
            timeout = timedelta(minutes=self.session_timeout_minutes)
            if datetime.utcnow() - session.updated_at > timeout:
                logger.warning(f"Session {session_id} has expired")
                session.mark_expired()

        return session

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session identifier

        Returns:
            True if session was deleted, False if not found
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
            return True

        return False

    def cleanup_session(self, session_id: str) -> None:
        """
        Clean up a session (alias for delete_session for clarity).

        Args:
            session_id: Session identifier
        """
        self.delete_session(session_id)

    def get_active_session_count(self) -> int:
        """
        Get the count of active sessions.

        Returns:
            Number of active sessions
        """
        return sum(1 for session in self.sessions.values() if session.is_active())

    def get_total_session_count(self) -> int:
        """
        Get the total count of sessions (including stopped/expired).

        Returns:
            Total number of sessions
        """
        return len(self.sessions)

    def _cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions.

        Returns:
            Number of sessions cleaned up
        """
        timeout = timedelta(minutes=self.session_timeout_minutes)
        now = datetime.utcnow()

        expired_ids = [
            session_id
            for session_id, session in self.sessions.items()
            if now - session.updated_at > timeout
        ]

        for session_id in expired_ids:
            self.delete_session(session_id)

        if expired_ids:
            logger.info(f"Cleaned up {len(expired_ids)} expired sessions")

        return len(expired_ids)

    def list_sessions(self) -> Dict[str, dict]:
        """
        Get a summary of all sessions.

        Returns:
            Dictionary mapping session IDs to session summaries
        """
        return {
            session_id: {
                "session_id": session.session_id,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "status": session.status,
                "word_count": session.transcription_buffer.word_count(),
            }
            for session_id, session in self.sessions.items()
        }


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """
    Get the global session manager instance.

    Returns:
        SessionManager instance
    """
    global _session_manager

    if _session_manager is None:
        _session_manager = SessionManager()

    return _session_manager
