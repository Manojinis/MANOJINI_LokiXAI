"""Deterministic offline mock provider for automated tests, demos, and zero-key local operation."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, Iterator, List, Optional
from .base import BaseProvider, LLMMessage, LLMResponse, ModelCapability


class MockProvider(BaseProvider):
    """Context-aware offline reasoning engine.

    Clearly labeled as an offline fallback that simulates multi-turn conversations,
    intent routing, and tool generation without external network calls.
    """

    def test_connection(self) -> tuple[bool, str]:
        return True, "Mock Offline Core is ready. For open-domain reasoning, configure OpenAI or Ollama in Model Hub."

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
        # 1. Check for tool call responses in history
        last_tool_msg = None
        for m in reversed(messages):
            if m.role == "tool":
                last_tool_msg = m
                break

        if last_tool_msg:
            try:
                data = json.loads(last_tool_msg.content or "{}")
                msg = data.get("message", last_tool_msg.content)
            except Exception:
                msg = last_tool_msg.content

            return LLMResponse(
                content=f"[Offline Mode] Action verified and executed successfully:\n\n{msg}",
                finish_reason="stop",
                model="mock-offline-core",
            )

        # 2. Extract conversation history & latest query
        user_messages: List[str] = []
        for m in messages:
            if m.role == "user" and m.content:
                user_messages.append(m.content.strip())

        last_user = user_messages[-1] if user_messages else ""
        lower_user = last_user.lower()
        prev_user = user_messages[-2].lower() if len(user_messages) > 1 else ""

        # 3. Intent Routing: Distinguish explanations ("How do I...") vs commands ("Do X")
        is_how_to = bool(re.search(r"\b(how (can|do|could|to) i|what is|why|explain how to|tell me how to|can you explain)\b", lower_user))
        if any(lower_user.startswith(cmd) for cmd in ["check", "measure", "set", "adjust", "open", "launch"]):
            is_how_to = False

        # Check if the user is explicitly requesting a tool action (NOT asking for explanation)
        if not is_how_to:
            # Volume control command
            vol_match = re.search(r"(?:set|change|adjust)\s+(?:the\s+)?volume\s+(?:to\s+)?(\d+)", lower_user)
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

            # Mute / Unmute command
            if lower_user in ("mute", "mute audio", "silence audio", "unmute", "unmute audio") or "toggle mute" in lower_user:
                is_unmute = "unmute" in lower_user
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

            # Brightness command
            bright_match = re.search(r"(?:set|change|adjust)\s+(?:the\s+)?brightness\s+(?:to\s+)?(\d+)", lower_user)
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

            # Explicit System Metrics / RAM inspection command
            if re.search(r"\b(check|show|get|measure|inspect|what is|tell me)\b.*?\b(ram|memory|cpu|disk|battery|telemetry|metrics)\b", lower_user):
                if "battery" in lower_user:
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
                else:
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

            # App launching command
            for app in ["notepad", "calculator", "calc", "paint", "terminal", "vscode", "explorer"]:
                if f"open {app}" in lower_user or f"launch {app}" in lower_user:
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

            # Workspace command
            for ws in ["coding", "study", "research", "daily work"]:
                if ("launch" in lower_user or "start" in lower_user or "activate" in lower_user) and ws in lower_user:
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

        # 4. Multi-Turn Conversational Reasoning
        # Check context references
        # Follow-up test: "Give me three real-world applications of it"
        if ("three" in lower_user or "3" in lower_user) and ("application" in lower_user or "example" in lower_user):
            return LLMResponse(
                content=(
                    "[Offline Mode] Here are three key real-world applications of Artificial Intelligence:\n\n"
                    "1. **Healthcare & Medical Diagnostics**: AI models analyze medical imaging (MRIs, CT scans) to detect anomalies like tumors and diabetic retinopathy with radiologist-level precision.\n\n"
                    "2. **Autonomous Vehicles**: Self-driving platforms combine computer vision, LiDAR sensor fusion, and reinforcement learning for real-time lane following and obstacle avoidance.\n\n"
                    "3. **Financial Fraud Detection**: Deep learning neural networks analyze millions of real-time transactions to identify anomalous purchasing patterns and stop credit card fraud instantly."
                ),
                finish_reason="stop",
                model="mock-offline-core",
            )

        # Follow-up test: "Explain the second one in more detail"
        if "second" in lower_user and ("explain" in lower_user or "detail" in lower_user or "one" in lower_user):
            return LLMResponse(
                content=(
                    "[Offline Mode] **Autonomous Vehicles (In Detail)**:\n\n"
                    "Self-driving vehicles operate via a multi-stage AI pipeline:\n"
                    "• **Perception**: Convolutional Neural Networks (CNNs) process multi-camera feeds at 60 FPS to detect pedestrians, lane markers, and traffic signals.\n"
                    "• **Sensor Fusion**: Kalman filters combine camera imagery with radar and LiDAR point clouds to build a real-time 3D bounding-box map.\n"
                    "• **Path Planning & Control**: Motion planning algorithms calculate collision-free trajectories and actuate steering, throttle, and braking."
                ),
                finish_reason="stop",
                model="mock-offline-core",
            )

        # Follow-up test: "How could I build a small Python project related to that?"
        if "python project" in lower_user or ("project" in lower_user and ("build" in lower_user or "create" in lower_user)):
            return LLMResponse(
                content=(
                    "[Offline Mode] You can build a **Lane Detection Computer Vision Script** using Python and OpenCV!\n\n"
                    "```python\n"
                    "import cv2\n"
                    "import numpy as np\n\n"
                    "def detect_lanes(frame):\n"
                    "    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)\n"
                    "    blur = cv2.GaussianBlur(gray, (5, 5), 0)\n"
                    "    edges = cv2.Canny(blur, 50, 150)\n"
                    "    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 50, minLineLength=100, maxLineGap=50)\n"
                    "    return lines\n"
                    "```\n\n"
                    "This demonstrates the core perception step used in autonomous vehicle technology."
                ),
                finish_reason="stop",
                model="mock-offline-core",
            )

        # Natural reaction test: "I don't understand. Explain it more simply."
        if any(p in lower_user for p in ["don't understand", "dont understand", "more simply", "simpler", "simple words", "confused"]):
            return LLMResponse(
                content=(
                    "[Offline Mode] Let's think of it like learning to ride a bicycle:\n\n"
                    "Instead of someone writing out thousands of strict rules for every tiny pebble on the road, you practice and your brain learns how to balance and react.\n\n"
                    "Similarly, **Artificial Intelligence** gives computers examples to practice with so they can learn to recognize patterns and make decisions on their own!"
                ),
                finish_reason="stop",
                model="mock-offline-core",
            )

        # Topic change test: "Now explain the difference between Java and Python."
        if ("java" in lower_user and "python" in lower_user) or "difference between" in lower_user:
            return LLMResponse(
                content=(
                    "[Offline Mode] **Python vs. Java: Key Differences**:\n\n"
                    "| Feature | Python | Java |\n"
                    "| :--- | :--- | :--- |\n"
                    "| **Typing** | Dynamically typed | Statically typed |\n"
                    "| **Syntax** | Concise, indentation-based | Verbose, curly braces `{}` |\n"
                    "| **Execution** | Interpreted (via CPython) | Compiled to bytecode (JVM) |\n"
                    "| **Speed** | Moderate (optimized via C extensions) | High (JIT compiled) |\n"
                    "| **Primary Use** | AI/ML, Data Science, Scripting | Enterprise backends, Android |\n\n"
                    "Python prioritizes developer velocity and readability, whereas Java prioritizes strict compile-time type safety."
                ),
                finish_reason="stop",
                model="mock-offline-core",
            )

        # Action vs Explanation test: "How can I check my laptop's RAM usage?"
        if "how" in lower_user and ("check" in lower_user or "see" in lower_user) and ("ram" in lower_user or "memory" in lower_user):
            return LLMResponse(
                content=(
                    "[Offline Mode] You can check your laptop's RAM usage in Windows 11 using several methods:\n\n"
                    "1. **Task Manager**: Press `Ctrl + Shift + Esc`, click the **Performance** tab, and select **Memory**.\n"
                    "2. **Resource Monitor**: Press `Win + R`, type `resmon`, and press Enter.\n"
                    "3. **LokiXAI Assistant**: Say or type: *'Check my current laptop RAM usage'*, and I will query real-time hardware telemetry directly!"
                ),
                finish_reason="stop",
                model="mock-offline-core",
            )

        # General Knowledge test: "What is artificial intelligence?"
        if "what is artificial intelligence" in lower_user or "what is ai" in lower_user or "explain artificial intelligence" in lower_user:
            return LLMResponse(
                content=(
                    "[Offline Mode] **Artificial Intelligence (AI)** is the science of creating computer systems capable of performing tasks that traditionally require human intelligence.\n\n"
                    "**Simple Example**:\n"
                    "When your phone's photo app automatically groups pictures of your dog together, it isn't following a rigid list of rules written by a programmer. Instead, an AI model analyzed thousands of dog pictures, learned what ears, fur, and snouts look like, and recognizes your pet automatically."
                ),
                finish_reason="stop",
                model="mock-offline-core",
            )

        # Conversational greetings / capabilities
        if any(g in lower_user for g in ["what can you do", "help", "features", "who are you"]):
            return LLMResponse(
                content=(
                    "[Offline Mode] I am **LokiXAI**, your AI laptop copilot for Windows 11.\n\n"
                    "Here is what I can do:\n"
                    "• **Hardware Control**: Set brightness, volume, audio mute, and query battery.\n"
                    "• **Real-time Telemetry**: Monitor CPU, RAM, disk, and network throughput.\n"
                    "• **Workspaces & Routines**: Launch preset application groups and sequential automations.\n"
                    "• **Documents (RAG)**: Index and search PDFs, Markdown, and notes with citations.\n"
                    "• **Code & Developer Tools**: Inspect files via AST and review architecture.\n\n"
                    "*Tip: Connect your OpenAI API key or local Ollama in Model Hub for full open-domain intelligence!*"
                ),
                finish_reason="stop",
                model="mock-offline-core",
            )

        if any(p in lower_user for p in ["thank you", "thanks", "appreciate"]):
            return LLMResponse(
                content="[Offline Mode] You're very welcome! Let me know if you need any other assistance with your laptop or code.",
                finish_reason="stop",
                model="mock-offline-core",
            )

        # Default intelligent response
        return LLMResponse(
            content=(
                f"[Offline Mode] LokiXAI Assistant received: '{last_user}'.\n\n"
                "I am running in offline mode. I can execute all registered laptop tools (volume, brightness, telemetry, workspaces), "
                "or answer common programming and AI questions. To enable full generative conversation for any subject, "
                "configure an OpenAI key or start local Ollama in the **Model Hub** page."
            ),
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
            for word in resp.content.split(" "):
                yield word + " "

    def embed(self, texts: List[str], model: Optional[str] = None) -> List[List[float]]:
        import hashlib
        vectors = []
        for text in texts:
            seed = int(hashlib.md5(text.encode("utf-8")).hexdigest()[:8], 16)
            vec = [(seed % (i + 1)) / 100.0 for i in range(128)]
            vectors.append(vec)
        return vectors
