
import json
import hashlib
import re

from app.db.redis import redis_client


class FAQCache:

    def __init__(self, ttl: int = 3600):
        self.ttl = ttl

    def _normalize(self, question: str) -> str:
        question = question.lower().strip()
        question = re.sub(r"[^\w\s]", "", question)
        question = re.sub(r"\s+", " ", question)
        return question

    def _key(self, question: str, language: str) -> str:
        normalized = self._normalize(question)

        question_hash = hashlib.sha256(
            normalized.encode("utf-8")
        ).hexdigest()

        return f"samvadai:faq:{language}:{question_hash}"

    async def get(
        self,
        question: str,
        language: str = "en",
    ) -> dict | None:

        key = self._key(question, language)

        cached = await redis_client.get(key)

        if cached is None:
            return None

        return json.loads(cached)

    async def set(
        self,
        question: str,
        answer: str,
        language: str = "en",
        sources: list | None = None,
    ):

        key = self._key(question, language)

        value = {
            "answer": answer,
            "sources": sources or [],
        }

        await redis_client.set(
            key,
            json.dumps(value),
            ex=self.ttl,
        )
