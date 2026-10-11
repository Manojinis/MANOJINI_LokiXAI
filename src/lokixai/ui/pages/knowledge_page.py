"""Knowledge Base page for RAG document indexing, semantic query, and citation viewing."""

from __future__ import annotations

from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.lokixai.rag.vector_store import get_vector_store, RetrievalResult


class KnowledgePage(QWidget):
    """Document Assistant for semantic search and RAG knowledge retrieval."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.store = get_vector_store()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header
        title_box = QVBoxLayout()
        h = QLabel("📚 Knowledge Base & Document Assistant (RAG)")
        h.setStyleSheet("font-size: 18px; font-weight: 700; color: #00f2fe;")
        s = QLabel("Index PDFs, Markdown notes, or text files to retrieve verified passages with page-level citations.")
        s.setStyleSheet("font-size: 12px; color: #94a3b8;")
        title_box.addWidget(h)
        title_box.addWidget(s)
        layout.addLayout(title_box)

        # Ingestion Toolbar
        tool_frame = QFrame()
        tool_frame.setObjectName("CardFrame")
        t_layout = QHBoxLayout(tool_frame)
        t_layout.setContentsMargins(12, 12, 12, 12)
        t_layout.setSpacing(12)

        self.index_btn = QPushButton("📁 Select & Index Document")
        self.index_btn.setObjectName("PrimaryButton")
        self.index_btn.clicked.connect(self._select_and_index)
        t_layout.addWidget(self.index_btn)

        self.status_lbl = QLabel(f"Indexed Documents: {len(self.store.indexed_files)} | Total Chunks: {len(self.store.chunks)}")
        self.status_lbl.setStyleSheet("color: #94a3b8; font-size: 12px;")
        t_layout.addWidget(self.status_lbl)
        t_layout.addStretch()

        layout.addWidget(tool_frame)

        # Document chips frame
        self.docs_chip_frame = QFrame()
        self.docs_chip_frame.setStyleSheet("background: transparent;")
        self.chips_layout = QHBoxLayout(self.docs_chip_frame)
        self.chips_layout.setContentsMargins(0, 0, 0, 0)
        self.chips_layout.setSpacing(8)
        self._refresh_doc_chips()
        layout.addWidget(self.docs_chip_frame)

        # Disclosure notice
        privacy_note = QLabel("🔒 Privacy Notice: Documents are chunked locally. When cloud embeddings are configured, passages are securely embedded. When offline, local hash indexing is used.")
        privacy_note.setStyleSheet("font-size: 11px; color: #64748b; font-style: italic;")
        layout.addWidget(privacy_note)

        # Semantic Query Input
        search_box = QHBoxLayout()
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Enter question to search indexed passages (e.g. 'What are the security policies?')...")
        self.query_input.setFixedHeight(38)
        self.query_input.returnPressed.connect(self._perform_search)

        search_btn = QPushButton("Semantic Search 🔍")
        search_btn.setObjectName("PrimaryButton")
        search_btn.setFixedHeight(38)
        search_btn.clicked.connect(self._perform_search)

        search_box.addWidget(self.query_input)
        search_box.addWidget(search_btn)
        layout.addLayout(search_box)

        # Results area
        results_lbl = QLabel("RETRIEVED PASSAGES & CITATIONS")
        results_lbl.setStyleSheet("font-size: 11px; font-weight: 700; color: #64748b; letter-spacing: 0.5px;")
        layout.addWidget(results_lbl)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        self.results_container = QWidget()
        self.results_container.setStyleSheet("background: transparent;")
        self.res_layout = QVBoxLayout(self.results_container)
        self.res_layout.setContentsMargins(0, 0, 0, 0)
        self.res_layout.setSpacing(10)
        self.res_layout.addStretch()

        scroll.setWidget(self.results_container)
        layout.addWidget(scroll, 1)

    def _refresh_doc_chips(self):
        while self.chips_layout.count() > 0:
            item = self.chips_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for doc_name, entry in list(self.store.indexed_files.items()):
            chip = QPushButton(f"📄 {doc_name} ({entry.chunk_count} chunks) ✕")
            chip.setObjectName("SuggestionPill")
            chip.setToolTip("Click to remove from index")
            chip.clicked.connect(lambda checked=False, name=doc_name: self._remove_doc(name))
            self.chips_layout.addWidget(chip)
        self.chips_layout.addStretch()

    def _remove_doc(self, doc_name: str):
        self.store.remove_document(doc_name)
        self.status_lbl.setText(f"Removed {doc_name}. Total docs: {len(self.store.indexed_files)}")
        self._refresh_doc_chips()

    def _select_and_index(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Document", "", "Documents (*.pdf *.txt *.md *.py *.json)"
        )
        if not file_path:
            return

        self.status_lbl.setText("Extracting text and computing embeddings...")
        try:
            count = self.store.add_document(file_path)
            if count == 0:
                self.status_lbl.setText(f"⚠️ Document '{Path(file_path).name}' contains no extractable text (Scanned image or empty).")
            else:
                self.status_lbl.setText(
                    f"✓ Indexed {Path(file_path).name} ({count} chunks). Total docs: {len(self.store.indexed_files)}"
                )
                self._refresh_doc_chips()
        except Exception as e:
            self.status_lbl.setText(f"❌ Indexing failed: {e}")

    def _perform_search(self):
        query = self.query_input.text().strip()
        if not query:
            return

        # Clear previous results
        while self.res_layout.count() > 1:
            item = self.res_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        results = self.store.query(query, top_k=4)
        if not results:
            empty_card = QFrame()
            empty_card.setObjectName("CardFrame")
            el = QVBoxLayout(empty_card)
            el.addWidget(QLabel("No matching passages found. Index more documents or refine query."))
            self.res_layout.insertWidget(0, empty_card)
            return

        for r in results:
            card = self._create_result_card(r)
            self.res_layout.insertWidget(self.res_layout.count() - 1, card)

    def _create_result_card(self, r: RetrievalResult) -> QFrame:
        card = QFrame()
        card.setObjectName("CardFrame")
        l = QVBoxLayout(card)
        l.setContentsMargins(14, 14, 14, 14)
        l.setSpacing(8)

        # Header with source and score
        top = QHBoxLayout()
        source_lbl = QLabel(f"📄 {r.chunk.document_name} — Page {r.chunk.page_number}")
        source_lbl.setObjectName("SenderLabel")
        source_lbl.setStyleSheet("font-weight: 700; font-size: 12px;")
        
        score_lbl = QLabel(f"Relevance: {int(r.similarity_score * 100)}%")
        score_lbl.setStyleSheet("font-size: 11px; color: #10b981; font-weight: 600;")
        
        top.addWidget(source_lbl)
        top.addStretch()
        top.addWidget(score_lbl)
        l.addLayout(top)

        # Passage text
        text_lbl = QLabel(r.chunk.text)
        text_lbl.setStyleSheet("font-size: 12px; line-height: 1.4;")
        text_lbl.setWordWrap(True)
        text_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        l.addWidget(text_lbl)

        return card
