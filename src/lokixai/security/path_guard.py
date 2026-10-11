"""Canonical path validation and boundary guard to prevent traversal."""

import os
from pathlib import Path
from typing import List, Union
from .permissions import SecurityAccessDeniedError


class PathGuard:
    """Enforces strict directory boundary confinement for file operations."""

    def __init__(self, approved_directories: List[Union[str, Path]]):
        self.approved_roots: List[Path] = []
        for root in approved_directories:
            try:
                resolved = Path(root).expanduser().resolve()
                self.approved_roots.append(resolved)
            except Exception:
                continue

    def is_safe_path(self, target_path: Union[str, Path]) -> bool:
        """Check if target_path resides within one of the approved directories."""
        try:
            resolved_target = Path(target_path).expanduser().resolve()
        except Exception:
            return False

        # Disallow sensitive Windows system directories even if accidentally included
        win_sys = os.environ.get("SystemRoot", r"C:\Windows")
        if str(resolved_target).lower().startswith(win_sys.lower()):
            return False

        for approved_root in self.approved_roots:
            try:
                # Check if resolved_target is equal or relative to approved_root
                resolved_target.relative_to(approved_root)
                return True
            except ValueError:
                continue
        return False

    def validate_or_raise(self, target_path: Union[str, Path]) -> Path:
        """Validate path or raise SecurityAccessDeniedError."""
        resolved = Path(target_path).expanduser().resolve()
        if not self.is_safe_path(resolved):
            raise SecurityAccessDeniedError(
                f"Access Denied: Path '{target_path}' is outside approved directories."
            )
        return resolved
