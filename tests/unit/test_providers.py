"""Unit tests for AI providers, capabilities, and offline mock logic."""

import pytest
from src.lokixai.providers.base import LLMMessage
from src.lokixai.providers.mock_provider import MockProvider
from src.lokixai.ai.conversation import ConversationSession
from src.lokixai.ai.agent import AgentOrchestrator


def test_mock_provider_capabilities():
    provider = MockProvider()
    caps = provider.get_capabilities("mock")
    assert caps.supports_tools is True
    assert caps.supports_streaming is True


def test_mock_provider_volume_tool_generation():
    provider = MockProvider()
    msgs = [LLMMessage(role="user", content="Please set volume to 45")]
    res = provider.generate(msgs)
    assert len(res.tool_calls) == 1
    call = res.tool_calls[0]
    assert call["function"]["name"] == "set_master_volume"
    assert "45" in call["function"]["arguments"]


def test_mock_provider_conversational_reply():
    provider = MockProvider()
    msgs = [LLMMessage(role="user", content="Hello assistant")]
    res = provider.generate(msgs)
    assert res.content is not None
    assert "LokiXAI" in res.content


def test_agent_orchestrator_turn_with_mock():
    orchestrator = AgentOrchestrator(provider=MockProvider())
    session = ConversationSession()
    reply = orchestrator.process_turn(session, "set volume to 30")
    assert "Action complete" in reply or "Master volume" in reply
    assert len(session.messages) >= 2


def test_openai_provider_missing_key_error():
    from src.lokixai.providers.openai_provider import OpenAIProvider
    provider = OpenAIProvider(api_key="")
    success, msg = provider.test_connection()
    assert success is False
    assert "OpenAI API key is not configured" in msg
    assert "APIStatusError" not in msg


def test_openai_provider_generate_missing_key_error():
    from src.lokixai.providers.openai_provider import OpenAIProvider
    provider = OpenAIProvider(api_key="")
    msgs = [LLMMessage(role="user", content="Hello")]
    with pytest.raises(RuntimeError) as exc_info:
        provider.generate(msgs)
    assert "OpenAI API key is not configured" in str(exc_info.value)
    assert "APIStatusError" not in str(exc_info.value)


def test_theme_manager_stylesheets():
    from src.lokixai.config.theme import ThemeManager, DARK_STYLESHEET, LIGHT_STYLESHEET
    dark_qss = ThemeManager.get_stylesheet("dark")
    light_qss = ThemeManager.get_stylesheet("light")
    assert dark_qss == DARK_STYLESHEET
    assert light_qss == LIGHT_STYLESHEET
    assert dark_qss != light_qss
    assert "#090d16" in dark_qss
    assert "#f8fafc" in light_qss
