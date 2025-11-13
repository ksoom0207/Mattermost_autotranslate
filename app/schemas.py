"""
Pydantic models for request/response schemas
"""
from pydantic import BaseModel, Field
from typing import Optional


class MattermostOutgoingWebhook(BaseModel):
    """Schema for incoming Mattermost Outgoing Webhook payload"""
    token: Optional[str] = None
    team_id: str
    team_domain: Optional[str] = None
    channel_id: str
    channel_name: Optional[str] = None
    timestamp: Optional[str] = None
    user_id: str
    user_name: str
    post_id: str
    text: str
    trigger_word: Optional[str] = None
    file_ids: Optional[str] = None


class MattermostIncomingWebhook(BaseModel):
    """Schema for outgoing Mattermost Incoming Webhook payload"""
    username: str = Field(default="ai-translator-bot", description="Bot username to display")
    icon_url: Optional[str] = Field(default=None, description="Bot icon URL")
    text: str = Field(..., description="Translated message text")
    channel: Optional[str] = Field(default=None, description="Optional channel override")


class TranslationRequest(BaseModel):
    """Internal translation request schema"""
    text: str
    source_language: Optional[str] = None
    target_language: Optional[str] = None
    preserve_format: bool = True


class TranslationResponse(BaseModel):
    """Internal translation response schema"""
    original_text: str
    translated_text: str
    detected_language: Optional[str] = None
    target_language: Optional[str] = None
    model_used: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str = "1.0.0"
    ai_configured: bool
