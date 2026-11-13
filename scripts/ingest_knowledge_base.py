
from pathlib import Path

from app.rag.ingestion.pipeline import IngestionPipeline
from app.rag.chunking.splitter import DocumentChunker
from app.rag.indexing.document_store import DocumentStore


def main():
    file_path = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "knowledge_base"
        / "btech_admission.txt"
    )

    if not file_path.exists():
        raise FileNotFoundError(f"Knowledge base file not found: {file_path}")

    # 1. Load and clean the document
    pipeline = IngestionPipeline()
    documents = pipeline.ingest(file_path)

    print(f"Documents loaded: {len(documents)}")

    if not documents:
        print("No document content found.")
        return

    # 2. Split into chunks
    chunker = DocumentChunker()
    chunks = chunker.split(documents)

    print(f"Chunks generated: {len(chunks)}")

    # 3. Generate embeddings and index in OpenSearch
    store = DocumentStore()
    indexed_count = store.index_chunks(chunks)

    print(f"Chunks indexed: {indexed_count}")
    print("Knowledge base ingestion completed successfully!")


if __name__ == "__main__":
    main()
