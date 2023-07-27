from enum import IntEnum
from typing import Any

from pydantic import Field

from app.config import settings
from app.utils.schema import BaseModel


class UploadResult(BaseModel):
    filename: str
    file_url: str


class DiscordType(IntEnum):
    IMAGINE = 2
    DESCRIBE = 2
    BLEND = 2
    UPSCALE = 3
    VARIATION = 3
    RESET = 3


class DiscordPayload(BaseModel):
    type: int
    application_id: str = Field(default=settings.DISCORD_APPLICATION_ID)
    guild_id: str = Field(default=settings.DISCORD_GUILD_ID)
    channel_id: str = Field(default=settings.DISCORD_CHANNEL_ID)
    session_id: str = Field(default=settings.DISCORD_SESSION_ID)
    data: Any
    nonce: str
