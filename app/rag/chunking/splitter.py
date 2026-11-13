
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings
from app.rag.schemas import DocumentRecord, ChunkRecord


class DocumentChunker:
    """Split normalized documents into searchable chunks."""

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = (
            chunk_overlap
            if chunk_overlap is not None
            else settings.CHUNK_OVERLAP
        )

        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")

        if self.chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")

        if self.chunk_overlap >= self.chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size"
            )

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", "? ", "! ", " ", ""],
            length_function=len,
            add_start_index=True,
        )

    def split(
        self,
        documents: list[DocumentRecord],
    ) -> list[ChunkRecord]:

        chunks: list[ChunkRecord] = []

        for document in documents:
            split_documents = self.splitter.create_documents(
                texts=[document.content],
                metadatas=[
                    {
                        "document_id": document.document_id,
                        "filename": document.metadata.filename,
                        "file_type": document.metadata.file_type,
                        "source": document.metadata.source,
                        "title": document.metadata.title,
                        **document.metadata.metadata,
                    }
                ],
            )

            for index, chunk in enumerate(split_documents):
                chunk_id = (
                    f"{document.document_id}-"
                    f"{chunk.metadata.get('page_index', 0)}-"
                    f"{index}"
                )

                chunks.append(
                    ChunkRecord(
                        chunk_id=chunk_id,
                        document_id=document.document_id,
                        content=chunk.page_content,
                        chunk_index=index,
                        metadata=chunk.metadata,
                    )
                )

        return chunks
