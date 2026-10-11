"""Structured audit logging and action history."""

from __future__ import annotations

from collections import deque
from datetime import datetime
import json
import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field

from .redaction import SecretRedactor

logger = logging.getLogger("lokixai.audit")


class AuditEvent(BaseModel):
    """Represents a discrete tool invocation or system action."""
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    event_id: str = Field(default_factory=lambda: datetime.now().strftime("%Y%m%d%H%M%S%f"))
    tool_name: str
    caller: str = "assistant"
    parameters: Dict[str, Any] = Field(default_factory=dict)
    status: str = "PENDING"  # PENDING, SUCCESS, DENIED, FAILED, CANCELLED
    duration_ms: float = 0.0
    error: Optional[str] = None
    output_summary: Optional[str] = None


class AuditLogger:
    """Manages appending and retrieval of structured audit trails."""

    def __init__(self, log_dir: str = "data", max_in_memory: int = 250):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "audit_log.jsonl"
        self._history: deque[AuditEvent] = deque(maxlen=max_in_memory)
        self._listeners: List[Callable[[AuditEvent], None]] = []
        self._load_recent()

    def _load_recent(self) -> None:
        if not self.log_file.exists():
            return
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines[-100:]:
                    try:
                        record = json.loads(line)
                        self._history.append(AuditEvent(**record))
                    except Exception:
                        continue
        except Exception as e:
            logger.warning(f"Could not load previous audit logs: {e}")

    def add_listener(self, callback: Callable[[AuditEvent], None]) -> None:
        """Register a callback for real-time UI notification."""
        self._listeners.append(callback)

    def log_event(self, event: AuditEvent) -> None:
        """Log an event, masking secrets and persisting to JSONL."""
        # Redact parameters
        safe_params = SecretRedactor.redact_structure(event.parameters)
        safe_event = event.model_copy(update={"parameters": safe_params})
        
        self._history.append(safe_event)
        
        # Append to jsonl
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(safe_event.model_dump_json() + "\n")
        except Exception as e:
            logger.error(f"Failed to persist audit log: {e}")

        # Notify UI listeners
        for listener in self._listeners:
            try:
                listener(safe_event)
            except Exception as e:
                logger.error(f"Error in audit listener: {e}")

    def get_recent(self, limit: int = 50) -> List[AuditEvent]:
        """Return the most recent audit events."""
        items = list(self._history)
        return items[-limit:]


_global_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    global _global_audit_logger
    if _global_audit_logger is None:
        _global_audit_logger = AuditLogger()
    return _global_audit_logger
