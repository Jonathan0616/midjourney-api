import concurrent.futures


class ThreadPoolTaskExecutor:
    def __init__(self, max_workers=5, thread_name_prefix="TaskQueue-"):
        print(f"ThreadPoolTaskExecutor init, max_workers: {max_workers}")
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix=thread_name_prefix,
        )

    def submit_task(self, task_func, *args, **kwargs):
        return self.executor.submit(task_func, *args, **kwargs)

    def shutdown(self, wait=True):
        self.executor.shutdown(wait=wait)

    def work_qsize(self):
        return self.executor._work_queue.qsize()
