"""Headless GUI test verifying that PySide6 windows and pages instantiate cleanly."""

import os
import pytest

# Ensure headless Qt offscreen platform if running in automated environment
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication
from src.lokixai.ui.main_window import MainWindow


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_main_window_instantiation(qapp):
    window = MainWindow()
    assert window is not None
    assert len(window.pages) == 13
    assert "overview" in window.pages
    assert "chat" in window.pages
    assert "voice" in window.pages
    assert "monitor" in window.pages
    assert "automation" in window.pages
    assert "routines" in window.pages
    assert "knowledge" in window.pages
    assert "files" in window.pages
    assert "developer" in window.pages
    assert "screen" in window.pages
    assert "model_hub" in window.pages
    assert "audit" in window.pages
    assert "settings" in window.pages

    # Test navigation through all pages
    for key in window.pages:
        window._on_navigate(key)
        assert window.stack.currentWidget() == window.pages[key]

    window.close()
