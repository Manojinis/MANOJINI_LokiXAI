"""Agent orchestrator for managing the LLM reasoning and bounded tool calling loop."""

from __future__ import annotations

import json
import logging
from typing import Any, Callable, Dict, List, Optional

from src.lokixai.config.settings import get_settings
from src.lokixai.providers import BaseProvider, get_provider
from src.lokixai.security.permissions import PermissionLevel
from src.lokixai.tools.base import ToolResult
from src.lokixai.tools.registry import ToolRegistry, get_tool_registry
from .conversation import ConversationSession, ChatMessage

logger = logging.getLogger("lokixai.ai.agent")

DEFAULT_SYSTEM_PROMPT = """You are LokiXAI, a high-performance, secure AI laptop copilot for Windows 11.
Your role is to assist the user with natural-language laptop automation, telemetry monitoring, document analysis, and developer workflows.

Core Guidelines:
1. Distinguish between explaining an action and performing it:
   - If the user asks how to do something (e.g. "How can I check RAM usage?", "How do I increase brightness?"), provide a clear, helpful explanation. Do NOT invoke tools.
   - If the user explicitly requests an action (e.g. "Check my RAM usage", "Set volume to 50", "Launch Coding workspace"), execute the verified tool from the registry.
2. Never claim an action succeeded unless the tool execution result confirms success.
3. Be concise, direct, helpful, and technically accurate.
4. If a tool fails or requires user confirmation, report the exact status honestly.
5. Format code blocks using Markdown with language identifiers (e.g. ```python).
"""


class AgentOrchestrator:
    """Coordinates reasoning, multi-step tool calls, and UI event streaming."""

    def __init__(
        self,
        provider: Optional[BaseProvider] = None,
        tool_registry: Optional[ToolRegistry] = None,
        max_turns: int = 5,
    ):
        self._custom_provider = provider
        self.tool_registry = tool_registry or get_tool_registry()
        self.max_turns = max_turns
        self.is_cancelled = False

    def get_active_provider(self) -> BaseProvider:
        """Dynamically resolve active provider from settings if not overridden."""
        if self._custom_provider:
            return self._custom_provider
        settings = get_settings()
        return get_provider(settings.ai_provider)

    def cancel(self) -> None:
        """Signal the agent loop to stop processing."""
        self.is_cancelled = True

    def process_turn(
        self,
        session: ConversationSession,
        user_input: str,
        confirm_callback: Optional[Callable[[str, Dict[str, Any], PermissionLevel], bool]] = None,
        on_token: Optional[Callable[[str], None]] = None,
        on_tool_start: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        on_tool_end: Optional[Callable[[str, ToolResult], None]] = None,
    ) -> str:
        """Execute one complete conversational turn with bounded tool calling."""
        if self.is_cancelled:
            self.is_cancelled = False
            msg = "[Operation cancelled by user]"
            if on_token:
                on_token(msg)
            session.add_assistant_message(msg)
            return msg
        self.is_cancelled = False
        session.add_user_message(user_input)
        tools_schema = self.tool_registry.get_openai_tools()
        active_provider = self.get_active_provider()

        accumulated_response = ""


        for turn_idx in range(self.max_turns):
            if self.is_cancelled:
                msg = "\n[Operation cancelled by user]"
                if on_token:
                    on_token(msg)
                session.add_assistant_message(accumulated_response + msg)
                return accumulated_response + msg

            llm_msgs = session.to_llm_messages(system_prompt=DEFAULT_SYSTEM_PROMPT)

            try:
                response = active_provider.generate(
                    messages=llm_msgs,
                    tools=tools_schema if tools_schema else None,
                )
            except Exception as e:
                err_text = f"AI Provider Error: {e}"
                logger.error(err_text)
                if on_token:
                    on_token(f"\n{err_text}")
                session.add_assistant_message(err_text)
                return err_text

            # Handle text content
            if response.content:
                accumulated_response += response.content
                if on_token:
                    on_token(response.content)

            # If no tool calls were requested, we are done
            if not response.tool_calls:
                session.add_assistant_message(response.content or accumulated_response)
                return accumulated_response

            # Process tool calls
            session.add_assistant_message(response.content, tool_calls=response.tool_calls)

            for tc in response.tool_calls:
                if self.is_cancelled:
                    break

                func_name = tc.get("function", {}).get("name", "")
                raw_args = tc.get("function", {}).get("arguments", "{}")
                tool_call_id = tc.get("id", "call_id")

                try:
                    args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                except Exception:
                    args = {}

                if on_tool_start:
                    on_tool_start(func_name, args)

                # Execute through secure registry
                result = self.tool_registry.execute(
                    name=func_name,
                    arguments=args,
                    caller="assistant",
                    confirm_callback=confirm_callback,
                )

                if on_tool_end:
                    on_tool_end(func_name, result)

                # Feed tool result back to session
                tool_output_str = json.dumps({
                    "success": result.success,
                    "message": result.message,
                    "data": result.data,
                    "error": result.error,
                })
                session.add_tool_result(
                    tool_call_id=tool_call_id,
                    tool_name=func_name,
                    content=tool_output_str,
                    is_error=not result.success,
                )

        return accumulated_response
