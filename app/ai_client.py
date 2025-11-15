"""
AI Translation Client using OpenAI SDK v1 with LiteLLM Proxy
Connects to local LiteLLM proxy server with OpenAI-compatible API
"""
import logging
from typing import Optional
from openai import OpenAI, AsyncOpenAI

from app.config import settings
from app.schemas import TranslationResponse

logger = logging.getLogger(__name__)


class AITranslationClient:
    """AI-powered translation client using OpenAI SDK with LiteLLM Proxy"""

    def __init__(self):
        """Initialize AI client with LiteLLM Proxy configuration"""
        self.model = settings.AI_MODEL
        self.temperature = settings.AI_TEMPERATURE
        self.max_tokens = settings.AI_MAX_TOKENS
        self.timeout = settings.AI_TIMEOUT

        # Initialize OpenAI client pointing to LiteLLM Proxy
        self.client = AsyncOpenAI(
            api_key=settings.LITELLM_API_KEY,
            base_url=settings.LITELLM_API_BASE,
            timeout=self.timeout
        )

        logger.info(f"AI Translation Client initialized")
        logger.info(f"  Base URL: {settings.LITELLM_API_BASE}")
        logger.info(f"  Model: {self.model}")
        logger.info(f"  Temperature: {self.temperature}")

    def _build_translation_prompt(self, text: str) -> str:
        """
        Build translation prompt with language detection and bidirectional translation

        Args:
            text: Original message text

        Returns:
            Formatted prompt string
        """
        prompt = f"""Translate the following message:

Rules:
- Korean text → English translation
- English text → Korean translation
- Other languages → Provide both: [KO] Korean translation [EN] English translation

Important: Output ONLY the translation. Do not include any explanations, notes, or this instruction.

Message to translate:
{text}"""

        return prompt

    async def translate(self, text: str) -> TranslationResponse:
        """
        Translate text using LiteLLM Proxy via OpenAI SDK

        Args:
            text: Text to translate

        Returns:
            TranslationResponse with translated text and metadata

        Raises:
            Exception: If translation fails
        """
        try:
            logger.info(f"Starting translation for text: {text[:50]}...")

            # Build prompt
            prompt = self._build_translation_prompt(text)

            # Call LiteLLM Proxy using OpenAI SDK
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            # Extract translated text
            translated_text = response.choices[0].message.content.strip()

            logger.info(f"Translation completed: {translated_text[:50]}...")

            return TranslationResponse(
                original_text=text,
                translated_text=translated_text,
                detected_language=None,  # Could be enhanced with language detection
                target_language=None,
                model_used=self.model
            )

        except Exception as e:
            logger.error(f"Translation error: {str(e)}", exc_info=True)
            raise Exception(f"Translation failed: {str(e)}")

    def validate_configuration(self) -> bool:
        """
        Validate that AI client is properly configured

        Returns:
            True if configuration is valid
        """
        return settings.validate_api_keys()


# Global AI client instance
ai_client = AITranslationClient()
