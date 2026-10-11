# LokiXAI — Verification Report & Manual Testing Guide

**Date of Verification:** 2026-10-11  
**Target Workspace:** `D:\MANOJINI_LokiXAI`  
**Environment:** Windows 11 (64-bit), Python 3.12.10 (`.\venv`)  
**Automated Test Suite Status:** 34 PASSED / 0 FAILED (100% PASS)  
**Manual Verification Status:** Prepared for User Manual Execution

---

## 1. Root Cause Diagnosis: The AI Chat Error

### Symptom
The UI displayed:
```
APIStatusError.__init__() missing 2 required keyword-only arguments: 'response' and 'body'
```

### Root Cause Analysis
In `src/lokixai/providers/openai_provider.py`, when credentials were unset, the code previously contained:
```python
raise AuthenticationError("OpenAI API key not configured. Please add your key in Settings or Model Hub.")
```
In the official OpenAI Python SDK (`openai>=1.0.0`), `openai.AuthenticationError` inherits from `openai.APIStatusError`. Its constructor signature is:
```python
def __init__(self, message: str, *, response: httpx.Response, body: object | None) -> None:
```
Because `response` and `body` are mandatory keyword-only arguments required by the SDK for HTTP errors, calling `AuthenticationError("message")` directly caused Python to raise a `TypeError` in the error constructor. The chat worker caught this `TypeError` and displayed it to the user instead of explaining that the API key was missing.

### Root Cause Fix
1. Refactored `OpenAIProvider._get_client()` to raise a clean standard `ValueError` if the API key is not configured locally or is set to a placeholder:
   ```python
   if not api_key or not api_key.strip() or "your_openai_api_key_here" in str(api_key).lower():
       raise ValueError("OpenAI API key is not configured. Please enter your API key in Settings or Model Hub, or set OPENAI_API_KEY in your .env file.")
   ```
2. Implemented `_format_openai_error()` to translate authentic SDK exceptions without ever manually instantiating internal SDK error classes.
3. Added unit tests (`test_openai_provider_missing_key_error`, `test_openai_provider_generate_missing_key_error`) in `tests/unit/test_providers.py` to prevent any regressions.

---

## 2. Automated Test Suite Results

> [!NOTE]
> These automated tests validate internal code logic, tool schemas, security path traversal rules, secret redaction, and headless UI instantiation. They do not simulate live external cloud models.

**Command:**
```powershell
.\venv\Scripts\pytest -v tests
```

**Results:** **34 passed in 4.29s (100% PASS)**

| Test Module | Tests | Focus Area | Status |
| :--- | :---: | :--- | :---: |
| `tests/unit/test_conversational_ai.py` | 9 | Multi-turn reasoning logic, follow-ups, topic changes, natural reactions, action vs. explanation intent routing, cancellation | **PASS (9/9)** |
| `tests/unit/test_providers.py` | 7 | Provider capabilities, volume tool generation, conversational replies, agent orchestrator, OpenAI missing key error handling, ThemeManager stylesheets | **PASS (7/7)** |
| `tests/unit/test_security.py` | 7 | OpenAI key regex redaction, nested dict redaction, PathGuard canonical checks, directory traversal blocks, Windows system folder protection, PermissionManager, AuditLogger | **PASS (7/7)** |
| `tests/unit/test_tools.py` | 6 | Central tool registry, open_app allowlist, open_website scheme validation, workspace presets, argument schema validation, real telemetry | **PASS (6/6)** |
| `tests/unit/test_rag.py` | 2 | Text chunking, metadata preservation, vector store indexing and query | **PASS (2/2)** |
| `tests/unit/test_routines.py` | 2 | JSON routine loading, sequential execution, error halting | **PASS (2/2)** |
| `tests/unit/test_ui_headless.py` | 1 | Headless Qt instantiation across all 13 sidebar navigation pages | **PASS (1/1)** |
| **TOTAL** | **34** | **Full System Logic Coverage** | **PASS (34/34, 100%)** |

---

## 3. Light / Dark / System Theme Verification

- **Theme Switching:** Selecting "light", "dark", or "system" in **Settings** immediately triggers `apply_theme` across the main window, header, sidebar, chat cards, and navigation stack without requiring an application restart.
- **Light Theme Appearance:**
  - Background: Soft modern off-white (`#f8fafc`).
  - Cards & Panels: Crisp white (`#ffffff`) with subtle borders (`#e2e8f0`).
  - Typography: High-contrast dark text (`#0f172a`, `#475569`).
  - Accents: Oceanic cyan/teal (`#0284c7`).
  - Message Bubbles: Soft ice-blue user cards (`#e0f2fe`) and clean white assistant cards.
  - Markdown Code Blocks: Light slate backgrounds (`#f1f5f9`) with blue syntax styling (`#0369a1`).
- **Persistence:** Selected theme persists in `data/settings.json` across application restarts.

---

## 4. User Manual Verification Checklist

Follow this checklist to verify LokiXAI directly on your Windows machine:

### 4.1 Launching the Application
```powershell
Set-Location -Path "D:\MANOJINI_LokiXAI"
.\venv\Scripts\python main.py
```
- **Expected Result:** The application launches cleanly with high-DPI scaling. Header, left sidebar, middle workspace, and right telemetry panel appear without visual clipping.

### 4.2 Light / Dark / System Theme Verification
1. Navigate to **Settings** in the left sidebar.
2. Under **APPEARANCE & THEME**, open the **Interface Theme** dropdown.
3. Select **light**: The entire application (sidebar, header, cards, inputs, tables) switches instantly to a clean white and soft-gray theme.
4. Select **dark**: The application switches to the dark aesthetic.
5. Select **system**: The application adapts to your Windows 11 appearance setting.
6. Click **Save Preferences**, close the application, and re-launch: Confirm the selected theme persists.

### 4.3 OpenAI Configuration & Live Connection Test
1. Navigate to **Model Hub**.
2. Confirm the **Primary Active Provider** dropdown lists only `openai` and `local` (Zero-Mock Policy).
3. Under **OpenAI Cloud Configuration**, enter your OpenAI API key in the password field (`sk-...`).
4. Select your desired model (e.g., `gpt-4o` or `gpt-4o-mini`).
5. Click **Test OpenAI Connection**.
   - **Expected Result if Key is Valid:** A green status badge appears (`✓ Connected: Model 'gpt-4o' active`) and an informational popup confirms successful connection.
   - **Expected Result if Key is Invalid:** A red error status appears displaying the exact error (e.g., Authentication Error 401).
6. Click **Apply Active Provider** to persist.

### 4.4 AI Chat Conversational Verification
Navigate to **AI Chat** and submit each prompt sequentially in the same conversation:

1. **General Knowledge:**
   `What is artificial intelligence? Explain it in simple words with an example.`
   - *Expected:* Detailed answer with clear formatting. No tools executed.
2. **Context Retention & Follow-Up:**
   `Give me three real-world applications of it.`
   - *Expected:* The model uses prior context to list three applications.
3. **Follow-Up on Specific Item:**
   `Explain the second application in more detail.`
   - *Expected:* Identifies and elaborates specifically on the second application from prompt 2.
4. **Topic Connection:**
   `How could I build a small Python project related to that?`
   - *Expected:* Provides runnable Python code with markdown syntax highlighting.
5. **Topic Change:**
   `Now explain the difference between Java and Python.`
   - *Expected:* Recognizes the shift in topic and generates a comparison table or bulleted summary.
6. **Action vs. Explanation (Instruction):**
   `How can I check my laptop's RAM usage?`
   - *Expected:* Explains how to check RAM using Windows Task Manager, Resource Monitor, or LokiXAI. Executes zero tools.
7. **Actual Hardware Action:**
   `Check my current laptop RAM usage and tell me how much is being used.`
   - *Expected:* Detects the imperative command, invokes the verified `get_system_metrics` tool, and outputs live measured RAM (total, used, percentage) directly from your laptop.

### 4.5 Hardware Telemetry & System Controls
1. On the **Overview** page or **System Monitor**, inspect CPU, RAM, and Disk metrics. Compare them with Windows Task Manager (`Ctrl + Shift + Esc`) to verify real readings.
2. Test volume adjustment using the slider or quick actions. Verify real audio level changes on your laptop.
3. If on a laptop with a built-in display, test the brightness slider.

### 4.6 Knowledge Base (RAG) Ingestion
1. Navigate to **Knowledge Base**.
2. Click **Browse Document** and select a real local `.pdf`, `.txt`, or `.md` file.
3. Click **Ingest Document**: Confirm the document is chunked, indexed, and appears in the Indexed Documents list.
4. In the Q&A box, ask a question answered only by that document. Verify that the answer cites the source filename and passage.
5. Click the `✕` chip button on the indexed document to remove it from the index.

### 4.7 File Manager Boundary Enforcement
1. Navigate to **File Manager**.
2. Verify that files are listed within your approved workspace (`D:\MANOJINI_LokiXAI`).
3. Attempt to navigate outside approved roots or type `C:\Windows`: Verify access is blocked with a security warning.

### 4.8 Screen Assistant Capture
1. Navigate to **Screen Assistant**.
2. Click **Capture Screen**: Confirm a snapshot of your screen is grabbed and displayed in the preview frame.
3. If OpenAI `gpt-4o` is configured, click **Analyze with Vision**: Confirm structured analysis of your screen contents.

### 4.9 Smart Routines & Audit Log
1. Navigate to **Smart Routines** and click **Run Routine** on a non-destructive preset: Confirm steps execute sequentially with a live progress indicator.
2. Navigate to **Activity & Audit Log**: Confirm executed actions appear in the table with timestamps, tool names, and outcomes. Confirm API keys and secrets are masked as `[REDACTED]`.
