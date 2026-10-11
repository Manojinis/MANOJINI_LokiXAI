"""OpenAI provider implementation supporting modern SDK, robust exception handling, and tool calling."""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Iterator, List, Optional
import openai
from openai import OpenAI
from openai import (
    APIConnectionError,
    APIError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
)

from src.lokixai.config.settings import get_settings
from .base import BaseProvider, LLMMessage, LLMResponse, ModelCapability

logger = logging.getLogger("lokixai.providers.openai")


class OpenAIProvider(BaseProvider):
    """Integrates with OpenAI API for completions, vision, tools, and embeddings."""

    def __init__(self, api_key: Optional[str] = None, timeout: int = 45):
        settings = get_settings()
        self.api_key = api_key if api_key is not None else settings.openai_api_key
        self.timeout = timeout or settings.openai_timeout_seconds
        self._client: Optional[OpenAI] = None

    def _get_client(self) -> OpenAI:
        settings = get_settings()
        api_key = self.api_key if self.api_key is not None else (settings.openai_api_key or os.getenv("OPENAI_API_KEY"))
        if not api_key or not api_key.strip() or "your_openai_api_key_here" in str(api_key).lower():
            raise ValueError(
                "OpenAI API key is not configured. Please enter your API key in Settings or Model Hub, "
                "or set OPENAI_API_KEY in your .env file."
            )
        timeout = self.timeout or settings.openai_timeout_seconds
        return OpenAI(api_key=api_key.strip(), timeout=timeout)

    def _format_openai_error(self, e: Exception, model: str) -> str:
        """Translate OpenAI SDK exceptions into actionable, user-friendly guidance."""
        if isinstance(e, AuthenticationError):
            return (
                "OpenAI Authentication Error (401): Invalid API key or unauthorized access. "
                "Please verify your API key in Settings or Model Hub."
            )
        if isinstance(e, RateLimitError):
            return (
                "OpenAI Quota / Rate Limit Exceeded (429): You have exceeded your OpenAI API quota "
                "or rate limit. Please check your account billing and credit balance at "
                "https://platform.openai.com/account/billing."
            )
        if isinstance(e, NotFoundError):
            return (
                f"OpenAI Model Not Found (404): The selected model '{model}' does not exist or your account "
                f"lacks access to it. Try selecting 'gpt-4o' or 'gpt-4o-mini' in Model Hub."
            )
        if isinstance(e, PermissionDeniedError):
            return (
                f"OpenAI Permission Denied (403): Your API key does not have permissions to access '{model}'. "
                f"Please check your project and key permissions at platform.openai.com."
            )
        if isinstance(e, BadRequestError):
            return f"OpenAI Bad Request (400): {getattr(e, 'message', str(e))}"
        if isinstance(e, APITimeoutError):
            return "OpenAI Request Timeout: The request took too long to complete. Please check your network and retry."
        if isinstance(e, APIConnectionError):
            return "OpenAI Connection Error: Unable to reach OpenAI API servers. Please check your internet connectivity."
        if isinstance(e, InternalServerError):
            req_id = getattr(e, "request_id", None) or "N/A"
            return (
                f"OpenAI Server Error (500/503): OpenAI servers are currently experiencing issues "
                f"(Request ID: {req_id}). Please retry shortly."
            )
        if isinstance(e, APIStatusError):
            req_id = getattr(e, "request_id", None) or "N/A"
            return f"OpenAI API Error ({e.status_code}): {getattr(e, 'message', str(e))} (Request ID: {req_id})"
        if isinstance(e, APIError):
            return f"OpenAI API Error: {getattr(e, 'message', str(e))}"
        if isinstance(e, ValueError):
            return str(e)
        return f"AI Provider Error: {e}"

    def test_connection(self) -> tuple[bool, str]:
        """Verify API key validity against OpenAI API with a minimal chat request."""
        target_model = get_settings().openai_model or "gpt-4o"
        try:
            client = self._get_client()
            client.chat.completions.create(
                model=target_model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=2,
            )
            return True, f"Successfully connected to OpenAI API! Model '{target_model}' is active and operational."
        except Exception as e:
            err_msg = self._format_openai_error(e, target_model)
            logger.error(f"OpenAI test connection failed: {err_msg}")
            return False, err_msg

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
        target_model = model or get_settings().openai_model or "gpt-4o"
        try:
            client = self._get_client()

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
        except Exception as e:
            err_msg = self._format_openai_error(e, target_model)
            logger.error(f"OpenAI generate failed: {err_msg}")
            raise RuntimeError(err_msg) from e

    def stream(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
    ) -> Iterator[str]:
        target_model = model or get_settings().openai_model or "gpt-4o"
        try:
            client = self._get_client()
            formatted_msgs = [{"role": m.role, "content": m.content or ""} for m in messages]

            resp = client.chat.completions.create(
                model=target_model,
                messages=formatted_msgs,
                temperature=temperature,
                stream=True,
            )
            for chunk in resp:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            err_msg = self._format_openai_error(e, target_model)
            logger.error(f"OpenAI stream failed: {err_msg}")
            raise RuntimeError(err_msg) from e

    def embed(self, texts: List[str], model: Optional[str] = None) -> List[List[float]]:
        target_model = model or get_settings().openai_embedding_model or "text-embedding-3-small"
        try:
            client = self._get_client()
            res = client.embeddings.create(input=texts, model=target_model)
            return [item.embedding for item in res.data]
        except Exception as e:
            err_msg = self._format_openai_error(e, target_model)
            logger.error(f"OpenAI embeddings failed: {err_msg}")
            raise RuntimeError(err_msg) from e
