
from typing import Any

from app.core.config import settings
from app.rag.indexing.index_manager import OpenSearchIndexManager
from app.rag.schemas import RetrievedChunk


class BM25Retriever:
    """Retrieve relevant document chunks using BM25 keyword search."""

    def __init__(
        self,
        index_manager: OpenSearchIndexManager | None = None,
    ):
        self.index_manager = index_manager or OpenSearchIndexManager()
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

        top_k = top_k or settings.RETRIEVAL_TOP_K

        filter_conditions = []

        for field, value in (filters or {}).items():
            filter_conditions.append({
                "term": {
                    f"metadata.{field}": value
                }
            })

        search_body = {
            "size": top_k,
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": [
                                    "content^2",
                                    "title",
                                    "filename",
                                ],
                                "type": "best_fields",
                                "fuzziness": "AUTO",
                            }
                        }
                    ],
                    "filter": filter_conditions,
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
