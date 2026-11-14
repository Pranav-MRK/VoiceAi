from langchain_groq import ChatGroq
from functools import lru_cache
from app.core.config import settings
from app.rag.retrieval.retriever import RAGRetriever
from app.rag.context.builder import ContextBuilder
from app.rag.schemas import RetrievalRequest
from app.rag.graph.state import SamvadState
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)

from pydantic import SecretStr
@lru_cache(maxsize=1)
def get_retriever():
    return RAGRetriever()
context_builder = ContextBuilder()

llm = ChatGroq(
    api_key=SecretStr(settings.GROQ_API_KEY)
    if settings.GROQ_API_KEY
    else None,
    model=settings.GROQ_MODEL,
    temperature=0,
)

#  retrival node 

def retrieve_node(state: SamvadState):
    request = RetrievalRequest(
        query=state.get("query", ""),
        top_k=settings.RETRIEVAL_TOP_K,
    )

    retriever = get_retriever()
    response = retriever.retrieve(request)

    return {
        "retrieved_chunks": response.results
    }



def context_node(state: SamvadState):
    result = context_builder.build(
        state.get("retrieved_chunks", [])
    )

    return {
        "context": result.context,
        "sources": result.sources,
    }



def generate_node(state: SamvadState):
    history = state.get("messages", [])

    conversation: list[BaseMessage] = [
        SystemMessage(
            content=f"""
            You are SamvadAI, a multilingual college admission assistant.
            Answer using only the retrieved context when answering
            admission-related questions.

            If the answer is unavailable, say so clearly.
            Keep responses concise and suitable for voice.
            Respond in the caller's language: {state.get("language", "en")}.
            """
        )
    ]

    for message in history:
        if isinstance(message, dict):
            role = message.get("role")
            content = message.get("content", "")

            if role == "user":
                conversation.append(HumanMessage(content=content))
            elif role == "assistant":
                conversation.append(AIMessage(content=content))

        else:
            conversation.append(message)

    # Add the current question if it isn't already in history.
    last_message = history[-1] if history else None

    if isinstance(last_message, dict):
        last_content = last_message.get("content", "")
    else:
        last_content = getattr(last_message, "content", None)

    if last_content != state.get("query", ""):
        conversation.append(
            HumanMessage(content=state.get("query", ""))
        )

    conversation.append(
        SystemMessage(
            content=f"Relevant admission information:\n{state.get('context', '')}"
        )
    )

    response = llm.invoke(conversation)

    return {"answer": response.content}
















