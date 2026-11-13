
from unittest.mock import MagicMock

import pytest

from app.rag.retrieval.bm25 import BM25Retriever


@pytest.fixture
def retriever():
    manager = MagicMock()
    manager.index_name = "test_documents"
    manager.index_exists.return_value = True

    manager.client.search.return_value = {
        "hits": {
            "hits": [
                {
                    "_score": 8.5,
                    "_source": {
                        "chunk_id": "chunk-001",
                        "document_id": "doc-001",
                        "content": "Admission applications open in June.",
                        "source": "admission.pdf",
                        "metadata": {"page_index": 0},
                    },
                }
            ]
        }
    }

    return BM25Retriever(index_manager=manager)


def test_bm25_search(retriever):
    results = retriever.search("Admission applications")

    assert len(results) == 1
    assert results[0].chunk_id == "chunk-001"
    assert results[0].score == 8.5


def test_bm25_search_empty_query(retriever):
    with pytest.raises(ValueError):
        retriever.search("  ")


def test_bm25_search_without_index(retriever):
    retriever.index_manager.index_exists.return_value = False

    results = retriever.search("Admission")

    assert results == []
