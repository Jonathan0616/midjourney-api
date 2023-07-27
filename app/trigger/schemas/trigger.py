from typing import Any

from pydantic import Field

from app.config import settings
from app.utils.schema import BaseModel


class UploadResponse(BaseModel):
    task_id: str
    filename: str
    file_url: str


class ImagineRequest(BaseModel):
    prompt: str = Field(description="prompt")
    img_url: str = Field(description="images url")
    notify_hook: str = Field(
        default=settings.NOTIFY_HOOK, description="notify hook"
    )


class CommonRequest(BaseModel):
    msg_id: str
    msg_hash: str


class UpscaleRequest(CommonRequest):
    index: int


class VariationRequest(CommonRequest):
    index: int


class ResetRequest(CommonRequest):
    ...


class DescribeRequest(BaseModel):
    file_size: int
    file_type: str
    image_bytes: bytes


class BlendRequest(BaseModel):
    file_size: int
    file_type: str
    image_bytes: bytes
    file_size2: int
    file_type2: str
    image_bytes2: bytes
