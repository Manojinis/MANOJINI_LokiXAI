"""Smart routine builder and sequential workflow execution studio."""

from __future__ import annotations

import json
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.lokixai.automation.routines import RoutineEngine, SmartRoutine
from src.lokixai.tools.base import ToolResult


class RoutinesPage(QWidget):
    """Visual routine builder and automated step-by-step executor."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.engine = RoutineEngine()
        self.active_routine: SmartRoutine = self.engine.get_all()[0] if self.engine.get_all() else None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header
        title_box = QVBoxLayout()
        h = QLabel("🔁 Smart Routines & Workflow Sequences")
        h.setStyleSheet("font-size: 18px; font-weight: 700; color: #00f2fe;")
        s = QLabel("Define sequential laptop automations with verified safety stops and parameter controls.")
        s.setStyleSheet("font-size: 12px; color: #94a3b8;")
        title_box.addWidget(h)
        title_box.addWidget(s)
        layout.addLayout(title_box)

        content = QHBoxLayout()
        content.setSpacing(16)

        # Left: Routine List Card
        left_card = QFrame()
        left_card.setObjectName("CardFrame")
        left_card.setFixedWidth(280)
        left_l = QVBoxLayout(left_card)
        left_l.setContentsMargins(12, 12, 12, 12)
        left_l.setSpacing(10)

        left_l.addWidget(QLabel("SAVED ROUTINES"))

        self.routine_list = QListWidget()
        for r in self.engine.get_all():
            item = QListWidgetItem(f"⚡ {r.name}")
            item.setData(Qt.UserRole, r.id)
            self.routine_list.addItem(item)

        self.routine_list.currentRowChanged.connect(self._on_routine_selected)
        left_l.addWidget(self.routine_list, 1)

        content.addWidget(left_card)

        # Right: Detail & Execution View
        right_card = QFrame()
        right_card.setObjectName("CardFrame")
        self.right_l = QVBoxLayout(right_card)
        self.right_l.setContentsMargins(16, 16, 16, 16)
        self.right_l.setSpacing(12)

        # Top action bar
        r_top = QHBoxLayout()
        self.name_lbl = QLabel(self.active_routine.name if self.active_routine else "No Routine")
        self.name_lbl.setStyleSheet("font-size: 16px; font-weight: 700; color: #f8fafc;")
        r_top.addWidget(self.name_lbl)
        r_top.addStretch()

        self.run_btn = QPushButton("▶ Run Routine Now")
        self.run_btn.setObjectName("PrimaryButton")
        self.run_btn.clicked.connect(self._run_active_routine)
        r_top.addWidget(self.run_btn)

        self.right_l.addLayout(r_top)

        self.desc_lbl = QLabel(self.active_routine.description if self.active_routine else "")
        self.desc_lbl.setStyleSheet("font-size: 12px; color: #94a3b8;")
        self.desc_lbl.setWordWrap(True)
        self.right_l.addWidget(self.desc_lbl)

        # Step Sequence Inspector
        self.right_l.addWidget(QLabel("WORKFLOW STEPS (SEQUENTIAL):"))

        self.steps_container = QWidget()
        self.steps_l = QVBoxLayout(self.steps_container)
        self.steps_l.setContentsMargins(0, 0, 0, 0)
        self.steps_l.setSpacing(8)

        self.right_l.addWidget(self.steps_container)
        self.right_l.addStretch()

        # Output Log Console
        self.right_l.addWidget(QLabel("EXECUTION LOG & OUTCOME:"))
        self.log_console = QPlainTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setFixedHeight(120)
        self.log_console.setStyleSheet("""
            background-color: #0c1322;
            border: 1px solid #1e293b;
            color: #38bdf8;
            font-family: monospace;
            font-size: 11px;
        """)
        self.right_l.addWidget(self.log_console)

        content.addWidget(right_card, 1)
        layout.addLayout(content)

        # Render active steps
        self._render_steps()

    def _on_routine_selected(self, row: int):
        routines = self.engine.get_all()
        if 0 <= row < len(routines):
            self.active_routine = routines[row]
            self.name_lbl.setText(self.active_routine.name)
            self.desc_lbl.setText(self.active_routine.description)
            self._render_steps()

    def _render_steps(self):
        while self.steps_l.count() > 0:
            item = self.steps_l.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.active_routine:
            return

        for idx, step in enumerate(self.active_routine.steps):
            f = QFrame()
            f.setStyleSheet("""
                background-color: #0c1322;
                border: 1px solid #1e293b;
                border-radius: 6px;
                padding: 8px;
            """)
            hl = QHBoxLayout(f)
            hl.setContentsMargins(8, 6, 8, 6)
            
            num_lbl = QLabel(f"Step {idx + 1}:")
            num_lbl.setStyleSheet("font-weight: 700; color: #00f2fe;")
            
            act_lbl = QLabel(f"{step.action_name} — {step.description}")
            act_lbl.setStyleSheet("color: #f8fafc; font-size: 12px;")
            
            p_lbl = QLabel(json.dumps(step.parameters))
            p_lbl.setStyleSheet("color: #64748b; font-size: 10px; font-family: monospace;")

            hl.addWidget(num_lbl)
            hl.addWidget(act_lbl)
            hl.addStretch()
            hl.addWidget(p_lbl)
            self.steps_l.addWidget(f)

    def _run_active_routine(self):
        if not self.active_routine:
            return

        self.log_console.clear()
        self.log_console.appendPlainText(f">> Executing Routine: {self.active_routine.name}")

        results = self.engine.execute_routine(
            routine_id=self.active_routine.id,
            on_step_start=lambda idx, step: self.log_console.appendPlainText(f"Step {idx + 1}: Running {step.action_name}..."),
            on_step_complete=lambda idx, step, res: self.log_console.appendPlainText(
                f"Step {idx + 1} [{'SUCCESS' if res.success else 'FAILED'}]: {res.message}"
            ),
        )

        all_ok = all(r.success for r in results)
        if all_ok:
            self.log_console.appendPlainText(">> Routine completed successfully without errors.")
        else:
            self.log_console.appendPlainText(">> Routine terminated early due to step failure.")
