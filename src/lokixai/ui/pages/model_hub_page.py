"""Model Hub page for configuring AI providers, model parameters, and capability inspection."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.lokixai.config.settings import get_settings


class ModelHubPage(QWidget):
    """Multi-Model Hub for switching providers and verifying API endpoints."""

    model_changed = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = get_settings()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header
        title_box = QVBoxLayout()
        h = QLabel("🤖 Multi-Model Hub & Provider Switcher")
        h.setStyleSheet("font-size: 18px; font-weight: 700; color: #00f2fe;")
        s = QLabel("Connect to OpenAI, local Ollama/vLLM endpoints, or offline deterministic core.")
        s.setStyleSheet("font-size: 12px; color: #94a3b8;")
        title_box.addWidget(h)
        title_box.addWidget(s)
        layout.addLayout(title_box)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(16)

        # Provider Selector Card
        active_card = QFrame()
        active_card.setObjectName("CardFrame")
        a_layout = QVBoxLayout(active_card)
        a_layout.setContentsMargins(16, 16, 16, 16)
        a_layout.setSpacing(10)

        a_layout.addWidget(QLabel("PRIMARY ACTIVE PROVIDER"))

        p_row = QHBoxLayout()
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["openai", "local", "mock"])
        self.provider_combo.setCurrentText(self.settings.ai_provider)
        self.provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        p_row.addWidget(self.provider_combo, 1)

        apply_btn = QPushButton("Apply Active Provider")
        apply_btn.setObjectName("PrimaryButton")
        apply_btn.clicked.connect(self._save_settings)
        p_row.addWidget(apply_btn)

        a_layout.addLayout(p_row)
        c_layout.addWidget(active_card)

        # 1. OpenAI Configuration Card
        openai_card = QFrame()
        openai_card.setObjectName("CardFrame")
        o_layout = QVBoxLayout(openai_card)
        o_layout.setContentsMargins(16, 16, 16, 16)
        o_layout.setSpacing(10)

        o_layout.addWidget(QLabel("OPENAI CLOUD CONFIGURATION"))

        key_row = QHBoxLayout()
        key_lbl = QLabel("OpenAI API Key:")
        key_lbl.setFixedWidth(130)
        self.key_input = QLineEdit()
        self.key_input.setEchoMode(QLineEdit.Password)
        self.key_input.setText(self.settings.openai_api_key or "")
        self.key_input.setPlaceholderText("sk-...")
        key_row.addWidget(key_lbl)
        key_row.addWidget(self.key_input)
        o_layout.addLayout(key_row)

        model_row = QHBoxLayout()
        model_lbl = QLabel("Default Model:")
        model_lbl.setFixedWidth(130)
        self.model_combo = QComboBox()
        self.model_combo.addItems(["gpt-4o", "gpt-4o-mini", "o1-mini", "gpt-4-turbo"])
        self.model_combo.setCurrentText(self.settings.openai_model)
        model_row.addWidget(model_lbl)
        model_row.addWidget(self.model_combo)
        o_layout.addLayout(model_row)

        c_layout.addWidget(openai_card)

        # 2. Local Ollama Provider Card
        local_card = QFrame()
        local_card.setObjectName("CardFrame")
        l_layout = QVBoxLayout(local_card)
        l_layout.setContentsMargins(16, 16, 16, 16)
        l_layout.setSpacing(10)

        l_layout.addWidget(QLabel("LOCAL OLLAMA / VLLM CONFIGURATION"))

        url_row = QHBoxLayout()
        url_lbl = QLabel("Base API Endpoint:")
        url_lbl.setFixedWidth(130)
        self.local_url_input = QLineEdit()
        self.local_url_input.setText(self.settings.local_ai_base_url)
        url_row.addWidget(url_lbl)
        url_row.addWidget(self.local_url_input)
        l_layout.addLayout(url_row)

        lmodel_row = QHBoxLayout()
        lmodel_lbl = QLabel("Local Model Tag:")
        lmodel_lbl.setFixedWidth(130)
        self.local_model_input = QLineEdit()
        self.local_model_input.setText(self.settings.local_ai_model)
        lmodel_row.addWidget(lmodel_lbl)
        lmodel_row.addWidget(self.local_model_input)
        l_layout.addLayout(lmodel_row)

        test_local_btn = QPushButton("Test Local Connection")
        test_local_btn.clicked.connect(self._test_local_connection)
        l_layout.addWidget(test_local_btn)

        c_layout.addWidget(local_card)

        # 3. Capability Matrix Card
        cap_card = QFrame()
        cap_card.setObjectName("CardFrame")
        cap_l = QVBoxLayout(cap_card)
        cap_l.setContentsMargins(16, 16, 16, 16)
        cap_l.setSpacing(8)

        cap_l.addWidget(QLabel("PROVIDER CAPABILITIES MATRIX"))
        matrix_txt = QLabel(
            "• OpenAI: Function Calling ✓ | Vision ✓ | Streaming ✓ | RAG Embeddings ✓\n"
            "• Local Ollama: Function Calling ✓ | Vision (Llava) ✓ | Streaming ✓ | Embeddings ✓\n"
            "• Mock Core: Deterministic Tool Calling ✓ | Zero-API-Key ✓ | Offline Fallback ✓"
        )
        matrix_txt.setStyleSheet("color: #94a3b8; font-size: 12px; line-height: 1.5;")
        cap_l.addWidget(matrix_txt)
        c_layout.addWidget(cap_card)

        c_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll, 1)

    def _on_provider_changed(self):
        pass

    def _test_local_connection(self):
        url = self.local_url_input.text().strip()
        try:
            import urllib.request
            req = urllib.request.Request(url.replace("/v1", ""), method="GET")
            with urllib.request.urlopen(req, timeout=3) as resp:
                QMessageBox.information(self, "Connection Success", f"Connected successfully to local server at {url}!")
        except Exception as e:
            QMessageBox.warning(
                self,
                "Connection Warning",
                f"Could not connect to {url}: {e}\n(Ensure Ollama is running: 'ollama serve')",
            )

    def _save_settings(self):
        self.settings.ai_provider = self.provider_combo.currentText()
        if self.key_input.text().strip():
            self.settings.openai_api_key = self.key_input.text().strip()
        self.settings.openai_model = self.model_combo.currentText()
        self.settings.local_ai_base_url = self.local_url_input.text().strip()
        self.settings.local_ai_model = self.local_model_input.text().strip()
        self.settings.save()

        self.model_changed.emit(self.settings.ai_provider, self.settings.openai_model)
        QMessageBox.information(self, "Saved", f"Active provider set to {self.settings.ai_provider.upper()}.")
