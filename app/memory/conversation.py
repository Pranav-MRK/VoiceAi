
import logging

logger = logging.getLogger("samvadai.cache")
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.messages import (
    AIMessage,
    AnyMessage,
    HumanMessage,
)

from app.rag.graph.state import SamvadState
from app.memory.manager import MemoryManager
from app.memory.faq_cache import FAQCache
from app.rag.graph.workflow import rag_workflow


memory_manager = MemoryManager()
faq_cache = FAQCache()


async def process_message(
    db: AsyncSession,
    call_id: str,
    query: str,
    language: str = "en",
):
    # 1. Save the caller's message
    await memory_manager.add_message(
        db=db,
        call_id=call_id,
        role="user",
        content=query,
    )

    # 2. Check the FAQ cache
    cached_result = await faq_cache.get(
        question=query,
        language=language,
    )

    if cached_result is not None:
        logger.info("FAQ CACHE Hit: %s", query)
        answer = cached_result["answer"]
        sources = cached_result.get("sources", [])

        # Save cached answer to conversation history
        await memory_manager.add_message(
            db=db,
            call_id=call_id,
            role="assistant",
            content=answer,
        )

        return {
            "call_id": call_id,
            "query": query,
            "answer": answer,
            "sources": sources,
            "cache_hit": True,
        }

    # 3. Load conversation history
    history = await memory_manager.get_conversation(
        db=db,
        call_id=call_id,
    )

    history_messages: list[AnyMessage] = []

    for message in history:
        if message["role"] == "user":
            history_messages.append(
                HumanMessage(content=message["content"])
            )
        elif message["role"] == "assistant":
            history_messages.append(
                AIMessage(content=message["content"])
            )

    logger.info("FAQ CACHE MISS: %s", query)
    # 4. Execute RAG workflow
    initial_state: SamvadState = {
        "call_id": call_id,
        "query": query,
        "language": language,
        "messages": history_messages,
    }

    result = await rag_workflow.ainvoke(initial_state)

    answer = result["answer"]
    sources = result["sources"]

    # 5. Cache the generated answer
    await faq_cache.set(
        question=query,
        answer=answer,
        language=language,
        sources=sources,
    )

    # 6. Save assistant response
    await memory_manager.add_message(
        db=db,
        call_id=call_id,
        role="assistant",
        content=answer,
    )

    return {
        "call_id": call_id,
        "query": query,
        "answer": answer,
        "sources": sources,
        "cache_hit": False,
    }
