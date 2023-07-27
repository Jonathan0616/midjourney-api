import os

from app.config import settings


class MidjourneyService:
    BANNED_WORDS_FILE_PATH = os.path.join(
        settings.BASE_DIR, "templates", "banned-words.txt"
    )

    def __init__(self):
        self.banned_words = []
        print(
            "Loading banned words...", MidjourneyService.BANNED_WORDS_FILE_PATH
        )
        with open(MidjourneyService.BANNED_WORDS_FILE_PATH, "r") as f:
            self.banned_words += f.read().splitlines()

    def is_banned(self, prompt_en: str):
        exist = False
        prompt_en = prompt_en.lower()
        for word in self.banned_words:
            if word in prompt_en:
                exist = True
                break
        return exist


midjourney_service = MidjourneyService()
