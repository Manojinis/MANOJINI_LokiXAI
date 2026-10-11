# LokiXAI — Advanced AI Laptop Automation Assistant

> **"Your Laptop. Your Intelligence. Your Control."**  
> An intelligent, secure desktop AI copilot engineered for **Windows 11**.

---

## 1. Project Overview

**LokiXAI** is an advanced desktop AI assistant built in Python and PySide6 (Qt) designed to control laptop settings, stream telemetry, automate daily workflows, analyze documents via RAG, assist developers, and inspect visual screen captures—backed by a centralized cybersecurity architecture.

### Key Capabilities
- **AI Chat & Agent Orchestrator:** Multi-step function calling through safe tool registries, streaming responses, context memory, and graceful fallbacks.
- **Hardware Telemetry & System Controls:** Real-time CPU, RAM, disk, battery, network throughput, and uptime tracking; direct display brightness and master audio volume controls.
- **Multi-App Workspaces:** One-click launch presets for **Coding** (VSCode + Terminal + GitHub), **Study**, **Research**, and **Daily Work**.
- **Smart Routines Studio:** Visual routine builder with sequential execution, structured JSON definitions, and automatic stop-on-failure safety.
- **RAG Document Assistant:** PDF/Markdown text extraction, semantic chunking, vector indexing, and passage retrieval with page-level citations.
- **Safe File Manager:** Bounded directory browsing, search, file preview, and deletion/move operations protected by confirmation dialogs and path traversal guards.
- **Developer Copilot:** Static AST code analysis, symbol inspection (classes/functions), secret redaction, architecture reviews, and test generation.
- **Screen-Aware Assistant:** User-initiated screenshot capture, preview thumbnail, cancel/discard protection, and structured vision analysis.
- **Multi-Model Hub:** Dynamic switching between **OpenAI** (`gpt-4o`, `gpt-4o-mini`, `o1-mini`), local OpenAI-compatible endpoints (**Ollama**, **vLLM**), and offline deterministic core.
- **Security & Audit Trail:** Allowlisted executables only, parameter schema validation, secret masking (API keys, tokens), and real-time immutable JSONL audit logging.

---

## 2. Architecture & Directory Structure

```
LokiXAI/
├── main.py                     # Application entry point with high-DPI scaling & rotating logs
├── requirements.txt            # Pinned, tested dependency configuration
├── .env.example                # Configuration template
├── .gitignore                  # Git ignore rules
├── README.md                   # Complete documentation & operational manual
├── src/
│   └── lokixai/
│       ├── config/             # Pydantic AppSettings, dark futuristic styling (QSS)
│       ├── security/           # PathGuard, PermissionManager, SecretRedactor, AuditLogger
│       ├── monitoring/         # Real-time hardware telemetry background worker (psutil)
│       ├── tools/              # Allowlisted system, app, and safe file tools + registry
│       ├── providers/          # OpenAI, Ollama Local, and Mock offline model adapters
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
│   └── unit/                   # 22 automated unit and headless GUI tests
└── data/                       # Local session storage, audit logs, and vector indexes
```

---

## 3. Installation & Setup

### Prerequisites
- **Operating System:** Windows 11 (or Windows 10)
- **Python Version:** Python 3.11 or Python 3.12 64-bit

### Setup Commands (PowerShell)

1. **Clone or Navigate to the Workspace:**
   ```powershell
   cd D:\MANOJINI_LokiXAI
   ```

2. **Create and Activate Python Virtual Environment:**
   ```powershell
   py -3.12 -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install Dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Copy `.env.example` to `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```
   Open `.env` in your editor and configure your OpenAI API key or local Ollama URL (optional if testing with the built-in offline mock core):
   ```env
   LOKIXAI_AI_PROVIDER=openai
   OPENAI_API_KEY=sk-your-openai-api-key
   OPENAI_MODEL=gpt-4o
   ```

---

## 4. Running the Application

Launch the desktop copilot GUI directly from PowerShell:

```powershell
.\venv\Scripts\python main.py
```

### Launch in Zero-Key / Offline Mode
If you don't have an OpenAI API key configured, LokiXAI automatically operates in deterministic offline mode or connects to a local Ollama instance (`http://localhost:11434/v1`). You can toggle this anytime under **Model Hub**.

---

## 5. Running the Automated Test Suite

Run pytest to verify all security assertions, tool allowlists, path traversal protections, RAG vector searches, and headless UI instantiations:

```powershell
.\venv\Scripts\pytest -v tests
```

Output:
```
tests/unit/test_providers.py ......................... PASSED
tests/unit/test_rag.py ............................... PASSED
tests/unit/test_routines.py .......................... PASSED
tests/unit/test_security.py .......................... PASSED
tests/unit/test_tools.py ............................. PASSED
tests/unit/test_ui_headless.py ....................... PASSED
============================= 22 passed ==============================
```

---

## 6. Security Architecture Guarantees

1. **Allowlisted Tools Only:** No unrestricted shell access, PowerShell eval, or arbitrary execution. Applications are launched via verified executables (`calc.exe`, `notepad.exe`, `code`, `wt.exe`, etc.).
2. **Path Traversal Shield (`PathGuard`):** Resolves canonical paths. Files outside approved directories (or inside sensitive Windows system directories) raise `SecurityAccessDeniedError`.
3. **Sensitive Action Modals:** Actions classified as `DESTRUCTIVE_ACTION` (e.g. file deletion, file move) trigger an explicit modal dialog showing the exact parameters before proceeding.
4. **Credential Redaction (`SecretRedactor`):** Automatically masks OpenAI API keys (`sk-...`), Bearer tokens, GitHub keys, and password patterns in audit trails, exceptions, and console logs.
5. **Screen Privacy:** Screenshots are strictly captured on explicit user initiation. Captured images can be previewed or discarded/deleted at any time.

---

## 7. Windows Executable Packaging (PyInstaller)

To package LokiXAI as a standalone Windows executable:

1. Install PyInstaller:
   ```powershell
   .\venv\Scripts\pip install pyinstaller
   ```
2. Build executable:
   ```powershell
   .\venv\Scripts\pyinstaller --noconsole --name "LokiXAI" --add-data "src;src" main.py
   ```
3. The executable will be produced in `dist/LokiXAI/LokiXAI.exe`.
