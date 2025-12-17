"""
LiveKit API Routes - Endpoints for LiveKit token generation.
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.livekit_service import get_livekit_service
from backend.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/livekit", tags=["livekit"])


class TokenRequest(BaseModel):
    """Request model for LiveKit token."""
    room_name: str
    participant_name: str


class TokenResponse(BaseModel):
    """Response model with LiveKit token and URL."""
    token: str
    url: str


@router.post("/token", response_model=TokenResponse)
async def get_token(request: TokenRequest):
    """
    Generate a LiveKit access token for a participant.

    Args:
        request: Token request with room and participant names

    Returns:
        Token and LiveKit server URL
    """
    try:
        livekit_service = get_livekit_service()
        settings = get_settings()

        token = livekit_service.create_token(
            room_name=request.room_name,
            participant_name=request.participant_name
        )

        return TokenResponse(
            token=token,
            url=settings.livekit_url
        )

    except Exception as e:
        logger.error(f"Failed to create LiveKit token: {e}")
        raise HTTPException(status_code=500, detail=str(e))
