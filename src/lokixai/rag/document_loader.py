"""Document ingestion and text extraction for PDF, Markdown, and text files."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("lokixai.rag.loader")


class DocumentPage(BaseModel):
    page_number: int
    text: str
    metadata: Dict[str, str] = Field(default_factory=dict)


class LoadedDocument(BaseModel):
    file_path: str
    file_name: str
    pages: List[DocumentPage] = Field(default_factory=list)
    total_characters: int = 0


class DocumentLoader:
    """Safely extracts text and structure from user-provided files."""

    @staticmethod
    def load(file_path: str) -> LoadedDocument:
        path = Path(file_path).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        suffix = path.suffix.lower()
        pages: List[DocumentPage] = []

        if suffix == ".pdf":
            pages = DocumentLoader._load_pdf(path)
        else:
            pages = DocumentLoader._load_text(path)

        total_chars = sum(len(p.text) for p in pages)
        return LoadedDocument(
            file_path=str(path),
            file_name=path.name,
            pages=pages,
            total_characters=total_chars,
        )

    @staticmethod
    def _load_pdf(path: Path) -> List[DocumentPage]:
        import pypdf

        pages: List[DocumentPage] = []
        try:
            reader = pypdf.PdfReader(str(path))
            if reader.is_encrypted:
                raise ValueError("PDF is password protected.")

            for idx, page in enumerate(reader.pages):
                extracted = page.extract_text() or ""
                pages.append(DocumentPage(
                    page_number=idx + 1,
                    text=extracted.strip(),
                    metadata={"source": path.name, "type": "pdf"},
                ))
        except Exception as e:
            logger.error(f"Error reading PDF {path}: {e}")
            raise
        return pages

    @staticmethod
    def _load_text(path: Path) -> List[DocumentPage]:
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error reading text file {path}: {e}")
            raise

        return [DocumentPage(
            page_number=1,
            text=content.strip(),
            metadata={"source": path.name, "type": path.suffix},
        )]
