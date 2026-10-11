"""AI Conversation workspace with tool execution cards and streaming responses."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional
from PySide6.QtCore import QObject, QThread, Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from src.lokixai.ai.agent import AgentOrchestrator
from src.lokixai.ai.conversation import ConversationSession, ChatMessage
from src.lokixai.security.permissions import PermissionLevel
from src.lokixai.storage.local_store import get_local_store
from src.lokixai.tools.base import ToolResult
from src.lokixai.ui.components.dialogs import ConfirmationDialog
from src.lokixai.voice.tts_engine import get_tts_engine


class AgentWorker(QObject):
    """Executes AI turns in a background thread to prevent UI freezing."""

    token_received = Signal(str)
    tool_started = Signal(str, dict)
    tool_finished = Signal(str, object)
    finished = Signal(str)
    error_occurred = Signal(str)
    confirmation_requested = Signal(str, dict, object)

    def __init__(
        self,
        orchestrator: AgentOrchestrator,
        session: ConversationSession,
        user_input: str,
        confirm_handler,
    ):
        super().__init__()
        self.orchestrator = orchestrator
        self.session = session
        self.user_input = user_input
        self.confirm_handler = confirm_handler

    def run(self):
        try:
            res = self.orchestrator.process_turn(
                session=self.session,
                user_input=self.user_input,
                confirm_callback=self.confirm_handler,
                on_token=lambda tok: self.token_received.emit(tok),
                on_tool_start=lambda name, args: self.tool_started.emit(name, args),
                on_tool_end=lambda name, tr: self.tool_finished.emit(name, tr),
            )
            self.finished.emit(res)
        except Exception as e:
            self.error_occurred.emit(str(e))


class ChatPage(QWidget):
    """Full-featured conversational agent workspace."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.store = get_local_store()
        self.session = ConversationSession()
        self.orchestrator = AgentOrchestrator()
        self.active_worker_thread: Optional[QThread] = None
        self._current_assistant_bubble = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Chat top toolbar
        top_bar = QHBoxLayout()
        self.session_title_lbl = QLabel("Active Session: New Conversation")
        self.session_title_lbl.setStyleSheet("font-size: 14px; font-weight: 700; color: #f8fafc;")
        top_bar.addWidget(self.session_title_lbl)

        top_bar.addStretch()

        new_btn = QPushButton("+ New Chat")
        new_btn.clicked.connect(self._on_new_chat)
        top_bar.addWidget(new_btn)

        clear_btn = QPushButton("Clear History")
        clear_btn.clicked.connect(self._on_clear_chat)
        top_bar.addWidget(clear_btn)

        layout.addLayout(top_bar)

        # Message Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("background-color: #0b1120; border-radius: 10px; border: 1px solid #1e293b;")

        self.messages_container = QWidget()
        self.messages_container.setStyleSheet("background: transparent;")
        self.msg_layout = QVBoxLayout(self.messages_container)
        self.msg_layout.setContentsMargins(16, 16, 16, 16)
        self.msg_layout.setSpacing(12)
        self.msg_layout.addStretch()

        self.scroll.setWidget(self.messages_container)
        layout.addWidget(self.scroll, 1)

        # Command Composer Bar
        composer_frame = QFrame()
        composer_frame.setObjectName("CardFrame")
        composer_frame.setStyleSheet("""
            background-color: #0f172a;
            border: 1px solid #1e293b;
            border-radius: 12px;
            padding: 6px;
        """)
        c_layout = QHBoxLayout(composer_frame)
        c_layout.setContentsMargins(8, 4, 8, 4)
        c_layout.setSpacing(8)

        # File attach button
        attach_btn = QPushButton("📎")
        attach_btn.setFixedSize(36, 36)
        attach_btn.setToolTip("Attach Document for RAG or Inspection")
        attach_btn.clicked.connect(self._on_attach_file)
        c_layout.addWidget(attach_btn)

        # Text input
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("Ask LokiXAI anything or command laptop settings...")
        self.input_edit.setFixedHeight(38)
        self.input_edit.returnPressed.connect(self._send_message)
        c_layout.addWidget(self.input_edit, 1)

        # Mic button
        self.mic_btn = QPushButton("🎙️")
        self.mic_btn.setFixedSize(36, 36)
        self.mic_btn.setToolTip("Push-to-talk Voice Input")
        self.mic_btn.clicked.connect(self._on_mic_clicked)
        c_layout.addWidget(self.mic_btn)

        # Send button
        self.send_btn = QPushButton("Send")
        self.send_btn.setObjectName("PrimaryButton")
        self.send_btn.setFixedHeight(38)
        self.send_btn.clicked.connect(self._send_message)
        c_layout.addWidget(self.send_btn)

        layout.addWidget(composer_frame)

        # Welcome initial bubble
        self._add_assistant_message(
            "Greetings! I am LokiXAI, your laptop automation copilot. "
            "I can adjust brightness & volume, launch workspaces, monitor system telemetry, inspect files, and automate routines. How may I assist you?"
        )

    def _on_new_chat(self):
        self.session = ConversationSession()
        self.session_title_lbl.setText("Active Session: New Conversation")
        self._clear_bubbles()
        self._add_assistant_message("Started a new session. How can I help you today?")

    def _on_clear_chat(self):
        self._clear_bubbles()

    def _clear_bubbles(self):
        while self.msg_layout.count() > 1:
            item = self.msg_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def send_prompt(self, prompt: str):
        """Programmatically inject prompt from quick actions or voice."""
        self.input_edit.setText(prompt)
        self._send_message()

    def _send_message(self):
        text = self.input_edit.text().strip()
        if not text:
            return

        self.input_edit.clear()
        self._add_user_message(text)

        # Prepare for assistant reply
        self._current_assistant_bubble = self._create_assistant_bubble_widget()
        self.msg_layout.insertWidget(self.msg_layout.count() - 1, self._current_assistant_bubble)
        self._scroll_to_bottom()

        self.send_btn.setEnabled(False)
        self.send_btn.setText("Processing...")

        # Run in background QThread
        self.thread = QThread()
        self.worker = AgentWorker(
            orchestrator=self.orchestrator,
            session=self.session,
            user_input=text,
            confirm_handler=self._handle_confirmation,
        )
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.token_received.connect(self._on_token)
        self.worker.tool_started.connect(self._on_tool_started)
        self.worker.tool_finished.connect(self._on_tool_finished)
        self.worker.finished.connect(self._on_turn_finished)
        self.worker.error_occurred.connect(self._on_turn_error)

        self.active_worker_thread = self.thread
        self.thread.start()

    def _handle_confirmation(self, tool_name: str, args: Dict[str, Any], level: PermissionLevel) -> bool:
        # Display modal confirmation dialog
        dlg = ConfirmationDialog(tool_name, args, level, self)
        return dlg.exec() == QDialog.Accepted

    def _on_token(self, token: str):
        if self._current_assistant_bubble:
            lbl = self._current_assistant_bubble.findChild(QLabel, "BubbleText")
            if lbl:
                lbl.setText(lbl.text() + token)
                self._scroll_to_bottom()

    def _on_tool_started(self, name: str, args: dict):
        card = QFrame()
        card.setStyleSheet("""
            background-color: #141e33;
            border-left: 3px solid #f59e0b;
            border-radius: 6px;
            padding: 8px;
        """)
        l = QVBoxLayout(card)
        l.setSpacing(2)
        h = QLabel(f"⚙️ Calling Tool: {name}")
        h.setStyleSheet("color: #f59e0b; font-weight: 700; font-size: 11px;")
        p = QLabel(f"Arguments: {json.dumps(args)}")
        p.setStyleSheet("color: #94a3b8; font-size: 10px; font-family: monospace;")
        l.addWidget(h)
        l.addWidget(p)
        self.msg_layout.insertWidget(self.msg_layout.count() - 1, card)
        self._scroll_to_bottom()

    def _on_tool_finished(self, name: str, result: ToolResult):
        card = QFrame()
        border_col = "#10b981" if result.success else "#ef4444"
        card.setStyleSheet(f"""
            background-color: #141e33;
            border-left: 3px solid {border_col};
            border-radius: 6px;
            padding: 8px;
        """)
        l = QVBoxLayout(card)
        l.setSpacing(2)
        status_txt = "SUCCESS" if result.success else "FAILED"
        h = QLabel(f"⚡ {name} [{status_txt}]")
        h.setStyleSheet(f"color: {border_col}; font-weight: 700; font-size: 11px;")
        m = QLabel(result.message)
        m.setStyleSheet("color: #f8fafc; font-size: 11px;")
        m.setWordWrap(True)
        l.addWidget(h)
        l.addWidget(m)
        self.msg_layout.insertWidget(self.msg_layout.count() - 1, card)
        self._scroll_to_bottom()

    def _on_turn_finished(self, final_text: str):
        self.send_btn.setEnabled(True)
        self.send_btn.setText("Send")
        if self.thread:
            self.thread.quit()
        self.store.save_session(self.session)
        self.session_title_lbl.setText(f"Active Session: {self.session.title}")
        get_tts_engine().speak(final_text[:200])

    def _on_turn_error(self, err: str):
        self.send_btn.setEnabled(True)
        self.send_btn.setText("Send")
        if self.thread:
            self.thread.quit()
        if self._current_assistant_bubble:
            lbl = self._current_assistant_bubble.findChild(QLabel, "BubbleText")
            if lbl:
                lbl.setText(lbl.text() + f"\n\n[Error: {err}]")

    def _add_user_message(self, text: str):
        bubble = QFrame()
        bubble.setStyleSheet("""
            background-color: #1e293b;
            border-radius: 12px;
            padding: 12px;
            margin-left: 80px;
        """)
        l = QVBoxLayout(bubble)
        h = QLabel("You")
        h.setStyleSheet("font-size: 11px; font-weight: 700; color: #00f2fe;")
        t = QLabel(text)
        t.setStyleSheet("font-size: 13px; color: #f8fafc;")
        t.setWordWrap(True)
        l.addWidget(h)
        l.addWidget(t)
        self.msg_layout.insertWidget(self.msg_layout.count() - 1, bubble)
        self._scroll_to_bottom()

    def _create_assistant_bubble_widget(self) -> QFrame:
        bubble = QFrame()
        bubble.setStyleSheet("""
            background-color: #131d31;
            border: 1px solid #1e293b;
            border-radius: 12px;
            padding: 12px;
            margin-right: 80px;
        """)
        l = QVBoxLayout(bubble)
        h = QLabel("⚡ LokiXAI")
        h.setStyleSheet("font-size: 11px; font-weight: 700; color: #00f2fe;")
        t = QLabel("")
        t.setObjectName("BubbleText")
        t.setStyleSheet("font-size: 13px; color: #f8fafc; line-height: 1.4;")
        t.setWordWrap(True)
        t.setTextInteractionFlags(Qt.TextSelectableByMouse)
        l.addWidget(h)
        l.addWidget(t)
        return bubble

    def _add_assistant_message(self, text: str):
        bubble = self._create_assistant_bubble_widget()
        lbl = bubble.findChild(QLabel, "BubbleText")
        if lbl:
            lbl.setText(text)
        self.msg_layout.insertWidget(self.msg_layout.count() - 1, bubble)
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        from PySide6.QtCore import QTimer
        QTimer.singleShot(50, lambda: self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()
        ))

    def _on_attach_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Attach Document", "", "Documents (*.pdf *.txt *.md *.py *.json)"
        )
        if file_path:
            self.input_edit.setText(f"Analyze attached document: {file_path}")

    def _on_mic_clicked(self):
        # Trigger voice transcription test
        from src.lokixai.voice.stt_engine import get_stt_engine
        stt = get_stt_engine()
        stt.start_recording()
        text = stt.stop_recording_and_transcribe()
        if text:
            self.input_edit.setText(text)
