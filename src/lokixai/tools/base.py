"""Base tool contract and schema definition for LokiXAI."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel
from src.lokixai.security.permissions import PermissionLevel


class ToolResult(BaseModel):
    """Normalized result of any tool invocation."""
    success: bool
    data: Any = None
    message: str = ""
    error: Optional[str] = None


class BaseTool(ABC):
    """Abstract base class for all callable tools."""

    name: str
    description: str
    permission_level: PermissionLevel = PermissionLevel.SAFE_READ_ONLY
    args_schema: Optional[Type[BaseModel]] = None

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Synchronously execute the tool action."""
        pass

    def to_openai_schema(self) -> Dict[str, Any]:
        """Generate OpenAI function/tool calling schema."""
        properties = {}
        required = []

        if self.args_schema:
            schema = self.args_schema.model_json_schema()
            properties = schema.get("properties", {})
            required = schema.get("required", [])

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }
