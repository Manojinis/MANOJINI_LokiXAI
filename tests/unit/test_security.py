"""Unit tests for security policies, boundary guards, and secret redaction."""

import os
from pathlib import Path
import pytest

from src.lokixai.security.path_guard import PathGuard
from src.lokixai.security.permissions import (
    PermissionLevel,
    PermissionManager,
    SecurityAccessDeniedError,
)
from src.lokixai.security.redaction import SecretRedactor, redact_text
from src.lokixai.security.audit import AuditEvent, AuditLogger


def test_secret_redactor_openai_key():
    sample = "My key is sk-1234567890abcdef1234567890 and Bearer eyJhbGciOiJIUzI1NiIsIn"
    redacted = redact_text(sample)
    assert "sk-1234567890abcdef1234567890" not in redacted
    assert "[REDACTED_SECRET]" in redacted


def test_secret_redactor_nested_dict():
    data = {
        "user": "alice",
        "api_key": "sk-secret1234567890abcdefghij",
        "nested": {"token": "sensitive_val_12345"},
    }
    cleaned = SecretRedactor.redact_structure(data)
    assert cleaned["api_key"] == "[REDACTED_SECRET]"
    assert cleaned["nested"]["token"] == "[REDACTED_SECRET]"
    assert cleaned["user"] == "alice"


def test_path_guard_approved_directory(tmp_path):
    guard = PathGuard([tmp_path])
    safe_file = tmp_path / "doc.txt"
    safe_file.write_text("safe content")

    assert guard.is_safe_path(safe_file) is True
    validated = guard.validate_or_raise(safe_file)
    assert validated.resolve() == safe_file.resolve()


def test_path_guard_blocks_traversal(tmp_path):
    guard = PathGuard([tmp_path])
    # Outside directory traversal
    outside_target = tmp_path / ".." / "outside.txt"
    assert guard.is_safe_path(outside_target) is False

    with pytest.raises(SecurityAccessDeniedError):
        guard.validate_or_raise(outside_target)


def test_path_guard_blocks_windows_system():
    guard = PathGuard([r"C:\Windows\System32", r"C:\Users\Public"])
    assert guard.is_safe_path(r"C:\Windows\System32\cmd.exe") is False


def test_permission_manager():
    assert PermissionManager.needs_confirmation(PermissionLevel.SAFE_READ_ONLY) is False
    assert PermissionManager.needs_confirmation(PermissionLevel.LOW_RISK_ACTION, auto_approve_safe=True) is False
    assert PermissionManager.needs_confirmation(PermissionLevel.LOW_RISK_ACTION, auto_approve_safe=False) is True
    assert PermissionManager.needs_confirmation(PermissionLevel.DESTRUCTIVE_ACTION, require_confirmation_destructive=True) is True

    with pytest.raises(SecurityAccessDeniedError):
        PermissionManager.needs_confirmation(PermissionLevel.RESTRICTED)


def test_audit_logger(tmp_path):
    logger = AuditLogger(log_dir=str(tmp_path))
    ev = AuditEvent(
        tool_name="test_tool",
        parameters={"token": "sk-1234567890abcdef1234567890"},
        status="SUCCESS",
        duration_ms=42.5,
    )
    logger.log_event(ev)

    recent = logger.get_recent(limit=5)
    assert len(recent) == 1
    assert recent[0].tool_name == "test_tool"
    assert recent[0].parameters["token"] == "[REDACTED_SECRET]"
