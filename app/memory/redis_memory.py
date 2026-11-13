
import json

from app.db.redis import redis_client


class RedisMemory:

    def __init__(self, ttl: int = 3600, max_messages: int = 30):
        self.ttl = ttl
        self.max_messages = max_messages

    def _key(self, call_id: str) -> str:
        return f"samvadai:call:{call_id}:messages"

    async def add_message(
        self,
        call_id: str,
        role: str,
        content: str,
    ):
        message = {
            "role": role,
            "content": content,
        }

        key = self._key(call_id)

        async with redis_client.pipeline(transaction=True) as pipe:
            pipe.rpush(key, json.dumps(message))
            pipe.ltrim(key, -self.max_messages, -1)
            pipe.expire(key, self.ttl)
            await pipe.execute()

    async def get_messages(self, call_id: str) -> list[dict]:
        key = self._key(call_id)

        messages = await redis_client.lrange(key, 0, -1)

        return [
            json.loads(message)
            for message in messages
        ]

    async def clear_memory(self, call_id: str):
        await redis_client.delete(self._key(call_id))
