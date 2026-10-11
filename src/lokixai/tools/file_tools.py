"""Safe file management tools bound to approved directories with traversal guard."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
from typing import List, Optional
from pydantic import BaseModel, Field

from src.lokixai.config.settings import get_settings
from src.lokixai.security.path_guard import PathGuard
from src.lokixai.security.permissions import PermissionLevel
from .base import BaseTool, ToolResult


class ListDirArgs(BaseModel):
    directory_path: str = Field(..., description="Directory path to inspect (must be in approved directories)")


class ReadFileArgs(BaseModel):
    file_path: str = Field(..., description="Path to file to read")
    max_lines: int = Field(default=100, ge=1, le=500, description="Maximum lines to read")


class CopyFileArgs(BaseModel):
    source_path: str = Field(..., description="Source file path")
    destination_path: str = Field(..., description="Destination file path")


class MoveFileArgs(BaseModel):
    source_path: str = Field(..., description="Source file path")
    destination_path: str = Field(..., description="Destination file path")


class DeleteFileArgs(BaseModel):
    file_path: str = Field(..., description="File path to delete")


class ListDirectoryTool(BaseTool):
    name = "list_directory"
    description = "List files and subdirectories within an approved directory."
    permission_level = PermissionLevel.SAFE_READ_ONLY
    args_schema = ListDirArgs

    def execute(self, directory_path: str, **kwargs) -> ToolResult:
        settings = get_settings()
        guard = PathGuard(settings.approved_directories)
        try:
            target = guard.validate_or_raise(directory_path)
            if not target.is_dir():
                return ToolResult(success=False, error="NotADirectory", message=f"'{target}' is not a directory.")

            entries = []
            for item in sorted(target.iterdir()):
                entries.append({
                    "name": item.name,
                    "is_dir": item.is_dir(),
                    "size_bytes": item.stat().st_size if item.is_file() else 0,
                })
            return ToolResult(
                success=True,
                data={"path": str(target), "entries": entries[:100], "total": len(entries)},
                message=f"Found {len(entries)} items in {target.name}.",
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e), message=f"Failed to list directory: {e}")


class ReadFilePreviewTool(BaseTool):
    name = "read_file_preview"
    description = "Preview the first lines of a text or code document within approved directories."
    permission_level = PermissionLevel.SAFE_READ_ONLY
    args_schema = ReadFileArgs

    def execute(self, file_path: str, max_lines: int = 100, **kwargs) -> ToolResult:
        settings = get_settings()
        guard = PathGuard(settings.approved_directories)
        try:
            target = guard.validate_or_raise(file_path)
            if not target.is_file():
                return ToolResult(success=False, error="FileNotFound", message=f"'{target}' does not exist or is not a file.")

            if target.stat().st_size > 10 * 1024 * 1024:
                return ToolResult(success=False, error="FileTooLarge", message="File exceeds 10MB safe preview limit.")

            lines = []
            with open(target, "r", encoding="utf-8", errors="replace") as f:
                for _ in range(max_lines):
                    line = f.readline()
                    if not line:
                        break
                    lines.append(line)

            content = "".join(lines)
            return ToolResult(
                success=True,
                data={"path": str(target), "line_count": len(lines), "content": content},
                message=f"Read {len(lines)} lines from {target.name}.",
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e), message=f"Failed to read file: {e}")


class CopyFileTool(BaseTool):
    name = "copy_file"
    description = "Safely copy a file between approved locations."
    permission_level = PermissionLevel.LOW_RISK_ACTION
    args_schema = CopyFileArgs

    def execute(self, source_path: str, destination_path: str, **kwargs) -> ToolResult:
        settings = get_settings()
        guard = PathGuard(settings.approved_directories)
        try:
            src = guard.validate_or_raise(source_path)
            dst = guard.validate_or_raise(destination_path)
            if not src.is_file():
                return ToolResult(success=False, error="SourceNotFound", message=f"Source file '{src}' does not exist.")

            shutil.copy2(src, dst)
            return ToolResult(
                success=True,
                data={"source": str(src), "destination": str(dst)},
                message=f"Copied {src.name} to {dst}.",
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e), message=f"Failed to copy file: {e}")


class MoveFileTool(BaseTool):
    name = "move_file"
    description = "Move a file from one approved location to another. Requires confirmation."
    permission_level = PermissionLevel.DESTRUCTIVE_ACTION
    args_schema = MoveFileArgs

    def execute(self, source_path: str, destination_path: str, **kwargs) -> ToolResult:
        settings = get_settings()
        guard = PathGuard(settings.approved_directories)
        try:
            src = guard.validate_or_raise(source_path)
            dst = guard.validate_or_raise(destination_path)
            if not src.is_file():
                return ToolResult(success=False, error="SourceNotFound", message=f"Source file '{src}' does not exist.")

            shutil.move(src, dst)
            return ToolResult(
                success=True,
                data={"source": str(src), "destination": str(dst)},
                message=f"Moved {src.name} to {dst}.",
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e), message=f"Failed to move file: {e}")


class DeleteFileTool(BaseTool):
    name = "delete_file"
    description = "Permanently delete a file in an approved directory. Requires confirmation."
    permission_level = PermissionLevel.DESTRUCTIVE_ACTION
    args_schema = DeleteFileArgs

    def execute(self, file_path: str, **kwargs) -> ToolResult:
        settings = get_settings()
        guard = PathGuard(settings.approved_directories)
        try:
            target = guard.validate_or_raise(file_path)
            if not target.is_file():
                return ToolResult(success=False, error="FileNotFound", message=f"File '{target}' not found.")

            target.unlink()
            return ToolResult(
                success=True,
                data={"deleted_path": str(target)},
                message=f"Successfully deleted {target.name}.",
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e), message=f"Failed to delete file: {e}")
