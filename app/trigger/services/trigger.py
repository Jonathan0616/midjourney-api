import json
import random
import uuid

from app.errors import DiscordBizError
from app.trigger.enums import TaskAction
from app.trigger.schemas.trigger import (
    BlendRequest,
    DescribeRequest,
    ImagineRequest,
    ResetRequest,
    UploadResponse,
    UpscaleRequest,
    VariationRequest,
)
from app.trigger.services.discord import discord_service
from app.trigger.services.midjourney import midjourney_service
from app.trigger.services.queue import task_queue_service
from app.trigger.services.task import task_service
from app.trigger.services.translate import translate_service
from app.utils.exception import APPException


class TriggerService:
    @staticmethod
    def generate_task_id():
        return uuid.uuid4().hex[:19]

    @staticmethod
    def wrapper_prompt(
        task_id: str,
        prompt: str,
        file_url: str = None,
    ):
        return f"{file_url + ' ' if file_url else ''}<#{task_id}#>{prompt}"

    async def upload(self, file_size: int, file_type: str, image_bytes: bytes):
        task_id = self.generate_task_id()
        upload_img = await discord_service.upload(
            file_size, file_type, image_bytes
        )
        return UploadResponse(
            task_id=task_id,
            **upload_img.dict(),
        )

    async def imagine(self, obj_in: ImagineRequest):
        prompt_en = await translate_service.translate_to_en(obj_in.prompt)
        if midjourney_service.is_banned(prompt_en):
            raise APPException(DiscordBizError.BANNED_WORDS)

        task_id = self.generate_task_id()
        task = task_service.add(
            task_id=task_id,
            action=TaskAction.IMAGINE.value,
            prompt=self.wrapper_prompt(task_id, obj_in.prompt, obj_in.img_url),
            prompt_en=self.wrapper_prompt(task_id, prompt_en, obj_in.img_url),
            notify_hook=obj_in.notify_hook,
        )

        return task_queue_service.submit_task(
            task,
            "imagine",
            dict(prompt=task.prompt_en),
        )

    async def upscale(self, obj_in: UpscaleRequest):
        task_id = self.generate_task_id()
        task = task_service.add(
            task_id=task_id,
            action=TaskAction.UPSCALE.value,
        )

        return task_queue_service.submit_task(
            task,
            "upscale",
            dict(
                msg_id=obj_in.msg_id,
                index=obj_in.index,
                msg_hash=obj_in.msg_hash,
            ),
        )

    async def variation(self, obj_in: VariationRequest):
        task_id = self.generate_task_id()
        task = task_service.add(
            task_id=task_id,
            action=TaskAction.VARIATION.value,
        )

        return task_queue_service.submit_task(
            task,
            "variation",
            dict(
                msg_id=obj_in.msg_id,
                index=obj_in.index,
                msg_hash=obj_in.msg_hash,
            ),
        )

    async def reset(self, obj_in: ResetRequest):
        task_id = self.generate_task_id()
        task = task_service.add(
            task_id=task_id,
            action=TaskAction.RESET.value,
        )

        return task_queue_service.submit_task(
            task,
            "reset",
            dict(
                msg_id=obj_in.msg_id,
                msg_hash=obj_in.msg_hash,
            ),
        )

    async def describe(self, obj_in: DescribeRequest):
        task_id = self.generate_task_id()
        task = task_service.add(
            task_id=task_id,
            action=TaskAction.DESCRIBE.value,
        )

        return task_queue_service.submit_task(
            task,
            "describe",
            dict(
                file_size=obj_in.file_size,
                file_type=obj_in.file_type,
                image_bytes=obj_in.image_bytes,
            ),
        )

    async def blend(self, obj_in: BlendRequest):
        task_id = self.generate_task_id()
        task = task_service.add(
            task_id=task_id,
            action=TaskAction.BLEND.value,
        )

        return task_queue_service.submit_task(
            task,
            "blend",
            dict(
                file_size=obj_in.file_size,
                file_type=obj_in.file_type,
                image_bytes=obj_in.image_bytes,
                file_size2=obj_in.file_size2,
                file_type2=obj_in.file_type2,
                image_bytes2=obj_in.image_bytes2,
            ),
        )


trigger_service = TriggerService()
