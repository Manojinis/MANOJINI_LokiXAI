"""Top application header with live metrics pill, provider status, and quick actions."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

import os
from src.lokixai.config.settings import get_settings
from src.lokixai.monitoring.system_monitor import SystemMetrics


class Header(QFrame):
    """Top shell header."""

    quick_action_triggered = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("HeaderFrame")
        self.setFixedHeight(56)
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        # Title & subtitle
        title_box = QVBoxLayout()
        title_box.setSpacing(0)
        self.title_lbl = QLabel("Overview")
        self.title_lbl.setObjectName("HeaderTitle")
        self.sub_lbl = QLabel("System telemetry and copilot command center")
        self.sub_lbl.setObjectName("HeaderSubtitle")
        title_box.addWidget(self.title_lbl)
        title_box.addWidget(self.sub_lbl)
        layout.addLayout(title_box)

        layout.addStretch()

        # Telemetry Pill
        self.metric_pill = QLabel("CPU: --% | RAM: --% | Bat: --%")
        self.metric_pill.setObjectName("PillText")
        layout.addWidget(self.metric_pill)

        # Active Model Pill
        self.model_pill = QLabel("⚡ OPENAI: gpt-4o")
        self.model_pill.setObjectName("PillText")
        layout.addWidget(self.model_pill)

        # Quick action buttons
        self.mute_btn = QPushButton("🔊 Mute")
        self.mute_btn.setFixedHeight(30)
        self.mute_btn.clicked.connect(lambda: self.quick_action_triggered.emit("toggle_mute"))
        layout.addWidget(self.mute_btn)

        self.panel_btn = QPushButton("📊 Panel")
        self.panel_btn.setFixedHeight(30)
        self.panel_btn.setToolTip("Toggle Right Telemetry & Activity Panel")
        self.panel_btn.clicked.connect(lambda: self.quick_action_triggered.emit("toggle_panel"))
        layout.addWidget(self.panel_btn)

        self.screen_btn = QPushButton("📷 Analyze Screen")
        self.screen_btn.setFixedHeight(30)
        self.screen_btn.setObjectName("PrimaryButton")
        self.screen_btn.clicked.connect(lambda: self.quick_action_triggered.emit("analyze_screen"))
        layout.addWidget(self.screen_btn)

    def set_title(self, title: str, subtitle: str = ""):
        self.title_lbl.setText(title)
        self.sub_lbl.setText(subtitle)

    def update_metrics(self, m: SystemMetrics):
        bat_str = f"{m.battery_percent}%" if m.battery_percent is not None else "AC"
        self.metric_pill.setText(f"CPU: {m.cpu_percent}% | RAM: {m.ram_percent}% | Bat: {bat_str}")

    def set_model_label(self, provider: str, model_name: str):
        settings = get_settings()
        p_lower = provider.lower()
        if p_lower == "openai":
            has_key = bool(settings.openai_api_key or os.getenv("OPENAI_API_KEY"))
            if has_key:
                self.model_pill.setText(f"⚡ OPENAI: {model_name}")
                self.model_pill.setStyleSheet("""
                    background-color: rgba(2, 132, 199, 0.12);
                    color: #0284c7;
                    border: 1px solid rgba(2, 132, 199, 0.35);
                    border-radius: 14px;
                    padding: 4px 12px;
                    font-size: 11px;
                    font-weight: 600;
                """)
            else:
                self.model_pill.setText("⚠️ OPENAI: Key Unset")
                self.model_pill.setStyleSheet("""
                    background-color: rgba(245, 158, 11, 0.12);
                    color: #f59e0b;
                    border: 1px solid rgba(245, 158, 11, 0.35);
                    border-radius: 14px;
                    padding: 4px 12px;
                    font-size: 11px;
                    font-weight: 600;
                """)
        elif p_lower in ("local", "ollama"):
            self.model_pill.setText(f"🦙 OLLAMA: {model_name}")
            self.model_pill.setStyleSheet("""
                background-color: rgba(16, 185, 129, 0.12);
                color: #10b981;
                border: 1px solid rgba(16, 185, 129, 0.35);
                border-radius: 14px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 600;
            """)
        else:
            self.model_pill.setText(f"⚡ {provider.upper()}: {model_name}")
            self.model_pill.setStyleSheet("""
                background-color: rgba(2, 132, 199, 0.12);
                color: #0284c7;
                border: 1px solid rgba(2, 132, 199, 0.35);
                border-radius: 14px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 600;
            """)

