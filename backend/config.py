"""
Backend Configuration - Environment variables and settings.

Loads configuration from environment variables with sensible defaults.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI API Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    whisper_model: str = Field(default="whisper-1", env="WHISPER_MODEL")
    gpt_model: str = Field(default="gpt-4o", env="GPT_MODEL")

    # AssemblyAI API Configuration
    assemblyai_api_key: Optional[str] = Field(default=None, env="ASSEMBLYAI_API_KEY")

    # LiveKit Configuration
    livekit_url: str = Field(default="ws://localhost:7880", env="LIVEKIT_URL")
    livekit_api_key: Optional[str] = Field(default=None, env="LIVEKIT_API_KEY")
    livekit_api_secret: Optional[str] = Field(default=None, env="LIVEKIT_API_SECRET")

    # Processing Configuration
    audio_chunk_duration: int = Field(default=3, env="AUDIO_CHUNK_DURATION")
    transcription_window_size: int = Field(default=250, env="TRANSCRIPTION_WINDOW_SIZE")

    # Server Configuration
    host: str = Field(default="localhost", env="HOST")
    port: int = Field(default=8000, env="PORT")
    frontend_url: str = Field(default="http://localhost:5173", env="FRONTEND_URL")

    # Session Configuration
    session_timeout_minutes: int = Field(default=60, env="SESSION_TIMEOUT_MINUTES")
    max_sessions: int = Field(default=100, env="MAX_SESSIONS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get the global settings instance.

    Loads settings from .env file on first call, then caches the instance.

    Returns:
        Settings instance with configuration values

    Raises:
        ValueError: If OPENAI_API_KEY is not set
    """
    global _settings

    if _settings is None:
        _settings = Settings()

        # Validate critical settings
        if not _settings.openai_api_key or _settings.openai_api_key == "sk-...":
            raise ValueError(
                "OPENAI_API_KEY must be set in .env file or environment variables. "
                "Copy .env.example to .env and add your API key."
            )

    return _settings


def reset_settings() -> None:
    """
    Reset the global settings instance.

    Useful for testing to reload settings.
    """
    global _settings
    _settings = None
