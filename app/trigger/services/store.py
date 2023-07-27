import json
from abc import ABC, abstractmethod

import redis

from app.config import settings
from app.trigger.schemas.task import Task


class TaskStoreAbstract(ABC):
    @abstractmethod
    def save(task: Task):
        pass

    @abstractmethod
    def delete(task_id: str):
        pass

    @abstractmethod
    def get(task_id: str):
        pass

    # @abstractmethod
    # def find_all():
    #     pass

    # @abstractmethod
    # def find_one(condition):
    #     pass


class RedisTaskStoreService(TaskStoreAbstract):
    KEY_PREFIX = "mj-task:"

    def __init__(
        self,
        timeout: int = 60 * 60 * 24 * 7,
        redis_url: str = "redis://localhost:6379/0",
    ):
        self.timeout = timeout
        self.redis_client = redis.Redis.from_url(redis_url)

    def save(self, task: Task):
        self.redis_client.set(
            self.KEY_PREFIX + task.id, task.json(), ex=self.timeout
        )

    def delete(self, task_id: str):
        self.redis_client.delete(self.KEY_PREFIX + task_id)

    def get(self, task_id: str):
        res = self.redis_client.get(self.KEY_PREFIX + task_id)
        if res:
            data = json.loads(res)
            return Task(**data)
        return None

    def find_all(self):
        pass

    def find_one(self):
        pass


task_store_service = RedisTaskStoreService(redis_url=settings.REDIS_URL)
