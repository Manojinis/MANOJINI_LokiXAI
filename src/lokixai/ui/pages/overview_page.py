"""Overview dashboard page displaying hardware cards, quick controls, and workspace launchers."""

from __future__ import annotations

from typing import Callable, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from src.lokixai.monitoring.system_monitor import SystemMetrics, get_system_monitor
from src.lokixai.tools.system_tools import SetBrightnessTool, SetVolumeTool, SetMuteTool
from src.lokixai.automation.workspaces import WorkspaceManager


class OverviewPage(QWidget):
    """Main overview and quick command dashboard."""

    navigate_requested = Signal(str)
    quick_command_submitted = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ws_manager = WorkspaceManager()
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Welcome Banner
        banner = QFrame()
        banner.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0f172a, stop:1 #1e1b4b);
            border: 1px solid #1e293b;
            border-radius: 14px;
            padding: 18px;
        """)
        b_layout = QVBoxLayout(banner)
        b_layout.setSpacing(6)

        b_title = QLabel("LokiXAI Intelligent Copilot")
        b_title.setStyleSheet("font-size: 20px; font-weight: 800; color: #00f2fe;")
        b_desc = QLabel("Your laptop hardware telemetry is active. Ready to automate approved workflows, control settings, or assist with code.")
        b_desc.setStyleSheet("font-size: 13px; color: #94a3b8;")
        b_desc.setWordWrap(True)

        b_layout.addWidget(b_title)
        b_layout.addWidget(b_desc)

        # Quick command input inside banner
        cmd_box = QHBoxLayout()
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("Type a natural command (e.g. 'set volume to 60', 'launch Coding workspace', 'show battery')...")
        self.cmd_input.setFixedHeight(38)
        self.cmd_input.returnPressed.connect(self._send_quick_cmd)

        send_btn = QPushButton("Execute ⚡")
        send_btn.setObjectName("PrimaryButton")
        send_btn.setFixedHeight(38)
        send_btn.clicked.connect(self._send_quick_cmd)

        cmd_box.addWidget(self.cmd_input)
        cmd_box.addWidget(send_btn)
        b_layout.addSpacing(6)
        b_layout.addLayout(cmd_box)

        layout.addWidget(banner)

        # Hardware Metric Cards Grid
        grid_lbl = QLabel("REAL-TIME HARDWARE METRICS")
        grid_lbl.setStyleSheet("font-size: 11px; font-weight: 700; color: #64748b; letter-spacing: 0.5px;")
        layout.addWidget(grid_lbl)

        grid = QGridLayout()
        grid.setSpacing(14)

        # CPU Card
        self.cpu_card, self.cpu_val, self.cpu_bar = self._create_metric_card("CPU LOAD", "0%", "Core stats")
        grid.addWidget(self.cpu_card, 0, 0)

        # RAM Card
        self.ram_card, self.ram_val, self.ram_bar = self._create_metric_card("MEMORY (RAM)", "0%", "Used of Total")
        grid.addWidget(self.ram_card, 0, 1)

        # Disk Card
        self.disk_card, self.disk_val, self.disk_bar = self._create_metric_card("PRIMARY STORAGE", "0%", "Disk usage")
        grid.addWidget(self.disk_card, 0, 2)

        # Battery Card
        self.bat_card, self.bat_val, self.bat_bar = self._create_metric_card("BATTERY POWER", "AC", "Power status")
        grid.addWidget(self.bat_card, 0, 3)

        layout.addLayout(grid)

        # Quick Hardware Sliders Frame
        ctrl_lbl = QLabel("HARDWARE QUICK CONTROLS")
        ctrl_lbl.setStyleSheet("font-size: 11px; font-weight: 700; color: #64748b; letter-spacing: 0.5px;")
        layout.addWidget(ctrl_lbl)

        ctrl_frame = QFrame()
        ctrl_frame.setObjectName("CardFrame")
        c_layout = QHBoxLayout(ctrl_frame)
        c_layout.setContentsMargins(16, 14, 16, 14)
        c_layout.setSpacing(24)

        # Brightness slider
        bright_box = QVBoxLayout()
        self.bright_lbl = QLabel("Display Brightness: 75%")
        self.bright_lbl.setStyleSheet("font-weight: 600; font-size: 12px;")
        self.bright_slider = QSlider(Qt.Horizontal)
        self.bright_slider.setRange(0, 100)
        self.bright_slider.setValue(75)
        self.bright_slider.sliderReleased.connect(self._on_brightness_change)
        bright_box.addWidget(self.bright_lbl)
        bright_box.addWidget(self.bright_slider)
        c_layout.addLayout(bright_box)

        # Volume slider
        vol_box = QVBoxLayout()
        self.vol_lbl = QLabel("Master Volume: 50%")
        self.vol_lbl.setStyleSheet("font-weight: 600; font-size: 12px;")
        self.vol_slider = QSlider(Qt.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(50)
        self.vol_slider.sliderReleased.connect(self._on_volume_change)
        vol_box.addWidget(self.vol_lbl)
        vol_box.addWidget(self.vol_slider)
        c_layout.addLayout(vol_box)

        # Mute toggle button
        self.mute_btn = QPushButton("🔊 Mute Audio")
        self.mute_btn.setFixedHeight(36)
        self.mute_btn.clicked.connect(self._on_toggle_mute)
        c_layout.addWidget(self.mute_btn)

        layout.addWidget(ctrl_frame)

        # Workspace Launcher Cards
        ws_lbl = QLabel("WORKSPACE PRESETS")
        ws_lbl.setStyleSheet("font-size: 11px; font-weight: 700; color: #64748b; letter-spacing: 0.5px;")
        layout.addWidget(ws_lbl)

        ws_grid = QGridLayout()
        ws_grid.setSpacing(14)
        for idx, ws in enumerate(self.ws_manager.get_all()):
            card = self._create_workspace_card(ws.name, ws.description, ws.icon)
            ws_grid.addWidget(card, idx // 2, idx % 2)

        layout.addLayout(ws_grid)
        layout.addStretch()

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def _create_metric_card(self, title: str, init_val: str, subtitle: str):
        card = QFrame()
        card.setObjectName("CardFrame")
        l = QVBoxLayout(card)
        l.setContentsMargins(14, 14, 14, 14)
        l.setSpacing(6)

        t_lbl = QLabel(title)
        t_lbl.setStyleSheet("font-size: 11px; font-weight: 700; color: #64748b;")

        v_lbl = QLabel(init_val)
        v_lbl.setStyleSheet("font-size: 22px; font-weight: 800; color: #00f2fe;")

        p_bar = QProgressBar()
        p_bar.setRange(0, 100)
        p_bar.setFixedHeight(6)
        p_bar.setTextVisible(False)

        s_lbl = QLabel(subtitle)
        s_lbl.setStyleSheet("font-size: 11px; color: #94a3b8;")

        l.addWidget(t_lbl)
        l.addWidget(v_lbl)
        l.addWidget(p_bar)
        l.addWidget(s_lbl)
        return card, v_lbl, p_bar

    def _create_workspace_card(self, name: str, desc: str, icon: str):
        card = QFrame()
        card.setObjectName("CardFrame")
        l = QVBoxLayout(card)
        l.setContentsMargins(14, 14, 14, 14)
        l.setSpacing(6)

        h = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 20px;")
        title_lbl = QLabel(name)
        title_lbl.setStyleSheet("font-size: 15px; font-weight: 700; color: #f8fafc;")
        h.addWidget(icon_lbl)
        h.addWidget(title_lbl)
        h.addStretch()

        btn = QPushButton("Launch Workspace")
        btn.setObjectName("PrimaryButton")
        btn.clicked.connect(lambda checked=False, n=name: self.ws_manager.launch(n))
        h.addWidget(btn)

        d_lbl = QLabel(desc)
        d_lbl.setStyleSheet("font-size: 12px; color: #94a3b8;")
        d_lbl.setWordWrap(True)

        l.addLayout(h)
        l.addWidget(d_lbl)
        return card

    def _send_quick_cmd(self):
        text = self.cmd_input.text().strip()
        if text:
            self.cmd_input.clear()
            self.quick_command_submitted.emit(text)

    def _on_brightness_change(self):
        val = self.bright_slider.value()
        self.bright_lbl.setText(f"Display Brightness: {val}%")
        SetBrightnessTool().execute(level=val)

    def _on_volume_change(self):
        val = self.vol_slider.value()
        self.vol_lbl.setText(f"Master Volume: {val}%")
        SetVolumeTool().execute(level=val)

    def _on_toggle_mute(self):
        if "Unmute" in self.mute_btn.text():
            SetMuteTool().execute(mute=False)
            self.mute_btn.setText("🔊 Mute Audio")
        else:
            SetMuteTool().execute(mute=True)
            self.mute_btn.setText("🔈 Unmute Audio")

    def update_metrics(self, m: SystemMetrics):
        self.cpu_val.setText(f"{m.cpu_percent}%")
        self.cpu_bar.setValue(int(m.cpu_percent))

        self.ram_val.setText(f"{m.ram_percent}%")
        self.ram_bar.setValue(int(m.ram_percent))

        self.disk_val.setText(f"{m.disk_percent}%")
        self.disk_bar.setValue(int(m.disk_percent))

        if m.battery_percent is not None:
            self.bat_val.setText(f"{m.battery_percent}%")
            self.bat_bar.setValue(int(m.battery_percent))
        else:
            self.bat_val.setText("AC Power")
            self.bat_bar.setValue(100)
