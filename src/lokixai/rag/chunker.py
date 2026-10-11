"""Text chunker with configurable token/character window and overlap."""

from __future__ import annotations

from typing import List
from pydantic import BaseModel, Field

from .document_loader import LoadedDocument


class DocumentChunk(BaseModel):
    chunk_id: str
    document_name: str
    file_path: str
    page_number: int
    text: str
    chunk_index: int


class TextChunker:
    """Splits documents into overlapping semantic passages."""

    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, doc: LoadedDocument) -> List[DocumentChunk]:
        chunks: List[DocumentChunk] = []
        overall_idx = 0

        for page in doc.pages:
            text = page.text
            if not text:
                continue

            start = 0
            while start < len(text):
                end = min(start + self.chunk_size, len(text))
                passage = text[start:end].strip()

                if passage:
                    chunks.append(DocumentChunk(
                        chunk_id=f"{doc.file_name}_p{page.page_number}_c{overall_idx}",
                        document_name=doc.file_name,
                        file_path=doc.file_path,
                        page_number=page.page_number,
                        text=passage,
                        chunk_index=overall_idx,
                    ))
                    overall_idx += 1

                if end == len(text):
                    break
                start += (self.chunk_size - self.chunk_overlap)

        return chunks
