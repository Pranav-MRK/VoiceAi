
from unittest.mock import MagicMock, patch

from app.rag.indexing.index_manager import OpenSearchIndexManager


@patch("app.rag.indexing.index_manager.OpenSearch")
def test_create_index(mock_opensearch):
    client = MagicMock()
    mock_opensearch.return_value = client

    client.indices.exists.return_value = False

    manager = OpenSearchIndexManager()

    result = manager.create_index()

    assert result is True
    client.indices.create.assert_called_once()


@patch("app.rag.indexing.index_manager.OpenSearch")
def test_existing_index_is_not_recreated(mock_opensearch):
    client = MagicMock()
    mock_opensearch.return_value = client

    client.indices.exists.return_value = True

    manager = OpenSearchIndexManager()

    result = manager.create_index()

    assert result is False
    client.indices.create.assert_not_called()


@patch("app.rag.indexing.index_manager.OpenSearch")
def test_health_check(mock_opensearch):
    client = MagicMock()
    mock_opensearch.return_value = client
    client.ping.return_value = True

    manager = OpenSearchIndexManager()

    assert manager.health_check() is True
