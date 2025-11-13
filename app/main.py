"""
FastAPI Application for Mattermost AI Translation Service
Receives Mattermost Outgoing Webhooks, translates messages, and posts back via Incoming Webhooks
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.schemas import MattermostOutgoingWebhook, HealthResponse
from app.ai_client import ai_client
from app.mattermost_client import mattermost_client
from app.utils import (
    should_ignore_user,
    is_empty_message,
    sanitize_text,
    format_translation_message,
    setup_logging
)

# Setup logging
setup_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Mattermost AI Translation Service")
    logger.info(f"AI Model: {settings.AI_MODEL}")
    logger.info(f"Bot Username: {settings.MATTERMOST_BOT_USERNAME}")

    # Validate configuration
    if not ai_client.validate_configuration():
        logger.error("AI client not properly configured - missing API keys")
        raise RuntimeError("Missing AI API keys in configuration")

    if not mattermost_client.validate_configuration():
        logger.error("Mattermost client not properly configured - missing webhook URL")
        raise RuntimeError("Missing Mattermost webhook URL in configuration")

    logger.info("Configuration validated successfully")

    yield

    # Shutdown
    logger.info("Shutting down Mattermost AI Translation Service")


# Create FastAPI app
app = FastAPI(
    title="Mattermost AI Translator",
    description="Automatic message translation service for Mattermost",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint

    Returns:
        HealthResponse with service status
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        ai_configured=ai_client.validate_configuration()
    )


@app.post("/mattermost/translate")
async def translate_webhook(
    token: str = Form(None),
    team_id: str = Form(...),
    team_domain: str = Form(None),
    channel_id: str = Form(...),
    channel_name: str = Form(None),
    timestamp: str = Form(None),
    user_id: str = Form(...),
    user_name: str = Form(...),
    post_id: str = Form(...),
    text: str = Form(...),
    trigger_word: str = Form(None),
    file_ids: str = Form(None)
):
    """
    Handle Mattermost Outgoing Webhook for translation

    Receives message from Mattermost, translates it, and posts back

    Args:
        Form data from Mattermost Outgoing Webhook

    Returns:
        200 OK response
    """
    try:
        logger.info(f"Received webhook from user '{user_name}' in channel '{channel_name}': {text[:50]}...")

        # Validate and parse webhook data
        webhook_data = MattermostOutgoingWebhook(
            token=token,
            team_id=team_id,
            team_domain=team_domain,
            channel_id=channel_id,
            channel_name=channel_name,
            timestamp=timestamp,
            user_id=user_id,
            user_name=user_name,
            post_id=post_id,
            text=text,
            trigger_word=trigger_word,
            file_ids=file_ids
        )

        # Check if user should be ignored (e.g., bots)
        if should_ignore_user(webhook_data.user_name):
            logger.info(f"Ignoring message from {webhook_data.user_name}")
            return JSONResponse(
                status_code=200,
                content={"status": "ignored", "reason": "user in ignore list"}
            )

        # Check if message is empty
        if is_empty_message(webhook_data.text):
            logger.info("Ignoring empty message")
            return JSONResponse(
                status_code=200,
                content={"status": "ignored", "reason": "empty message"}
            )

        # Sanitize text
        clean_text = sanitize_text(webhook_data.text)

        # Translate message using AI
        logger.info(f"Translating message: {clean_text[:50]}...")
        translation_result = await ai_client.translate(clean_text)

        # Format translated message
        translated_message = format_translation_message(
            original=translation_result.original_text,
            translated=translation_result.translated_text,
            show_original=False  # Set to True if you want to show original
        )

        # Log translation
        logger.info(f"Translation complete:")
        logger.info(f"  Original:   {translation_result.original_text}")
        logger.info(f"  Translated: {translation_result.translated_text}")
        logger.info(f"  Model:      {translation_result.model_used}")

        # Post translated message back to Mattermost
        await mattermost_client.post_message(
            text=translated_message,
            username=settings.MATTERMOST_BOT_USERNAME,
            icon_url=settings.MATTERMOST_BOT_ICON_URL
        )

        logger.info("Message posted successfully to Mattermost")

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "translated": True,
                "model": translation_result.model_used
            }
        )

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)

        # Return 200 to prevent Mattermost from retrying
        # But log the error for monitoring
        return JSONResponse(
            status_code=200,
            content={
                "status": "error",
                "error": str(e)
            }
        )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler

    Args:
        request: FastAPI request
        exc: Exception

    Returns:
        JSON error response
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )
