from pathlib  import Path

from langchain_community.document_loaders import(
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
    Docx2txtLoader,
)

from langchain_core.documents import Document


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
    ".md",
}


class DocumentLoader:
     """Load supported files into LangChain Document objects."""

     def load(self, file_path: str | Path) -> list[Document]:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if not path.is_file():
            raise ValueError(f"Expected a file, received: {path}")

        extension = path.suffix.lower()

        if extension not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file format: {extension}. "
                f"Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}"
            )

        loader_map = {
            ".pdf": PyPDFLoader,
            ".docx": Docx2txtLoader,
            ".txt": TextLoader,
            ".md": TextLoader,
        }

        loader_class = loader_map[extension]

        if extension in {".txt", ".md"}:
            loader = loader_class(
                str(path),
                encoding="utf-8",
            )
        else:
            loader = loader_class(str(path))

        documents = loader.load()

        return [
            document
            for document in documents
            if document.page_content.strip()
        ]