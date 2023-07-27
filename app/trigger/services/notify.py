import json
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from functools import partial

import requests

from app.trigger.schemas.task import Task


class NotifyService:
    def __init__(self, max_workers: int = 5):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.task_locks = {}
        self.locks_cleanup_interval = timedelta(hours=1)

    def _cleanup_task_lock(self, task_id):
        self.task_locks.pop(task_id, None)

    def notify_task_change(self, task: Task) -> None:
        notify_hook = task.notify_hook
        if not notify_hook:
            return

        task_id = task.id
        task_lock = self.task_locks.setdefault(task_id, threading.Lock())

        try:
            params_str = json.dumps(task.dict())
            post_request = partial(self._post_json, notify_hook, params_str)
            future = self.executor.submit(
                self._execute_post_request,
                task_lock,
                post_request,
            )

            # Use add_done_callback to clean up the task_lock after the task is completed
            future.add_done_callback(
                lambda f: self.task_locks.pop(task_id, None)
            )
        except json.JSONDecodeError as e:
            logging.warn(f"Failed to convert task to JSON: {e}")
        except Exception as e:
            logging.warn(f"Failed to notify task change: {e}")

    def _execute_post_request(
        self, task_lock: threading.Lock, post_request: callable
    ):
        with task_lock:
            try:
                response = post_request()
                if response.status_code == requests.codes.OK:
                    logging.debug(
                        f"Task change notification successful, status: {response.status_code}, URL: {response.url}"
                    )
                else:
                    logging.warning(
                        f"Task change notification failed, status: {response.status_code}, URL: {response.url}"
                    )
            except requests.RequestException as e:
                logging.warning(f"Task change notification failed: {e}")

    def _post_json(
        self, notify_hook: str, params_json: str
    ) -> requests.Response:
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            notify_hook, headers=headers, data=params_json
        )
        return response


notify_service = NotifyService()
