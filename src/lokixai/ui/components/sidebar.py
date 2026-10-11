"""Sidebar navigation component for LokiXAI desktop shell."""

from __future__ import annotations

from typing import Callable, List, Tuple
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


NAV_ITEMS: List[Tuple[str, str, str]] = [
    ("overview", "🏠 Overview", "Dashboard"),
    ("chat", "💬 AI Chat", "Conversation"),
    ("voice", "🎙️ Voice Assistant", "Push-to-talk"),
    ("monitor", "📊 System Monitor", "Hardware Telemetry"),
    ("automation", "⚡ Workspaces", "App Automation"),
    ("routines", "🔁 Smart Routines", "Workflow Sequences"),
    ("knowledge", "📚 Knowledge Base", "RAG Documents"),
    ("files", "📁 File Manager", "Safe Browser"),
    ("developer", "🛠️ Developer Copilot", "Code Inspection"),
    ("screen", "👁️ Screen Assistant", "Vision Analysis"),
    ("model_hub", "🤖 Model Hub", "AI Providers"),
    ("audit", "🛡️ Audit & Activity", "Security Logs"),
    ("settings", "⚙️ Settings", "Configuration"),
]


class Sidebar(QFrame):
    """Futuristic navigation sidebar."""

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
        logo_label.setStyleSheet("font-size: 20px; font-weight: 800; color: #00f2fe; letter-spacing: 1px;")
        subtitle_label = QLabel("Laptop Copilot • v1.0")
        subtitle_label.setStyleSheet("font-size: 11px; color: #64748b; font-weight: 500;")
        
        brand_layout.addWidget(logo_label)
        brand_layout.addWidget(subtitle_label)
        layout.addLayout(brand_layout)
        layout.addSpacing(14)

        # Scrollable navigation list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(4)

        for key, label, tooltip in NAV_ITEMS:
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
        sec_frame.setStyleSheet("""
            background-color: #131d31;
            border: 1px solid #1e293b;
            border-radius: 8px;
            padding: 8px;
        """)
        sec_layout = QHBoxLayout(sec_frame)
        sec_layout.setContentsMargins(4, 4, 4, 4)
        
        sec_icon = QLabel("🔒")
        sec_text = QLabel("Security Guard Active\nSandboxed Access")
        sec_text.setStyleSheet("font-size: 10px; color: #94a3b8;")
        sec_layout.addWidget(sec_icon)
        sec_layout.addWidget(sec_text)
        layout.addWidget(sec_frame)

        # Set default active
        self.set_active("overview")

    def _on_nav_click(self, key: str):
        self.set_active(key)
        self.page_selected.emit(key)

    def set_active(self, key: str):
        for k, btn in self.buttons.items():
            if k == key:
                btn.setProperty("active", "true")
            else:
                btn.setProperty("active", "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
