"""OpenAI provider implementation supporting modern SDK and tool calling."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Iterator, List, Optional
import openai
from openai import OpenAI, APIError, AuthenticationError, APITimeoutError

from src.lokixai.config.settings import get_settings
from .base import BaseProvider, LLMMessage, LLMResponse, ModelCapability

logger = logging.getLogger("lokixai.providers.openai")


class OpenAIProvider(BaseProvider):
    """Integrates with OpenAI API for completions, vision, tools, and embeddings."""

    def __init__(self, api_key: Optional[str] = None, timeout: int = 45):
        settings = get_settings()
        self.api_key = api_key or settings.openai_api_key
        self.timeout = timeout or settings.openai_timeout_seconds
        self._client: Optional[OpenAI] = None

    def _get_client(self) -> OpenAI:
        settings = get_settings()
        api_key = self.api_key or settings.openai_api_key
        if not api_key:
            raise AuthenticationError("OpenAI API key not configured. Please add your key in Settings or Model Hub.")
        timeout = self.timeout or settings.openai_timeout_seconds
        return OpenAI(api_key=api_key, timeout=timeout)

    def test_connection(self) -> tuple[bool, str]:
        """Verify API key validity against OpenAI API."""
        try:
            client = self._get_client()
            client.models.list()
            return True, "Successfully connected to OpenAI API."
        except AuthenticationError:
            return False, "Authentication Error: Invalid OpenAI API key. Please check your credentials in Settings."
        except APITimeoutError:
            return False, "Timeout Error: OpenAI API took too long to respond. Check network connectivity."
        except Exception as e:
            return False, f"Connection Failed: {e}"


    def get_capabilities(self, model: str) -> ModelCapability:
        model_lower = model.lower()
        is_vision = any(k in model_lower for k in ["vision", "gpt-4o", "4o-mini"])
        return ModelCapability(
            name=model,
            provider="OpenAI",
            supports_tools=True,
            supports_vision=is_vision,
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
        client = self._get_client()
        target_model = model or get_settings().openai_model

        # Format messages for OpenAI
        formatted_msgs = []
        for m in messages:
            msg_dict: Dict[str, Any] = {"role": m.role}
            if m.content is not None:
                msg_dict["content"] = m.content
            if m.name:
                msg_dict["name"] = m.name
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
            kwargs["tool_choice"] = "auto"

        try:
            resp = client.chat.completions.create(**kwargs)
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
                model=resp.model,
            )
        except AuthenticationError:
            raise AuthenticationError("Invalid OpenAI API key. Please check your credentials in Settings.")
        except APITimeoutError:
            raise TimeoutError("OpenAI API request timed out. Please try again.")
        except APIError as e:
            raise RuntimeError(f"OpenAI API error: {e.message}")

    def stream(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
    ) -> Iterator[str]:
        client = self._get_client()
        target_model = model or get_settings().openai_model
        formatted_msgs = [{"role": m.role, "content": m.content or ""} for m in messages]

        resp = client.chat.completions.create(
            model=target_model,
            messages=formatted_msgs,
            temperature=temperature,
            stream=True,
        )
        for chunk in resp:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content

    def embed(self, texts: List[str], model: Optional[str] = None) -> List[List[float]]:
        client = self._get_client()
        target_model = model or get_settings().openai_embedding_model
        res = client.embeddings.create(input=texts, model=target_model)
        return [item.embedding for item in res.data]
