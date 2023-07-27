from fastapi import APIRouter, UploadFile

from app.errors import TriggerBizError
from app.trigger.schemas.trigger import (
    BlendRequest,
    DescribeRequest,
    ImagineRequest,
    ResetRequest,
    UploadResponse,
    UpscaleRequest,
    VariationRequest,
)
from app.trigger.services.trigger import trigger_service
from app.utils.exception import APPException
from app.utils.json import json_response
from app.utils.response import Response

router = APIRouter(
    prefix="/trigger",
    tags=["trigger"],
)


@router.post(
    "/upload",
    response_model=Response[UploadResponse],
    summary="Upload attachment",
)
async def upload(file: UploadFile):
    if not file.content_type.startswith("image/"):
        raise APPException(TriggerBizError.NOT_SUPPORT_FILE_TYPE)

    file_size = file.size
    file_type = file.content_type.split("/")[-1]
    image_bytes = await file.read()
    data = await trigger_service.upload(
        file_size,
        file_type,
        image_bytes,
    )
    return json_response(data=data)


@router.post(
    "/imagine",
    response_model=Response,
    summary="Imagine trigger",
)
async def imagine(request: ImagineRequest):
    data = await trigger_service.imagine(request)
    return json_response(data=data)


@router.post(
    "/upscale",
    response_model=Response,
    summary="Upscale images",
)
async def upscale(request: UpscaleRequest):
    data = await trigger_service.upscale(request)
    return json_response(data=data)


@router.post(
    "/variation",
    response_model=Response,
    summary="Variation",
)
async def variation(request: VariationRequest):
    data = await trigger_service.variation(request)
    return json_response(data=data)


@router.post(
    "/reset",
    response_model=Response,
    summary="Reset",
)
async def reset(request: ResetRequest):
    data = await trigger_service.reset(request)
    return json_response(data=data)


@router.post(
    "/describe",
    response_model=Response,
    summary="Describe",
)
async def describe(request: DescribeRequest):
    data = await trigger_service.describe(request)
    return json_response(data=data)


@router.post(
    "/blend",
    response_model=Response,
    summary="Blend",
)
async def blend(request: BlendRequest):
    data = await trigger_service.blend(request)
    return json_response(data=data)
