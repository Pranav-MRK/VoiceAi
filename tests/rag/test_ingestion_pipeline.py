
from app.rag.ingestion.pipeline import IngestionPipeline


def test_generate_document_id_is_stable():
    pipeline = IngestionPipeline()

    first = pipeline.generate_document_id("SamvadAI admission")
    second = pipeline.generate_document_id("SamvadAI admission")

    assert first == second


def test_different_content_has_different_id():
    pipeline = IngestionPipeline()

    first = pipeline.generate_document_id("Admission details")
    second = pipeline.generate_document_id("Fee details")

    assert first != second


def test_ingest_txt_file(tmp_path):
    file_path = tmp_path / "admission.txt"

    file_path.write_text(
        "SamvadAI Admission Information\n"
        "Applications open in June.",
        encoding="utf-8",
    )

    pipeline = IngestionPipeline()
    records = pipeline.ingest(file_path)

    assert len(records) == 1
    assert records[0].metadata.filename == "admission.txt"
    assert records[0].metadata.file_type == "txt"
    assert records[0].document_id
    assert "Applications open in June" in records[0].content


def test_empty_document(tmp_path):
    file_path = tmp_path / "empty.txt"
    file_path.write_text("   ", encoding="utf-8")

    pipeline = IngestionPipeline()
    records = pipeline.ingest(file_path)

    assert records == []
