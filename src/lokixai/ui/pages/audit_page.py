"""Activity and audit log viewer with real-time security event tracking."""

from __future__ import annotations

import json
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.lokixai.security.audit import AuditEvent, get_audit_logger


class AuditPage(QWidget):
    """Activity & Audit Log table viewer."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.audit = get_audit_logger()
        self._init_ui()
        self.audit.add_listener(self._on_new_event)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Header
        title_box = QVBoxLayout()
        h = QLabel("🛡️ Activity & Security Audit Log")
        h.setStyleSheet("font-size: 18px; font-weight: 700; color: #00f2fe;")
        s = QLabel("Immutable audit trail of all executed tools, permissions, durations, and system changes.")
        s.setStyleSheet("font-size: 12px; color: #94a3b8;")
        title_box.addWidget(h)
        title_box.addWidget(s)
        layout.addLayout(title_box)

        # Toolbar
        top_bar = QHBoxLayout()
        f_lbl = QLabel("Filter Status:")
        f_lbl.setStyleSheet("font-weight: 600; color: #94a3b8;")
        top_bar.addWidget(f_lbl)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["ALL", "SUCCESS", "DENIED", "FAILED"])
        self.filter_combo.currentIndexChanged.connect(self._reload_table)
        top_bar.addWidget(self.filter_combo)

        top_bar.addStretch()

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self._reload_table)
        top_bar.addWidget(refresh_btn)

        export_btn = QPushButton("📥 Export Log (JSONL)")
        export_btn.clicked.connect(self._export_log)
        top_bar.addWidget(export_btn)

        clear_btn = QPushButton("🗑️ Clear Log")
        clear_btn.setObjectName("DangerButton")
        clear_btn.clicked.connect(self._clear_log)
        top_bar.addWidget(clear_btn)

        layout.addLayout(top_bar)


        # Audit Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Tool", "Caller", "Status", "Duration", "Details / Params"])
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table, 1)

        self._reload_table()

    def _reload_table(self):
        events = self.audit.get_recent(limit=100)
        filt = self.filter_combo.currentText()
        if filt != "ALL":
            events = [e for e in events if e.status == filt]

        self.table.setRowCount(len(events))
        for row, ev in enumerate(reversed(events)):
            t_short = ev.timestamp.split("T")[-1][:8] if "T" in ev.timestamp else ev.timestamp
            
            # Status badge
            status_item = QTableWidgetItem(ev.status)
            if ev.status == "SUCCESS":
                status_item.setForeground(Qt.green)
            elif ev.status == "DENIED":
                status_item.setForeground(Qt.yellow)
            else:
                status_item.setForeground(Qt.red)

            dur_str = f"{ev.duration_ms:.1f} ms" if ev.duration_ms > 0 else "-"
            details = ev.output_summary or ev.error or json.dumps(ev.parameters)

            self.table.setItem(row, 0, QTableWidgetItem(t_short))
            self.table.setItem(row, 1, QTableWidgetItem(ev.tool_name))
            self.table.setItem(row, 2, QTableWidgetItem(ev.caller))
            self.table.setItem(row, 3, status_item)
            self.table.setItem(row, 4, QTableWidgetItem(dur_str))
            self.table.setItem(row, 5, QTableWidgetItem(details))

    def _on_new_event(self, ev: AuditEvent):
        self._reload_table()

    def _export_log(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Audit Log", "audit_log_export.jsonl", "JSONL Files (*.jsonl)")
        if path:
            try:
                import shutil
                shutil.copyfile(self.audit.log_file, path)
                QMessageBox.information(self, "Export Complete", f"Audit log exported to:\n{path}")
            except Exception as e:
                QMessageBox.warning(self, "Export Failed", str(e))

    def _clear_log(self):
        reply = QMessageBox.question(
            self,
            "Confirm Clear Log",
            "Are you sure you want to clear the audit action log?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.audit._history.clear()
            try:
                with open(self.audit.log_file, "w", encoding="utf-8") as f:
                    f.write("")
            except Exception:
                pass
            self._reload_table()
            QMessageBox.information(self, "Audit Log", "Audit log has been cleared.")

