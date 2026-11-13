
from app.rag.chunking.splitter import DocumentChunker
from app.rag.schemas import DocumentMetadata, DocumentRecord


def create_document(content: str) -> DocumentRecord:
    document_id = "test-document-001"

    return DocumentRecord(
        document_id=document_id,
        content=content,
        metadata=DocumentMetadata(
            document_id=document_id,
            filename="admission.txt",
            file_type="txt",
            source="admission.txt",
            title="Admission Information",
        ),
    )


def test_split_document():
    content = "Admission information. " * 100

    chunker = DocumentChunker(
        chunk_size=200,
        chunk_overlap=30,
    )

    chunks = chunker.split([create_document(content)])

    assert len(chunks) > 1
    assert all(chunk.document_id == "test-document-001" for chunk in chunks)


def test_chunk_metadata_preserved():
    chunker = DocumentChunker(chunk_size=200, chunk_overlap=30)

    chunks = chunker.split([
        create_document("SamvadAI provides admission assistance.")
    ])

    assert chunks
    assert chunks[0].metadata["filename"] == "admission.txt"
    assert chunks[0].metadata["title"] == "Admission Information"


def test_empty_document_list():
    chunker = DocumentChunker()

    assert chunker.split([]) == []


def test_invalid_chunk_configuration():
    try:
        DocumentChunker(chunk_size=100, chunk_overlap=100)
        assert False, "Expected ValueError"
    except ValueError:
        pass
