"""Automation package for routines and workspaces."""

from .workspaces import WorkspaceDefinition, WorkspaceManager
from .routines import SmartRoutine, RoutineStep, RoutineEngine

__all__ = [
    "WorkspaceDefinition",
    "WorkspaceManager",
    "SmartRoutine",
    "RoutineStep",
    "RoutineEngine",
]
