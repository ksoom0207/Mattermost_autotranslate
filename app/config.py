"""
Configuration management for Mattermost AI Translator
Manages environment variables and application settings
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    # AI Model Configuration
    AI_MODEL: str = "gpt-4o-mini"  # Default model: gpt-4o-mini, claude-3-5-sonnet-20241022, etc.
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
        """Validate that at least one AI API key is configured"""
        return bool(self.OPENAI_API_KEY or self.ANTHROPIC_API_KEY)


# Global settings instance
settings = Settings()
