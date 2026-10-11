"""Local AI provider compatible with Ollama and vLLM OpenAI-compatible endpoints."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, List, Optional
from openai import OpenAI

from src.lokixai.config.settings import get_settings
from .base import BaseProvider, LLMMessage, LLMResponse, ModelCapability

logger = logging.getLogger("lokixai.providers.local")


class LocalProvider(BaseProvider):
    """Integrates with local Ollama, vLLM, or LMStudio servers."""

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        settings = get_settings()
        self.base_url = base_url or settings.local_ai_base_url
        self.default_model = model or settings.local_ai_model
        self.api_key = settings.local_ai_api_key or "ollama"
        self._client = OpenAI(base_url=self.base_url, api_key=self.api_key)

    def get_capabilities(self, model: str) -> ModelCapability:
        return ModelCapability(
            name=model or self.default_model,
            provider="Local/Ollama",
            supports_tools=True,
            supports_vision="vision" in model.lower(),
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
        target_model = model or self.default_model
        formatted_msgs = []
        for m in messages:
            msg_dict: Dict[str, Any] = {"role": m.role}
            if m.content is not None:
                msg_dict["content"] = m.content
            if m.tool_call_id:
                msg_dict["tool_call_id"] = m.tool_call_id
            if m.tool_calls:
                msg_dict["tool_calls"] = m.tool_calls
            formatted_msgs.append(msg_dict)

        kwargs: Dict[str, Any] = {
            "model": target_model,
            "messages": formatted_msgs,
            "temperature": temperature,
        }
        if tools:
            kwargs["tools"] = tools

        try:
            resp = self._client.chat.completions.create(**kwargs)
            choice = resp.choices[0]
            msg = choice.message
            tool_calls = []
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    tool_calls.append({
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    })

            return LLMResponse(
                content=msg.content,
                tool_calls=tool_calls,
                finish_reason=choice.finish_reason or "stop",
                model=target_model,
            )
        except Exception as e:
            raise ConnectionError(
                f"Failed to connect to Local AI server at {self.base_url}: {e}. Make sure Ollama or local LLM server is running."
            )

    def stream(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
    ) -> Iterator[str]:
        target_model = model or self.default_model
        formatted_msgs = [{"role": m.role, "content": m.content or ""} for m in messages]

        resp = self._client.chat.completions.create(
            model=target_model,
            messages=formatted_msgs,
            temperature=temperature,
            stream=True,
        )
        for chunk in resp:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content
