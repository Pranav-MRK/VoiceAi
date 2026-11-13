
from typing import Any

from opensearchpy import helpers

from app.rag.schemas import ChunkRecord
from app.rag.indexing.index_manager import OpenSearchIndexManager
from app.rag.embeddings.provider import EmbeddingProvider


class DocumentStore:
    """Store and manage embedded document chunks in OpenSearch."""

    def __init__(
        self,
        index_manager: OpenSearchIndexManager | None = None,
        embedding_provider: EmbeddingProvider | None = None,
    ):
        self.index_manager = index_manager or OpenSearchIndexManager()
        self.embedding_provider = embedding_provider or EmbeddingProvider()

        self.client = self.index_manager.client
        self.index_name = self.index_manager.index_name

    def index_chunks(self, chunks: list[ChunkRecord]) -> int:
        """Generate embeddings and bulk-index chunks."""

        if not chunks:
            return 0

        self.index_manager.create_index()

        texts = [chunk.content for chunk in chunks]
        embeddings = self.embedding_provider.embed_documents(texts)

        if len(embeddings) != len(chunks):
            raise ValueError("Embedding count does not match chunk count")

        actions = []

        for chunk, embedding in zip(chunks, embeddings):
            metadata = chunk.metadata

            source: dict[str, Any] = {
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "content": chunk.content,
                "embedding": embedding,
                "chunk_index": chunk.chunk_index,
                "filename": metadata.get("filename"),
                "source": metadata.get("source"),
                "title": metadata.get("title"),
                "metadata": metadata,
            }

            if metadata.get("page_index") is not None:
                source["page_index"] = metadata["page_index"]

            actions.append({
                "_op_type": "index",
                "_index": self.index_name,
                "_id": chunk.chunk_id,
                "_source": source,
            })

        success, errors = helpers.bulk(
            self.client,
            actions,
            raise_on_error=False,
        )

        self.client.indices.refresh(index=self.index_name)

        if errors:
            raise RuntimeError(
                f"OpenSearch indexing failed for {len(errors)} chunks: "
                f"{errors[:3]}"
            )

        return success

    
    def delete_document(self, document_id: str) -> int:
        """Delete all chunks belonging to a document."""

        if not self.index_manager.index_exists():
            return 0

        response = self.client.delete_by_query(
            index=self.index_name,
            body={
                "query": {
                    "term": {
                        "document_id": document_id,
                    }
                }
            },
            params={"refresh": "true"},
        )

        return response.get("deleted", 0)


    def replace_document(
        self,
        document_id: str,
        chunks: list[ChunkRecord],
    ) -> int:
        """Replace all indexed chunks for a document."""

        if any(chunk.document_id != document_id for chunk in chunks):
            raise ValueError(
                "All chunks must belong to the specified document"
            )

        if not chunks:
            return self.delete_document(document_id)

        # Generate vectors before deleting the existing document.
        texts = [chunk.content for chunk in chunks]
        embeddings = self.embedding_provider.embed_documents(texts)

        if len(embeddings) != len(chunks):
            raise ValueError("Embedding count does not match chunk count")

        self.index_manager.create_index()

        # Delete previous version only after embeddings are generated.
        self.delete_document(document_id)

        actions = []

        for chunk, embedding in zip(chunks, embeddings):
            metadata = chunk.metadata

            source = {
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "content": chunk.content,
                "embedding": embedding,
                "chunk_index": chunk.chunk_index,
                "filename": metadata.get("filename"),
                "source": metadata.get("source"),
                "title": metadata.get("title"),
                "metadata": metadata,
            }

            if metadata.get("page_index") is not None:
                source["page_index"] = metadata["page_index"]

            actions.append({
                "_op_type": "index",
                "_index": self.index_name,
                "_id": chunk.chunk_id,
                "_source": source,
            })

        success, errors = helpers.bulk(
            self.client,
            actions,
            raise_on_error=False,
        )

        self.client.indices.refresh(index=self.index_name)

        if errors:
            raise RuntimeError(
                f"Document replacement failed: {errors[:3]}"
            )

        return success

    def get_document_chunks(
        self,
        document_id: str,
    ) -> list[dict]:
        """Fetch all chunks belonging to a document."""

        if not self.index_manager.index_exists():
            return []

        response = self.client.search(
            index=self.index_name,
            body={
                "size": 1000,
                "query": {
                    "term": {
                        "document_id": document_id,
                    }
                },
                "sort": [
                    {"chunk_index": {"order": "asc"}}
                ],
            },
        )

        return [
            hit["_source"]
            for hit in response["hits"]["hits"]
        ]
