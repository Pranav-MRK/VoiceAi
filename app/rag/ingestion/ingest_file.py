
from pathlib import Path

from app.rag.ingestion.pipeline import IngestionPipeline
from app.rag.chunking.splitter import DocumentChunker
from app.rag.embeddings.provider import EmbeddingProvider
from app.rag.indexing.document_store import DocumentStore


def ingest_file(file_path: str):
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # 1. Load and clean document
    pipeline = IngestionPipeline()
    documents = pipeline.process(str(file_path))

    print(f"Loaded documents: {len(documents)}")

    # 2. Split into chunks
    chunker = DocumentChunker()
    chunks = chunker.split_documents(documents)

    print(f"Generated chunks: {len(chunks)}")

    if not chunks:
        raise ValueError("No chunks generated from document")

    # 3. Generate embeddings and index in OpenSearch
    embedding_provider = EmbeddingProvider()
    document_store = DocumentStore(
        embedding_provider=embedding_provider
    )

    indexed_count = document_store.index_chunks(chunks)

    print(f"Successfully indexed: {indexed_count} chunks")

    return indexed_count


if __name__ == "__main__":
    ingest_file("data/knowledge_base/btech_admission.txt")
