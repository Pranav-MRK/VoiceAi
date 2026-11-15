
from unittest.mock import MagicMock

from app.rag.graph.workflow import rag_workflow
from app.rag.graph import nodes
from app.rag.schemas import RetrievedChunk


def test_rag_workflow(monkeypatch):
    # Mock retriever
    mock_retriever = MagicMock()

    chunk = RetrievedChunk(
        chunk_id="chunk-1",
        document_id="doc-1",
        content="B.Tech admission requires 10+2 qualification.",
        score=0.95,
        source="admission.pdf",
        metadata={"page": 2},
    )

    mock_retriever.retrieve.return_value.results = [chunk]

    # Mock context builder
    mock_context_builder = MagicMock()
    mock_context_builder.build.return_value.context = (
        "B.Tech admission requires 10+2 qualification."
    )
    mock_context_builder.build.return_value.sources = [
        {"source": "admission.pdf", "page": 2}
    ]

    # Mock Groq LLM
    mock_llm = MagicMock()
    mock_llm.invoke.return_value.content = (
        "B.Tech admission requires a 10+2 qualification."
    )

    # Replace actual services with mocks
    monkeypatch.setattr(
        nodes,
        "get_retriever",
        lambda: mock_retriever,
    )
    monkeypatch.setattr(
        nodes, "context_builder", mock_context_builder
    )
    monkeypatch.setattr(nodes, "llm", mock_llm)

    # Execute complete workflow
    result = rag_workflow.invoke({
        "query": "What is the B.Tech eligibility criteria?",
        "call_id": "test-call-001",
        "language": "en",
    })

    # Verify final answer
    assert result["answer"] == (
        "B.Tech admission requires a 10+2 qualification."
    )

    # Verify every stage executed
    mock_retriever.retrieve.assert_called_once()
    mock_context_builder.build.assert_called_once()
    mock_llm.invoke.assert_called_once()

    # Verify context reached the LLM
    messages = mock_llm.invoke.call_args.args[0]

    prompt_text = "\n".join(
        str(message.content) for message in messages
    )

    assert "10+2 qualification" in prompt_text