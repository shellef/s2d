"""
Connection Manager - Manages WebSocket connections per session.
"""

import logging
from typing import Dict, List
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for each session.
    Allows broadcasting messages to all connections in a session.
    """

    def __init__(self):
        """Initialize connection manager with empty connection store."""
        # Maps session_id -> List[WebSocket]
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        """
        Register a new WebSocket connection for a session.

        Args:
            websocket: WebSocket connection
            session_id: Session identifier
        """
        await websocket.accept()

        if session_id not in self.active_connections:
            self.active_connections[session_id] = []

        self.active_connections[session_id].append(websocket)
        logger.info(f"Session {session_id}: WebSocket connected (total: {len(self.active_connections[session_id])})")

    def disconnect(self, websocket: WebSocket, session_id: str):
        """
        Unregister a WebSocket connection from a session.

        Args:
            websocket: WebSocket connection
            session_id: Session identifier
        """
        if session_id in self.active_connections:
            if websocket in self.active_connections[session_id]:
                self.active_connections[session_id].remove(websocket)
                logger.info(f"Session {session_id}: WebSocket disconnected (remaining: {len(self.active_connections[session_id])})")

            # Clean up empty session entries
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
                logger.info(f"Session {session_id}: No more connections, cleaned up")

    async def broadcast_to_session(self, session_id: str, message: dict):
        """
        Broadcast a message to all WebSocket connections in a session.

        Args:
            session_id: Session identifier
            message: Message dictionary to send (will be JSON serialized)
        """
        if session_id not in self.active_connections:
            logger.warning(f"Session {session_id}: No active connections to broadcast to")
            return

        connections = self.active_connections[session_id].copy()
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Session {session_id}: Failed to send message to connection: {e}")
                # Remove failed connection
                self.disconnect(connection, session_id)

    def get_connection_count(self, session_id: str) -> int:
        """
        Get the number of active connections for a session.

        Args:
            session_id: Session identifier

        Returns:
            Number of active connections
        """
        return len(self.active_connections.get(session_id, []))


# Global connection manager instance
_connection_manager = None


def get_connection_manager() -> ConnectionManager:
    """
    Get the global connection manager instance.

    Returns:
        ConnectionManager instance
    """
    global _connection_manager

    if _connection_manager is None:
        _connection_manager = ConnectionManager()

    return _connection_manager
