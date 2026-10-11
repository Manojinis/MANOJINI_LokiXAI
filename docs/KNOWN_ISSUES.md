# LokiXAI — Known Issues & Environmental Prerequisites

**Last Updated:** 2026-10-11  
**Project:** LokiXAI — Advanced AI Laptop Automation Assistant

---

## 1. External Prerequisites & Environmental Dependencies

### 1.1 Cloud AI (OpenAI)
- **Prerequisite:** Valid OpenAI API key (`OPENAI_API_KEY`) with active credit balance.
- **Behavior without key:** The application runs in **Offline Mode** using `mock-offline-core`.
- **Honest Disclosure:** The offline mode is a deterministic reasoning and tool-calling engine, not an omniscient language model. For open-ended conversation across arbitrary domains, an OpenAI key or local Ollama model must be configured in **Model Hub** or **Settings**.

### 1.2 Local AI (Ollama)
- **Prerequisite:** Ollama installed and running on `http://localhost:11434` with at least one model pulled (e.g. `ollama run llama3.2`).
- **Behavior if offline:** Model Hub provides a direct connection test button that reports whether the daemon is unreachable and provides setup commands (`ollama serve`, `ollama pull llama3.2`).

### 1.3 Voice Input (Speech-to-Text)
- **Prerequisite:** Functional microphone input device and internet connectivity for OpenAI Whisper API (or local Vosk/Whisper model).
- **Behavior without API key / mic:** The Voice Assistant displays an honest notification explaining that transcription requires an active backend, rather than fabricating transcribed text. Text-to-speech (TTS via Windows SAPI `pyttsx3`) remains operational offline.

### 1.4 Windows Screen Brightness Control
- **Prerequisite:** Built-in laptop display or DDC/CI-compatible external monitor.
- **Behavior on desktop monitors without DDC/CI:** `screen_brightness_control` may return an error or empty list if the monitor does not expose hardware brightness over HDMI/DisplayPort. LokiXAI handles this gracefully without crashing and logs a notice.

---

## 2. Resolved Issues Catalog

| Issue ID | Description | Resolution Status |
| :--- | :--- | :--- |
| **SYM-01** | Pytest on Windows crashed with `WinError 5 Access is denied` when cleaning up dead symlinks in `%TEMP%\pytest-of-<user>`. | **RESOLVED:** Configured `pytest.ini` with `-p no:tmpdir` and established a workspace-local `tmp_path` fixture in `tests/conftest.py`. |
| **VOL-01** | `pycaw-2024+` raised `AttributeError: AudioDevice has no attribute Activate`. | **RESOLVED:** Updated `_get_endpoint_volume()` to access `device.EndpointVolume` directly while retaining backward-compatible COM casting fallback. |
| **DEV-01** | Missing `btn_row` variable in `developer_page.py` when building the review diff button layout. | **RESOLVED:** Added horizontal layout container `btn_row` to house the Analyze, Fix, and Review Diff buttons cleanly. |
| **CAN-01** | `AgentOrchestrator.process_turn` reset `self.is_cancelled = False` immediately at turn start, discarding pre-turn cancellations. | **RESOLVED:** Checked `if self.is_cancelled:` at function entry before clearing the flag, aborting turns cleanly. |
| **RAM-01** | Imperative commands like *"Check my current laptop RAM usage and tell me how much is being used"* were mistakenly categorized as how-to explanation questions due to `"tell me how"`. | **RESOLVED:** Refined regex and added imperative action prefix override (`check`, `measure`, `set`, etc.) so tool calls execute as intended while questions like *"How can I check RAM?"* return pure instructions. |

---

## 3. Security Boundary Verification

- **Arbitrary Command Execution:** Completely prevented. Shell commands, `eval()`, and `exec()` are disallowed.
- **File System Access:** Strictly bounded to `approved_roots`. Windows system directories (`C:\Windows`, `System32`) and directory traversal attacks (`..\..\`) are actively blocked by `PathGuard`.
- **API Keys & Credentials:** Automatically redacted by `SecretRedactor` before saving to audit logs or rendering in UI.
