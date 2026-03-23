"""Configuration loading from .env.bot.secret"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Find .env.bot.secret in parent directory (repo root)
BASE_DIR = Path(__file__).parent.parent
ENV_FILE = BASE_DIR / ".env.bot.secret"


class Settings(BaseSettings):
    """Bot configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram bot token
    bot_token: str = ""

    # LMS API credentials
    lms_api_base_url: str = "http://localhost:42002"
    lms_api_key: str = ""

    # LLM API credentials
    llm_api_model: str = "coder-model"
    llm_api_key: str = ""
    llm_api_base_url: str = "http://localhost:42005/v1"


# Global settings instance
settings = Settings()
