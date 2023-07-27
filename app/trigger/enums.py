from enum import Enum, IntEnum, StrEnum


class TaskAction(StrEnum):
    IMAGINE = "imagine"
    UPSCALE = "upscale"
    VARIATION = "variation"
    RESET = "reset"
    DESCRIBE = "describe"
    BLEND = "blend"


class TaskStatus(StrEnum):
    NOT_START = "not_start"
    SUBMITTED = "submitted"
    IN_PROGRESS = "in_progress"
    FAILURE = "failure"
    SUCCESS = "success"


class ScaleCategory(Enum):
    SCALE_1_1 = "1:1"
    SCALE_16_9 = "16:9"
    SCALE_9_16 = "9:16"
    SCALE_4_3 = "4:3"
    SCALE_3_4 = "3:4"

    @classmethod
    def get_names(cls):
        return [i.name for i in cls]

    @classmethod
    def get_value(cls, name: str):
        for i in cls:
            if i.name == name:
                return i.value
        return None


class TriggerType(IntEnum):
    IMAGINE = 2
    UPSCALE = 3
    VARIATION = 3
    RESET = 3
