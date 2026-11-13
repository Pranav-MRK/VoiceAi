
import hashlib
from pathlib import Path

from app.rag.ingestion.loaders import DocumentLoader
from app.rag.ingestion.cleaner import DocumentCleaner
from app.rag.schemas import DocumentMetadata, DocumentRecord


class IngestionPipeline:
    """Coordinate document loading, cleaning and normalization."""

    def __init__(self):
        self.loader = DocumentLoader()
        self.cleaner = DocumentCleaner()

    @staticmethod
    def generate_document_id(content: str) -> str:
        """Generate a deterministic ID from normalized content."""
        return hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()

    def ingest(self, file_path: str | Path) -> list[DocumentRecord]:
        path = Path(file_path)

        # Load and clean
        raw_documents = self.loader.load(path)
        cleaned_documents = self.cleaner.clean_documents(raw_documents)

        # Combine pages to create a stable document-level ID
        full_content = "\n\n".join(
            document.page_content for document in cleaned_documents
        )

        if not full_content:
            return []

        document_id = self.generate_document_id(full_content)

        records = []

        for index, document in enumerate(cleaned_documents):
            metadata = DocumentMetadata(
                document_id=document_id,
                filename=path.name,
                file_type=path.suffix.lower().lstrip("."),
                source=str(path.resolve()),
                title=path.stem,
                metadata={
                    **document.metadata,
                    "page_index": index,
                },
            )

            records.append(
                DocumentRecord(
                    document_id=document_id,
                    content=document.page_content,
                    metadata=metadata,
                )
            )

        return records
