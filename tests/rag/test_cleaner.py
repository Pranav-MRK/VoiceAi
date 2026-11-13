
from langchain_core.documents import Document

from app.rag.ingestion.cleaner import DocumentCleaner


def test_clean_text():
    cleaner = DocumentCleaner()

    text = "  Hello   World  \n\n\nSamvadAI  "

    result = cleaner.clean_text(text)

    assert result == "Hello World\n\nSamvadAI"


def test_remove_null_characters():
    cleaner = DocumentCleaner()

    result = cleaner.clean_text("Hello\x00World")

    assert result == "HelloWorld"


def test_preserve_multilingual_text():
    cleaner = DocumentCleaner()

    text = "नमस्ते   दुनिया\nमराठी भाषा"

    result = cleaner.clean_text(text)

    assert result == "नमस्ते दुनिया\nमराठी भाषा"


def test_clean_documents():
    cleaner = DocumentCleaner()

    documents = [
        Document(
            page_content="  Admission   Information  ",
            metadata={"page": 1},
        ),
        Document(
            page_content="   ",
            metadata={"page": 2},
        ),
    ]

    result = cleaner.clean_documents(documents)

    assert len(result) == 1
    assert result[0].page_content == "Admission Information"
    assert result[0].metadata == {"page": 1}
