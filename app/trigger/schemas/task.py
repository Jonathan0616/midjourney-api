import time
from typing import Any, Optional

from pydantic import Field

from app.trigger.enums import TaskAction, TaskStatus
from app.utils.schema import BaseModel


class Task(BaseModel):
    id: str
    prompt: Optional[str] = Field(description="prompt")
    prompt_en: Optional[str] = Field(description="prompt_en")
    action: TaskAction
    notify_hook: Optional[str]

    # use timestamp to record time
    submit_time: int
    start_time: int = Field(default=0)
    finish_time: int = Field(default=0)
    status: TaskStatus = Field(default=TaskStatus.NOT_START.value)
    process: str = Field(default="0%")
    fail_reason: Optional[str]
    description: Optional[str]

    # support scale
    properties: Any = Field(default={})

    def set_status(self, status: str):
        self.status = status

    def set_description(self, description: str):
        self.description = description

    def start(self):
        self.start_time = int(round(time.time() * 1000))
        self.status = TaskStatus.SUBMITTED.value
        self.process = "0%"

    def success(self):
        self.finish_time = int(round(time.time() * 1000))
        self.status = TaskStatus.SUCCESS.value
        self.process = "100%"

    def fail(self, reason: str):
        self.finish_time = int(round(time.time() * 1000))
        self.status = TaskStatus.FAILURE.value
        self.fail_reason = reason
        self.process = ""

    def sleep(self):
        with self._lock:
            self._lock.wait()

    def awake(self):
        with self._lock:
            self._lock.notify_all()
