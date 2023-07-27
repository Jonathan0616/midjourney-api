import time

from app.errors import TriggerBizError
from app.trigger.schemas.task import Task
from app.trigger.services.store import task_store_service
from app.utils.exception import APPException


class TaskService:
    @classmethod
    def add(
        cls,
        task_id: str,
        action: str,
        prompt: str = None,
        prompt_en: str = None,
        notify_hook: str = None,
    ):
        return Task(
            id=task_id,
            prompt=prompt,
            prompt_en=prompt_en,
            action=action,
            submit_time=int(round(time.time() * 1000)),
            notify_hook=notify_hook,
        )

    @classmethod
    def details(
        cls,
        task_id: str,
    ):
        task = task_store_service.get(task_id)
        if not task:
            raise APPException(TriggerBizError.TASK_NOT_FOUNT)
        return task


task_service = TaskService()
