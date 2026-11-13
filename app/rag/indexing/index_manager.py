
from urllib.parse import urlparse

from opensearchpy import OpenSearch

from app.core.config import settings


class OpenSearchIndexManager:
    """Manage the SamvadAI RAG index."""

    def __init__(self):
        parsed_url = urlparse(settings.OPENSEARCH_URL)

        self.client = OpenSearch(
            hosts=[
                {
                    "host": parsed_url.hostname or "localhost",
                    "port": parsed_url.port or 9200,
                }
            ],
            http_auth=(
                settings.OPENSEARCH_USERNAME,
                settings.OPENSEARCH_PASSWORD,
            ),
            use_ssl=parsed_url.scheme == "https",
            verify_certs=settings.OPENSEARCH_VERIFY_CERTS,
            ssl_show_warn=False,
        )
        print("OpenSearch hosts:", self.client.transport.hosts)
        print("OpenSearch URL:", settings.OPENSEARCH_URL)
        print("OpenSearch SSL:", parsed_url.scheme == "https")

        self.index_name = settings.OPENSEARCH_INDEX
        self.dimension = settings.EMBEDDING_DIMENSION


    def create_index(self) -> bool:
        """Create the vector index if it does not exist."""

        if self.client.indices.exists(index=self.index_name):
            return False

        index_body = {
            "settings": {
                "index": {
                    "knn": True,
                    "number_of_shards": 1,
                    "number_of_replicas": 0,
                }
            },
            "mappings": {
                "properties": {
                    "chunk_id": {"type": "keyword"},
                    "document_id": {"type": "keyword"},
                    "content": {"type": "text"},
                    "embedding": {
                        "type": "knn_vector",
                        "dimension": self.dimension,
                        "method": {
                            "name": "hnsw",
                            "space_type": "cosinesimil",
                            "engine": "lucene",
                            "parameters": {
                                "ef_construction": 128,
                                "m": 16,
                            },
                        },
                    },
                    "chunk_index": {"type": "integer"},
                    "filename": {"type": "keyword"},
                    "source": {"type": "keyword"},
                    "title": {"type": "text"},
                    "page_index": {"type": "integer"},
                    "metadata": {
                        "type": "object",
                        "dynamic": True,
                    },
                }
            },
        }

        self.client.indices.create(
            index=self.index_name,
            body=index_body,
        )

        return True

    def index_exists(self) -> bool:
        return self.client.indices.exists(index=self.index_name)

    def delete_index(self) -> None:
        """Delete the index. Use carefully."""
        if self.index_exists():
            self.client.indices.delete(index=self.index_name)

    def health_check(self) -> bool:
        return self.client.ping()
