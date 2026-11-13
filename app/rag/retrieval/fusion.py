
from collections import defaultdict
from typing import Any

from app.core.config import settings
from app.rag.retrieval.bm25 import BM25Retriever
from app.rag.retrieval.semantic import SemanticRetriever
from app.rag.schemas import RetrievedChunk


class HybridRetriever:
    """Combine BM25 and semantic retrieval using RRF."""

    def __init__(
        self,
        bm25_retriever: BM25Retriever | None = None,
        semantic_retriever: SemanticRetriever | None = None,
        rrf_k: int = 60,
        bm25_weight: float = 1.0,
        semantic_weight: float = 1.0,
    ):
        if rrf_k <= 0:
            raise ValueError("rrf_k must be greater than zero")

        if bm25_weight < 0 or semantic_weight < 0:
            raise ValueError("RRF weights cannot be negative")

        if bm25_weight + semantic_weight == 0:
            raise ValueError("At least one RRF weight must be positive")

        self.bm25_retriever = bm25_retriever or BM25Retriever()
        self.semantic_retriever = (
            semantic_retriever or SemanticRetriever()
        )

        self.rrf_k = rrf_k
        self.bm25_weight = bm25_weight
        self.semantic_weight = semantic_weight

    def search(
        self,
        query: str,
        top_k: int | None = None,
        filters: dict[str, Any] | None = None,
    ) -> list[RetrievedChunk]:

        if not query.strip():
            raise ValueError("Search query cannot be empty")

        final_top_k = (
            top_k if top_k is not None else settings.RETRIEVAL_TOP_K
        )

        if final_top_k < 1:
            raise ValueError("top_k must be greater than zero")

        # Retrieve a larger candidate set before fusion.
        candidate_k = max(final_top_k * 2, 10)

        bm25_results = self.bm25_retriever.search(
            query=query,
            top_k=candidate_k,
            filters=filters,
        )

        semantic_results = self.semantic_retriever.search(
            query=query,
            top_k=candidate_k,
            filters=filters,
        )

        scores = defaultdict(float)
        chunks = {}
        ranks = defaultdict(dict)

        retrievers = [
            ("bm25", bm25_results, self.bm25_weight),
            ("semantic", semantic_results, self.semantic_weight),
        ]

        for retriever_name, results, weight in retrievers:
            for rank, chunk in enumerate(results, start=1):
                chunk_id = chunk.chunk_id

                scores[chunk_id] += weight / (
                    self.rrf_k + rank
                )

                chunks[chunk_id] = chunk
                ranks[chunk_id][retriever_name] = rank

        ranked_chunks = sorted(
            chunks.values(),
            key=lambda chunk: scores[chunk.chunk_id],
            reverse=True,
        )

        fused_results = []

        for chunk in ranked_chunks[:final_top_k]:
            metadata = dict(chunk.metadata)

            metadata["rrf_score"] = scores[chunk.chunk_id]
            metadata["bm25_rank"] = ranks[chunk.chunk_id].get("bm25")
            metadata["semantic_rank"] = ranks[chunk.chunk_id].get(
                "semantic"
            )

            fused_results.append(
                RetrievedChunk(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    content=chunk.content,
                    score=scores[chunk.chunk_id],
                    source=chunk.source,
                    metadata=metadata,
                )
            )

        return fused_results
