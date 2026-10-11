"""Safe file browser and previewer restricted to approved directory roots."""

from __future__ import annotations

from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.lokixai.config.settings import get_settings
from src.lokixai.files.manager import SafeFileManager, FileEntry
from src.lokixai.tools.file_tools import DeleteFileTool


class FilesPage(QWidget):
    """Secure File Manager strictly bound to approved roots."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = SafeFileManager()
        self.settings = get_settings()
        self.current_root = self.settings.approved_directories[0] if self.settings.approved_directories else str(Path.cwd())
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Header
        title_box = QVBoxLayout()
        h = QLabel("📁 Safe File Manager")
        h.setStyleSheet("font-size: 18px; font-weight: 700; color: #00f2fe;")
        s = QLabel("Browse, preview, and organize files within approved directory roots. Traversal outside is blocked.")
        s.setStyleSheet("font-size: 12px; color: #94a3b8;")
        title_box.addWidget(h)
        title_box.addWidget(s)
        layout.addLayout(title_box)

        # Directory Selector and Search
        nav_box = QHBoxLayout()
        root_lbl = QLabel("Root Directory:")
        root_lbl.setStyleSheet("font-weight: 600; color: #94a3b8;")
        nav_box.addWidget(root_lbl)

        self.root_combo = QComboBox()
        for d in self.settings.approved_directories:
            self.root_combo.addItem(d)
        self.root_combo.currentIndexChanged.connect(self._on_root_changed)
        nav_box.addWidget(self.root_combo, 1)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter files by name...")
        self.search_input.textChanged.connect(self._on_filter_changed)
        nav_box.addWidget(self.search_input)

        self.up_btn = QPushButton("⬆ Up")
        self.up_btn.clicked.connect(self._navigate_up)
        nav_box.addWidget(self.up_btn)

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self._load_files)
        nav_box.addWidget(refresh_btn)

        layout.addLayout(nav_box)

        # Splitter with File List and Preview
        splitter = QSplitter(Qt.Horizontal)

        # Table Card
        table_card = QFrame()
        table_card.setObjectName("CardFrame")
        t_layout = QVBoxLayout(table_card)
        t_layout.setContentsMargins(8, 8, 8, 8)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Name", "Type", "Size", "Modified"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.table.cellDoubleClicked.connect(self._on_item_double_clicked)
        t_layout.addWidget(self.table)
        splitter.addWidget(table_card)


        # Preview Card
        preview_card = QFrame()
        preview_card.setObjectName("CardFrame")
        p_layout = QVBoxLayout(preview_card)
        p_layout.setContentsMargins(12, 12, 12, 12)
        p_layout.setSpacing(8)

        p_top = QHBoxLayout()
        self.preview_title = QLabel("FILE PREVIEW")
        self.preview_title.setStyleSheet("font-size: 11px; font-weight: 700; color: #64748b;")
        p_top.addWidget(self.preview_title)
        p_top.addStretch()

        self.del_btn = QPushButton("🗑️ Delete File")
        self.del_btn.setObjectName("DangerButton")
        self.del_btn.clicked.connect(self._on_delete_file)
        p_top.addWidget(self.del_btn)
        p_layout.addLayout(p_top)

        self.preview_text = QPlainTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setStyleSheet("""
            background-color: #0c1322;
            border: 1px solid #1e293b;
            color: #f8fafc;
            font-family: 'Consolas', monospace;
            font-size: 12px;
        """)
        p_layout.addWidget(self.preview_text)
        splitter.addWidget(preview_card)

        splitter.setSizes([450, 400])
        layout.addWidget(splitter, 1)

        self._load_files()

    def _on_root_changed(self, idx: int):
        self.current_root = self.root_combo.currentText()
        self._load_files()

    def _navigate_up(self):
        curr = Path(self.current_root)
        parent = curr.parent
        guard = self.manager.get_guard()
        if guard.is_safe_path(parent):
            self.current_root = str(parent)
            self._load_files()
        else:
            QMessageBox.information(self, "Boundary", "Already at the approved directory boundary.")

    def _on_item_double_clicked(self, row: int, col: int):
        item = self.table.item(row, 0)
        if item:
            path_str = item.data(Qt.UserRole)
            target = Path(path_str)
            if target.is_dir():
                guard = self.manager.get_guard()
                if guard.is_safe_path(target):
                    self.current_root = str(target)
                    self._load_files()


    def _load_files(self):
        try:
            entries = self.manager.list_directory(self.current_root)
            self._display_entries(entries)
        except Exception as e:
            self.table.setRowCount(0)
            self.preview_text.setPlainText(f"Error accessing directory: {e}")

    def _on_filter_changed(self, query: str):
        try:
            all_entries = self.manager.list_directory(self.current_root)
            filtered = [e for e in all_entries if query.lower() in e.name.lower()]
            self._display_entries(filtered)
        except Exception:
            pass

    def _display_entries(self, entries: list[FileEntry]):
        self.table.setRowCount(len(entries))
        for row, item in enumerate(entries):
            type_str = "Folder" if item.is_dir else item.extension or "File"
            size_str = "" if item.is_dir else f"{item.size_bytes / 1024:.1f} KB"
            icon = "📁" if item.is_dir else "📄"

            name_item = QTableWidgetItem(f"{icon} {item.name}")
            name_item.setData(Qt.UserRole, item.path)
            
            self.table.setItem(row, 0, name_item)
            self.table.setItem(row, 1, QTableWidgetItem(type_str))
            self.table.setItem(row, 2, QTableWidgetItem(size_str))
            self.table.setItem(row, 3, QTableWidgetItem(item.modified_time))

    def _on_selection_changed(self):
        selected = self.table.selectedItems()
        if not selected:
            return

        file_path = self.table.item(self.table.currentRow(), 0).data(Qt.UserRole)
        p = Path(file_path)
        if p.is_file():
            self.preview_title.setText(f"PREVIEW: {p.name}")
            try:
                content = self.manager.read_preview(file_path, max_lines=200)
                self.preview_text.setPlainText(content)
            except Exception as e:
                self.preview_text.setPlainText(f"Unable to preview file: {e}")
        else:
            self.preview_title.setText(f"FOLDER: {p.name}")
            self.preview_text.setPlainText(f"Directory path: {p}\nSelect a text file to view preview.")

    def _on_delete_file(self):
        selected = self.table.selectedItems()
        if not selected:
            return

        file_path = self.table.item(self.table.currentRow(), 0).data(Qt.UserRole)
        p = Path(file_path)
        if not p.is_file():
            QMessageBox.information(self, "Delete", "Please select a file to delete.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to permanently delete '{p.name}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            tool = DeleteFileTool()
            res = tool.execute(file_path=file_path)
            if res.success:
                QMessageBox.information(self, "Deleted", f"Deleted {p.name}")
                self._load_files()
            else:
                QMessageBox.warning(self, "Error", f"Delete failed: {res.message}")
