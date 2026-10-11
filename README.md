# LokiXAI — Advanced AI Laptop Automation Assistant

> **"Your Laptop. Your Intelligence. Your Control."**  
> An intelligent, secure desktop AI copilot engineered for **Windows 11**.

---

## 1. Project Overview

**LokiXAI** is an advanced desktop AI copilot built with Python and PySide6 (Qt) designed to control Windows laptop hardware, stream telemetry, automate daily workflows, analyze documents via RAG, assist developers, and inspect visual screen captures—backed by a centralized cybersecurity architecture.

### Key Capabilities
- **Real AI Chat & Agent Orchestrator:** Multi-step function calling through allowlisted tool registries, streaming responses, context memory, and authentic error diagnostics with recovery guidance. Operates under a strict **Zero-Mock Policy**: never silently substitutes fake or canned responses.
- **Light / Dark / System Themes:** Complete theme engine supporting clean Light mode, sleek futuristic Dark mode, and automatic Windows 11 system theme synchronization.
- **Hardware Telemetry & System Controls:** Real-time CPU, RAM, disk, battery, network throughput, and uptime tracking; direct display brightness and master audio volume controls.
- **Multi-App Workspaces:** One-click launch presets for **Coding** (VSCode + Terminal + GitHub), **Study**, **Research**, and **Daily Work**.
- **Smart Routines Studio:** Visual routine builder with sequential execution, structured JSON definitions, and automatic stop-on-failure safety.
- **RAG Document Assistant:** PDF/Markdown text extraction, semantic chunking, vector indexing, and passage retrieval with genuine citations.
- **Safe File Manager:** Bounded directory browsing, search, file preview, and deletion/move operations protected by confirmation dialogs and path traversal guards.
- **Developer Copilot:** Static AST code analysis, symbol inspection (classes/functions), secret redaction, architecture reviews, and test generation.
- **Screen-Aware Assistant:** User-initiated screenshot capture, preview thumbnail, cancel/discard protection, and structured vision analysis via OpenAI GPT-4o.
- **Model Hub:** Dynamic switching between **OpenAI Cloud** (`gpt-4o`, `gpt-4o-mini`, `o1-mini`) and local OpenAI-compatible endpoints (**Ollama**, **vLLM**) with active connection testing.
- **Security & Audit Trail:** Allowlisted executables only, parameter schema validation, secret masking (API keys, tokens), and real-time immutable JSONL audit logging.

---

## 2. Architecture & Directory Structure

```
LokiXAI/
├── main.py                     # Application entry point with high-DPI scaling & rotating logs
├── requirements.txt            # Dependency configuration
├── .env.example                # Configuration environment template
├── .gitignore                  # Git ignore rules (protects .env and local data)
├── README.md                   # Complete documentation & operational manual
├── docs/                       # Audit, verification, and environmental issue documentation
│   ├── IMPLEMENTATION_AUDIT.md # Discovery checklist and root-cause resolution matrix
│   ├── VERIFICATION_REPORT.md  # Test results & step-by-step user manual verification guide
│   └── KNOWN_ISSUES.md         # Prerequisites, environmental notes, and resolved defects
├── src/
│   └── lokixai/
│       ├── config/             # AppSettings (Pydantic), ThemeManager (Light/Dark/System QSS)
│       ├── security/           # PathGuard, PermissionManager, SecretRedactor, AuditLogger
│       ├── monitoring/         # Real-time hardware telemetry background worker (psutil)
│       ├── tools/              # Allowlisted system, app, and safe file tools + registry
│       ├── providers/          # OpenAI Cloud and Ollama Local provider implementations
│       ├── ai/                 # Bounded agent orchestrator & conversation session models
│       ├── automation/         # Workspace launchers & sequential Smart Routines engine
│       ├── voice/              # Push-to-talk recording (STT) & non-blocking pyttsx3 (TTS)
│       ├── rag/                # DocumentLoader (pypdf), TextChunker, and VectorStore
│       ├── files/              # Safe file manager with boundary enforcement
│       ├── developer/          # Static AST code analyzer & unit test suggester
│       ├── screen/             # Explicit screenshot grabber & base64 vision formatter
│       ├── storage/            # Local JSON session, routine, and workspace persistence
│       └── ui/
│           ├── main_window.py  # Central shell hosting header, sidebar, right panel, and stack
│           ├── components/     # Sidebar, Header, RightPanel, ConfirmationDialog
│           └── pages/          # 13 Dedicated functional pages
├── tests/
│   └── unit/                   # 34 automated unit, headless GUI, and security tests
└── data/                       # Local session storage, audit logs, and settings
```

---

## 3. Quick Start & Launch Instructions

### 3.1 Prerequisites
- **Operating System:** Windows 10 or Windows 11 (64-bit).
- **Python Version:** Python 3.10 to 3.12 (Python 3.12.10 recommended).
- **Virtual Environment:** Active virtual environment in `.\venv`.

### 3.2 Launch the Application
In Windows PowerShell:
```powershell
Set-Location -Path "D:\MANOJINI_LokiXAI"
.\venv\Scripts\python main.py
```

### 3.3 Run Automated Tests
```powershell
Set-Location -Path "D:\MANOJINI_LokiXAI"
.\venv\Scripts\pytest -v tests
```
*Current test suite: 34 passed (100% PASS).*

---

## 4. Configuring Real AI Providers

### OpenAI Cloud (Primary Provider)
1. In the application, navigate to **Model Hub** or **Settings**.
2. Enter your OpenAI API key in the password field (`sk-...`).
3. Alternatively, copy `.env.example` to `.env` in the root folder and set:
   ```env
   OPENAI_API_KEY=sk-your-actual-api-key-here
   OPENAI_MODEL=gpt-4o
   ```
4. Click **Test OpenAI Connection** in Model Hub to verify credentials against live servers.

### Local AI (Ollama)
1. Ensure Ollama is installed and running (`http://localhost:11434`).
2. Pull a model: `ollama run llama3.2`.
3. In Model Hub, select **local** as your active provider and click **Test Local Connection**.

---

## 5. Light & Dark Theme Configuration

To switch themes:
1. Open **Settings** in the left sidebar.
2. Under **APPEARANCE & THEME**, select **dark**, **light**, or **system**.
3. The UI updates instantly without restart. Click **Save Preferences** to persist your choice.

---

## 6. Manual Verification Guide

For a complete step-by-step verification checklist covering real OpenAI conversations, multi-turn follow-ups, hardware actions, telemetry comparisons, and RAG document Q&A, refer to:
[docs/VERIFICATION_REPORT.md](file:///D:/MANOJINI_LokiXAI/docs/VERIFICATION_REPORT.md)
