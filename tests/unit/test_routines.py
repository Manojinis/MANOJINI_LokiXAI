"""Unit tests for smart routine definitions and sequential execution."""

import pytest
from src.lokixai.automation.routines import RoutineEngine, SmartRoutine, RoutineStep


def test_routine_loading():
    engine = RoutineEngine(data_file="data/test_routines.json")
    all_r = engine.get_all()
    assert len(all_r) >= 3
    assert any(r.name == "Morning Focus Mode" for r in all_r)


def test_routine_execution_halt_on_error():
    engine = RoutineEngine(data_file="data/test_routines_err.json")
    bad_routine = SmartRoutine(
        name="Bad Sequence",
        steps=[
            RoutineStep(action_name="open_application", parameters={"app_name": "forbidden_tool.exe"}),
            RoutineStep(action_name="set_screen_brightness", parameters={"level": 50}),
        ]
    )
    engine.routines[bad_routine.id] = bad_routine

    executed_steps = []
    results = engine.execute_routine(
        routine_id=bad_routine.id,
        on_step_start=lambda idx, step: executed_steps.append(idx),
    )

    # Step 1 should fail because app is not allowlisted, halting step 2
    assert len(results) == 1
    assert results[0].success is False
    assert len(executed_steps) == 1
