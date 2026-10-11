"""Semantic vector store and retrieval engine with source citation tracking."""

from __future__ import annotations

import json
import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from src.lokixai.config.settings import get_settings
from src.lokixai.providers import BaseProvider, get_provider
from .chunker import DocumentChunk, TextChunker
from .document_loader import DocumentLoader

logger = logging.getLogger("lokixai.rag.store")


class RetrievalResult(BaseModel):
    chunk: DocumentChunk
    similarity_score: float


class DocumentIndexEntry(BaseModel):
    file_name: str
    file_path: str
    chunk_count: int
    indexed_at: str


class VectorStore:
    """Manages document chunk embeddings and similarity search."""

    def __init__(self, data_dir: str = "data/knowledge"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.store_file = self.data_dir / "vector_index.json"

        self.chunks: List[DocumentChunk] = []
        self.embeddings: List[List[float]] = []
        self.indexed_files: Dict[str, DocumentIndexEntry] = {}

        self.load()

    def load(self) -> None:
        if not self.store_file.exists():
            return
        try:
            with open(self.store_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.chunks = [DocumentChunk(**c) for c in data.get("chunks", [])]
                self.embeddings = data.get("embeddings", [])
                self.indexed_files = {
                    k: DocumentIndexEntry(**v) for k, v in data.get("indexed_files", {}).items()
                }
        except Exception as e:
            logger.warning(f"Could not load vector index: {e}")

    def save(self) -> None:
        try:
            data = {
                "chunks": [c.model_dump() for c in self.chunks],
                "embeddings": self.embeddings,
                "indexed_files": {k: v.model_dump() for k, v in self.indexed_files.items()},
            }
            with open(self.store_file, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Failed to save vector index: {e}")

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    def add_document(self, file_path: str, provider: Optional[BaseProvider] = None) -> int:
        """Load, chunk, embed, and store document passages."""
        doc = DocumentLoader.load(file_path)
        chunker = TextChunker()
        new_chunks = chunker.chunk_document(doc)
        if not new_chunks:
            return 0

        # Remove existing index for this file if present
        self.remove_document(doc.file_name)

        active_provider = provider or get_provider(get_settings().ai_provider)
        texts = [c.text for c in new_chunks]

        try:
            new_embeddings = active_provider.embed(texts)
        except Exception as e:
            logger.warning(f"Embedding generation with provider failed: {e}. Using local hash vectors.")
            import hashlib
            new_embeddings = []
            for t in texts:
                seed = int(hashlib.md5(t.encode()).hexdigest()[:8], 16)
                new_embeddings.append([(seed % (i + 1)) / 100.0 for i in range(128)])

        self.chunks.extend(new_chunks)
        self.embeddings.extend(new_embeddings)

        import datetime
        self.indexed_files[doc.file_name] = DocumentIndexEntry(
            file_name=doc.file_name,
            file_path=doc.file_path,
            chunk_count=len(new_chunks),
            indexed_at=datetime.datetime.now().isoformat(),
        )

        self.save()
        return len(new_chunks)

    def remove_document(self, file_name: str) -> None:
        kept_chunks = []
        kept_embeddings = []
        for c, emb in zip(self.chunks, self.embeddings):
            if c.document_name != file_name:
                kept_chunks.append(c)
                kept_embeddings.append(emb)

        self.chunks = kept_chunks
        self.embeddings = kept_embeddings
        self.indexed_files.pop(file_name, None)
        self.save()

    def query(self, query_text: str, top_k: int = 3, provider: Optional[BaseProvider] = None) -> List[RetrievalResult]:
        """Perform semantic search across indexed passages."""
        if not self.chunks or not self.embeddings:
            return []

        active_provider = provider or get_provider(get_settings().ai_provider)
        try:
            q_emb = active_provider.embed([query_text])[0]
        except Exception:
            import hashlib
            seed = int(hashlib.md5(query_text.encode()).hexdigest()[:8], 16)
            q_emb = [(seed % (i + 1)) / 100.0 for i in range(len(self.embeddings[0]))]

        scored: List[Tuple[float, DocumentChunk]] = []
        for c, emb in zip(self.chunks, self.embeddings):
            score = self._cosine_similarity(q_emb, emb)
            scored.append((score, c))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            RetrievalResult(chunk=chunk, similarity_score=round(score, 4))
            for score, chunk in scored[:top_k]
        ]


_global_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    global _global_vector_store
    if _global_vector_store is None:
        _global_vector_store = VectorStore()
    return _global_vector_store
