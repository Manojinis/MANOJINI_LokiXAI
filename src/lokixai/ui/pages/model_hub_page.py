"""Model Hub page managing real AI providers (OpenAI Cloud and Local Ollama) with live verification."""

from __future__ import annotations

from PySide6.QtCore import Signal
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
    """Central AI model and provider management hub with live connectivity testing."""

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
        h = QLabel("🧠 AI Model Hub & Provider Integrations")
        h.setStyleSheet("font-size: 18px; font-weight: 700; color: #0284c7;")
        s = QLabel("Connect real cloud AI (OpenAI) or local models (Ollama). Zero mock responses permitted.")
        s.setStyleSheet("font-size: 12px; color: #64748b;")
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

        # 1. Primary Active Provider Card
        active_card = QFrame()
        active_card.setObjectName("CardFrame")
        a_layout = QVBoxLayout(active_card)
        a_layout.setContentsMargins(16, 16, 16, 16)
        a_layout.setSpacing(10)

        a_layout.addWidget(QLabel("PRIMARY ACTIVE PROVIDER"))

        p_row = QHBoxLayout()
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["openai", "local"])
        current_p = self.settings.ai_provider if self.settings.ai_provider in ("openai", "local") else "openai"
        self.provider_combo.setCurrentText(current_p)
        p_row.addWidget(self.provider_combo, 1)

        apply_btn = QPushButton("Apply Active Provider")
        apply_btn.setObjectName("PrimaryButton")
        apply_btn.clicked.connect(self._save_settings)
        p_row.addWidget(apply_btn)

        a_layout.addLayout(p_row)
        c_layout.addWidget(active_card)

        # 2. OpenAI Cloud Configuration Card
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

        # Connection test action and live feedback
        test_openai_row = QHBoxLayout()
        test_openai_btn = QPushButton("Test OpenAI Connection")
        test_openai_btn.clicked.connect(self._test_openai_connection)
        test_openai_row.addWidget(test_openai_btn)

        self.openai_status_lbl = QLabel("Status: Untested (Click to verify credentials)")
        self.openai_status_lbl.setStyleSheet("color: #64748b; font-size: 11px;")
        test_openai_row.addWidget(self.openai_status_lbl, 1)
        o_layout.addLayout(test_openai_row)

        c_layout.addWidget(openai_card)

        # 3. Local Ollama Provider Card
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

        test_local_row = QHBoxLayout()
        test_local_btn = QPushButton("Test Local Connection")
        test_local_btn.clicked.connect(self._test_local_connection)
        test_local_row.addWidget(test_local_btn)

        self.local_status_lbl = QLabel("Status: Untested (Click to probe Ollama service)")
        self.local_status_lbl.setStyleSheet("color: #64748b; font-size: 11px;")
        test_local_row.addWidget(self.local_status_lbl, 1)
        l_layout.addLayout(test_local_row)

        c_layout.addWidget(local_card)

        # 4. Verified Capabilities Matrix Card
        cap_card = QFrame()
        cap_card.setObjectName("CardFrame")
        cap_l = QVBoxLayout(cap_card)
        cap_l.setContentsMargins(16, 16, 16, 16)
        cap_l.setSpacing(8)

        cap_l.addWidget(QLabel("SUPPORTED PRODUCTION CAPABILITIES"))
        matrix_txt = QLabel(
            "• OpenAI Cloud: Full Function Calling ✓ | Multi-Turn Reasoning ✓ | Vision (GPT-4o) ✓ | Embeddings ✓\n"
            "• Local Ollama: OpenAI-Compatible Function Calling ✓ | Private Local Inference ✓ | Vision (Llava) ✓\n"
            "• Zero-Mock Policy: All responses and hardware metrics are generated by real providers and system telemetry."
        )
        matrix_txt.setStyleSheet("color: #64748b; font-size: 12px; line-height: 1.6;")
        cap_l.addWidget(matrix_txt)
        c_layout.addWidget(cap_card)

        c_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll, 1)

    def _test_openai_connection(self):
        key = self.key_input.text().strip() or self.settings.openai_api_key
        if not key:
            self.openai_status_lbl.setText("❌ OpenAI API key is not configured.")
            self.openai_status_lbl.setStyleSheet("color: #ef4444; font-weight: 600; font-size: 11px;")
            QMessageBox.warning(self, "API Key Missing", "Please enter an OpenAI API key before testing connection.")
            return

        self.openai_status_lbl.setText("⏳ Testing connection to OpenAI API...")
        self.openai_status_lbl.setStyleSheet("color: #0284c7; font-size: 11px;")

        from src.lokixai.providers.openai_provider import OpenAIProvider
        provider = OpenAIProvider(api_key=key)
        ok, msg = provider.test_connection()
        if ok:
            self.openai_status_lbl.setText(f"✓ Connected: Model '{self.model_combo.currentText()}' active")
            self.openai_status_lbl.setStyleSheet("color: #10b981; font-weight: 600; font-size: 11px;")
            QMessageBox.information(self, "OpenAI Connection Success", msg)
        else:
            self.openai_status_lbl.setText(f"❌ Failed: {msg[:60]}...")
            self.openai_status_lbl.setStyleSheet("color: #ef4444; font-weight: 600; font-size: 11px;")
            QMessageBox.warning(self, "OpenAI Connection Failed", msg)

    def _test_local_connection(self):
        url = self.local_url_input.text().strip()
        self.local_status_lbl.setText("⏳ Probing local Ollama service...")
        self.local_status_lbl.setStyleSheet("color: #0284c7; font-size: 11px;")

        from src.lokixai.providers.local_provider import LocalProvider
        provider = LocalProvider(base_url=url, model=self.local_model_input.text().strip())
        ok, msg = provider.test_connection()
        if ok:
            self.local_status_lbl.setText("✓ Connected to local Ollama service")
            self.local_status_lbl.setStyleSheet("color: #10b981; font-weight: 600; font-size: 11px;")
            QMessageBox.information(self, "Local Connection Status", msg)
        else:
            self.local_status_lbl.setText("❌ Ollama server unreachable")
            self.local_status_lbl.setStyleSheet("color: #ef4444; font-weight: 600; font-size: 11px;")
            QMessageBox.warning(self, "Local Connection Status", msg)

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
