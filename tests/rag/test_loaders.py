
import pytest

from app.rag.ingestion.loaders import DocumentLoader


def test_load_txt_file(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text(
        "SamvadAI is a multilingual admission assistant.",
        encoding="utf-8",
    )

    loader = DocumentLoader()
    documents = loader.load(file_path)

    assert len(documents) == 1
    assert "SamvadAI" in documents[0].page_content


def test_unsupported_file(tmp_path):
    file_path = tmp_path / "sample.csv"
    file_path.write_text("name,age", encoding="utf-8")

    loader = DocumentLoader()

    with pytest.raises(ValueError):
        loader.load(file_path)


def test_missing_file():
    loader = DocumentLoader()

    with pytest.raises(FileNotFoundError):
        loader.load("missing.pdf")


def test_empty_text_file(tmp_path):
    file_path = tmp_path / "empty.txt"
    file_path.write_text("   \n  ", encoding="utf-8")

    loader = DocumentLoader()
    documents = loader.load(file_path)

    assert documents == []
