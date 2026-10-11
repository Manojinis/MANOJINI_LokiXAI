"""Smart routine builder and sequential workflow execution studio."""

from __future__ import annotations

import json
from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from src.lokixai.automation.routines import RoutineEngine, SmartRoutine, RoutineStep
from src.lokixai.tools.base import ToolResult


class CreateRoutineDialog(QDialog):
    """Modal dialog to construct and validate new custom sequential routines."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Smart Routine")
        self.setFixedSize(500, 480)
        self.steps: list[RoutineStep] = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        # Name & Description
        layout.addWidget(QLabel("Routine Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Study Session Prep")
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Description:"))
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("e.g., Set volume, dim display, and open research portal")
        layout.addWidget(self.desc_input)

        # Step Builder Card
        step_box = QFrame()
        step_box.setObjectName("CardFrame")
        s_layout = QVBoxLayout(step_box)
        s_layout.setContentsMargins(10, 10, 10, 10)
        s_layout.setSpacing(8)

        s_layout.addWidget(QLabel("ADD ACTION STEP:"))
        
        self.action_combo = QComboBox()
        self.action_combo.addItems([
            "set_screen_brightness (level: 0-100)",
            "set_master_volume (level: 0-100)",
            "set_audio_mute (mute: true/false)",
            "launch_workspace (Coding/Study/Research/Daily Work)",
            "open_application (notepad/calc/code/terminal)",
            "open_website (url: https://...)",
            "get_system_metrics",
            "get_battery_status",
        ])
        s_layout.addWidget(self.action_combo)

        param_row = QHBoxLayout()
        param_row.addWidget(QLabel("Parameter Value:"))
        self.param_input = QLineEdit()
        self.param_input.setPlaceholderText("e.g. 50 or notepad or https://wikipedia.org")
        param_row.addWidget(self.param_input)
        s_layout.addLayout(param_row)

        add_step_btn = QPushButton("+ Add Step to Sequence")
        add_step_btn.clicked.connect(self._add_step)
        s_layout.addWidget(add_step_btn)

        layout.addWidget(step_box)

        # Steps list
        layout.addWidget(QLabel("Configured Steps:"))
        self.steps_list = QListWidget()
        layout.addWidget(self.steps_list, 1)

        # Bottom buttons
        btn_box = QHBoxLayout()
        btn_box.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(cancel_btn)

        save_btn = QPushButton("Save Routine")
        save_btn.setObjectName("PrimaryButton")
        save_btn.clicked.connect(self._save_routine)
        btn_box.addWidget(save_btn)

        layout.addLayout(btn_box)

    def _add_step(self):
        act_raw = self.action_combo.currentText().split(" ")[0]
        val = self.param_input.text().strip()

        params = {}
        desc = ""
        if act_raw == "set_screen_brightness":
            try:
                num = int(val) if val else 70
                params = {"level": min(100, max(0, num))}
                desc = f"Set brightness to {params['level']}%"
            except ValueError:
                params = {"level": 70}
                desc = "Set brightness to 70%"
        elif act_raw == "set_master_volume":
            try:
                num = int(val) if val else 40
                params = {"level": min(100, max(0, num))}
                desc = f"Set volume to {params['level']}%"
            except ValueError:
                params = {"level": 40}
                desc = "Set volume to 40%"
        elif act_raw == "set_audio_mute":
            params = {"mute": val.lower() in ("true", "1", "yes")}
            desc = "Mute audio" if params["mute"] else "Unmute audio"
        elif act_raw == "launch_workspace":
            ws = val if val else "Coding"
            params = {"workspace_name": ws}
            desc = f"Launch {ws} workspace"
        elif act_raw == "open_application":
            app = val if val else "notepad"
            params = {"app_name": app}
            desc = f"Launch {app}"
        elif act_raw == "open_website":
            url = val if val else "https://google.com"
            params = {"url": url}
            desc = f"Open {url}"
        elif act_raw in ("get_system_metrics", "get_battery_status"):
            params = {}
            desc = f"Query {act_raw}"

        step = RoutineStep(
            action_name=act_raw,
            parameters=params,
            description=desc,
        )
        self.steps.append(step)
        self.steps_list.addItem(f"Step {len(self.steps)}: {act_raw} — {desc}")
        self.param_input.clear()

    def _save_routine(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation", "Please provide a name for the routine.")
            return
        if not self.steps:
            QMessageBox.warning(self, "Validation", "Please add at least one step to the routine.")
            return
        self.accept()

    def get_created_routine(self) -> SmartRoutine:
        return SmartRoutine(
            name=self.name_input.text().strip(),
            description=self.desc_input.text().strip(),
            steps=self.steps,
        )


class RoutinesPage(QWidget):
    """Visual routine builder and automated step-by-step executor."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.engine = RoutineEngine()
        self.active_routine: Optional[SmartRoutine] = self.engine.get_all()[0] if self.engine.get_all() else None
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
        self._populate_routine_list()
        self.routine_list.currentRowChanged.connect(self._on_routine_selected)
        left_l.addWidget(self.routine_list, 1)

        create_btn = QPushButton("+ New Routine")
        create_btn.setObjectName("PrimaryButton")
        create_btn.clicked.connect(self._create_routine_dialog)
        left_l.addWidget(create_btn)

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
        self.name_lbl.setObjectName("CardTitle")
        self.name_lbl.setStyleSheet("font-size: 16px; font-weight: 700;")
        r_top.addWidget(self.name_lbl)
        r_top.addStretch()

        self.run_btn = QPushButton("▶ Run Routine Now")
        self.run_btn.setObjectName("PrimaryButton")
        self.run_btn.clicked.connect(self._run_active_routine)
        r_top.addWidget(self.run_btn)

        self.right_l.addLayout(r_top)

        self.desc_lbl = QLabel(self.active_routine.description if self.active_routine else "")
        self.desc_lbl.setObjectName("SubText")
        self.desc_lbl.setStyleSheet("font-size: 12px;")
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
        self.log_console.setStyleSheet("font-family: Consolas, monospace; font-size: 11px;")
        self.right_l.addWidget(self.log_console)

        content.addWidget(right_card, 1)
        layout.addLayout(content)

        # Render active steps
        self._render_steps()

    def _populate_routine_list(self):
        self.routine_list.clear()
        for r in self.engine.get_all():
            item = QListWidgetItem(f"⚡ {r.name}")
            item.setData(Qt.UserRole, r.id)
            self.routine_list.addItem(item)

    def _on_routine_selected(self, row: int):
        routines = self.engine.get_all()
        if 0 <= row < len(routines):
            self.active_routine = routines[row]
            self.name_lbl.setText(self.active_routine.name)
            self.desc_lbl.setText(self.active_routine.description)
            self._render_steps()

    def _create_routine_dialog(self):
        dlg = CreateRoutineDialog(self)
        if dlg.exec() == QDialog.Accepted:
            new_r = dlg.get_created_routine()
            self.engine.routines[new_r.id] = new_r
            self.engine.save()
            self._populate_routine_list()
            self.active_routine = new_r
            self.name_lbl.setText(new_r.name)
            self.desc_lbl.setText(new_r.description)
            self._render_steps()
            QMessageBox.information(self, "Saved", f"Created routine '{new_r.name}'.")

    def _render_steps(self):
        while self.steps_l.count() > 0:
            item = self.steps_l.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.active_routine:
            return

        for idx, step in enumerate(self.active_routine.steps):
            f = QFrame()
            f.setObjectName("InnerBox")
            hl = QHBoxLayout(f)
            hl.setContentsMargins(8, 6, 8, 6)
            
            num_lbl = QLabel(f"Step {idx + 1}:")
            num_lbl.setObjectName("SenderLabel")
            num_lbl.setStyleSheet("font-weight: 700;")
            
            act_lbl = QLabel(f"{step.action_name} — {step.description}")
            act_lbl.setObjectName("CardTitle")
            act_lbl.setStyleSheet("font-size: 12px; font-weight: 500;")
            
            p_lbl = QLabel(json.dumps(step.parameters))
            p_lbl.setObjectName("SubText")
            p_lbl.setStyleSheet("font-size: 10px; font-family: monospace;")

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
