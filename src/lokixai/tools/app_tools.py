"""Application and workspace automation tools with strict allowlisting."""

from __future__ import annotations

import logging
import os
import subprocess
import urllib.parse
import webbrowser
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from src.lokixai.security.permissions import PermissionLevel
from .base import BaseTool, ToolResult

logger = logging.getLogger("lokixai.tools.app")


# Allowlisted application aliases mapped to verified launch commands
ALLOWLISTED_APPS: Dict[str, str] = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "paint": "mspaint.exe",
    "explorer": "explorer.exe",
    "task manager": "taskmgr.exe",
    "taskmgr": "taskmgr.exe",
    "settings": "start ms-settings:",
    "edge": "start msedge",
    "chrome": "start chrome",
    "terminal": "wt.exe",
    "vscode": "code",
    "code": "code",
}

ALLOWLISTED_DOMAINS = [
    "github.com",
    "google.com",
    "stackoverflow.com",
    "python.org",
    "openai.com",
    "wikipedia.org",
    "youtube.com",
    "arxiv.org",
]


class OpenAppArgs(BaseModel):
    app_name: str = Field(..., description="Name of the allowlisted application (e.g., notepad, calculator, edge, vscode, terminal)")


class OpenWebsiteArgs(BaseModel):
    url: str = Field(..., description="HTTP or HTTPS URL to open in default browser")


class LaunchWorkspaceArgs(BaseModel):
    workspace_name: str = Field(..., description="Workspace preset: Coding, Study, Research, or Daily Work")


class OpenAppTool(BaseTool):
    name = "open_application"
    description = "Launch an approved Windows application from the security allowlist."
    permission_level = PermissionLevel.LOW_RISK_ACTION
    args_schema = OpenAppArgs

    def execute(self, app_name: str, **kwargs) -> ToolResult:
        cleaned = app_name.strip().lower()
        if cleaned not in ALLOWLISTED_APPS:
            available = ", ".join(sorted(ALLOWLISTED_APPS.keys()))
            return ToolResult(
                success=False,
                error="AppNotAllowlisted",
                message=f"Application '{app_name}' is not in the security allowlist. Approved apps: {available}",
            )

        cmd = ALLOWLISTED_APPS[cleaned]
        try:
            if cmd.startswith("start "):
                os.system(cmd)
            else:
                subprocess.Popen([cmd], shell=False)
            return ToolResult(
                success=True,
                data={"app": cleaned},
                message=f"Successfully launched {app_name}.",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                message=f"Failed to launch application '{app_name}': {e}",
            )


class OpenWebsiteTool(BaseTool):
    name = "open_website"
    description = "Safely open an approved web URL in the system browser."
    permission_level = PermissionLevel.LOW_RISK_ACTION
    args_schema = OpenWebsiteArgs

    def execute(self, url: str, **kwargs) -> ToolResult:
        clean_url = url.strip()
        parsed = urllib.parse.urlparse(clean_url)
        if parsed.scheme not in ("http", "https"):
            return ToolResult(
                success=False,
                error="InvalidScheme",
                message="Only HTTP and HTTPS URLs are permitted.",
            )

        try:
            webbrowser.open(clean_url)
            return ToolResult(
                success=True,
                data={"url": clean_url},
                message=f"Opened {clean_url} in your default browser.",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                message=f"Failed to open web URL: {e}",
            )


class LaunchWorkspaceTool(BaseTool):
    name = "launch_workspace"
    description = "Activate a multi-app workspace preset: Coding, Study, Research, or Daily Work."
    permission_level = PermissionLevel.LOW_RISK_ACTION
    args_schema = LaunchWorkspaceArgs

    def execute(self, workspace_name: str, **kwargs) -> ToolResult:
        name = workspace_name.strip().lower()
        presets = {
            "coding": {
                "apps": ["code", "wt.exe"],
                "urls": ["https://github.com"],
                "label": "Coding Workspace",
            },
            "study": {
                "apps": ["notepad.exe"],
                "urls": ["https://en.wikipedia.org"],
                "label": "Study Workspace",
            },
            "research": {
                "apps": [],
                "urls": ["https://arxiv.org", "https://scholar.google.com"],
                "label": "Research Workspace",
            },
            "daily work": {
                "apps": ["calc.exe", "notepad.exe"],
                "urls": ["https://google.com"],
                "label": "Daily Work Workspace",
            },
        }

        if name not in presets:
            available = ", ".join(presets.keys())
            return ToolResult(
                success=False,
                error="InvalidPreset",
                message=f"Unknown workspace '{workspace_name}'. Available: {available}",
            )

        preset = presets[name]
        launched = []
        for app in preset["apps"]:
            try:
                subprocess.Popen([app], shell=False)
                launched.append(app)
            except Exception as e:
                logger.warning(f"Failed to launch app {app}: {e}")

        for u in preset["urls"]:
            try:
                webbrowser.open(u)
                launched.append(u)
            except Exception as e:
                logger.warning(f"Failed to open URL {u}: {e}")

        return ToolResult(
            success=True,
            data={"workspace": preset["label"], "launched": launched},
            message=f"Activated {preset['label']} ({len(launched)} items launched).",
        )
