
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    """Metadata associated with an ingested document."""

    document_id: str
    filename: str
    file_type: str

    source: str | None = None
    title: str | None = None
    language: str | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class DocumentRecord(BaseModel):
    """Normalized document representation."""

    document_id: str
    content: str
    metadata: DocumentMetadata


class ChunkRecord(BaseModel):
    """A single chunk generated from a document."""

    chunk_id: str
    document_id: str

    content: str
    chunk_index: int

    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievedChunk(BaseModel):
    """A chunk returned by the retrieval system."""

    chunk_id: str
    document_id: str

    content: str
    score: float

    source: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


from pydantic import BaseModel, Field, field_validator

class RetrievalRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=50)
    language: str | None = None
    filters: dict[str, Any] = Field(default_factory=dict)

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Query cannot be empty")

        return value


class RetrievalResponse(BaseModel):
    """Output from the retrieval pipeline."""

    query: str
    results: list[RetrievedChunk] = Field(default_factory=list)

    total_results: int = 0
    retrieval_method: Literal["semantic", "bm25", "hybrid"] = "hybrid"

    processing_time_ms: float | None = None
