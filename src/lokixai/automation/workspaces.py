"""Workspace manager for multi-application environments."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from src.lokixai.tools.app_tools import LaunchWorkspaceTool


class WorkspaceDefinition(BaseModel):
    name: str
    description: str
    icon: str = "💻"
    apps: List[str] = Field(default_factory=list)
    urls: List[str] = Field(default_factory=list)


DEFAULT_WORKSPACES: List[WorkspaceDefinition] = [
    WorkspaceDefinition(
        name="Coding",
        description="Launch VSCode, Windows Terminal, and GitHub repository.",
        icon="⚡",
        apps=["code", "wt.exe"],
        urls=["https://github.com"],
    ),
    WorkspaceDefinition(
        name="Study",
        description="Focus on learning with note-taking, browser, and documentation.",
        icon="📚",
        apps=["notepad.exe"],
        urls=["https://en.wikipedia.org"],
    ),
    WorkspaceDefinition(
        name="Research",
        description="Open scholarly search engines and academic archives.",
        icon="🔬",
        apps=[],
        urls=["https://arxiv.org", "https://scholar.google.com"],
    ),
    WorkspaceDefinition(
        name="Daily Work",
        description="Essential daily productivity utilities and dashboard.",
        icon="📊",
        apps=["calc.exe", "notepad.exe"],
        urls=["https://google.com"],
    ),
]


class WorkspaceManager:
    """Manages workspace configurations and launches."""

    def __init__(self, data_file: str = "data/workspaces.json"):
        self.data_file = Path(data_file)
        self.workspaces: Dict[str, WorkspaceDefinition] = {w.name: w for w in DEFAULT_WORKSPACES}
        self.load()

    def load(self) -> None:
        if not self.data_file.exists():
            return
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                items = json.load(f)
                for item in items:
                    ws = WorkspaceDefinition(**item)
                    self.workspaces[ws.name] = ws
        except Exception:
            pass

    def save(self) -> None:
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump([w.model_dump() for w in self.workspaces.values()], f, indent=2)
        except Exception:
            pass

    def get_all(self) -> List[WorkspaceDefinition]:
        return list(self.workspaces.values())

    def launch(self, name: str) -> bool:
        tool = LaunchWorkspaceTool()
        res = tool.execute(workspace_name=name)
        return res.success
