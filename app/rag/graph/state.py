
from typing import Annotated, Any
from typing_extensions import TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

from app.rag.schemas import RetrievedChunk


class SamvadState(TypedDict, total=False):
    """
    Shared state for one SamvadAI conversation turn.

    Each phone call has its own call_id and its own
    graph execution state.
    """

    # Call identification
    call_id: str

    # Caller information
    query: str
    language: str

    # Conversation history
    messages: Annotated[list[AnyMessage], add_messages]

    # RAG retrieval output
    retrieved_chunks: list[RetrievedChunk]

    # Context builder output
    context: str
    sources: list[dict[str, Any]]

    # LLM output
    answer: str

    # Error handling
    error: str | None
