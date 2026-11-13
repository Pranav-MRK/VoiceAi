
from time import perf_counter
from typing import Any

from app.rag.retrieval.fusion import HybridRetriever
from app.rag.schemas import RetrievalRequest, RetrievalResponse


class RAGRetriever:
    """Unified retrieval interface for the RAG system."""

    def __init__(
        self,
        hybrid_retriever: HybridRetriever | None = None,
    ):
        self.hybrid_retriever = hybrid_retriever or HybridRetriever()

    def retrieve(
        self,
        request: RetrievalRequest,
    ) -> RetrievalResponse:
        """Retrieve relevant chunks using hybrid search."""

        if not request.query.strip():
            raise ValueError("Search query cannot be empty")

        start_time = perf_counter()

        results = self.hybrid_retriever.search(
            query=request.query,
            top_k=request.top_k,
            filters=request.filters,
        )

        processing_time = (perf_counter() - start_time) * 1000

        return RetrievalResponse(
            query=request.query,
            results=results,
            total_results=len(results),
            retrieval_method="hybrid",
            processing_time_ms=round(processing_time, 2),
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> RetrievalResponse:
        """Convenience method for direct retrieval."""

        request = RetrievalRequest(
            query=query,
            top_k=top_k,
            filters=filters or {},
        )

        return self.retrieve(request)
