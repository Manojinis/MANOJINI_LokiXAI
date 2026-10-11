"""Conversation sessions and message history management."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field

from src.lokixai.providers.base import LLMMessage


class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: str  # user, assistant, system, tool
    content: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    tool_name: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))
    is_error: bool = False


class ConversationSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "New Conversation"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    messages: List[ChatMessage] = Field(default_factory=list)

    def add_user_message(self, text: str) -> ChatMessage:
        msg = ChatMessage(role="user", content=text)
        self.messages.append(msg)
        if len(self.messages) == 1 or self.title == "New Conversation":
            # Generate short title from first query
            clean = text.strip()
            self.title = (clean[:30] + "...") if len(clean) > 30 else clean
        return msg

    def add_assistant_message(
        self,
        text: Optional[str] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
    ) -> ChatMessage:
        msg = ChatMessage(role="assistant", content=text, tool_calls=tool_calls)
        self.messages.append(msg)
        return msg

    def add_tool_result(self, tool_call_id: str, tool_name: str, content: str, is_error: bool = False) -> ChatMessage:
        msg = ChatMessage(
            role="tool",
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            content=content,
            is_error=is_error,
        )
        self.messages.append(msg)
        return msg

    def to_llm_messages(self, system_prompt: Optional[str] = None) -> List[LLMMessage]:
        result = []
        if system_prompt:
            result.append(LLMMessage(role="system", content=system_prompt))

        for m in self.messages:
            result.append(LLMMessage(
                role=m.role,
                content=m.content,
                tool_calls=m.tool_calls,
                tool_call_id=m.tool_call_id,
                name=m.tool_name,
            ))
        return result
