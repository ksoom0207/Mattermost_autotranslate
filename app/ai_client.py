"""
AI Translation Client using LiteLLM
Supports OpenAI, Anthropic Claude, and other LLM providers
"""
import logging
from typing import Optional
import litellm
from litellm import completion

from app.config import settings
from app.schemas import TranslationResponse

logger = logging.getLogger(__name__)

# Configure litellm settings
litellm.drop_params = True  # Drop unsupported params for different providers
litellm.set_verbose = False  # Set to True for debugging


class AITranslationClient:
    """AI-powered translation client using LiteLLM"""

    def __init__(self):
        """Initialize AI client with configured settings"""
        self.model = settings.AI_MODEL
        self.temperature = settings.AI_TEMPERATURE
        self.max_tokens = settings.AI_MAX_TOKENS
        self.timeout = settings.AI_TIMEOUT

        # Configure LiteLLM API Base (for custom proxy server)
        if settings.LITELLM_API_BASE:
            litellm.api_base = settings.LITELLM_API_BASE
            logger.info(f"Using LiteLLM proxy at: {settings.LITELLM_API_BASE}")

            # Set custom API key for LiteLLM proxy if provided
            if settings.LITELLM_API_KEY:
                # For custom proxy, use the appropriate key based on model prefix
                if self.model.startswith("openai/") or self.model.startswith("gpt"):
                    litellm.openai_key = settings.LITELLM_API_KEY
                elif self.model.startswith("anthropic/") or self.model.startswith("claude"):
                    litellm.anthropic_key = settings.LITELLM_API_KEY
                else:
                    # Generic API key for custom models
                    litellm.api_key = settings.LITELLM_API_KEY
        else:
            # Set API keys for direct provider access
            if settings.OPENAI_API_KEY:
                litellm.openai_key = settings.OPENAI_API_KEY
            if settings.ANTHROPIC_API_KEY:
                litellm.anthropic_key = settings.ANTHROPIC_API_KEY

        logger.info(f"AI Translation Client initialized with model: {self.model}")

    def _build_translation_prompt(self, text: str) -> str:
        """
        Build translation prompt with language detection and bidirectional translation

        Args:
            text: Original message text

        Returns:
            Formatted prompt string
        """
        prompt = f"""You are a professional translator. Follow these rules exactly:

1. Detect the language of the message
2. Translation rules:
   - If Korean → translate to English only
   - If English → translate to Korean only
   - If other language → translate to both Korean and English (format: "[KO] Korean translation\\n[EN] English translation")
3. Preserve the original tone, style, and formatting (including Markdown)
4. Do NOT modify, censor, or add any content
5. Return ONLY the translated text, no explanations or metadata

Original Message:
{text}

Translated Message:"""

        return prompt

    async def translate(self, text: str) -> TranslationResponse:
        """
        Translate text using AI model

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

            # Call AI model via litellm
            response = await litellm.acompletion(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout,
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

        except litellm.Timeout as e:
            logger.error(f"Translation timeout: {str(e)}")
            raise Exception(f"Translation timeout after {self.timeout}s")

        except litellm.APIError as e:
            logger.error(f"API error during translation: {str(e)}")
            raise Exception(f"API error: {str(e)}")

        except Exception as e:
            logger.error(f"Unexpected error during translation: {str(e)}")
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
