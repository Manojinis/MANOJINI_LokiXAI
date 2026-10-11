"""Real-time laptop health telemetry dashboard with process table."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QProgressBar,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.lokixai.monitoring.system_monitor import SystemMetrics, get_system_monitor


class MonitorPage(QWidget):
    """Detailed hardware telemetry and laptop health dashboard."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.monitor = get_system_monitor()
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Top Bar
        top_bar = QHBoxLayout()
        title_box = QVBoxLayout()
        h = QLabel("📊 Laptop Health & Telemetry")
        h.setStyleSheet("font-size: 18px; font-weight: 700; color: #00f2fe;")
        s = QLabel("Real-time hardware statistics, battery state, network rates, and running processes.")
        s.setStyleSheet("font-size: 12px; color: #94a3b8;")
        title_box.addWidget(h)
        title_box.addWidget(s)
        top_bar.addLayout(title_box)

        top_bar.addStretch()

        # Refresh interval selector
        ref_box = QHBoxLayout()
        r_lbl = QLabel("Polling Interval:")
        r_lbl.setStyleSheet("font-size: 12px; color: #94a3b8;")
        self.interval_combo = QComboBox()
        self.interval_combo.addItems(["1.0 sec", "2.0 sec", "5.0 sec"])
        self.interval_combo.setCurrentIndex(1)
        self.interval_combo.currentIndexChanged.connect(self._on_interval_change)
        ref_box.addWidget(r_lbl)
        ref_box.addWidget(self.interval_combo)
        top_bar.addLayout(ref_box)

        main_layout.addLayout(top_bar)

        # Metrics 6-Card Grid
        grid = QGridLayout()
        grid.setSpacing(12)

        # CPU
        self.cpu_card, self.cpu_val, self.cpu_sub = self._make_stat_card("CPU TOTAL", "0%", "Cores: --")
        grid.addWidget(self.cpu_card, 0, 0)

        # RAM
        self.ram_card, self.ram_val, self.ram_sub = self._make_stat_card("SYSTEM MEMORY", "0%", "0 / 0 GB")
        grid.addWidget(self.ram_card, 0, 1)

        # Storage
        self.disk_card, self.disk_val, self.disk_sub = self._make_stat_card("PRIMARY DISK", "0%", "Free: -- GB")
        grid.addWidget(self.disk_card, 0, 2)

        # Battery
        self.bat_card, self.bat_val, self.bat_sub = self._make_stat_card("BATTERY", "AC", "Plugged in")
        grid.addWidget(self.bat_card, 1, 0)

        # Network
        self.net_card, self.net_val, self.net_sub = self._make_stat_card("NETWORK SPEED", "0 KB/s", "Tx: 0 | Rx: 0")
        grid.addWidget(self.net_card, 1, 1)

        # Uptime
        self.up_card, self.up_val, self.up_sub = self._make_stat_card("SYSTEM UPTIME", "0h 0m", "Active session")
        grid.addWidget(self.up_card, 1, 2)

        main_layout.addLayout(grid)

        # Top processes section
        proc_title = QLabel("TOP ACTIVE PROCESSES (BY MEMORY)")
        proc_title.setStyleSheet("font-size: 11px; font-weight: 700; color: #64748b; letter-spacing: 0.5px;")
        main_layout.addWidget(proc_title)

        self.proc_table = QTableWidget()
        self.proc_table.setColumnCount(4)
        self.proc_table.setHorizontalHeaderLabels(["PID", "Process Name", "CPU %", "RAM (MB)"])
        self.proc_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.proc_table.verticalHeader().setVisible(False)
        self.proc_table.setSelectionBehavior(QTableWidget.SelectRows)
        main_layout.addWidget(self.proc_table, 1)

    def _make_stat_card(self, title: str, init_val: str, subtitle: str):
        card = QFrame()
        card.setObjectName("CardFrame")
        l = QVBoxLayout(card)
        l.setContentsMargins(12, 12, 12, 12)
        l.setSpacing(4)

        t = QLabel(title)
        t.setStyleSheet("font-size: 10px; font-weight: 700; color: #64748b;")

        v = QLabel(init_val)
        v.setStyleSheet("font-size: 20px; font-weight: 800; color: #00f2fe;")

        s = QLabel(subtitle)
        s.setStyleSheet("font-size: 11px; color: #94a3b8;")

        l.addWidget(t)
        l.addWidget(v)
        l.addWidget(s)
        return card, v, s

    def _on_interval_change(self, idx: int):
        intervals = [1.0, 2.0, 5.0]
        self.monitor.interval = intervals[idx]

    def update_metrics(self, m: SystemMetrics):
        self.cpu_val.setText(f"{m.cpu_percent}%")
        freq_str = f" @ {m.cpu_freq_mhz}MHz" if m.cpu_freq_mhz else ""
        self.cpu_sub.setText(f"{m.cpu_count} Logical Cores{freq_str}")

        self.ram_val.setText(f"{m.ram_percent}%")
        self.ram_sub.setText(f"{m.ram_used_gb} GB / {m.ram_total_gb} GB")

        self.disk_val.setText(f"{m.disk_percent}%")
        self.disk_sub.setText(f"Used: {m.disk_used_gb} GB (Free: {m.disk_free_gb} GB)")

        if m.battery_percent is not None:
            self.bat_val.setText(f"{m.battery_percent}%")
            self.bat_sub.setText(m.battery_time_left_str or "Calculating...")
        else:
            self.bat_val.setText("AC Connected")
            self.bat_sub.setText("Desktop / Continuous Power")

        self.net_val.setText(f"↓ {m.net_recv_speed_kbps} KB/s")
        self.net_sub.setText(f"Tx: {m.net_sent_speed_kbps} KB/s | Rx: {m.net_recv_speed_kbps} KB/s")

        self.up_val.setText(m.uptime_str)

        # Update process table
        self.proc_table.setRowCount(len(m.top_processes))
        for row, p in enumerate(m.top_processes):
            self.proc_table.setItem(row, 0, QTableWidgetItem(str(p.pid)))
            self.proc_table.setItem(row, 1, QTableWidgetItem(p.name))
            self.proc_table.setItem(row, 2, QTableWidgetItem(f"{p.cpu_percent}%"))
            self.proc_table.setItem(row, 3, QTableWidgetItem(f"{p.memory_mb:.1f} MB"))
