
import pytest

from app.rag.context.builder import ContextBuilder
from app.rag.schemas import RetrievedChunk


@pytest.fixture
def sample_chunks():
    return [
        RetrievedChunk(
            chunk_id="chunk-1",
            document_id="doc-1",
            content="B.Tech admission requires meeting the eligibility criteria.",
            score=0.95,
            source="admission.pdf",
            metadata={"page": 2},
        ),
        RetrievedChunk(
            chunk_id="chunk-2",
            document_id="doc-1",
            content="Students must complete their application process.",
            score=0.85,
            source="admission.pdf",
            metadata={"page": 3},
        ),
    ]


def test_empty_chunks():
    builder = ContextBuilder()

    result = builder.build([])

    assert result.context == ""
    assert result.sources == []
    assert result.chunks_used == 0
    assert result.estimated_tokens == 0


def test_build_context(sample_chunks):
    builder = ContextBuilder()

    result = builder.build(sample_chunks)

    assert result.chunks_used == 2
    assert "B.Tech admission" in result.context
    assert "application process" in result.context


def test_duplicate_chunks_are_removed(sample_chunks):
    builder = ContextBuilder()

    chunks = sample_chunks + [sample_chunks[0]]

    result = builder.build(chunks)

    assert result.chunks_used == 2


def test_source_and_page_are_preserved(sample_chunks):
    builder = ContextBuilder()

    result = builder.build(sample_chunks)

    assert len(result.sources) == 2
    assert result.sources[0]["source"] == "admission.pdf"
    assert result.sources[0]["page"] == 2


def test_context_token_budget():
    builder = ContextBuilder(
        max_context_tokens=10,
        chars_per_token=4,
    )

    chunks = [
        RetrievedChunk(
            chunk_id="chunk-1",
            document_id="doc-1",
            content="A" * 200,
            score=0.9,
            source="large.pdf",
            metadata={},
        )
    ]

    result = builder.build(chunks)

    assert result.chunks_used == 0
    assert result.estimated_tokens == 0


def test_estimated_tokens(sample_chunks):
    builder = ContextBuilder(
        max_context_tokens=3000,
        chars_per_token=4,
    )

    result = builder.build(sample_chunks)

    expected = (
        len(result.context) + 3
    ) // 4

    assert result.estimated_tokens == expected
