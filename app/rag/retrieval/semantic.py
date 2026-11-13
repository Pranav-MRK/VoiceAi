
from typing import Any

from app.core.config import settings
from app.rag.embeddings.provider import EmbeddingProvider
from app.rag.indexing.index_manager import OpenSearchIndexManager
from app.rag.schemas import RetrievedChunk


class SemanticRetriever:
    """Retrieve relevant chunks using vector similarity."""

    def __init__(
        self,
        index_manager: OpenSearchIndexManager | None = None,
        embedding_provider: EmbeddingProvider | None = None,
    ):
        self.index_manager = index_manager or OpenSearchIndexManager()
        self.embedding_provider = embedding_provider or EmbeddingProvider()

        self.client = self.index_manager.client
        self.index_name = self.index_manager.index_name

    def search(
        self,
        query: str,
        top_k: int | None = None,
        filters: dict[str, Any] | None = None,
    ) -> list[RetrievedChunk]:

        if not query.strip():
            raise ValueError("Search query cannot be empty")

        if not self.index_manager.index_exists():
            return []

        top_k = (
            top_k if top_k is not None else settings.RETRIEVAL_TOP_K
        )

        if top_k < 1:
            raise ValueError("top_k must be greater than zero")

        # Convert the question into a query embedding.
        query_vector = self.embedding_provider.embed_query(query)

        # Build optional metadata filters.
        filter_conditions = [
            {
                "term": {
                    f"metadata.{field}": value
                }
            }
            for field, value in (filters or {}).items()
        ]

        knn_query = {
            "vector": query_vector,
            "k": top_k,
        }

        if filter_conditions:
            knn_query["filter"] = {
                "bool": {
                    "filter": filter_conditions
                }
            }

        search_body = {
            "size": top_k,
            "query": {
                "knn": {
                    "embedding": knn_query
                }
            },
        }

        response = self.client.search(
            index=self.index_name,
            body=search_body,
        )

        results = []

        for hit in response["hits"]["hits"]:
            source = hit["_source"]

            results.append(
                RetrievedChunk(
                    chunk_id=source["chunk_id"],
                    document_id=source["document_id"],
                    content=source["content"],
                    score=float(hit["_score"] or 0.0),
                    source=source.get("source"),
                    metadata=source.get("metadata", {}),
                )
            )

        return results
