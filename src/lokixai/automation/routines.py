"""Smart routine automation models and sequential execution engine."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field

from src.lokixai.security.permissions import PermissionLevel
from src.lokixai.tools.base import ToolResult
from src.lokixai.tools.registry import ToolRegistry, get_tool_registry

logger = logging.getLogger("lokixai.automation.routines")


class RoutineStep(BaseModel):
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    action_name: str
    description: str = ""
    parameters: Dict[str, Any] = Field(default_factory=dict)


class SmartRoutine(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    enabled: bool = True
    schedule_cron: Optional[str] = None
    steps: List[RoutineStep] = Field(default_factory=list)


DEFAULT_ROUTINES: List[SmartRoutine] = [
    SmartRoutine(
        name="Morning Focus Mode",
        description="Optimize laptop for deep morning work: dim screen, adjust volume, launch Coding workspace.",
        steps=[
            RoutineStep(action_name="set_screen_brightness", parameters={"level": 70}, description="Set brightness to 70%"),
            RoutineStep(action_name="set_master_volume", parameters={"level": 30}, description="Set volume to 30%"),
            RoutineStep(action_name="launch_workspace", parameters={"workspace_name": "Coding"}, description="Open coding tools"),
        ],
    ),
    SmartRoutine(
        name="Night Wind-Down",
        description="Prepare for late evening: lower brightness, mute audio.",
        steps=[
            RoutineStep(action_name="set_screen_brightness", parameters={"level": 25}, description="Lower brightness to 25%"),
            RoutineStep(action_name="set_audio_mute", parameters={"mute": True}, description="Mute audio"),
        ],
    ),
    SmartRoutine(
        name="Health Check & Status",
        description="Query battery and full laptop telemetry.",
        steps=[
            RoutineStep(action_name="get_battery_status", parameters={}, description="Check battery"),
            RoutineStep(action_name="get_system_metrics", parameters={}, description="Inspect CPU/RAM/Disk"),
        ],
    ),
]


class RoutineEngine:
    """Sequential executor for smart automation routines with failure stop."""

    def __init__(self, data_file: str = "data/routines.json"):
        self.data_file = Path(data_file)
        self.routines: Dict[str, SmartRoutine] = {}
        self.registry = get_tool_registry()
        self.load()

    def load(self) -> None:
        if not self.data_file.exists():
            self.routines = {r.id: r for r in DEFAULT_ROUTINES}
            self.save()
            return

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                items = json.load(f)
                for item in items:
                    r = SmartRoutine(**item)
                    self.routines[r.id] = r
        except Exception:
            self.routines = {r.id: r for r in DEFAULT_ROUTINES}

    def save(self) -> None:
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump([r.model_dump() for r in self.routines.values()], f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save routines: {e}")

    def get_all(self) -> List[SmartRoutine]:
        return list(self.routines.values())

    def execute_routine(
        self,
        routine_id: str,
        on_step_start: Optional[Callable[[int, RoutineStep], None]] = None,
        on_step_complete: Optional[Callable[[int, RoutineStep, ToolResult], None]] = None,
        confirm_callback: Optional[Callable[[str, Dict[str, Any], PermissionLevel], bool]] = None,
    ) -> List[ToolResult]:
        """Execute all steps in order, stopping if any step fails."""
        routine = self.routines.get(routine_id)
        if not routine:
            raise ValueError(f"Routine {routine_id} not found.")

        results = []
        for idx, step in enumerate(routine.steps):
            if on_step_start:
                on_step_start(idx, step)

            res = self.registry.execute(
                name=step.action_name,
                arguments=step.parameters,
                caller=f"routine:{routine.name}",
                confirm_callback=confirm_callback,
            )
            results.append(res)

            if on_step_complete:
                on_step_complete(idx, step, res)

            # Stop safely if a step fails
            if not res.success:
                logger.warning(f"Routine '{routine.name}' aborted at step {idx + 1}: {res.message}")
                break

        return results
