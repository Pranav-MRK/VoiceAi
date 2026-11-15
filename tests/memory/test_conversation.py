
import uuid

import pytest
from sqlalchemy import select

from app.db.postgres import Base, engine, AsyncSessionLocal
from app.db.redis import redis_client
from app.memory.models import Call, ConversationMessage
from app.memory import conversation


class MockWorkflow:
    def __init__(self):
        self.received_states = []

    async def ainvoke(self, state):
        self.received_states.append(state)

        return {
            "answer": f"Mock answer {len(self.received_states)}",
            "sources": [],
        }

class MockFAQCache:
    async def get(self, question, language="en"):
        return None

    async def set(
        self,
        question,
        answer,
        language="en",
        sources=None,
    ):
        pass

@pytest.mark.asyncio
async def test_multi_turn_conversation(monkeypatch):
    # Create database tables
  
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    call_id = f"test-{uuid.uuid4()}"
    mock_workflow = MockWorkflow()

    monkeypatch.setattr(
        conversation,
        "rag_workflow",
        mock_workflow,
    )
    monkeypatch.setattr(
        conversation,
        "faq_cache",
        MockFAQCache(),
    )

    async with AsyncSessionLocal() as db:
        try:
            # Start a new call
            await conversation.memory_manager.start_call(
                db=db,
                call_id=call_id,
                language="en",
            )

            # First question
            first = await conversation.process_message(
                db=db,
                call_id=call_id,
                query="What documents are required for B.Tech admission?",
            )

            assert first["answer"] == "Mock answer 1"

            # Second question
            second = await conversation.process_message(
                db=db,
                call_id=call_id,
                query="What about scholarship documents?",
            )

            assert second["answer"] == "Mock answer 2"

            # Verify second turn received previous conversation
            second_history = mock_workflow.received_states[1]["messages"]

            assert len(second_history) == 3
            assert second_history[0].content == (
                "What documents are required for B.Tech admission?"
            )
            assert second_history[1].content == "Mock answer 1"
            assert second_history[2].content == (
                "What about scholarship documents?"
            )

            # Verify Redis contains all four messages
            redis_messages = (
                await conversation.memory_manager.redis.get_messages(call_id)
            )
            assert len(redis_messages) == 4

            # Verify PostgreSQL contains all four messages
            result = await db.execute(
                select(ConversationMessage)
                .where(ConversationMessage.call_id == call_id)
                .order_by(ConversationMessage.id)
            )
            db_messages = result.scalars().all()

            assert len(db_messages) == 4

            print("\nMulti-turn memory test passed!")

        finally:
            await conversation.memory_manager.redis.clear_memory(call_id)

            call = await db.get(Call, call_id)
            if call:
                await db.delete(call)
                await db.commit()
