import os
import secrets
from typing import List

from pydantic import AnyHttpUrl, BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str
    SERVER_HOST: str
    SERVER_PORT: int
    API_V1_STR: str = "/api/v1"
    TOKEN_URL: str = "/auth/token"
    DEBUG: bool = False
    DEBUG_sql: bool = False
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 40  # 40 hours
    APP_SECRET_KEY: str = secrets.token_urlsafe(32)
    APP_API_KEY: str = secrets.token_urlsafe(32)
    BASE_DIR: str = os.path.dirname(os.path.dirname(__file__))
    DATABASE_URL: str

    # redis
    REDIS_BROKER: str
    REDIS_BACKEND: str
    REDIS_TESTING: bool
    REDIS_URL: str
    REDIS_HOST: str
    REDIS_PORT: str
    APP_CACHE_EXPIRE_IN_SECONDS: int = 3600

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # tasks
    TASK_TYPES_WHITELIST: List[int] = [3]
    RETRY_INTERVAL_SECONDS: int = 15

    # apps
    APPLICATION_MODULES: List[str] = [
        "app.auth.models.user",
    ]

    # discord
    DISCORD_USER_TOKEN: str
    DISCORD_BOT_TOKEN: str
    DISCORD_GUILD_ID: str
    DISCORD_CHANNEL_ID: str
    DISCORD_APPLICATION_ID: str
    DISCORD_SESSION_ID: str

    NOTIFY_HOOK: AnyHttpUrl

    # baidu-translate
    BAIDU_APPID: str
    BAIDU_APPKEY: str

    # task queue
    TASK_QUEUE_CONCURRENCY_SIZE: int = 3
    TASK_QUEUE_WAIT_SIZE: int = 10


settings = Settings(_env_file=".env")  # type: ignore
