import re

from langchain_core.documents import Document


class DocumentCleaner:
    """Clean extracted document text while preserving metadata."""

    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""

        # Normalize Windows and Mac line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Remove null characters
        text = text.replace("\x00", "")

        # Replace tabs and repeated horizontal whitespace
        text = re.sub(r"[ \t]+", " ", text)

        # Remove spaces around line breaks
        text = re.sub(r" *\n *", "\n", text)

        # Collapse excessive blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    def clean_documents(
        self,
        documents: list[Document],
    ) -> list[Document]:
        cleaned_documents = []

        for document in documents:
            cleaned_content = self.clean_text(document.page_content)

            if not cleaned_content:
                continue

            cleaned_documents.append(
                Document(
                    page_content=cleaned_content,
                    metadata=document.metadata.copy(),
                )
            )

        return cleaned_documents
