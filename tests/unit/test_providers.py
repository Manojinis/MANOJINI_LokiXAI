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
