"""Contextual right panel showing real-time metrics, live tool activity, and provider status."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from src.lokixai.monitoring.system_monitor import SystemMetrics
from src.lokixai.security.audit import AuditEvent, get_audit_logger


class RightPanel(QFrame):
    """Contextual side panel for live metrics and tool audit feed."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RightPanelFrame")
        self.setFixedWidth(270)
        self._init_ui()
        self._connect_audit()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 16, 14, 16)
        layout.setSpacing(14)

        # Telemetry Section Title
        telem_title = QLabel("HARDWARE TELEMETRY")
        telem_title.setStyleSheet("font-size: 11px; font-weight: 700; color: #64748b; letter-spacing: 0.5px;")
        layout.addWidget(telem_title)

        # Metrics Card
        metrics_card = QFrame()
        metrics_card.setObjectName("CardFrame")
        m_layout = QVBoxLayout(metrics_card)
        m_layout.setContentsMargins(10, 10, 10, 10)
        m_layout.setSpacing(8)

        # CPU
        self.cpu_label = QLabel("CPU: 0%")
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        self.cpu_bar.setFixedHeight(8)
        self.cpu_bar.setTextVisible(False)
        m_layout.addWidget(self.cpu_label)
        m_layout.addWidget(self.cpu_bar)

        # RAM
        self.ram_label = QLabel("RAM: 0%")
        self.ram_bar = QProgressBar()
        self.ram_bar.setRange(0, 100)
        self.ram_bar.setFixedHeight(8)
        self.ram_bar.setTextVisible(False)
        m_layout.addWidget(self.ram_label)
        m_layout.addWidget(self.ram_bar)

        # Battery
        self.bat_label = QLabel("Battery: AC Power")
        self.bat_bar = QProgressBar()
        self.bat_bar.setRange(0, 100)
        self.bat_bar.setFixedHeight(8)
        self.bat_bar.setTextVisible(False)
        m_layout.addWidget(self.bat_label)
        m_layout.addWidget(self.bat_bar)

        layout.addWidget(metrics_card)

        # Live Tool Activity Header
        act_title = QLabel("LIVE ACTION FEED")
        act_title.setStyleSheet("font-size: 11px; font-weight: 700; color: #64748b; letter-spacing: 0.5px;")
        layout.addWidget(act_title)

        # Activity scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        self.activity_container = QWidget()
        self.activity_container.setStyleSheet("background: transparent;")
        self.act_layout = QVBoxLayout(self.activity_container)
        self.act_layout.setContentsMargins(0, 0, 0, 0)
        self.act_layout.setSpacing(6)
        self.act_layout.addStretch()

        scroll.setWidget(self.activity_container)
        layout.addWidget(scroll)

    def _connect_audit(self):
        audit = get_audit_logger()
        audit.add_listener(self.add_audit_event)

    def update_metrics(self, m: SystemMetrics):
        self.cpu_label.setText(f"CPU Load: {m.cpu_percent}%")
        self.cpu_bar.setValue(int(m.cpu_percent))

        self.ram_label.setText(f"RAM Usage: {m.ram_percent}% ({m.ram_used_gb} GB)")
        self.ram_bar.setValue(int(m.ram_percent))

        if m.battery_percent is not None:
            status = "Plugged In" if m.battery_plugged else "Discharging"
            self.bat_label.setText(f"Battery: {m.battery_percent}% ({status})")
            self.bat_bar.setValue(int(m.battery_percent))
        else:
            self.bat_label.setText("Battery: AC Connected")
            self.bat_bar.setValue(100)

    def add_audit_event(self, ev: AuditEvent):
        # Insert event at top of feed
        item_frame = QFrame()
        item_frame.setStyleSheet("""
            background-color: #131d31;
            border-left: 3px solid #00f2fe;
            border-radius: 6px;
            padding: 6px;
        """)
        v = QVBoxLayout(item_frame)
        v.setContentsMargins(4, 4, 4, 4)
        v.setSpacing(2)

        header = QLabel(f"⚡ {ev.tool_name}")
        header.setStyleSheet("font-weight: 600; font-size: 11px; color: #f8fafc;")

        status_color = "#10b981" if ev.status == "SUCCESS" else "#ef4444"
        dur_str = f"{ev.duration_ms}ms" if ev.duration_ms > 0 else ""
        sub = QLabel(f"{ev.status} {dur_str}")
        sub.setStyleSheet(f"font-size: 10px; color: {status_color}; font-weight: 500;")

        v.addWidget(header)
        v.addWidget(sub)

        # Insert at position 0
        self.act_layout.insertWidget(0, item_frame)
        # Limit visible feed cards
        if self.act_layout.count() > 15:
            last = self.act_layout.itemAt(self.act_layout.count() - 2)
            if last and last.widget():
                last.widget().deleteLater()
