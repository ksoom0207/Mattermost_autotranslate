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
    """Client for interacting with Mattermost Incoming Webhooks and API"""

    def __init__(self):
        """Initialize Mattermost client"""
        self.webhook_url = settings.MATTERMOST_INCOMING_WEBHOOK_URL
        self.bot_username = settings.MATTERMOST_BOT_USERNAME
        self.bot_icon_url = settings.MATTERMOST_BOT_ICON_URL
        self.api_url = settings.MATTERMOST_API_URL
        self.api_token = settings.MATTERMOST_API_TOKEN
        self.timeout = 10.0  # seconds

        logger.info(f"Mattermost client initialized for bot: {self.bot_username}")
        if self.api_token:
            logger.info(f"Mattermost API enabled for thread support")
        else:
            logger.warning(f"Mattermost API token not configured - thread support disabled")

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

    async def get_post(self, post_id: str) -> Optional[dict]:
        """
        Get post information from Mattermost API

        Args:
            post_id: Post ID to retrieve

        Returns:
            Post data dict with fields like root_id, or None if API not configured or request fails
        """
        if not self.api_token:
            logger.debug("Mattermost API token not configured, cannot fetch post data")
            return None

        try:
            url = f"{self.api_url}/posts/{post_id}"
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }

            logger.debug(f"Fetching post data for post_id={post_id}")

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)

                if response.status_code == 200:
                    post_data = response.json()
                    logger.info(f"Post data retrieved: root_id={post_data.get('root_id')}")
                    return post_data
                else:
                    logger.warning(
                        f"Failed to fetch post data. "
                        f"Status: {response.status_code}, Response: {response.text}"
                    )
                    return None

        except httpx.TimeoutException as e:
            logger.error(f"Timeout fetching post data: {str(e)}")
            return None

        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching post data: {str(e)}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error fetching post data: {str(e)}")
            return None

    def validate_configuration(self) -> bool:
        """
        Validate that Mattermost client is properly configured

        Returns:
            True if webhook URL is configured
        """
        return bool(self.webhook_url)


# Global Mattermost client instance
mattermost_client = MattermostClient()
