"""Sidebar navigation component for LokiXAI desktop shell with categorized sections."""

from __future__ import annotations

from typing import List, Tuple, Union
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

# Nav items with optional section headers (header_text or tuple of (key, label, tooltip))
NAV_SECTIONS: List[Union[str, Tuple[str, str, str]]] = [
    "CORE ASSISTANT",
    ("overview", "🏠 Overview", "Hardware Dashboard & Command Center"),
    ("chat", "💬 AI Chat", "Context-Aware AI Conversation"),
    ("voice", "🎙️ Voice Assistant", "Push-to-Talk Speech Copilot"),

    "AUTOMATION & SYSTEM",
    ("monitor", "📊 System Monitor", "Hardware Telemetry & Processes"),
    ("automation", "⚡ Workspaces", "App Automation Presets"),
    ("routines", "🔁 Smart Routines", "Sequential Workflow Automation"),

    "INTELLIGENT TOOLS",
    ("knowledge", "📚 Knowledge Base", "RAG Document Indexing & Search"),
    ("files", "📁 File Manager", "Safe Workspace File Operations"),
    ("developer", "🛠️ Developer Copilot", "AST Code Inspector & Review"),
    ("screen", "👁️ Screen Assistant", "Vision Analysis of Display"),

    "PREFERENCES & AUDIT",
    ("model_hub", "🤖 Model Hub", "AI Models & Provider Settings"),
    ("audit", "🛡️ Audit & Activity", "Security Logs & Redaction"),
    ("settings", "⚙️ Settings", "Appearance Themes & Configuration"),
]


class Sidebar(QFrame):
    """Categorized navigation sidebar."""

    page_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SidebarFrame")
        self.setFixedWidth(240)
        self.buttons: dict[str, QPushButton] = {}
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(6)

        # Brand header
        brand_layout = QVBoxLayout()
        brand_layout.setSpacing(2)

        logo_label = QLabel("⚡ LokiXAI")
        logo_label.setObjectName("PageTitle")
        logo_label.setStyleSheet("font-size: 20px; font-weight: 800; letter-spacing: 1px;")
        subtitle_label = QLabel("Laptop Copilot • v1.0")
        subtitle_label.setObjectName("SubText")
        subtitle_label.setStyleSheet("font-size: 11px; font-weight: 500;")

        brand_layout.addWidget(logo_label)
        brand_layout.addWidget(subtitle_label)
        layout.addLayout(brand_layout)
        layout.addSpacing(10)

        # Scrollable navigation list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(3)

        for item in NAV_SECTIONS:
            if isinstance(item, str):
                # Section Header
                sec_lbl = QLabel(item)
                sec_lbl.setObjectName("SectionTitle")
                sec_lbl.setStyleSheet("font-size: 10px; font-weight: 700; padding-top: 10px; padding-bottom: 2px;")
                c_layout.addWidget(sec_lbl)
            else:
                key, label, tooltip = item
                btn = QPushButton(label)
                btn.setObjectName("NavButton")
                btn.setToolTip(tooltip)
                btn.setCursor(Qt.PointingHandCursor)
                btn.clicked.connect(lambda checked=False, k=key: self._on_nav_click(k))
                c_layout.addWidget(btn)
                self.buttons[key] = btn

        c_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)

        # Security badge at bottom
        sec_frame = QFrame()
        sec_frame.setObjectName("InnerBox")
        sec_layout = QHBoxLayout(sec_frame)
        sec_layout.setContentsMargins(8, 8, 8, 8)

        sec_icon = QLabel("🔒")
        sec_icon.setStyleSheet("font-size: 14px;")
        sec_text = QLabel("Security Guard Active\nZero-Mock Policy")
        sec_text.setObjectName("SubText")
        sec_text.setStyleSheet("font-size: 10px; line-height: 1.2;")
        sec_layout.addWidget(sec_icon)
        sec_layout.addWidget(sec_text)
        layout.addWidget(sec_frame)

        # Set default active
        self.set_active("overview")

    def _on_nav_click(self, key: str):
        self.set_active(key)
        self.page_selected.emit(key)

    def set_active(self, active_key: str):
        for key, btn in self.buttons.items():
            is_active = (key == active_key)
            btn.setProperty("active", "true" if is_active else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
