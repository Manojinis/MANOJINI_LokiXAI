"""Providers package for LokiXAI model integrations."""

from .base import BaseProvider, LLMMessage, LLMResponse, ModelCapability
from .openai_provider import OpenAIProvider
from .local_provider import LocalProvider
from .mock_provider import MockProvider


def get_provider(provider_type: str = "openai") -> BaseProvider:
    """Factory to retrieve requested AI model provider."""
    p = provider_type.lower()
    if p == "openai":
        return OpenAIProvider()
    elif p in ("local", "ollama"):
        return LocalProvider()
    elif p == "mock":
        return MockProvider()
    else:
        return OpenAIProvider()


__all__ = [
    "BaseProvider",
    "LLMMessage",
    "LLMResponse",
    "ModelCapability",
    "OpenAIProvider",
    "LocalProvider",
    "MockProvider",
    "get_provider",
]
