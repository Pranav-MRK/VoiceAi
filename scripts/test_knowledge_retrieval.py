
from app.rag.retrieval.retriever import RAGRetriever
from app.rag.schemas import RetrievalRequest


def main():
    retriever = RAGRetriever()

    request = RetrievalRequest(
        query="What documents are required for B.Tech admission?",
        top_k=5,
    )

    response = retriever.retrieve(request)

    print(f"\nRetrieved chunks: {len(response.results)}")

    for index, chunk in enumerate(response.results, start=1):
        print(f"\n--- Result {index} ---")
        print(f"Score: {chunk.score}")
        print(f"Content: {chunk.content}")
        print(f"Metadata: {chunk.metadata}")


if __name__ == "__main__":
    main()
