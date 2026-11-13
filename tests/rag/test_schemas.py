
from app.rag.schemas import (
    ChunkRecord,
    DocumentMetadata,
    RetrievalRequest,
    RetrievedChunk,
)


def test_document_metadata():
    metadata = DocumentMetadata(
        document_id="doc-001",
        filename="admission.pdf",
        file_type="pdf",
    )

    assert metadata.document_id == "doc-001"
    assert metadata.file_type == "pdf"


def test_chunk_record():
    chunk = ChunkRecord(
        chunk_id="doc-001-chunk-0",
        document_id="doc-001",
        content="Admission starts in June.",
        chunk_index=0,
    )

    assert chunk.chunk_index == 0
    assert chunk.document_id == "doc-001"


def test_retrieval_request():
    request = RetrievalRequest(
        query="What are the admission requirements?",
        top_k=5,
    )

    assert request.top_k == 5


def test_retrieved_chunk():
    chunk = RetrievedChunk(
        chunk_id="chunk-001",
        document_id="doc-001",
        content="Admission requires an entrance examination.",
        score=0.92,
    )

    assert chunk.score == 0.92
