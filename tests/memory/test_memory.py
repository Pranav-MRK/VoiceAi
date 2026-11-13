
import uuid
import pytest

from sqlalchemy import select

from app.db.postgres import (
    engine,
    AsyncSessionLocal,
    Base,
)
from app.memory.models import Call, ConversationMessage
from app.memory.manager import MemoryManager


@pytest.mark.asyncio
async def test_memory_lifecycle():

    memory = MemoryManager()
    call_id = f"test-{uuid.uuid4()}"

    # Clear pooled connections from previous test event loops

    # Create database tables for this initial integration test.
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:

        # 1. Start call
        await memory.start_call(
            db=db,
            call_id=call_id,
            language="en",
        )

        # 2. Save conversation
        await memory.add_message(
            db=db,
            call_id=call_id,
            role="user",
            content="What documents are required for B.Tech?",
        )

        await memory.add_message(
            db=db,
            call_id=call_id,
            role="assistant",
            content="You need your identity proof and marksheets.",
        )

        # 3. Retrieve active conversation from Redis
        messages = await memory.get_conversation(db, call_id)

        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "assistant"

        # 4. End call and clear Redis
        await memory.end_call(db, call_id)

        redis_messages = await memory.redis.get_messages(call_id)

        assert redis_messages == []

        # 5. Recover conversation from PostgreSQL
        history = await memory.get_conversation(db, call_id)

        assert len(history) == 2
        assert history[0]["content"] == (
            "What documents are required for B.Tech?"
        )

        # Verify call status
        result = await db.execute(
            select(Call).where(Call.call_id == call_id)
        )
        call = result.scalar_one()

        assert call.status == "completed"
        assert call.ended_at is not None

        # Verify permanent message records
        result = await db.execute(
            select(ConversationMessage).where(
                ConversationMessage.call_id == call_id
            )
        )

        assert len(result.scalars().all()) == 2

    # Clean up test data
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Call).where(Call.call_id == call_id)
        )
        call = result.scalar_one()
        await db.delete(call)
        await db.commit()
