
from unittest.mock import MagicMock

import pytest

from app.rag.retrieval.retriever import RAGRetriever
from app.rag.schemas import RetrievalRequest, RetrievedChunk


@pytest.fixture
def retriever():
    hybrid = MagicMock()

    hybrid.search.return_value = [
        RetrievedChunk(
            chunk_id="chunk-001",
            document_id="doc-001",
            content="The annual tuition fee is 85000.",
            score=0.03,
            source="fees.pdf",
        ),
        RetrievedChunk(
            chunk_id="chunk-002",
            document_id="doc-002",
            content="Applications open in June.",
            score=0.02,
            source="admission.pdf",
        ),
    ]

    return RAGRetriever(hybrid_retriever=hybrid)


def test_retrieve(retriever):
    request = RetrievalRequest(
        query="What is the annual tuition fee?",
        top_k=5,
    )

    response = retriever.retrieve(request)

    assert response.retrieval_method == "hybrid"
    assert response.total_results == 2
    assert len(response.results) == 2
    assert response.processing_time_ms >= 0


def test_search(retriever):
    response = retriever.search(
        query="Admission requirements",
        top_k=3,
    )

    assert response.query == "Admission requirements"
    assert response.total_results == 2

    retriever.hybrid_retriever.search.assert_called_once()


def test_empty_query(retriever):
    with pytest.raises(ValueError):
        retriever.search("  ")


def test_retrieval_passes_filters(retriever):
    retriever.search(
        query="Admission requirements",
        filters={"language": "en"},
    )

    kwargs = retriever.hybrid_retriever.search.call_args.kwargs

    assert kwargs["filters"] == {"language": "en"}
