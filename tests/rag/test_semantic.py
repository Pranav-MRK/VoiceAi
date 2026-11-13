
from unittest.mock import MagicMock

import pytest

from app.rag.retrieval.semantic import SemanticRetriever


@pytest.fixture
def retriever():
    manager = MagicMock()
    manager.index_name = "test_documents"
    manager.index_exists.return_value = True

    manager.client.search.return_value = {
        "hits": {
            "hits": [
                {
                    "_score": 0.94,
                    "_source": {
                        "chunk_id": "chunk-001",
                        "document_id": "doc-001",
                        "content": "The annual tuition fee is 85000.",
                        "source": "fees.pdf",
                        "metadata": {
                            "page_index": 2,
                        },
                    },
                }
            ]
        }
    }

    embeddings = MagicMock()
    embeddings.embed_query.return_value = [0.1] * 384

    return SemanticRetriever(
        index_manager=manager,
        embedding_provider=embeddings,
    )


def test_semantic_search(retriever):
    results = retriever.search("How much is the annual fee?")

    assert len(results) == 1
    assert results[0].chunk_id == "chunk-001"
    assert results[0].score == 0.94

    retriever.embedding_provider.embed_query.assert_called_once_with(
        "How much is the annual fee?"
    )


def test_semantic_search_empty_query(retriever):
    with pytest.raises(ValueError):
        retriever.search("  ")


def test_semantic_search_without_index(retriever):
    retriever.index_manager.index_exists.return_value = False

    results = retriever.search("Admission information")

    assert results == []
    retriever.embedding_provider.embed_query.assert_not_called()


def test_semantic_search_with_filters(retriever):
    retriever.search(
        "Admission requirements",
        top_k=3,
        filters={"language": "en"},
    )

    search_call = retriever.client.search.call_args.kwargs
    knn = search_call["body"]["query"]["knn"]["embedding"]

    assert knn["k"] == 3
    assert knn["filter"]["bool"]["filter"][0]["term"] == {
        "metadata.language": "en"
    }


def test_invalid_top_k(retriever):
    with pytest.raises(ValueError):
        retriever.search("Admission", top_k=0)
