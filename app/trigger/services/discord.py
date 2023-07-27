import json
import random
import uuid
from typing import Any, Dict

import aiohttp

from app.config import settings
from app.errors import DiscordBizError
from app.trigger.schemas.discord import (
    DiscordPayload,
    DiscordType,
    UploadResult,
)
from app.utils.exception import APPException
from app.utils.http import FetchMethod, fetch
from app.utils.random import random_filename, randome_nonce


class DiscordService:
    TRIGGER_URL = "https://discord.com/api/v9/interactions"
    UPLOAD_ATTACHMENT_URL = f"https://discord.com/api/v9/channels/{settings.DISCORD_CHANNEL_ID}/attachments"
    SEND_MESSAGE_URL = f"https://discord.com/api/v9/channels/{settings.DISCORD_CHANNEL_ID}/messages"

    HEADERS = {
        "Content-Type": "application/json",
        "Authorization": settings.DISCORD_USER_TOKEN,
    }

    async def request(
        self,
        url: str,
        data: Dict[str, Any],
        headers: Dict[str, Any] = None,
        method=FetchMethod.post,
        is_json: bool = True,
    ):
        if headers is None:
            headers = self.HEADERS
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers=headers,
        ) as session:
            return await fetch(
                session,
                url,
                data=data,
                method=method,
                is_json=is_json,
            )

    async def put_attachment(self, url: str, image: bytes):
        headers = {"Content-Type": "image/png"}
        return await self.request(
            url=url,
            data=image,
            headers=headers,
            method=FetchMethod.put,
            is_json=False,
        )

    async def presigned_upload(
        self,
        file_size: int,
        file_type: str,
        image: bytes,
    ):
        filename = random_filename(16) + "." + file_type
        upload_attachment_resp = await self.request(
            url=self.UPLOAD_ATTACHMENT_URL,
            data=json.dumps(
                {
                    "files": [
                        {
                            "filename": filename,
                            "file_size": file_size,
                            "id": "0",
                            "is_clip": False,
                        }
                    ]
                }
            ),
        )
        if not upload_attachment_resp or not upload_attachment_resp.get(
            "attachments"
        ):
            raise APPException(DiscordBizError.UPLOAD_ATTACHMENT_ERR)
        presigned_attachment = upload_attachment_resp["attachments"][0]

        upload_url = presigned_attachment.pop("upload_url")
        upload_filename = presigned_attachment.pop("upload_filename")

        # upload image
        await self.put_attachment(upload_url, image)
        return filename, upload_filename

    async def upload(
        self,
        file_size: int,
        file_type: str,
        image: bytes,
    ) -> UploadResult:
        """Upload image to discord and return the url"""

        filename, upload_filename = await self.presigned_upload(
            file_size, file_type, image
        )
        # sent msg with imgs
        sent_msg_payload = dict(
            attachments=[
                {
                    "id": "0",
                    "filename": filename,
                    "uploaded_filename": upload_filename,
                }
            ],
            channel_id=settings.DISCORD_CHANNEL_ID,
            nonce=randome_nonce(),
            sticker_ids=[],
            type=0,
            content="",
        )
        response = await self.request(
            self.SEND_MESSAGE_URL,
            data=json.dumps(sent_msg_payload),
        )
        attachment = response["attachments"][0]
        return UploadResult(
            filename=attachment.get("filename"),
            file_url=attachment.get("url"),
        )

    async def imagine(self, prompt: str):
        version = "1118961510123847772"
        payload = DiscordPayload(
            type=DiscordType.IMAGINE.value,
            nonce=randome_nonce(),
            data={
                "version": version,
                "id": "938956540159881230",
                "name": "imagine",
                "type": 1,
                "options": [{"type": 3, "name": "prompt", "value": prompt}],
                "application_command": {
                    "id": "938956540159881230",
                    "application_id": settings.DISCORD_APPLICATION_ID,
                    "version": version,
                    "default_permission": True,
                    "default_member_permissions": None,
                    "type": 1,
                    "nsfw": False,
                    "name": "imagine",
                    "description": "Create images with Midjourney",
                    "dm_permission": True,
                    "contexts": [0, 1, 2],
                    "options": [
                        {
                            "type": 3,
                            "name": "prompt",
                            "description": "The prompt to imagine",
                            "required": True,
                        }
                    ],
                },
                "attachments": [],
            },
        )
        resp = await self.request(
            url=self.TRIGGER_URL,
            data=json.dumps(payload.dict()),
            is_json=False,
        )
        return resp

    async def upscale(
        self,
        msg_id: str,
        index: int,
        msg_hash: str,
    ):
        print("upscaling-->", msg_id, index, msg_hash)
        kwargs = {
            "message_flags": 0,
            "message_id": msg_id,
        }
        payload = DiscordPayload(
            type=DiscordType.UPSCALE.value,
            nonce=randome_nonce(),
            data={
                "component_type": 2,
                "custom_id": f"MJ::JOB::upsample::{index}::{msg_hash}",
            },
        ).dict()
        payload.update(kwargs)
        return await self.request(
            url=self.TRIGGER_URL, data=json.dumps(payload), is_json=False
        )

    async def variation(self, msg_id: str, index: int, msg_hash: str):
        kwargs = {
            "message_flags": 0,
            "message_id": msg_id,
        }
        payload = DiscordPayload(
            type=DiscordType.VARIATION.value,
            nonce=randome_nonce(),
            data={
                "component_type": 2,
                "custom_id": f"MJ::JOB::variation::{index}::{msg_hash}",
            },
        ).dict()
        payload.update(kwargs)
        await self.request(url=self.TRIGGER_URL, data=payload)

    async def reset(self, msg_id: str, msg_hash: str):
        kwargs = {
            "message_flags": 0,
            "message_id": msg_id,
        }
        payload = DiscordPayload(
            type=DiscordType.RESET.value,
            nonce=randome_nonce(),
            data={
                "component_type": 2,
                "custom_id": f"MJ::JOB::reroll::0::{msg_hash}::SOLO",
            },
        ).dict()
        payload.update(kwargs)
        await self.request(url=self.TRIGGER_URL, data=payload)

    async def describe(
        self, file_size: int, file_type: str, image_bytes: bytes
    ):
        filename, upload_filename = await self.presigned_upload(
            file_size, file_type, image_bytes
        )
        payload = DiscordPayload(
            type=DiscordType.DESCRIBE.value,
            nonce=randome_nonce(),
            data={
                "version": "1118961510123847774",
                "id": "938956540159881230",
                "name": "describe",
                "type": 1,
                "options": [{"type": 11, "name": "image", "value": 0}],
                "application_command": {
                    "id": "1092492867185950852",
                    "application_id": settings.DISCORD_APPLICATION_ID,
                    "version": "1118961510123847774",
                    "default_member_permissions": None,
                    "type": 1,
                    "nsfw": False,
                    "name": "describe",
                    "description": "Writes a prompt based on your image.",
                    "dm_permission": True,
                    "contexts": [0, 1, 2],
                    "options": [
                        {
                            "type": 11,
                            "name": "image",
                            "description": "The image to describe",
                            "required": True,
                        }
                    ],
                },
                "attachments": [
                    {
                        "id": "0",
                        "filename": filename,
                        "uploaded_filename": upload_filename,
                    }
                ],
            },
        )
        resp = await self.request(url=self.TRIGGER_URL, data=payload.dict())
        return resp
        ...

    async def blend(
        self,
        file_size: int,
        file_type: str,
        image_bytes: bytes,
        file_size2: int,
        file_type2: str,
        image_bytes2: bytes,
    ):
        filename, upload_filename = await self.presigned_upload(
            file_size, file_type, image_bytes
        )
        filename2, upload_filename2 = await self.presigned_upload(
            file_size2, file_type2, image_bytes2
        )
        payload = DiscordPayload(
            type=DiscordType.BLEND.value,
            nonce=randome_nonce(),
            data={
                "version": "1118961510123847773",
                "id": "1062880104792997970",
                "name": "blend",
                "type": 1,
                "options": [
                    {"type": 11, "name": "image1", "value": 0},
                    {"type": 11, "name": "image2", "value": 1},
                ],
                "application_command": {
                    "id": "1062880104792997970",
                    "application_id": settings.DISCORD_APPLICATION_ID,
                    "version": "1118961510123847773",
                    "default_member_permissions": None,
                    "type": 1,
                    "nsfw": False,
                    "name": "blend",
                    "description": "Blend images together seamlessly!",
                    "dm_permission": True,
                    "contexts": [0, 1, 2],
                    "options": [
                        {
                            "type": 11,
                            "name": "image1",
                            "description": "First image to add to the blend",
                            "required": True,
                        },
                        {
                            "type": 11,
                            "name": "image2",
                            "description": "Second image to add to the blend",
                            "required": True,
                        },
                        {
                            "type": 3,
                            "name": "dimensions",
                            "description": "The dimensions of the image. If not specified, the image will be square.",
                            "choices": [
                                {"name": "Portrait", "value": "--ar 2:3"},
                                {"name": "Square", "value": "--ar 1:1"},
                                {"name": "Landscape", "value": "--ar 3:2"},
                            ],
                        },
                        {
                            "type": 11,
                            "name": "image3",
                            "description": "Third image to add to the blend (optional)",
                        },
                        {
                            "type": 11,
                            "name": "image4",
                            "description": "Fourth image to add to the blend (optional)",
                        },
                        {
                            "type": 11,
                            "name": "image5",
                            "description": "Fifth image to add to the blend (optional)",
                        },
                    ],
                },
                "attachments": [
                    {
                        "id": "0",
                        "filename": filename,
                        "uploaded_filename": upload_filename,
                    },
                    {
                        "id": "1",
                        "filename": filename2,
                        "uploaded_filename": upload_filename2,
                    },
                ],
            },
        ).dict()
        await self.request(self.TRIGGER_URL, data=payload)


discord_service = DiscordService()
