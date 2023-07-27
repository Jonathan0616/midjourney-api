from enum import IntEnum


class UserBizError(IntEnum):
    USER_NOT_FOUND = 11001


class TriggerBizError(IntEnum):
    NOT_SUPPORT_FILE_TYPE = 21001
    TASK_NOT_FOUNT = 21002


class DiscordBizError(IntEnum):
    UPLOAD_ATTACHMENT_ERR = 31001
    BANNED_WORDS = 31002


class TranslateBizError(IntEnum):
    TRANSLATE_INVALID = 41001


class TaskQueueBizError(IntEnum):
    QUEUE_FILL = 51001
    SUBMIT_TASK_ERR = 51002


class ServiceError(IntEnum):
    SERVICE_ERROR = 61001
