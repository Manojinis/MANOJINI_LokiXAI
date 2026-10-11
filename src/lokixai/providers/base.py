"""Base provider interface and model capability abstractions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, Iterator, List, Optional
from pydantic import BaseModel, Field


class ModelCapability(BaseModel):
    name: str
    provider: str
    supports_tools: bool = True
    supports_vision: bool = False
    supports_streaming: bool = True
    supports_embeddings: bool = False
    context_window: int = 128000


class LLMMessage(BaseModel):
    role: str  # system, user, assistant, tool
    content: Optional[str] = None
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None


class LLMResponse(BaseModel):
    content: Optional[str] = None
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    finish_reason: str = "stop"
    model: str = ""


class BaseProvider(ABC):
    """Abstract interface for AI Model Providers."""

    @abstractmethod
    def get_capabilities(self, model: str) -> ModelCapability:
        """Query model capabilities."""
        pass

    @abstractmethod
    def generate(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Synchronously produce a completion."""
        pass

    @abstractmethod
    def stream(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
    ) -> Iterator[str]:
        """Stream completion tokens."""
        pass

    def embed(self, texts: List[str], model: Optional[str] = None) -> List[List[float]]:
        """Optional vector embeddings generation."""
        raise NotImplementedError("Embeddings not supported by this provider.")
