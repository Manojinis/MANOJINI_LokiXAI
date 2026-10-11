"""Theme system and dark futuristic stylesheets for LokiXAI."""

class ThemeColors:
    """Dark futuristic palette with cyan, teal, and violet accents."""
    BG_DARK = "#090d16"
    BG_SURFACE = "#0f172a"
    BG_CARD = "#141e33"
    BG_CARD_HOVER = "#1c2842"
    BG_INPUT = "#0c1322"
    
    BORDER_SUBTLE = "#1e293b"
    BORDER_GLOW = "rgba(0, 242, 254, 0.45)"
    BORDER_ACTIVE = "#00f2fe"
    
    PRIMARY_CYAN = "#00f2fe"
    PRIMARY_BLUE = "#4facfe"
    PRIMARY_PURPLE = "#8a2be2"
    ACCENT_VIOLET = "#7928ca"
    
    TEXT_PRIMARY = "#f8fafc"
    TEXT_SECONDARY = "#94a3b8"
    TEXT_MUTED = "#64748b"
    
    SUCCESS = "#10b981"
    WARNING = "#f59e0b"
    DANGER = "#ef4444"
    INFO = "#38bdf8"


STYLESHEET = """
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

/* Sidebar Navigation */
QFrame#SidebarFrame {
    background-color: #0b1120;
    border-right: 1px solid #1e293b;
}

QPushButton#NavButton {
    background-color: transparent;
    color: #94a3b8;
    text-align: left;
    padding: 10px 14px;
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

/* Cards */
QFrame.CardFrame, QFrame#CardFrame {
    background-color: #131d31;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 14px;
}

QFrame.CardFrame:hover, QFrame#CardFrame:hover {
    border: 1px solid rgba(0, 242, 254, 0.3);
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
