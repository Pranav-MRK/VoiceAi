
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.models import Call, ConversationMessage


class PostgresMemory:

    async def create_call(
        self,
        db: AsyncSession,
        call_id: str,
        language: str = "en",
    ):
        call = Call(
            call_id=call_id,
            language=language,
            status="active",
        )

        db.add(call)
        await db.commit()

        return call

    async def add_message(
        self,
        db: AsyncSession,
        call_id: str,
        role: str,
        content: str,
    ):
        message = ConversationMessage(
            call_id=call_id,
            role=role,
            content=content,
        )

        db.add(message)
        await db.commit()

        return message

    async def get_messages(
        self,
        db: AsyncSession,
        call_id: str,
    ):
        result = await db.execute(
            select(ConversationMessage)
            .where(ConversationMessage.call_id == call_id)
            .order_by(ConversationMessage.created_at)
        )

        return result.scalars().all()

    async def end_call(
        self,
        db: AsyncSession,
        call_id: str,
    ):
        result = await db.execute(
            select(Call).where(Call.call_id == call_id)
        )

        call = result.scalar_one_or_none()

        if call:
            from datetime import datetime, timezone

            call.status = "completed"
            call.ended_at = datetime.now(timezone.utc)

            await db.commit()
