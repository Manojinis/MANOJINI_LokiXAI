"""Safe file manager backend bound strictly to approved directory roots."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from src.lokixai.config.settings import get_settings
from src.lokixai.security.path_guard import PathGuard
from src.lokixai.security.permissions import SecurityAccessDeniedError


class FileEntry(BaseModel):
    name: str
    path: str
    is_dir: bool
    size_bytes: int
    modified_time: str
    extension: str


class SafeFileManager:
    """Provides high-level validated file operations strictly within approved roots."""

    def __init__(self):
        self.settings = get_settings()

    def get_guard(self) -> PathGuard:
        return PathGuard(self.settings.approved_directories)

    def list_directory(self, dir_path: str) -> List[FileEntry]:
        guard = self.get_guard()
        target = guard.validate_or_raise(dir_path)

        if not target.is_dir():
            raise NotADirectoryError(f"'{target}' is not a directory.")

        results: List[FileEntry] = []
        for item in sorted(target.iterdir()):
            try:
                stat = item.stat()
                import datetime
                mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                results.append(FileEntry(
                    name=item.name,
                    path=str(item),
                    is_dir=item.is_dir(),
                    size_bytes=stat.st_size if item.is_file() else 0,
                    modified_time=mtime,
                    extension=item.suffix.lower(),
                ))
            except (PermissionError, FileNotFoundError):
                continue

        return results

    def read_preview(self, file_path: str, max_lines: int = 150) -> str:
        guard = self.get_guard()
        target = guard.validate_or_raise(file_path)

        if not target.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        lines = []
        with open(target, "r", encoding="utf-8", errors="replace") as f:
            for _ in range(max_lines):
                line = f.readline()
                if not line:
                    break
                lines.append(line)
        return "".join(lines)

    def search_files(self, dir_path: str, query: str, extension: Optional[str] = None) -> List[FileEntry]:
        guard = self.get_guard()
        target = guard.validate_or_raise(dir_path)
        results: List[FileEntry] = []
        q = query.lower()

        for root, dirs, files in os.walk(target):
            # Check guard for walked subdirectories
            if not guard.is_safe_path(root):
                continue
            for f in files:
                if q in f.lower():
                    ext = os.path.splitext(f)[1].lower()
                    if extension and ext != extension.lower():
                        continue
                    full = Path(root) / f
                    try:
                        stat = full.stat()
                        import datetime
                        mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                        results.append(FileEntry(
                            name=f,
                            path=str(full),
                            is_dir=False,
                            size_bytes=stat.st_size,
                            modified_time=mtime,
                            extension=ext,
                        ))
                    except Exception:
                        continue
        return results
