import random
import re
from hashlib import md5

import aiohttp

from app.config import settings
from app.errors import TranslateBizError
from app.utils.exception import APPException
from app.utils.http import fetch


class TranslateService:
    TRANSLATE_URL = "https://fanyi-api.baidu.com/api/trans/vip/translate"

    @classmethod
    def make_md5(cls, s, encoding="utf-8"):
        return md5(s.encode(encoding)).hexdigest()

    @classmethod
    def containsChinese(cls, promt: str):
        pattern = re.compile(r"[\u4e00-\u9fa5]")
        return bool(pattern.search(promt))

    @classmethod
    async def translate_to_en(cls, prompt: str):
        if not cls.containsChinese(prompt):
            return prompt
        prompt_en = ""
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        ) as session:
            salt = str(random.randint(32768, 65536))
            sign = cls.make_md5(
                settings.BAIDU_APPID + prompt + salt + settings.BAIDU_APPKEY
            )
            payload = {
                "appid": settings.BAIDU_APPID,
                "q": prompt,
                "from": "zh",
                "to": "en",
                "salt": salt,
                "sign": sign,
            }

            result = await fetch(
                session,
                cls.TRANSLATE_URL,
                params=payload,
            )
            if result.get("error_code"):
                raise APPException(TranslateBizError.TRANSLATE_FAIL)
            prompt_en = result["trans_result"][0]["dst"]
        return prompt_en


translate_service = TranslateService()
