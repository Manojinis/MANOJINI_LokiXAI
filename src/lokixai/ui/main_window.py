"""Main desktop application window assembling all components and pages."""

from __future__ import annotations

import sys
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.lokixai.config.settings import get_settings
from src.lokixai.config.theme import STYLESHEET
from src.lokixai.monitoring.system_monitor import SystemMetrics, get_system_monitor
from src.lokixai.tools.system_tools import SetMuteTool, GetVolumeTool
from src.lokixai.ui.components import Header, RightPanel, Sidebar
from src.lokixai.ui.pages import (
    AuditPage,
    AutomationPage,
    ChatPage,
    DeveloperPage,
    FilesPage,
    KnowledgePage,
    ModelHubPage,
    MonitorPage,
    OverviewPage,
    RoutinesPage,
    ScreenPage,
    SettingsPage,
    VoicePage,
)


PAGE_TITLES = {
    "overview": ("Overview", "System telemetry and copilot command center"),
    "chat": ("AI Chat Workspace", "Context-aware reasoning and safe tool execution"),
    "voice": ("Voice Assistant", "Push-to-talk voice input and speech synthesis"),
    "monitor": ("System Monitor", "Real-time hardware performance & telemetry"),
    "automation": ("Automation Studio", "Workspace environments and app launchers"),
    "routines": ("Smart Routines", "Sequential workflow automation with safe stops"),
    "knowledge": ("Knowledge Base", "RAG document ingestion and passage citations"),
    "files": ("Safe File Manager", "Restricted directory browsing and operations"),
    "developer": ("Developer Copilot", "AST code inspector and test generation"),
    "screen": ("Screen Assistant", "Vision-aware display interpretation"),
    "model_hub": ("Model Hub", "AI provider configuration and capability inspection"),
    "audit": ("Activity & Audit Log", "Immutable security action audit trail"),
    "settings": ("Settings", "Personalization, directory roots, and preferences"),
}


class MainWindow(QMainWindow):
    """Primary application window for LokiXAI desktop assistant."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("LokiXAI — Advanced AI Laptop Automation Assistant")
        self.resize(1300, 840)
        self.setMinimumSize(1080, 680)

        self.settings = get_settings()
        self.monitor = get_system_monitor()

        # Apply dark futuristic styling
        self.setStyleSheet(STYLESHEET)

        self._init_ui()
        self._start_telemetry_timer()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Left Sidebar
        self.sidebar = Sidebar(self)
        self.sidebar.page_selected.connect(self._on_navigate)
        root_layout.addWidget(self.sidebar)

        # 2. Main Middle Area (Header + Stacked Pages)
        middle_widget = QWidget()
        middle_layout = QVBoxLayout(middle_widget)
        middle_layout.setContentsMargins(0, 0, 0, 0)
        middle_layout.setSpacing(0)

        # Top Header
        self.header = Header(self)
        self.header.quick_action_triggered.connect(self._on_quick_action)
        self.header.set_model_label(self.settings.ai_provider.upper(), self.settings.openai_model)
        middle_layout.addWidget(self.header)

        # Stacked Pages
        self.stack = QStackedWidget()
        self.pages: dict[str, QWidget] = {}

        # Instantiate all 13 pages
        self.overview_page = OverviewPage(self)
        self.chat_page = ChatPage(self)
        self.voice_page = VoicePage(self)
        self.monitor_page = MonitorPage(self)
        self.automation_page = AutomationPage(self)
        self.routines_page = RoutinesPage(self)
        self.knowledge_page = KnowledgePage(self)
        self.files_page = FilesPage(self)
        self.developer_page = DeveloperPage(self)
        self.screen_page = ScreenPage(self)
        self.model_hub_page = ModelHubPage(self)
        self.audit_page = AuditPage(self)
        self.settings_page = SettingsPage(self)

        # Wire navigation and quick commands
        self.overview_page.quick_command_submitted.connect(self._route_quick_command)
        self.model_hub_page.model_changed.connect(self._on_model_changed)

        page_list = [
            ("overview", self.overview_page),
            ("chat", self.chat_page),
            ("voice", self.voice_page),
            ("monitor", self.monitor_page),
            ("automation", self.automation_page),
            ("routines", self.routines_page),
            ("knowledge", self.knowledge_page),
            ("files", self.files_page),
            ("developer", self.developer_page),
            ("screen", self.screen_page),
            ("model_hub", self.model_hub_page),
            ("audit", self.audit_page),
            ("settings", self.settings_page),
        ]

        for key, widget in page_list:
            self.pages[key] = widget
            self.stack.addWidget(widget)

        middle_layout.addWidget(self.stack, 1)
        root_layout.addWidget(middle_widget, 1)

        # 3. Contextual Right Panel
        self.right_panel = RightPanel(self)
        root_layout.addWidget(self.right_panel)

    def _on_navigate(self, key: str):
        if key in self.pages:
            self.stack.setCurrentWidget(self.pages[key])
            title, subtitle = PAGE_TITLES.get(key, (key.capitalize(), ""))
            self.header.set_title(title, subtitle)

    def _route_quick_command(self, prompt: str):
        # Switch to chat and send prompt
        self.sidebar.set_active("chat")
        self._on_navigate("chat")
        self.chat_page.send_prompt(prompt)

    def _on_quick_action(self, action: str):
        if action == "toggle_mute":
            curr = GetVolumeTool().execute()
            is_muted = curr.data.get("is_muted", False) if curr.success and curr.data else False
            SetMuteTool().execute(mute=not is_muted)
        elif action == "analyze_screen":
            self.sidebar.set_active("screen")
            self._on_navigate("screen")
            self.screen_page._capture_screen()

    def _on_model_changed(self, provider: str, model: str):
        self.header.set_model_label(provider.upper(), model)

    def _start_telemetry_timer(self):
        self.timer = QTimer(self)
        self.timer.setInterval(int(self.settings.monitor_refresh_interval_sec * 1000))
        self.timer.timeout.connect(self._sync_metrics)
        self.timer.start()

    def _sync_metrics(self):
        metrics = self.monitor.get_latest()
        self.header.update_metrics(metrics)
        self.right_panel.update_metrics(metrics)
        self.overview_page.update_metrics(metrics)
        self.monitor_page.update_metrics(metrics)
