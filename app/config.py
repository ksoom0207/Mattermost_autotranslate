"""
Configuration management for Mattermost AI Translator
Manages environment variables and application settings
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # LiteLLM Proxy Configuration
    LITELLM_API_BASE: str = "http://localhost:4000"  # LiteLLM Proxy server URL
    LITELLM_API_KEY: str = "dummy-key"  # API key for LiteLLM Proxy (can be dummy for local)

    # AI Model Configuration
    AI_MODEL: str = "translator-local"  # Model name configured in LiteLLM Proxy
    AI_TEMPERATURE: float = 0.3
    AI_MAX_TOKENS: int = 2000
    AI_TIMEOUT: int = 30  # seconds

    # Mattermost Configuration
    MATTERMOST_INCOMING_WEBHOOK_URL: str
    MATTERMOST_BOT_USERNAME: str = "ai-translator-bot"
    MATTERMOST_BOT_ICON_URL: Optional[str] = None

    # Ignored Users (bot names that should not trigger translation)
    IGNORED_USERNAMES: str = "ai-translator-bot,mattermost-bot,github,gitlab"

    # Server Configuration
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # Feature Flags
    ENABLE_PROFANITY_FILTER: bool = False
    PRESERVE_MARKDOWN: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def get_ignored_usernames_list(self) -> list[str]:
        """Convert comma-separated ignored usernames to list"""
        return [username.strip() for username in self.IGNORED_USERNAMES.split(",") if username.strip()]

    def validate_api_keys(self) -> bool:
        """Validate that LiteLLM Proxy is configured"""
        return bool(self.LITELLM_API_BASE and self.LITELLM_API_KEY)


# Global settings instance
settings = Settings()
