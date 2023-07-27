import asyncio
import json
from typing import Dict, Optional

import redis

from app.config import settings
from app.errors import TaskQueueBizError
from app.trigger.enums import TaskStatus
from app.trigger.schemas.task import Task
from app.trigger.services.discord import discord_service
from app.trigger.services.notify import notify_service
from app.trigger.services.store import task_store_service
from app.utils.exception import APPException
from app.utils.logger import setup_logger

logger = setup_logger("TaskQueueService")


class SharedQueue:
    def __init__(self, name: str = "waiting"):
        self.redis_client = redis.Redis(
            settings.REDIS_HOST, settings.REDIS_PORT, db=1
        )
        self.name = name

    def push(self, item: Dict):
        self.redis_client.rpush(
            self.name, json.dumps(item, ensure_ascii=False)
        )

    def pop(self):
        data = self.redis_client.lpop(self.name)
        if data and isinstance(data, bytes):
            return json.loads(data.decode("utf-8"))
        return None

    def size(self):
        return self.redis_client.llen(self.name)


class SharedList:
    def __init__(self, name: str = "running"):
        self.redis_client = redis.Redis(
            settings.REDIS_HOST, settings.REDIS_PORT, db=1
        )
        self.name = name

    def add(self, task_id: str):
        self.redis_client.lpush(self.name, task_id)

    def remove(self, task_id: str):
        self.redis_client.lrem(self.name, 0, task_id.encode("utf-8"))

    def find_all(self):
        return self.redis_client.lrange(self.name, 0, -1)

    def find_one(self, task_id: str):
        task_ids = [
            task_id.decode("utf-8")
            for task_id in self.redis_client.lrange(self.name, 0, -1)
        ]
        if task_id in task_ids:
            return task_store_service.get(task_id)
        return None

    def size(self):
        return self.redis_client.llen(self.name)


class TaskQueueService:
    def __init__(
        self,
        concurrency_size: int = settings.TASK_QUEUE_CONCURRENCY_SIZE,
        wait_size: int = settings.TASK_QUEUE_WAIT_SIZE,
    ):
        self.concurrency_size = concurrency_size
        self.wait_size = wait_size

        self.running_tasks: SharedList = SharedList("running_tasks")
        self.waiting_tasks: SharedQueue = SharedQueue("waiting_tasks")

    def get_running_task(self, task_id: str) -> Optional[Task]:
        return self.running_tasks.find_one(task_id)

    def submit_task(
        self,
        task: Task,
        callback: str,
        params: Dict,
    ):
        task_store_service.save(task)
        if self.waiting_tasks.size() >= self.wait_size:
            raise APPException(TaskQueueBizError.QUEUE_FULL)
        self.waiting_tasks.push(
            {
                "task_id": task.id,
                "callback": callback,
                "params": params,
            }
        )
        self.execute_task()
        return task

    def execute_task(self):
        if (
            self.waiting_tasks.size()
            and self.running_tasks.size() < self.concurrency_size
        ):
            item = self.waiting_tasks.pop()
            if item:
                task_id = item.get("task_id")
                task = task_store_service.get(task_id)
                self._execute(task, item)

    def _execute(self, task: Task, item: Dict):
        self.running_tasks.add(task.id)
        task.start()
        task_store_service.save(task)

        callback = getattr(discord_service, item.get("callback"))
        if callback:
            loop = asyncio.get_running_loop()
            loop.create_task(callback(**item.get("params")))

    def change_status_and_notify(self, task: Task, status: TaskStatus) -> None:
        task.set_status(status)
        task_store_service.save(task)
        notify_service.notify_task_change(task)


task_queue_service = TaskQueueService()
