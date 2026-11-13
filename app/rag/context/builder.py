
from dataclasses import dataclass

from app.rag.schemas import RetrievedChunk


@dataclass
class BuiltContext:
    context: str
    sources: list[dict]
    chunks_used: int
    estimated_tokens: int


class ContextBuilder:
    """
    Converts retrieved RAG chunks into structured context
    that can be passed to an LLM.
    """

    def __init__(
        self,
        max_context_tokens: int = 3000,
        chars_per_token: int = 4,
    ):
        if max_context_tokens <= 0:
            raise ValueError("max_context_tokens must be positive")

        if chars_per_token <= 0:
            raise ValueError("chars_per_token must be positive")

        self.max_context_tokens = max_context_tokens
        self.chars_per_token = chars_per_token  # ADD THIS LINE
        self.max_chars = max_context_tokens * chars_per_token

    def build(
        self,
        chunks: list[RetrievedChunk],
    ) -> BuiltContext:

        if not chunks:
            return BuiltContext(
                context="",
                sources=[],
                chunks_used=0,
                estimated_tokens=0,
            )

        seen_chunk_ids = set()
        context_parts = []
        sources = []
        current_chars = 0

        for chunk in chunks:

            # Remove duplicate chunks
            if chunk.chunk_id in seen_chunk_ids:
                continue

            seen_chunk_ids.add(chunk.chunk_id)

            content = chunk.content.strip()

            if not content:
                continue

            metadata = chunk.metadata or {}

            source = (
                chunk.source
                or metadata.get("filename")
                or metadata.get("source")
                or "Unknown source"
            )

            page = metadata.get("page")

            source_label = f"[Source: {source}"

            if page is not None:
                source_label += f", Page: {page}"

            source_label += "]"

            formatted_chunk = (
                f"{source_label}\n"
                f"{content}"
            )

            # Enforce context budget
            required_chars = len(formatted_chunk) + 2

            if current_chars + required_chars > self.max_chars:
                continue

            context_parts.append(formatted_chunk)

            sources.append({
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "source": source,
                "page": page,
                "score": chunk.score,
            })

            current_chars += required_chars

        context = "\n\n".join(context_parts)

        estimated_tokens = (
            len(context) + self.chars_per_token - 1
        ) // self.chars_per_token

        return BuiltContext(
            context=context,
            sources=sources,
            chunks_used=len(context_parts),
            estimated_tokens=estimated_tokens,
        )
