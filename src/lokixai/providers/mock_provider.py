"""Deterministic offline mock provider for automated tests and zero-key local operation."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, Iterator, List, Optional
from .base import BaseProvider, LLMMessage, LLMResponse, ModelCapability


class MockProvider(BaseProvider):
    """Rule-based offline assistant that parses commands into real tool calls."""

    def get_capabilities(self, model: str) -> ModelCapability:
        return ModelCapability(
            name="mock-offline-core",
            provider="LokiOfflineCore",
            supports_tools=True,
            supports_vision=True,
            supports_streaming=True,
            supports_embeddings=True,
        )

    def generate(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
    ) -> LLMResponse:
        # Get last user message
        last_user = ""
        for m in reversed(messages):
            if m.role == "user" and m.content:
                last_user = m.content.strip().lower()
                break

        # Check for tool call responses in history
        last_tool_msg = None
        for m in reversed(messages):
            if m.role == "tool":
                last_tool_msg = m
                break

        if last_tool_msg:
            # We already ran a tool, summarize the outcome!
            return LLMResponse(
                content=f"Action complete! Tool result:\n{last_tool_msg.content}",
                finish_reason="stop",
                model="mock-offline-core",
            )

        # Match intent to registered tools
        # 1. Volume
        vol_match = re.search(r"(?:set\s+)?volume\s+(?:to\s+)?(\d+)", last_user)
        if vol_match:
            vol_val = int(vol_match.group(1))
            return LLMResponse(
                tool_calls=[{
                    "id": "call_mock_vol_1",
                    "type": "function",
                    "function": {
                        "name": "set_master_volume",
                        "arguments": json.dumps({"level": vol_val}),
                    },
                }],
                finish_reason="tool_calls",
                model="mock-offline-core",
            )

        if "mute" in last_user:
            is_unmute = "unmute" in last_user
            return LLMResponse(
                tool_calls=[{
                    "id": "call_mock_mute_1",
                    "type": "function",
                    "function": {
                        "name": "set_audio_mute",
                        "arguments": json.dumps({"mute": not is_unmute}),
                    },
                }],
                finish_reason="tool_calls",
                model="mock-offline-core",
            )

        # 2. Brightness
        bright_match = re.search(r"brightness\s+(?:to\s+)?(\d+)", last_user)
        if bright_match:
            b_val = int(bright_match.group(1))
            return LLMResponse(
                tool_calls=[{
                    "id": "call_mock_bright_1",
                    "type": "function",
                    "function": {
                        "name": "set_screen_brightness",
                        "arguments": json.dumps({"level": b_val}),
                    },
                }],
                finish_reason="tool_calls",
                model="mock-offline-core",
            )

        # 3. System stats / metrics / battery
        if any(k in last_user for k in ["metric", "cpu", "ram", "system health", "telemetry", "laptop status"]):
            return LLMResponse(
                tool_calls=[{
                    "id": "call_mock_metrics_1",
                    "type": "function",
                    "function": {
                        "name": "get_system_metrics",
                        "arguments": "{}",
                    },
                }],
                finish_reason="tool_calls",
                model="mock-offline-core",
            )

        if "battery" in last_user:
            return LLMResponse(
                tool_calls=[{
                    "id": "call_mock_battery_1",
                    "type": "function",
                    "function": {
                        "name": "get_battery_status",
                        "arguments": "{}",
                    },
                }],
                finish_reason="tool_calls",
                model="mock-offline-core",
            )

        # 4. Apps
        for app in ["notepad", "calculator", "calc", "paint", "terminal", "vscode", "explorer"]:
            if f"open {app}" in last_user or f"launch {app}" in last_user:
                return LLMResponse(
                    tool_calls=[{
                        "id": f"call_mock_app_{app}",
                        "type": "function",
                        "function": {
                            "name": "open_application",
                            "arguments": json.dumps({"app_name": app}),
                        },
                    }],
                    finish_reason="tool_calls",
                    model="mock-offline-core",
                )

        # 5. Workspaces
        for ws in ["coding", "study", "research", "daily work"]:
            if f"workspace" in last_user and ws in last_user:
                return LLMResponse(
                    tool_calls=[{
                        "id": f"call_mock_ws_{ws}",
                        "type": "function",
                        "function": {
                            "name": "launch_workspace",
                            "arguments": json.dumps({"workspace_name": ws}),
                        },
                    }],
                    finish_reason="tool_calls",
                    model="mock-offline-core",
                )

        # Default conversational reply
        return LLMResponse(
            content=f"Hello! I am LokiXAI, your intelligent Windows laptop assistant. You said: '{last_user}'. I can monitor system telemetry, adjust brightness or volume, launch workspaces, analyze files, and automate routines.",
            finish_reason="stop",
            model="mock-offline-core",
        )

    def stream(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
    ) -> Iterator[str]:
        resp = self.generate(messages, model, tools, temperature)
        if resp.content:
            for word in resp.content.split():
                yield word + " "

    def embed(self, texts: List[str], model: Optional[str] = None) -> List[List[float]]:
        # Return deterministic dummy 384-dim normalized vectors
        import hashlib
        vectors = []
        for text in texts:
            seed = int(hashlib.md5(text.encode("utf-8")).hexdigest()[:8], 16)
            vec = [(seed % (i + 1)) / 100.0 for i in range(384)]
            vectors.append(vec)
        return vectors
