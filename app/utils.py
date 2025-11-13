"""
Utility functions for the translation service
"""
import logging
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)


def should_ignore_user(username: str) -> bool:
    """
    Check if a user should be ignored (e.g., bots)

    Args:
        username: Username from Mattermost webhook

    Returns:
        True if user should be ignored
    """
    ignored_users = settings.get_ignored_usernames_list()

    # Case-insensitive comparison
    username_lower = username.lower().strip()

    for ignored_user in ignored_users:
        if ignored_user.lower() == username_lower:
            logger.info(f"Ignoring message from user: {username}")
            return True

    return False


def is_empty_message(text: str) -> bool:
    """
    Check if message text is empty or whitespace-only

    Args:
        text: Message text

    Returns:
        True if message is empty
    """
    return not text or not text.strip()


def sanitize_text(text: str) -> str:
    """
    Sanitize message text (basic cleaning)

    Args:
        text: Raw message text

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Strip leading/trailing whitespace
    sanitized = text.strip()

    return sanitized


def format_translation_message(original: str, translated: str, show_original: bool = False) -> str:
    """
    Format the translated message for posting to Mattermost

    Args:
        original: Original message text
        translated: Translated message text
        show_original: Whether to include original text

    Returns:
        Formatted message string
    """
    if show_original:
        return f"{translated}\n\n---\n*Original:* {original}"
    else:
        return translated


def setup_logging(level: str = "INFO"):
    """
    Configure application logging

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Set litellm logging level
    logging.getLogger("litellm").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
