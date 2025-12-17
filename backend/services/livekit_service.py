"""
LiveKit Service - Manages LiveKit rooms and access tokens.
"""

import logging
from livekit import api
from backend.config import get_settings

logger = logging.getLogger(__name__)


class LiveKitService:
    """Service for managing LiveKit rooms and generating access tokens."""

    def __init__(self):
        """Initialize LiveKit service."""
        settings = get_settings()
        self.api_key = settings.livekit_api_key
        self.api_secret = settings.livekit_api_secret
        self.url = settings.livekit_url

    def create_token(self, room_name: str, participant_name: str) -> str:
        """
        Create an access token for a participant to join a room.

        Args:
            room_name: Name of the LiveKit room
            participant_name: Name/ID of the participant

        Returns:
            JWT access token string
        """
        token = api.AccessToken(self.api_key, self.api_secret)
        token.with_identity(participant_name)
        token.with_name(participant_name)
        token.with_grants(api.VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True,
        ))

        logger.info(f"Created token for {participant_name} in room {room_name}")
        return token.to_jwt()


# Global service instance
_livekit_service = None


def get_livekit_service() -> LiveKitService:
    """Get the global LiveKit service instance."""
    global _livekit_service
    if _livekit_service is None:
        _livekit_service = LiveKitService()
    return _livekit_service
