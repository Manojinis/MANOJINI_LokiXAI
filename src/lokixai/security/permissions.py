"""Role and risk-based permission manager for LokiXAI tools."""

from enum import Enum
from typing import Optional


class PermissionLevel(str, Enum):
    """Risk classification for tool actions."""
    SAFE_READ_ONLY = "SAFE_READ_ONLY"      # Non-mutating (e.g. read stats, inspect dir)
    LOW_RISK_ACTION = "LOW_RISK_ACTION"    # Benign system control (e.g. volume, brightness, open app)
    DESTRUCTIVE_ACTION = "DESTRUCTIVE_ACTION"  # File delete, overwrite, termination
    RESTRICTED = "RESTRICTED"              # Strictly forbidden (arbitrary shell, raw eval)


class SecurityAccessDeniedError(Exception):
    """Raised when an operation is prohibited by policy or denied by the user."""
    pass


class PermissionManager:
    """Evaluates whether an action requires explicit human confirmation."""

    @staticmethod
    def needs_confirmation(
        level: PermissionLevel,
        auto_approve_safe: bool = True,
        require_confirmation_destructive: bool = True,
    ) -> bool:
        if level == PermissionLevel.RESTRICTED:
            raise SecurityAccessDeniedError("Operation is strictly restricted by security policy.")
        
        if level == PermissionLevel.DESTRUCTIVE_ACTION:
            return require_confirmation_destructive
        
        if level == PermissionLevel.LOW_RISK_ACTION:
            return not auto_approve_safe
            
        return False
