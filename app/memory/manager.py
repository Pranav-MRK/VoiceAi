
from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.redis_memory import RedisMemory
from app.memory.postgres_memory import PostgresMemory


class MemoryManager:

    def __init__(self):
        self.redis = RedisMemory()
        self.postgres = PostgresMemory()

    async def start_call(
        self,
        db: AsyncSession,
        call_id: str,
        language: str = "en",
    ):
        return await self.postgres.create_call(
            db=db,
            call_id=call_id,
            language=language,
        )

    async def add_message(
        self,
        db: AsyncSession,
        call_id: str,
        role: str,
        content: str,
    ):
        # PostgreSQL is the source of truth.
        await self.postgres.add_message(
            db=db,
            call_id=call_id,
            role=role,
            content=content,
        )

        # Redis maintains active conversation context.
        await self.redis.add_message(
            call_id=call_id,
            role=role,
            content=content,
        )

    async def get_conversation(
        self,
        db: AsyncSession,
        call_id: str,
    ) -> list[dict]:

        messages = await self.redis.get_messages(call_id)

        if messages:
            return messages

        # Fallback to PostgreSQL if Redis has expired.
        db_messages = await self.postgres.get_messages(
            db=db,
            call_id=call_id,
        )

        return [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in db_messages
        ]

    async def end_call(
        self,
        db: AsyncSession,
        call_id: str,
    ):
        await self.postgres.end_call(
            db=db,
            call_id=call_id,
        )

        await self.redis.clear_memory(call_id)
