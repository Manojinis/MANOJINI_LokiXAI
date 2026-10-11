"""AI Conversation workspace with tool execution cards, rich markdown, and multi-line composer."""

from __future__ import annotations

import html
import json
import re
from typing import Any, Dict, Optional
from PySide6.QtCore import QObject, QThread, Qt, Signal, QTimer
from PySide6.QtGui import QGuiApplication, QKeyEvent
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
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


class ChatInputTextEdit(QPlainTextEdit):
    """Multi-line composer that submits on Enter and inserts newline on Shift+Enter."""

    submit_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Ask LokiXAI anything or command laptop settings... (Enter to send, Shift+Enter for newline)")
        self.setFixedHeight(44)
        self.setStyleSheet("""
            background-color: #0c1322;
            border: 1px solid #1e293b;
            border-radius: 8px;
            color: #f8fafc;
            padding: 8px 10px;
            font-size: 13px;
        """)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if event.modifiers() & Qt.ShiftModifier:
                super().keyPressEvent(event)
            else:
                self.submit_requested.emit()
                event.accept()
                return
        else:
            super().keyPressEvent(event)


class AgentWorker(QObject):
    """Executes AI turns in a background thread to prevent UI freezing."""

    token_received = Signal(str)
    tool_started = Signal(str, dict)
    tool_finished = Signal(str, object)
    finished = Signal(str)
    error_occurred = Signal(str)

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
        self._current_assistant_raw_text = ""
        self._is_generating = False
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

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

        # Empty state suggestion pill container
        self.suggestions_frame = self._create_suggestions_widget()
        self.msg_layout.addWidget(self.suggestions_frame)

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

        # Multi-line Text input
        self.input_edit = ChatInputTextEdit()
        self.input_edit.submit_requested.connect(self._send_message)
        c_layout.addWidget(self.input_edit, 1)

        # Mic button
        self.mic_btn = QPushButton("🎙️")
        self.mic_btn.setFixedSize(36, 36)
        self.mic_btn.setToolTip("Push-to-talk Voice Input")
        self.mic_btn.clicked.connect(self._on_mic_clicked)
        c_layout.addWidget(self.mic_btn)

        # Send / Stop button
        self.send_btn = QPushButton("Send")
        self.send_btn.setObjectName("PrimaryButton")
        self.send_btn.setFixedHeight(36)
        self.send_btn.setMinimumWidth(75)
        self.send_btn.clicked.connect(self._on_send_or_stop_clicked)
        c_layout.addWidget(self.send_btn)

        layout.addWidget(composer_frame)

    def _create_suggestions_widget(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet("background: transparent;")
        l = QVBoxLayout(frame)
        l.setContentsMargins(0, 8, 0, 8)
        l.setSpacing(8)

        intro = QLabel("⚡ Welcome to LokiXAI. Try one of these prompts or type your own:")
        intro.setStyleSheet("font-size: 13px; color: #94a3b8; font-weight: 500;")
        l.addWidget(intro)

        pills = [
            ("🧠 What is Artificial Intelligence?", "What is artificial intelligence? Explain it in simple words with an example."),
            ("💻 Explain JavaScript Promises", "Explain JavaScript promises with examples."),
            ("📊 Check Current Laptop RAM", "Check my current laptop RAM usage and tell me how much is being used."),
            ("⚡ Launch Coding Workspace", "Launch Coding workspace"),
            ("🔁 Explain Java vs. Python", "Explain the difference between Java and Python."),
        ]

        pills_layout = QHBoxLayout()
        pills_layout.setSpacing(8)
        for label, prompt in pills[:3]:
            btn = QPushButton(label)
            btn.setStyleSheet("""
                background-color: #141e33;
                border: 1px solid #1e293b;
                border-radius: 8px;
                color: #00f2fe;
                padding: 6px 12px;
                font-size: 12px;
            """)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, p=prompt: self.send_prompt(p))
            pills_layout.addWidget(btn)
        pills_layout.addStretch()
        l.addLayout(pills_layout)

        pills_layout2 = QHBoxLayout()
        pills_layout2.setSpacing(8)
        for label, prompt in pills[3:]:
            btn = QPushButton(label)
            btn.setStyleSheet("""
                background-color: #141e33;
                border: 1px solid #1e293b;
                border-radius: 8px;
                color: #38bdf8;
                padding: 6px 12px;
                font-size: 12px;
            """)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, p=prompt: self.send_prompt(p))
            pills_layout2.addWidget(btn)
        pills_layout2.addStretch()
        l.addLayout(pills_layout2)

        return frame

    def _on_new_chat(self):
        self.session = ConversationSession()
        self.session_title_lbl.setText("Active Session: New Conversation")
        self._clear_bubbles()
        self.suggestions_frame.show()

    def _on_clear_chat(self):
        self._clear_bubbles()
        self.suggestions_frame.show()

    def _clear_bubbles(self):
        # Keep suggestions_frame and the stretch at the end
        while self.msg_layout.count() > 2:
            item = self.msg_layout.takeAt(1)
            if item.widget() and item.widget() != self.suggestions_frame:
                item.widget().deleteLater()

    def send_prompt(self, prompt: str):
        """Programmatically inject prompt and send immediately."""
        self.input_edit.setPlainText(prompt)
        self._send_message()

    def _on_send_or_stop_clicked(self):
        if self._is_generating:
            # Stop action
            self.orchestrator.cancel()
            self.send_btn.setText("Stopping...")
            self.send_btn.setEnabled(False)
        else:
            self._send_message()

    def _send_message(self):
        text = self.input_edit.toPlainText().strip()
        if not text:
            return

        self.input_edit.clear()
        self.suggestions_frame.hide()
        self._add_user_message(text)

        # Prepare assistant bubble
        self._current_assistant_raw_text = ""
        self._current_assistant_bubble = self._create_assistant_bubble_widget()
        self.msg_layout.insertWidget(self.msg_layout.count() - 1, self._current_assistant_bubble)
        self._scroll_to_bottom()

        self._is_generating = True
        self.send_btn.setText("■ Stop")
        self.send_btn.setObjectName("DangerButton")
        self.send_btn.style().unpolish(self.send_btn)
        self.send_btn.style().polish(self.send_btn)

        # Background thread
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
        dlg = ConfirmationDialog(tool_name, args, level, self)
        return dlg.exec() == QDialog.Accepted

    def _format_markdown(self, raw_text: str) -> str:
        """Convert basic markdown (headers, code blocks, lists, bold) to styled HTML."""
        escaped = html.escape(raw_text)

        # Code blocks
        def _code_block(match):
            code = match.group(1).strip()
            return f'<div style="background-color: #0c1322; border: 1px solid #1e293b; border-radius: 6px; padding: 10px; margin: 8px 0; font-family: Consolas, monospace; color: #38bdf8; white-space: pre-wrap;">{code}</div>'

        escaped = re.sub(r'```(?:[a-zA-Z0-9_\-]+)?\n(.*?)```', _code_block, escaped, flags=re.DOTALL)

        # Inline code
        escaped = re.sub(r'`([^`]+)`', r'<code style="background-color: #0c1322; padding: 2px 5px; border-radius: 4px; color: #00f2fe; font-family: monospace;">\1</code>', escaped)

        # Bold
        escaped = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', escaped)

        # Bullet points
        escaped = re.sub(r'^[•\*\-]\s+(.+)$', r'• \1', escaped, flags=re.MULTILINE)

        # Convert newlines to breaks except inside code
        lines = escaped.split('\n')
        formatted = '<br>'.join(lines)
        return formatted

    def _on_token(self, token: str):
        self._current_assistant_raw_text += token
        if self._current_assistant_bubble:
            lbl = self._current_assistant_bubble.findChild(QLabel, "BubbleText")
            if lbl:
                lbl.setText(self._format_markdown(self._current_assistant_raw_text))
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
        h = QLabel(f"⚙️ Calling Verified Tool: {name}")
        h.setStyleSheet("color: #f59e0b; font-weight: 700; font-size: 11px;")
        p = QLabel(f"Parameters: {json.dumps(args)}")
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
        self._is_generating = False
        self.send_btn.setEnabled(True)
        self.send_btn.setText("Send")
        self.send_btn.setObjectName("PrimaryButton")
        self.send_btn.style().unpolish(self.send_btn)
        self.send_btn.style().polish(self.send_btn)

        if self.thread:
            self.thread.quit()

        # Update bubble text fully formatted
        if self._current_assistant_bubble:
            lbl = self._current_assistant_bubble.findChild(QLabel, "BubbleText")
            if lbl:
                lbl.setText(self._format_markdown(final_text or self._current_assistant_raw_text))

        self.store.save_session(self.session)
        self.session_title_lbl.setText(f"Active Session: {self.session.title}")
        get_tts_engine().speak(final_text[:250])

    def _on_turn_error(self, err: str):
        self._is_generating = False
        self.send_btn.setEnabled(True)
        self.send_btn.setText("Send")
        self.send_btn.setObjectName("PrimaryButton")
        self.send_btn.style().unpolish(self.send_btn)
        self.send_btn.style().polish(self.send_btn)

        if self.thread:
            self.thread.quit()
        if self._current_assistant_bubble:
            lbl = self._current_assistant_bubble.findChild(QLabel, "BubbleText")
            if lbl:
                lbl.setText(lbl.text() + f"<br><br><span style='color: #ef4444;'>[Error: {html.escape(err)}]</span>")

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
        t.setTextInteractionFlags(Qt.TextSelectableByMouse)
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
        l.setSpacing(6)

        # Bubble header with copy button
        top = QHBoxLayout()
        h = QLabel("⚡ LokiXAI")
        h.setStyleSheet("font-size: 11px; font-weight: 700; color: #00f2fe;")
        top.addWidget(h)
        top.addStretch()

        copy_btn = QPushButton("📋 Copy")
        copy_btn.setFixedSize(56, 22)
        copy_btn.setStyleSheet("""
            background-color: #0c1322;
            border: 1px solid #1e293b;
            border-radius: 4px;
            color: #94a3b8;
            font-size: 10px;
        """)
        copy_btn.setCursor(Qt.PointingHandCursor)
        copy_btn.clicked.connect(lambda: self._copy_bubble_text(bubble))
        top.addWidget(copy_btn)
        l.addLayout(top)

        t = QLabel("")
        t.setObjectName("BubbleText")
        t.setStyleSheet("font-size: 13px; color: #f8fafc; line-height: 1.45;")
        t.setWordWrap(True)
        t.setTextInteractionFlags(Qt.TextSelectableByMouse)
        t.setTextFormat(Qt.RichText)
        l.addWidget(t)
        return bubble

    def _copy_bubble_text(self, bubble: QFrame):
        lbl = bubble.findChild(QLabel, "BubbleText")
        if lbl:
            # Clean copy
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(self._current_assistant_raw_text or lbl.text())

    def _scroll_to_bottom(self):
        v_bar = self.scroll.verticalScrollBar()
        # Only auto scroll if near bottom or just sent
        if (v_bar.maximum() - v_bar.value()) < 150 or not self._is_generating:
            QTimer.singleShot(40, lambda: v_bar.setValue(v_bar.maximum()))

    def _on_attach_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Attach Document", "", "Documents (*.pdf *.txt *.md *.py *.json)"
        )
        if file_path:
            self.input_edit.setPlainText(f"Analyze attached document: {file_path}")

    def _on_mic_clicked(self):
        from src.lokixai.voice.stt_engine import get_stt_engine
        stt = get_stt_engine()
        stt.start_recording()
        text = stt.stop_recording_and_transcribe()
        if text:
            self.input_edit.setPlainText(text)
