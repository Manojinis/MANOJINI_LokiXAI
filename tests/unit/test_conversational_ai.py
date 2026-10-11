"""Automated test suite verifying multi-turn conversational intelligence,

context continuity, intent routing, and action vs explanation differentiation.
"""

import pytest
from src.lokixai.ai.agent import AgentOrchestrator
from src.lokixai.ai.conversation import ConversationSession
from src.lokixai.providers.mock_provider import MockProvider


def test_general_knowledge_question():
    """Test 1: User asks a general knowledge question about artificial intelligence."""
    orchestrator = AgentOrchestrator(provider=MockProvider())
    session = ConversationSession()

    reply = orchestrator.process_turn(session, "What is artificial intelligence? Explain it in simple words with an example.")
    assert "Artificial Intelligence" in reply or "AI" in reply
    assert "Example" in reply or "example" in reply
    # Must NOT call tools for pure explanation
    assert len(session.messages) == 2  # 1 user + 1 assistant, 0 tool messages


def test_contextual_follow_up_three_applications():
    """Test 2: Follow-up asking for applications using conversation context."""
    orchestrator = AgentOrchestrator(provider=MockProvider())
    session = ConversationSession()

    orchestrator.process_turn(session, "What is artificial intelligence?")
    reply = orchestrator.process_turn(session, "Give me three real-world applications of it.")

    assert "Healthcare" in reply or "Autonomous Vehicles" in reply or "Fraud Detection" in reply
    assert len(session.messages) == 4


def test_reference_to_earlier_second_application():
    """Test 3: Referencing 'the second one' from previous answer."""
    orchestrator = AgentOrchestrator(provider=MockProvider())
    session = ConversationSession()

    orchestrator.process_turn(session, "What is artificial intelligence?")
    orchestrator.process_turn(session, "Give me three real-world applications of it.")
    reply = orchestrator.process_turn(session, "Explain the second application in more detail.")

    assert "Autonomous Vehicles" in reply or "Perception" in reply or "Sensor Fusion" in reply
    assert len(session.messages) == 6


def test_topic_connection_python_project():
    """Test 4: Topic continuation to build a related Python project."""
    orchestrator = AgentOrchestrator(provider=MockProvider())
    session = ConversationSession()

    orchestrator.process_turn(session, "What is artificial intelligence?")
    orchestrator.process_turn(session, "Give me three real-world applications of it.")
    orchestrator.process_turn(session, "Explain the second application in more detail.")
    reply = orchestrator.process_turn(session, "How could I build a small Python project related to that?")

    assert "python" in reply.lower()
    assert "```python" in reply or "OpenCV" in reply or "lane" in reply.lower()
    assert len(session.messages) == 8


def test_natural_reaction_simplification():
    """Test 5: Natural reaction when user says 'I don't understand. Explain more simply.'"""
    orchestrator = AgentOrchestrator(provider=MockProvider())
    session = ConversationSession()

    orchestrator.process_turn(session, "Explain how deep neural networks backpropagate gradients.")
    reply = orchestrator.process_turn(session, "I don't understand. Explain it more simply.")

    assert "learn" in reply.lower() or "bicycle" in reply.lower() or "practice" in reply.lower()


def test_topic_change_java_vs_python():
    """Test 6: Topic change comparing Python and Java."""
    orchestrator = AgentOrchestrator(provider=MockProvider())
    session = ConversationSession()

    orchestrator.process_turn(session, "Tell me about machine learning.")
    reply = orchestrator.process_turn(session, "Now explain the difference between Java and Python.")

    assert "Java" in reply and "Python" in reply
    assert "typed" in reply.lower() or "syntax" in reply.lower()


def test_action_vs_explanation_ram_explanation():
    """Test 7: Asking HOW to check RAM must explain, NOT execute a tool."""
    orchestrator = AgentOrchestrator(provider=MockProvider())
    session = ConversationSession()

    reply = orchestrator.process_turn(session, "How can I check my laptop's RAM usage?")
    # Must explain (e.g. Task Manager, Resource Monitor, etc.)
    assert "Task Manager" in reply or "Memory" in reply or "resmon" in reply
    # Must not contain tool call in session
    assert all(m.role != "tool" for m in session.messages)


def test_action_vs_explanation_ram_actual_execution():
    """Test 8: Explicit command to check RAM must call the system tool and report live telemetry."""
    orchestrator = AgentOrchestrator(provider=MockProvider())
    session = ConversationSession()

    reply = orchestrator.process_turn(session, "Check my current laptop RAM usage and tell me how much is being used.")
    # Must call get_system_metrics tool
    assert any(m.role == "tool" for m in session.messages)
    assert "RAM" in reply or "Memory" in reply or "Action verified" in reply or "CPU" in reply


def test_orchestrator_cancellation():
    """Test 9: Agent cancellation aborts turn cleanly."""
    orchestrator = AgentOrchestrator(provider=MockProvider())
    session = ConversationSession()
    orchestrator.cancel()

    reply = orchestrator.process_turn(session, "Hello assistant")
    assert "cancelled by user" in reply.lower()
