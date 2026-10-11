"""Security confirmation dialogs and user consent modals."""

from __future__ import annotations

import json
from typing import Any, Dict
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
)

from src.lokixai.security.permissions import PermissionLevel


class ConfirmationDialog(QDialog):
    """Explicit modal dialog confirming sensitive or destructive operations."""

    def __init__(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        level: PermissionLevel,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Security Confirmation — LokiXAI")
        self.setFixedSize(480, 320)
        self.setModal(True)
        self._init_ui(tool_name, parameters, level)

    def _init_ui(self, tool_name: str, parameters: Dict[str, Any], level: PermissionLevel):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Alert header
        header_box = QHBoxLayout()
        icon = QLabel("⚠️")
        icon.setStyleSheet("font-size: 24px;")
        
        info_box = QVBoxLayout()
        title = QLabel(f"Authorization Required: {tool_name}")
        title.setStyleSheet("font-size: 15px; font-weight: 700; color: #f59e0b;")
        
        risk_desc = (
            "This action is classified as DESTRUCTIVE (file modification or system change)."
            if level == PermissionLevel.DESTRUCTIVE_ACTION
            else "This action modifies laptop settings or opens external resources."
        )
        subtitle = QLabel(risk_desc)
        subtitle.setStyleSheet("font-size: 11px; color: #94a3b8;")
        subtitle.setWordWrap(True)

        info_box.addWidget(title)
        info_box.addWidget(subtitle)
        header_box.addWidget(icon)
        header_box.addLayout(info_box)
        layout.addLayout(header_box)

        # Parameters view
        params_label = QLabel("Action Parameters:")
        params_label.setStyleSheet("font-size: 11px; font-weight: 600; color: #64748b;")
        layout.addWidget(params_label)

        param_text = QPlainTextEdit()
        param_text.setReadOnly(True)
        param_text.setPlainText(json.dumps(parameters, indent=2))
        param_text.setStyleSheet("""
            background-color: #0c1322;
            border: 1px solid #1e293b;
            color: #38bdf8;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 11px;
        """)
        layout.addWidget(param_text)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel & Reject")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        self.confirm_btn = QPushButton("Authorize Action")
        if level == PermissionLevel.DESTRUCTIVE_ACTION:
            self.confirm_btn.setObjectName("DangerButton")
        else:
            self.confirm_btn.setObjectName("PrimaryButton")
        self.confirm_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.confirm_btn)

        layout.addLayout(btn_layout)
