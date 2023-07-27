import re
from enum import Enum
from typing import Dict, Optional

import discord
from discord.ext import commands

from app.config import settings
from app.trigger.enums import TaskStatus
from app.trigger.schemas.task import Task
from app.trigger.services.queue import task_queue_service
from app.trigger.services.store import task_store_service

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="", intents=intents)


def extract_trigger_id(content):
    pattern = r"<#(\w+?)#>"
    match = re.findall(pattern, content)
    return match[0] if match else None


class DiscordBotClient(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")

    async def handle(
        self, task: Task, properties: Optional[Dict], task_status: str
    ):
        if task_status == TaskStatus.SUCCESS.value:
            task.success()
            task_queue_service.running_tasks.remove(task.id)
            task_queue_service.execute_task()
        else:
            task.status = task_status
        task.properties = properties
        task_store_service.save(task)

    async def on_message(self, message: discord.Message):
        content = message.content
        task_id, process = self.parse(content)
        task = (
            task_queue_service.get_running_task(task_id) if task_id else None
        )
        if not task_id or not task:
            return

        msg_id = message.id
        properties = dict(
            msg_id=str(msg_id),
            msg_hash="",
            attachment="",
        )
        if "Waiting to start" in content:
            task_status = TaskStatus.IN_PROGRESS.value
        else:
            attachments = message.attachments
            if attachments:
                properties["msg_hash"] = (
                    attachments[0].filename.split("_")[-1].split(".")[0]
                )
                properties["attachment"] = attachments[0].url
                task_status = TaskStatus.SUCCESS.value
        await self.handle(task, properties, task_status)

    async def on_message_edit(
        self, before: discord.Message, after: discord.Message
    ):
        content = after.content
        task_id, process = self.parse(content, listen="on_message_edit")
        task = (
            task_queue_service.get_running_task(task_id) if task_id else None
        )
        if not task_id or not process or not task:
            return
        task.process = process + "%"
        await self.handle(
            task,
            properties=task.properties,
            task_status=TaskStatus.IN_PROGRESS.value,
        )

    def parse(self, content: str, listen: str = "on_message"):
        task_id = process = None
        if listen == "on_message":
            match = re.search(r"<#(.*?)#>", content)
            if match:
                task_id = match.group(1)
        else:
            match = re.search(r"<#(.*?)#>.*?\((\d+)%\)", content)
            if match:
                task_id, process = match.group(1), match.group(2)
        return task_id, process


intents = discord.Intents.default()
intents.message_content = True

client = DiscordBotClient(intents=intents)

if __name__ == "__main__":
    client.run(settings.DISCORD_BOT_TOKEN)
