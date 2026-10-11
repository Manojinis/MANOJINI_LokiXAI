"""Unit tests for RAG document chunking and vector storage."""

import pytest
from src.lokixai.rag.chunker import TextChunker
from src.lokixai.rag.document_loader import LoadedDocument, DocumentPage
from src.lokixai.rag.vector_store import VectorStore
from src.lokixai.providers.mock_provider import MockProvider


def test_chunker_basic():
    doc = LoadedDocument(
        file_path="sample.txt",
        file_name="sample.txt",
        pages=[DocumentPage(
            page_number=1,
            text="First sentence. Second sentence. Third sentence is quite long to ensure multiple chunks are generated properly.",
        )],
        total_characters=105,
    )

    chunker = TextChunker(chunk_size=40, chunk_overlap=10)
    chunks = chunker.chunk_document(doc)

    assert len(chunks) > 1
    assert chunks[0].document_name == "sample.txt"
    assert chunks[0].page_number == 1


def test_vector_store_add_and_query(tmp_path):
    store = VectorStore(data_dir=str(tmp_path))
    provider = MockProvider()

    sample_file = tmp_path / "guide.txt"
    sample_file.write_text("Windows 11 automation allows managing screen brightness, sound volume, and smart routines safely.")

    added = store.add_document(str(sample_file), provider=provider)
    assert added > 0
    assert "guide.txt" in store.indexed_files

    # Query
    results = store.query("screen brightness automation", top_k=1, provider=provider)
    assert len(results) == 1
    assert results[0].chunk.document_name == "guide.txt"
    assert results[0].similarity_score > 0.0
