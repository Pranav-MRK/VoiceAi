
from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

from app.core.config import settings


class EmbeddingProvider:
    """Generate multilingual embeddings using Hugging Face."""

    def __init__(self):
        self.model = self._load_model()

    @staticmethod
    @lru_cache(maxsize=1)
    def _load_model() -> HuggingFaceEmbeddings:
        return HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={
                "device": settings.EMBEDDING_DEVICE,
            },
            encode_kwargs={
                "batch_size": settings.EMBEDDING_BATCH_SIZE,
                "normalize_embeddings": True,
            },
        )

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """Generate embeddings for document chunks."""

        if not texts:
            return []

        prepared_texts = [
            f"passage: {text}" for text in texts
        ]

        return self.model.embed_documents(prepared_texts)

    def embed_query(self, query: str) -> list[float]:
        """Generate an embedding for a user query."""

        if not query.strip():
            raise ValueError("Query cannot be empty")

        return self.model.embed_query(
            f"query: {query.strip()}"
        )

    @property
    def dimension(self) -> int:
        return len(self.embed_query("dimension check"))
