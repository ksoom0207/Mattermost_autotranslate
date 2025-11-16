"""
Mattermost Webhook Client
Handles posting messages to Mattermost via Incoming Webhooks
"""
import logging
import httpx
from typing import Optional

from app.config import settings
from app.schemas import MattermostIncomingWebhook

logger = logging.getLogger(__name__)


class MattermostClient:
    """Client for interacting with Mattermost Incoming Webhooks"""

    def __init__(self):
        """Initialize Mattermost client"""
        self.webhook_url = settings.MATTERMOST_INCOMING_WEBHOOK_URL
        self.bot_username = settings.MATTERMOST_BOT_USERNAME
        self.bot_icon_url = settings.MATTERMOST_BOT_ICON_URL
        self.timeout = 10.0  # seconds

        logger.info(f"Mattermost client initialized for bot: {self.bot_username}")

    async def post_message(
        self,
        text: str,
        username: Optional[str] = None,
        icon_url: Optional[str] = None,
        channel: Optional[str] = None,
        root_id: Optional[str] = None
    ) -> bool:
        """
        Post a message to Mattermost via Incoming Webhook

        Args:
            text: Message text to post
            username: Override bot username (optional)
            icon_url: Override bot icon URL (optional)
            channel: Override channel (optional)
            root_id: Root post ID to reply in thread (optional)

        Returns:
            True if message was posted successfully

        Raises:
            Exception: If posting fails
        """
        try:
            # Build webhook payload
            payload = MattermostIncomingWebhook(
                username=username or self.bot_username,
                icon_url=icon_url or self.bot_icon_url,
                text=text,
                channel=channel,
                root_id=root_id
            )

            if root_id:
                logger.info(f"Posting message to Mattermost as thread reply (root_id={root_id}): {text[:50]}...")
            else:
                logger.info(f"Posting message to Mattermost: {text[:50]}...")

            # Send POST request to webhook
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload.model_dump(exclude_none=True)
                )

                # Check response status
                if response.status_code == 200:
                    logger.info("Message posted successfully to Mattermost")
                    return True
                else:
                    logger.error(
                        f"Failed to post message to Mattermost. "
                        f"Status: {response.status_code}, Response: {response.text}"
                    )
                    raise Exception(f"Mattermost webhook error: {response.status_code}")

        except httpx.TimeoutException as e:
            logger.error(f"Timeout posting to Mattermost: {str(e)}")
            raise Exception(f"Mattermost webhook timeout after {self.timeout}s")

        except httpx.HTTPError as e:
            logger.error(f"HTTP error posting to Mattermost: {str(e)}")
            raise Exception(f"Mattermost webhook HTTP error: {str(e)}")

        except Exception as e:
            logger.error(f"Unexpected error posting to Mattermost: {str(e)}")
            raise Exception(f"Failed to post to Mattermost: {str(e)}")

    def validate_configuration(self) -> bool:
        """
        Validate that Mattermost client is properly configured

        Returns:
            True if webhook URL is configured
        """
        return bool(self.webhook_url)


# Global Mattermost client instance
mattermost_client = MattermostClient()
