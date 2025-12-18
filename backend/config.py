"""
Backend Configuration - Environment variables and settings.

Loads configuration from environment variables with sensible defaults.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


def _load_yaml_config() -> dict:
    """
    Load configuration from config.yaml file in repo root.

    Returns:
        Dictionary of config values, or empty dict if file doesn't exist
    """
    # Path to config.yaml in repo root (parent of backend/)
    config_path = Path(__file__).parent.parent / "config.yaml"

    if not config_path.exists():
        return {}

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f) or {}
            return config
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to load config.yaml: {e}")
        return {}


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
    patch_history_count: int = Field(default=5, env="PATCH_HISTORY_COUNT")

    # Server Configuration
    host: str = Field(default="localhost", env="HOST")
    port: int = Field(default=8000, env="PORT")
    frontend_url: str = Field(default="http://localhost:5173", env="FRONTEND_URL")

    # Session Configuration
    session_timeout_minutes: int = Field(default=60, env="SESSION_TIMEOUT_MINUTES")
    max_sessions: int = Field(default=100, env="MAX_SESSIONS")

    # Logging Configuration
    verbose_llm_logging: bool = Field(default=False, env="VERBOSE_LLM_LOGGING")

    def __init__(self, **kwargs):
        """
        Initialize settings with layered configuration.

        Priority (highest to lowest):
        1. Environment variables
        2. ~/.env.s2d file
        3. config.yaml file
        4. Field defaults
        """
        # Load YAML config as lowest-priority defaults
        yaml_config = _load_yaml_config()

        # Merge YAML with any explicit kwargs (kwargs take precedence)
        merged = {**yaml_config, **kwargs}

        # Call parent __init__ - Pydantic will overlay .env.s2d and env vars
        super().__init__(**merged)

    class Config:
        env_file = os.path.expanduser("~/.env.s2d")
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get the global settings instance.

    Loads settings from ~/.env.s2d file on first call, then caches the instance.

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
                "OPENAI_API_KEY must be set in ~/.env.s2d or environment. "
                "Copy .env.example to ~/.env.s2d and add your API key. "
                "Regular config is in config.yaml."
            )

    return _settings


def reset_settings() -> None:
    """
    Reset the global settings instance.

    Useful for testing to reload settings.
    """
    global _settings
    _settings = None
