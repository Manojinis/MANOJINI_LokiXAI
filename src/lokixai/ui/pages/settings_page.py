"""Settings and application personalization page."""

from __future__ import annotations

from pathlib import Path
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.lokixai.config.settings import get_settings


class SettingsPage(QWidget):
    """Central settings manager for LokiXAI application."""

    theme_changed = Signal(str)
    provider_changed = Signal(str)

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
        h = QLabel("⚙️ Settings & System Personalization")
        h.setStyleSheet("font-size: 18px; font-weight: 700; color: #0284c7;")
        s = QLabel("Configure appearance themes, AI credentials, security boundaries, and preferences.")
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

        # 0. Appearance & Theme Card
        theme_card = QFrame()
        theme_card.setObjectName("CardFrame")
        tl = QVBoxLayout(theme_card)
        tl.setContentsMargins(16, 16, 16, 16)
        tl.setSpacing(10)
        tl.addWidget(QLabel("APPEARANCE & THEME"))

        theme_row = QHBoxLayout()
        theme_lbl = QLabel("Interface Theme:")
        theme_lbl.setFixedWidth(130)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light", "system"])
        self.theme_combo.setCurrentText(self.settings.theme or "dark")
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        theme_row.addWidget(theme_lbl)
        theme_row.addWidget(self.theme_combo, 1)
        tl.addLayout(theme_row)
        c_layout.addWidget(theme_card)

        # 1. AI Provider Card (Zero-Mock Policy: OpenAI and Local Ollama only)
        ai_card = QFrame()
        ai_card.setObjectName("CardFrame")
        ail = QVBoxLayout(ai_card)
        ail.setContentsMargins(16, 16, 16, 16)
        ail.setSpacing(10)
        ail.addWidget(QLabel("AI PROVIDER & CREDENTIALS"))

        prov_row = QHBoxLayout()
        prov_lbl = QLabel("Active Provider:")
        prov_lbl.setFixedWidth(130)
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["openai", "local"])
        current_p = self.settings.ai_provider if self.settings.ai_provider in ("openai", "local") else "openai"
        self.provider_combo.setCurrentText(current_p)
        prov_row.addWidget(prov_lbl)
        prov_row.addWidget(self.provider_combo, 1)
        ail.addLayout(prov_row)

        key_row = QHBoxLayout()
        key_lbl = QLabel("OpenAI API Key:")
        key_lbl.setFixedWidth(130)
        self.key_input = QLineEdit()
        self.key_input.setEchoMode(QLineEdit.Password)
        self.key_input.setText(self.settings.openai_api_key or "")
        self.key_input.setPlaceholderText("sk-...")
        key_row.addWidget(key_lbl)
        key_row.addWidget(self.key_input, 1)
        ail.addLayout(key_row)

        c_layout.addWidget(ai_card)

        # 2. Security & Privacy Card
        sec_card = QFrame()
        sec_card.setObjectName("CardFrame")
        sl = QVBoxLayout(sec_card)
        sl.setContentsMargins(16, 16, 16, 16)
        sl.setSpacing(10)
        sl.addWidget(QLabel("SECURITY & PERMISSION GUARD"))

        self.auto_safe_chk = QCheckBox("Auto-approve safe read-only and non-destructive tools")
        self.auto_safe_chk.setChecked(self.settings.auto_approve_safe_tools)
        sl.addWidget(self.auto_safe_chk)

        self.require_confirm_chk = QCheckBox("Require explicit popup confirmation for destructive actions (File Delete / Move)")
        self.require_confirm_chk.setChecked(self.settings.require_confirmation_destructive)
        sl.addWidget(self.require_confirm_chk)

        c_layout.addWidget(sec_card)

        # 3. Approved Directories Card
        dir_card = QFrame()
        dir_card.setObjectName("CardFrame")
        dl = QVBoxLayout(dir_card)
        dl.setContentsMargins(16, 16, 16, 16)
        dl.setSpacing(8)
        dl.addWidget(QLabel("APPROVED DIRECTORY BOUNDARIES (SEPARATED BY SEMICOLON)"))

        self.dirs_edit = QPlainTextEdit()
        self.dirs_edit.setFixedHeight(75)
        self.dirs_edit.setPlainText("; ".join(self.settings.approved_directories))
        dl.addWidget(self.dirs_edit)
        c_layout.addWidget(dir_card)

        # 4. Speech & Voice Card
        voice_card = QFrame()
        voice_card.setObjectName("CardFrame")
        vl = QVBoxLayout(voice_card)
        vl.setContentsMargins(16, 16, 16, 16)
        vl.setSpacing(10)
        vl.addWidget(QLabel("AUDIO & TEXT-TO-SPEECH"))

        self.tts_enable_chk = QCheckBox("Enable Spoken Text-to-Speech Responses (TTS)")
        self.tts_enable_chk.setChecked(self.settings.tts_enabled)
        vl.addWidget(self.tts_enable_chk)

        c_layout.addWidget(voice_card)

        # Bottom Buttons
        btn_box = QHBoxLayout()
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self._reset_defaults)
        btn_box.addWidget(reset_btn)

        btn_box.addStretch()

        save_btn = QPushButton("Save Preferences")
        save_btn.setObjectName("PrimaryButton")
        save_btn.clicked.connect(self._save_preferences)
        btn_box.addWidget(save_btn)

        c_layout.addLayout(btn_box)
        c_layout.addStretch()

        scroll.setWidget(container)
        layout.addWidget(scroll, 1)

    def _on_theme_changed(self, new_theme: str):
        self.settings.theme = new_theme
        self.settings.save()
        self.theme_changed.emit(new_theme)

    def _save_preferences(self):
        new_theme = self.theme_combo.currentText()
        self.settings.theme = new_theme
        self.theme_changed.emit(new_theme)

        self.settings.ai_provider = self.provider_combo.currentText()
        new_key = self.key_input.text().strip()
        if new_key:
            self.settings.openai_api_key = new_key
        self.settings.auto_approve_safe_tools = self.auto_safe_chk.isChecked()
        self.settings.require_confirmation_destructive = self.require_confirm_chk.isChecked()
        self.settings.tts_enabled = self.tts_enable_chk.isChecked()

        raw_dirs = self.dirs_edit.toPlainText().replace("\n", "").split(";")
        clean_dirs = [d.strip() for d in raw_dirs if d.strip()]
        if clean_dirs:
            self.settings.approved_directories = clean_dirs

        self.settings.save()
        self.provider_changed.emit(self.settings.ai_provider)
        QMessageBox.information(self, "Settings Saved", f"Configuration updated. Active theme: {new_theme.upper()}.")

    def _reset_defaults(self):
        self.theme_combo.setCurrentText("dark")
        self.provider_combo.setCurrentText("openai")
        self.auto_safe_chk.setChecked(True)
        self.require_confirm_chk.setChecked(True)
        self.tts_enable_chk.setChecked(True)
        self.dirs_edit.setPlainText(str(Path.cwd()))
        self._on_theme_changed("dark")
        QMessageBox.information(self, "Reset", "Values restored to defaults. Click 'Save Preferences' to persist.")
