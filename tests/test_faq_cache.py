
import uuid
import pytest

from app.memory.faq_cache import FAQCache


@pytest.mark.asyncio
async def test_faq_cache():
    cache = FAQCache(ttl=60)

    # Unique question prevents collisions with existing Redis data.
    question = f"What is the admission process? {uuid.uuid4()}"
    answer = "Students can apply through the admission portal."

    # First lookup should be a cache miss.
    result = await cache.get(question, "en")
    assert result is None

    # Store answer.
    await cache.set(
        question=question,
        answer=answer,
        language="en",
        sources=["btech_admission.txt"],
    )

    # Second lookup should be a cache hit.
    result = await cache.get(question, "en")

    assert result is not None
    assert result["answer"] == answer
    assert result["sources"] == ["btech_admission.txt"]

    # Normalized question should hit the same key.
    result = await cache.get(
        question.upper(),
        "en",
    )

    assert result is not None
    assert result["answer"] == answer

    # Different language should miss.
    result = await cache.get(question, "hi")
    assert result is None

    print("FAQ cache test passed!")
