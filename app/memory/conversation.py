

from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.messages import (
    AIMessage,
    AnyMessage,
    HumanMessage,
)
from app.rag.graph.state import SamvadState
from app.memory.manager import MemoryManager
from app.rag.graph.workflow import rag_workflow


memory_manager = MemoryManager()


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

    # 2. Load conversation history
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

    # 3. Execute the RAG workflow
    # 3. Execute the RAG workflow asynchronously
    initial_state: SamvadState = {
        "call_id": call_id,
        "query": query,
        "language": language,
        "messages": history_messages,
    }

    result = await rag_workflow.ainvoke(initial_state)

    answer = result["answer"]

    # 4. Save the assistant's response
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
        "sources": result["sources"],
    }