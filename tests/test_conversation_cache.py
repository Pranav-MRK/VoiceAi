
import pytest
from unittest.mock import AsyncMock, patch

from app.memory.conversation import process_message


@pytest.mark.asyncio
async def test_conversation_cache():
    mock_db = AsyncMock()

    call_id = "cache-test-call-001"
    question = "What is the admission process?"

    fake_result = {
        "answer": "Apply through the college admission portal.",
        "sources": ["btech_admission.txt"],
    }

    with (
        patch(
            "app.memory.conversation.memory_manager.add_message",
            new_callable=AsyncMock,
        ),
        patch(
            "app.memory.conversation.memory_manager.get_conversation",
            new_callable=AsyncMock,
            return_value=[],
        ),
        patch(
            "app.memory.conversation.rag_workflow.ainvoke",
            new_callable=AsyncMock,
            return_value=fake_result,
        ) as mock_rag,
        patch(
            "app.memory.conversation.faq_cache.get",
            new_callable=AsyncMock,
            side_effect=[None, {
                "answer": fake_result["answer"],
                "sources": fake_result["sources"],
            }],
        ) as mock_cache_get,
        patch(
            "app.memory.conversation.faq_cache.set",
            new_callable=AsyncMock,
        ) as mock_cache_set,
    ):
        # First question: cache miss
        first = await process_message(
            db=mock_db,
            call_id=call_id,
            query=question,
        )

        # Second question: cache hit
        second = await process_message(
            db=mock_db,
            call_id=call_id,
            query=question,
        )

        assert first["answer"] == second["answer"]
        assert first["cache_hit"] is False
        assert second["cache_hit"] is True

        # RAG must execute only once
        assert mock_rag.await_count == 1

        # Cache must be populated only after the miss
        mock_cache_set.assert_awaited_once()

        assert mock_cache_get.await_count == 2

    print("Conversation cache integration test passed!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_conversation_cache())
