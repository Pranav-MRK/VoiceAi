
from unittest.mock import MagicMock

import pytest

from app.rag.retrieval.fusion import HybridRetriever
from app.rag.schemas import RetrievedChunk


def make_chunk(chunk_id, score=1.0):
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id=f"doc-{chunk_id}",
        content=f"Content for {chunk_id}",
        score=score,
        source="admission.pdf",
    )


@pytest.fixture
def hybrid_retriever():
    bm25 = MagicMock()
    semantic = MagicMock()

    bm25.search.return_value = [
        make_chunk("A"),
        make_chunk("B"),
        make_chunk("C"),
    ]

    semantic.search.return_value = [
        make_chunk("B"),
        make_chunk("A"),
        make_chunk("D"),
    ]

    return HybridRetriever(
        bm25_retriever=bm25,
        semantic_retriever=semantic,
    )


def test_hybrid_search_combines_results(hybrid_retriever):
    results = hybrid_retriever.search(
        "What are the admission requirements?",
        top_k=4,
    )

    assert len(results) == 4

    chunk_ids = [chunk.chunk_id for chunk in results]

    assert set(chunk_ids) == {"A", "B", "C", "D"}


def test_rrf_ranking(hybrid_retriever):
    results = hybrid_retriever.search("Admission", top_k=4)

    # A and B appear in both result lists.
    assert results[0].chunk_id in {"A", "B"}
    assert results[1].chunk_id in {"A", "B"}


def test_rrf_score(hybrid_retriever):
    results = hybrid_retriever.search("Admission", top_k=4)

    chunk_a = next(
        chunk for chunk in results if chunk.chunk_id == "A"
    )

    expected_score = (1 / 61) + (1 / 62)

    assert chunk_a.score == pytest.approx(expected_score)


def test_empty_query(hybrid_retriever):
    with pytest.raises(ValueError):
        hybrid_retriever.search("  ")


def test_invalid_top_k(hybrid_retriever):
    with pytest.raises(ValueError):
        hybrid_retriever.search("Admission", top_k=0)


def test_retriever_receives_same_query(hybrid_retriever):
    hybrid_retriever.search("Admission requirements", top_k=5)

    hybrid_retriever.bm25_retriever.search.assert_called_once()
    hybrid_retriever.semantic_retriever.search.assert_called_once()
