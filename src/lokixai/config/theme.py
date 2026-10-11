"""Comprehensive Theme system supporting Dark, Light, and System themes for LokiXAI."""

from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger("lokixai.theme")


class ThemeColors:
    """Color tokens for UI elements."""
    # Dark Mode
    DARK_BG = "#090d16"
    DARK_SURFACE = "#0b1120"
    DARK_CARD = "#131d31"
    DARK_CARD_HOVER = "#1c2842"
    DARK_INPUT = "#0c1322"
    DARK_BORDER = "#1e293b"
    DARK_TEXT_PRIMARY = "#f8fafc"
    DARK_TEXT_SECONDARY = "#94a3b8"
    DARK_TEXT_MUTED = "#64748b"

    # Light Mode
    LIGHT_BG = "#f8fafc"
    LIGHT_SURFACE = "#ffffff"
    LIGHT_CARD = "#ffffff"
    LIGHT_CARD_HOVER = "#f1f5f9"
    LIGHT_INPUT = "#ffffff"
    LIGHT_BORDER = "#e2e8f0"
    LIGHT_TEXT_PRIMARY = "#0f172a"
    LIGHT_TEXT_SECONDARY = "#475569"
    LIGHT_TEXT_MUTED = "#64748b"

    # Accents
    CYAN_ACCENT = "#00f2fe"
    TEAL_ACCENT = "#0284c7"
    SKY_BLUE = "#0ea5e9"
    SUCCESS = "#10b981"
    WARNING = "#f59e0b"
    DANGER = "#ef4444"


DARK_STYLESHEET = """
QMainWindow, QDialog {
    background-color: #090d16;
    color: #f8fafc;
    font-family: 'Segoe UI', 'SF Pro Display', -apple-system, sans-serif;
}

QWidget {
    color: #f8fafc;
    font-family: 'Segoe UI', -apple-system, sans-serif;
    font-size: 13px;
}

/* Typography & Labels */
QLabel {
    color: #f8fafc;
}

QLabel#PageTitle {
    font-size: 18px;
    font-weight: 700;
    color: #00f2fe;
}

QLabel#PageSubtitle {
    font-size: 12px;
    color: #94a3b8;
}

QLabel#CardTitle {
    font-size: 14px;
    font-weight: 700;
    color: #f8fafc;
}

QLabel#SectionTitle {
    font-size: 11px;
    font-weight: 700;
    color: #64748b;
    letter-spacing: 0.5px;
}

QLabel#SubText {
    font-size: 12px;
    color: #94a3b8;
}

QLabel#MetricValue {
    font-size: 22px;
    font-weight: 800;
    color: #00f2fe;
}

QLabel#MetricLabel {
    font-size: 11px;
    font-weight: 600;
    color: #94a3b8;
}

QLabel#HeaderTitle {
    font-size: 15px;
    font-weight: 700;
    color: #f8fafc;
}

QLabel#HeaderSubtitle {
    font-size: 11px;
    color: #64748b;
}

QLabel#PillText {
    background-color: #131d31;
    color: #94a3b8;
    border: 1px solid #1e293b;
    border-radius: 14px;
    padding: 4px 12px;
    font-size: 11px;
    font-weight: 500;
}

QLabel#SenderLabel {
    font-size: 11px;
    font-weight: 700;
    color: #00f2fe;
}

QLabel#MessageText {
    font-size: 13px;
    color: #f8fafc;
}

QLabel#PreviewBox {
    background-color: #0c1322;
    border: 1px dashed #1e293b;
    border-radius: 8px;
    color: #64748b;
}

/* Sidebar Navigation */
QFrame#SidebarFrame {
    background-color: #0b1120;
    border-right: 1px solid #1e293b;
}

QPushButton#NavButton {
    background-color: transparent;
    color: #94a3b8;
    text-align: left;
    padding: 9px 12px;
    border-radius: 8px;
    border: none;
    font-size: 13px;
    font-weight: 500;
}

QPushButton#NavButton:hover {
    background-color: #141e33;
    color: #00f2fe;
}

QPushButton#NavButton[active="true"] {
    background-color: rgba(0, 242, 254, 0.12);
    color: #00f2fe;
    font-weight: 600;
    border-left: 3px solid #00f2fe;
}

/* Header & Panels */
QFrame#HeaderFrame {
    background-color: #0b1120;
    border-bottom: 1px solid #1e293b;
    padding: 8px 16px;
}

QFrame#RightPanelFrame {
    background-color: #0b1120;
    border-left: 1px solid #1e293b;
}

/* Cards & Containers */
QFrame.CardFrame, QFrame#CardFrame {
    background-color: #131d31;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 14px;
}

QFrame.CardFrame:hover, QFrame#CardFrame:hover {
    border: 1px solid rgba(0, 242, 254, 0.35);
}

QFrame#BannerCard {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0f172a, stop:1 #1e1b4b);
    border: 1px solid #1e293b;
    border-radius: 14px;
    padding: 18px;
}

QFrame#InnerBox, QFrame.InnerBox {
    background-color: #0c1322;
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 10px;
}

/* Buttons */
QPushButton {
    background-color: #1e293b;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #27354f;
    border-color: #00f2fe;
    color: #00f2fe;
}

QPushButton:pressed {
    background-color: #162035;
}

QPushButton:disabled {
    background-color: #0f172a;
    color: #475569;
    border-color: #1e293b;
}

QPushButton#PrimaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00f2fe, stop:1 #4facfe);
    color: #090d16;
    border: none;
    font-weight: 600;
    border-radius: 8px;
    padding: 8px 18px;
}

QPushButton#PrimaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #38f9d7, stop:1 #43e97b);
}

QPushButton#DangerButton {
    background-color: rgba(239, 68, 68, 0.15);
    color: #ef4444;
    border: 1px solid rgba(239, 68, 68, 0.4);
    border-radius: 8px;
}

QPushButton#DangerButton:hover {
    background-color: #ef4444;
    color: #ffffff;
}

QPushButton#SuggestionPill {
    background-color: #131d31;
    color: #94a3b8;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 6px 14px;
    font-size: 11px;
}

QPushButton#SuggestionPill:hover {
    background-color: #1c2842;
    color: #00f2fe;
    border-color: #00f2fe;
}

/* Text Inputs */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #0c1322;
    border: 1px solid #1e293b;
    border-radius: 8px;
    color: #f8fafc;
    padding: 8px 12px;
    selection-background-color: #00f2fe;
    selection-color: #090d16;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #00f2fe;
}

/* Chat Message Bubbles */
QFrame#UserBubble {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
}

QFrame#AssistantBubble {
    background-color: #131d31;
    border: 1px solid #1e293b;
    border-radius: 12px;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #090d16;
    width: 8px;
    margin: 0px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #1e293b;
    min-height: 24px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #00f2fe;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background: #090d16;
    height: 8px;
    margin: 0px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal {
    background: #1e293b;
    min-width: 24px;
    border-radius: 4px;
}

/* Progress Bar */
QProgressBar {
    background-color: #0c1322;
    border: 1px solid #1e293b;
    border-radius: 6px;
    text-align: center;
    color: #f8fafc;
    font-size: 11px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00f2fe, stop:1 #7928ca);
    border-radius: 5px;
}

/* ComboBox */
QComboBox {
    background-color: #0c1322;
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 6px 12px;
    color: #f8fafc;
}

QComboBox:hover {
    border-color: #00f2fe;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left: none;
}

QComboBox QAbstractItemView {
    background-color: #0f172a;
    border: 1px solid #1e293b;
    color: #f8fafc;
    selection-background-color: rgba(0, 242, 254, 0.2);
    selection-color: #00f2fe;
}

/* Table and Tree Views */
QTableWidget, QTreeWidget, QListWidget {
    background-color: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 8px;
    gridline-color: #1e293b;
    color: #f8fafc;
}

QHeaderView::section {
    background-color: #141e33;
    color: #94a3b8;
    padding: 6px;
    border: 1px solid #1e293b;
    font-weight: 600;
}

QTableWidget::item:selected, QTreeWidget::item:selected, QListWidget::item:selected {
    background-color: rgba(0, 242, 254, 0.15);
    color: #00f2fe;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #1e293b;
    background-color: #0f172a;
    border-radius: 8px;
}

QTabBar::tab {
    background-color: #0c1322;
    border: 1px solid #1e293b;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    color: #94a3b8;
}

QTabBar::tab:selected {
    background-color: #141e33;
    color: #00f2fe;
    border-bottom: 2px solid #00f2fe;
}
"""


LIGHT_STYLESHEET = """
QMainWindow, QDialog {
    background-color: #f8fafc;
    color: #0f172a;
    font-family: 'Segoe UI', 'SF Pro Display', -apple-system, sans-serif;
}

QWidget {
    color: #0f172a;
    font-family: 'Segoe UI', -apple-system, sans-serif;
    font-size: 13px;
}

/* Typography & Labels */
QLabel {
    color: #0f172a;
}

QLabel#PageTitle {
    font-size: 18px;
    font-weight: 700;
    color: #0284c7;
}

QLabel#PageSubtitle {
    font-size: 12px;
    color: #475569;
}

QLabel#CardTitle {
    font-size: 14px;
    font-weight: 700;
    color: #0f172a;
}

QLabel#SectionTitle {
    font-size: 11px;
    font-weight: 700;
    color: #64748b;
    letter-spacing: 0.5px;
}

QLabel#SubText {
    font-size: 12px;
    color: #475569;
}

QLabel#MetricValue {
    font-size: 22px;
    font-weight: 800;
    color: #0284c7;
}

QLabel#MetricLabel {
    font-size: 11px;
    font-weight: 600;
    color: #475569;
}

QLabel#HeaderTitle {
    font-size: 15px;
    font-weight: 700;
    color: #0f172a;
}

QLabel#HeaderSubtitle {
    font-size: 11px;
    color: #64748b;
}

QLabel#PillText {
    background-color: #ffffff;
    color: #475569;
    border: 1px solid #cbd5e1;
    border-radius: 14px;
    padding: 4px 12px;
    font-size: 11px;
    font-weight: 500;
}

QLabel#SenderLabel {
    font-size: 11px;
    font-weight: 700;
    color: #0284c7;
}

QLabel#MessageText {
    font-size: 13px;
    color: #0f172a;
}

QLabel#PreviewBox {
    background-color: #f1f5f9;
    border: 1px dashed #cbd5e1;
    border-radius: 8px;
    color: #64748b;
}

/* Sidebar Navigation */
QFrame#SidebarFrame {
    background-color: #f1f5f9;
    border-right: 1px solid #e2e8f0;
}

QPushButton#NavButton {
    background-color: transparent;
    color: #475569;
    text-align: left;
    padding: 9px 12px;
    border-radius: 8px;
    border: none;
    font-size: 13px;
    font-weight: 500;
}

QPushButton#NavButton:hover {
    background-color: #e2e8f0;
    color: #0284c7;
}

QPushButton#NavButton[active="true"] {
    background-color: rgba(2, 132, 199, 0.12);
    color: #0284c7;
    font-weight: 600;
    border-left: 3px solid #0284c7;
}

/* Header & Panels */
QFrame#HeaderFrame {
    background-color: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    padding: 8px 16px;
}

QFrame#RightPanelFrame {
    background-color: #f8fafc;
    border-left: 1px solid #e2e8f0;
}

/* Cards & Containers */
QFrame.CardFrame, QFrame#CardFrame {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 14px;
}

QFrame.CardFrame:hover, QFrame#CardFrame:hover {
    border: 1px solid #0ea5e9;
}

QFrame#BannerCard {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f0f9ff, stop:1 #e0f2fe);
    border: 1px solid #bae6fd;
    border-radius: 14px;
    padding: 18px;
}

QFrame#InnerBox, QFrame.InnerBox {
    background-color: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 10px;
}

/* Buttons */
QPushButton {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #f1f5f9;
    border-color: #0284c7;
    color: #0284c7;
}

QPushButton:pressed {
    background-color: #e2e8f0;
}

QPushButton:disabled {
    background-color: #f1f5f9;
    color: #94a3b8;
    border-color: #e2e8f0;
}

QPushButton#PrimaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #0ea5e9);
    color: #ffffff;
    border: none;
    font-weight: 600;
    border-radius: 8px;
    padding: 8px 18px;
}

QPushButton#PrimaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0369a1, stop:1 #0284c7);
}

QPushButton#DangerButton {
    background-color: #fee2e2;
    color: #dc2626;
    border: 1px solid #fca5a5;
    border-radius: 8px;
}

QPushButton#DangerButton:hover {
    background-color: #dc2626;
    color: #ffffff;
}

QPushButton#SuggestionPill {
    background-color: #ffffff;
    color: #475569;
    border: 1px solid #cbd5e1;
    border-radius: 12px;
    padding: 6px 14px;
    font-size: 11px;
}

QPushButton#SuggestionPill:hover {
    background-color: #f1f5f9;
    color: #0284c7;
    border-color: #0284c7;
}

/* Text Inputs */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    color: #0f172a;
    padding: 8px 12px;
    selection-background-color: #0284c7;
    selection-color: #ffffff;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #0284c7;
}

/* Chat Message Bubbles */
QFrame#UserBubble {
    background-color: #e0f2fe;
    border: 1px solid #bae6fd;
    border-radius: 12px;
}

QFrame#AssistantBubble {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #f8fafc;
    width: 8px;
    margin: 0px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #cbd5e1;
    min-height: 24px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #0284c7;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background: #f8fafc;
    height: 8px;
    margin: 0px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal {
    background: #cbd5e1;
    min-width: 24px;
    border-radius: 4px;
}

/* Progress Bar */
QProgressBar {
    background-color: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    text-align: center;
    color: #0f172a;
    font-size: 11px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #38bdf8);
    border-radius: 5px;
}

/* ComboBox */
QComboBox {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 6px 12px;
    color: #0f172a;
}

QComboBox:hover {
    border-color: #0284c7;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left: none;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    color: #0f172a;
    selection-background-color: rgba(2, 132, 199, 0.15);
    selection-color: #0284c7;
}

/* Table and Tree Views */
QTableWidget, QTreeWidget, QListWidget {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    gridline-color: #f1f5f9;
    color: #0f172a;
}

QHeaderView::section {
    background-color: #f8fafc;
    color: #475569;
    padding: 6px;
    border: 1px solid #e2e8f0;
    font-weight: 600;
}

QTableWidget::item:selected, QTreeWidget::item:selected, QListWidget::item:selected {
    background-color: rgba(2, 132, 199, 0.15);
    color: #0284c7;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #e2e8f0;
    background-color: #ffffff;
    border-radius: 8px;
}

QTabBar::tab {
    background-color: #f1f5f9;
    border: 1px solid #e2e8f0;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    color: #64748b;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #0284c7;
    border-bottom: 2px solid #0284c7;
}
"""

# Default backward compatibility export
STYLESHEET = DARK_STYLESHEET


class ThemeManager:
    """Manages application-wide theme resolution and dynamic switching."""

    @staticmethod
    def get_system_theme() -> str:
        """Detect Windows 11 system theme via registry."""
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return "light" if value == 1 else "dark"
        except Exception:
            return "dark"

    @staticmethod
    def get_stylesheet(theme_name: str = "dark") -> str:
        """Resolve theme name ('dark', 'light', 'system') to full QSS stylesheet."""
        t = (theme_name or "dark").lower()
        if t == "system":
            t = ThemeManager.get_system_theme()
        if t == "light":
            return LIGHT_STYLESHEET
        return DARK_STYLESHEET

    @staticmethod
    def apply_theme(target_widget, theme_name: str = "dark"):
        """Apply theme to application or top-level window."""
        qss = ThemeManager.get_stylesheet(theme_name)
        target_widget.setStyleSheet(qss)
        logger.info(f"Applied theme: {theme_name}")
