"""Settings and application personalization page."""

from __future__ import annotations

from pathlib import Path
from PySide6.QtCore import Qt
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
        h.setStyleSheet("font-size: 18px; font-weight: 700; color: #00f2fe;")
        s = QLabel("Configure security permissions, approved directory boundaries, and application behavior.")
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

        # 1. Security & Privacy Card
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

        # 2. Approved Directories Card
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

        # 3. Speech & Voice Card
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

    def _save_preferences(self):
        self.settings.auto_approve_safe_tools = self.auto_safe_chk.isChecked()
        self.settings.require_confirmation_destructive = self.require_confirm_chk.isChecked()
        self.settings.tts_enabled = self.tts_enable_chk.isChecked()

        raw_dirs = self.dirs_edit.toPlainText().replace("\n", "").split(";")
        clean_dirs = [d.strip() for d in raw_dirs if d.strip()]
        if clean_dirs:
            self.settings.approved_directories = clean_dirs

        self.settings.save()
        QMessageBox.information(self, "Settings Saved", "Your configuration has been updated.")

    def _reset_defaults(self):
        self.auto_safe_chk.setChecked(True)
        self.require_confirm_chk.setChecked(True)
        self.tts_enable_chk.setChecked(True)
        self.dirs_edit.setPlainText(str(Path.cwd()))
        QMessageBox.information(self, "Reset", "Values restored to defaults. Click 'Save Preferences' to persist.")
