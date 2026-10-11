"""Workspace automation studio for launching and configuring multi-app workflows."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.lokixai.automation.workspaces import WorkspaceManager, WorkspaceDefinition


class AutomationPage(QWidget):
    """Workspace Studio for managing productivity environments."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = WorkspaceManager()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header
        title_box = QVBoxLayout()
        h = QLabel("⚡ Automation Studio & Workspaces")
        h.setStyleSheet("font-size: 18px; font-weight: 700; color: #00f2fe;")
        s = QLabel("Activate curated application groups, open research portals, or define custom environments.")
        s.setStyleSheet("font-size: 12px; color: #94a3b8;")
        title_box.addWidget(h)
        title_box.addWidget(s)
        layout.addLayout(title_box)

        # Grid of Workspaces
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(16)

        grid = QGridLayout()
        grid.setSpacing(14)

        for idx, ws in enumerate(self.manager.get_all()):
            card = self._create_card(ws)
            grid.addWidget(card, idx // 2, idx % 2)

        c_layout.addLayout(grid)
        c_layout.addStretch()

        scroll.setWidget(container)
        layout.addWidget(scroll, 1)

    def _create_card(self, ws: WorkspaceDefinition) -> QFrame:
        card = QFrame()
        card.setObjectName("CardFrame")
        l = QVBoxLayout(card)
        l.setContentsMargins(16, 16, 16, 16)
        l.setSpacing(10)

        top = QHBoxLayout()
        icon = QLabel(ws.icon)
        icon.setStyleSheet("font-size: 24px;")
        title = QLabel(ws.name)
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #f8fafc;")
        top.addWidget(icon)
        top.addWidget(title)
        top.addStretch()

        launch_btn = QPushButton("Launch Workspace ⚡")
        launch_btn.setObjectName("PrimaryButton")
        launch_btn.clicked.connect(lambda checked=False, name=ws.name: self._launch(name, status_lbl))
        top.addWidget(launch_btn)
        l.addLayout(top)

        desc = QLabel(ws.description)
        desc.setStyleSheet("font-size: 12px; color: #94a3b8;")
        desc.setWordWrap(True)
        l.addWidget(desc)

        # Apps & URLs pills
        pills_box = QHBoxLayout()
        apps_txt = f"Apps: {', '.join(ws.apps) if ws.apps else 'None'}"
        urls_txt = f"Websites: {', '.join(ws.urls) if ws.urls else 'None'}"
        
        a_lbl = QLabel(apps_txt)
        a_lbl.setStyleSheet("font-size: 11px; color: #38bdf8; background-color: #0c1322; padding: 4px 8px; border-radius: 4px;")
        u_lbl = QLabel(urls_txt)
        u_lbl.setStyleSheet("font-size: 11px; color: #a78bfa; background-color: #0c1322; padding: 4px 8px; border-radius: 4px;")
        pills_box.addWidget(a_lbl)
        pills_box.addWidget(u_lbl)
        pills_box.addStretch()
        l.addLayout(pills_box)

        status_lbl = QLabel("")
        status_lbl.setStyleSheet("font-size: 11px; color: #10b981; font-weight: 600;")
        l.addWidget(status_lbl)

        return card

    def _launch(self, name: str, status_lbl: QLabel):
        status_lbl.setText("Launching workspace items...")
        success = self.manager.launch(name)
        if success:
            status_lbl.setText(f"✓ {name} workspace activated successfully.")
        else:
            status_lbl.setText(f"⚠️ Partial launch completed for {name}.")
