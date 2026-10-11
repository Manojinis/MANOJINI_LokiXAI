"""Centralized registry for tool registration, permission checks, and execution."""

from __future__ import annotations

import logging
import time
from typing import Any, Callable, Dict, List, Optional
from pydantic import ValidationError

from src.lokixai.config.settings import get_settings
from src.lokixai.security.audit import AuditEvent, get_audit_logger
from src.lokixai.security.permissions import PermissionLevel, PermissionManager, SecurityAccessDeniedError
from src.lokixai.security.redaction import SecretRedactor
from .base import BaseTool, ToolResult
from .system_tools import (
    GetSystemMetricsTool,
    GetBrightnessTool,
    SetBrightnessTool,
    GetVolumeTool,
    SetVolumeTool,
    SetMuteTool,
    GetBatteryInfoTool,
)
from .app_tools import OpenAppTool, OpenWebsiteTool, LaunchWorkspaceTool
from .file_tools import (
    ListDirectoryTool,
    ReadFilePreviewTool,
    CopyFileTool,
    MoveFileTool,
    DeleteFileTool,
)

logger = logging.getLogger("lokixai.tools.registry")


class ToolRegistry:
    """Manages tool registration, argument validation, and secure dispatch."""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self.register_default_tools()

    def register(self, tool: BaseTool) -> None:
        """Register a tool instance."""
        self._tools[tool.name] = tool
        logger.debug(f"Registered tool: {tool.name}")

    def get(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def list_tools(self) -> List[BaseTool]:
        return list(self._tools.values())

    def get_openai_tools(self) -> List[Dict[str, Any]]:
        """Return all tool schemas formatted for OpenAI tool calling."""
        return [tool.to_openai_schema() for tool in self._tools.values()]

    def register_default_tools(self) -> None:
        """Register core system, application, and file management tools."""
        tools = [
            GetSystemMetricsTool(),
            GetBrightnessTool(),
            SetBrightnessTool(),
            GetVolumeTool(),
            SetVolumeTool(),
            SetMuteTool(),
            GetBatteryInfoTool(),
            OpenAppTool(),
            OpenWebsiteTool(),
            LaunchWorkspaceTool(),
            ListDirectoryTool(),
            ReadFilePreviewTool(),
            CopyFileTool(),
            MoveFileTool(),
            DeleteFileTool(),
        ]
        for t in tools:
            self.register(t)

    def execute(
        self,
        name: str,
        arguments: Dict[str, Any],
        caller: str = "assistant",
        confirm_callback: Optional[Callable[[str, Dict[str, Any], PermissionLevel], bool]] = None,
    ) -> ToolResult:
        """Execute a tool with full security, argument validation, and audit trail."""
        start_time = time.time()
        audit = get_audit_logger()
        settings = get_settings()

        tool = self.get(name)
        if not tool:
            err = f"Tool '{name}' is not registered or permitted."
            audit.log_event(AuditEvent(
                tool_name=name,
                caller=caller,
                parameters=arguments,
                status="FAILED",
                error=err,
            ))
            return ToolResult(success=False, error="ToolNotFound", message=err)

        # Permission verification
        try:
            needs_confirm = PermissionManager.needs_confirmation(
                level=tool.permission_level,
                auto_approve_safe=settings.auto_approve_safe_tools,
                require_confirmation_destructive=settings.require_confirmation_destructive,
            )
            if needs_confirm:
                if confirm_callback:
                    approved = confirm_callback(tool.name, arguments, tool.permission_level)
                    if not approved:
                        audit.log_event(AuditEvent(
                            tool_name=name,
                            caller=caller,
                            parameters=arguments,
                            status="DENIED",
                            error="Action rejected by user.",
                        ))
                        return ToolResult(
                            success=False,
                            error="ActionDeniedByUser",
                            message="Action was cancelled by the user in the confirmation prompt.",
                        )
                else:
                    # No confirmation callback provided for a destructive action
                    err = f"Tool '{name}' requires explicit confirmation, but no dialog handler was provided."
                    audit.log_event(AuditEvent(
                        tool_name=name,
                        caller=caller,
                        parameters=arguments,
                        status="DENIED",
                        error=err,
                    ))
                    return ToolResult(success=False, error="ConfirmationRequired", message=err)

        except SecurityAccessDeniedError as e:
            audit.log_event(AuditEvent(
                tool_name=name,
                caller=caller,
                parameters=arguments,
                status="DENIED",
                error=str(e),
            ))
            return ToolResult(success=False, error="AccessDenied", message=str(e))

        # Schema Validation
        validated_args = arguments
        if tool.args_schema:
            try:
                parsed = tool.args_schema(**arguments)
                validated_args = parsed.model_dump()
            except ValidationError as ve:
                err = f"Invalid arguments for {name}: {ve}"
                audit.log_event(AuditEvent(
                    tool_name=name,
                    caller=caller,
                    parameters=arguments,
                    status="FAILED",
                    error=err,
                ))
                return ToolResult(success=False, error="InvalidArguments", message=err)

        # Tool Execution
        try:
            result = tool.execute(**validated_args)
            duration_ms = (time.time() - start_time) * 1000.0
            
            audit.log_event(AuditEvent(
                tool_name=name,
                caller=caller,
                parameters=validated_args,
                status="SUCCESS" if result.success else "FAILED",
                duration_ms=round(duration_ms, 2),
                output_summary=SecretRedactor.redact(result.message),
                error=result.error,
            ))
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000.0
            err_str = SecretRedactor.redact(str(e))
            audit.log_event(AuditEvent(
                tool_name=name,
                caller=caller,
                parameters=validated_args,
                status="FAILED",
                duration_ms=round(duration_ms, 2),
                error=err_str,
            ))
            return ToolResult(success=False, error=err_str, message=f"Execution error in {name}: {err_str}")


_global_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
    return _global_registry
