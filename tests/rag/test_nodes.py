
from unittest.mock import MagicMock

from app.rag.graph.nodes import (
    retrieve_node,
    context_node,
    generate_node,
)
from app.rag.graph import nodes
from app.rag.schemas import RetrievedChunk


def test_retrieve_node(monkeypatch):
    mock_retriever = MagicMock()

    mock_retriever.retrieve.return_value.results = [
        RetrievedChunk(
            chunk_id="chunk-1",
            document_id="doc-1",
            content="B.Tech admission information",
            score=0.9,
            source="admission.pdf",
            metadata={},
        )
    ]

    monkeypatch.setattr(
        nodes,
        "get_retriever",
        lambda: mock_retriever,
    )

    result = retrieve_node({
        "query": "B.Tech admission eligibility"
    })

    assert len(result["retrieved_chunks"]) == 1
    mock_retriever.retrieve.assert_called_once()


def test_context_node(monkeypatch):
    mock_builder = MagicMock()

    mock_builder.build.return_value.context = "Admission context"
    mock_builder.build.return_value.sources = []

    monkeypatch.setattr(nodes, "context_builder", mock_builder)

    result = context_node({
        "retrieved_chunks": []
    })

    assert result["context"] == "Admission context"
    assert result["sources"] == []


def test_generate_node(monkeypatch):
    mock_llm = MagicMock()

    mock_llm.invoke.return_value.content = (
        "Students must meet the admission eligibility criteria."
    )

    monkeypatch.setattr(nodes, "llm", mock_llm)

    result = generate_node({
        "query": "What are the admission requirements?",
        "context": "Students must meet the admission eligibility criteria."
    })

    assert "eligibility criteria" in result["answer"]
    mock_llm.invoke.assert_called_once()
