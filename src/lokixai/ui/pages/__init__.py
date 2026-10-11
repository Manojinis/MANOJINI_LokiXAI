"""Pages package for all 13 interactive views in LokiXAI."""

from .overview_page import OverviewPage
from .chat_page import ChatPage
from .voice_page import VoicePage
from .monitor_page import MonitorPage
from .automation_page import AutomationPage
from .routines_page import RoutinesPage
from .knowledge_page import KnowledgePage
from .files_page import FilesPage
from .developer_page import DeveloperPage
from .screen_page import ScreenPage
from .model_hub_page import ModelHubPage
from .audit_page import AuditPage
from .settings_page import SettingsPage

__all__ = [
    "OverviewPage",
    "ChatPage",
    "VoicePage",
    "MonitorPage",
    "AutomationPage",
    "RoutinesPage",
    "KnowledgePage",
    "FilesPage",
    "DeveloperPage",
    "ScreenPage",
    "ModelHubPage",
    "AuditPage",
    "SettingsPage",
]
