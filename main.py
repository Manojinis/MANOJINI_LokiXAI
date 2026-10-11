"""LokiXAI Desktop Application Entry Point.

Your Laptop. Your Intelligence. Your Control.
"""

from __future__ import annotations

import logging
import logging.handlers
import os
from pathlib import Path
import sys

from dotenv import load_dotenv

# Ensure 'src' is on sys.path
sys.path.insert(0, str(Path(__file__).parent))

from src.lokixai.config.settings import get_settings
from src.lokixai.security.redaction import SecretRedactor


class RedactingFormatter(logging.Formatter):
    """Custom logging formatter that strips sensitive secrets."""
    def format(self, record):
        orig = super().format(record)
        return SecretRedactor.redact(orig)


def setup_logging():
    """Initialize rotating file and console logging."""
    log_dir = Path("data/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "lokixai.log"

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = RedactingFormatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    ch.setFormatter(formatter)
    root_logger.addHandler(ch)

    # Rotating file handler (5MB, 3 backups)
    fh = logging.handlers.RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    root_logger.addHandler(fh)


def main():
    # Load environment variables from .env
    load_dotenv()
    setup_logging()
    logger = logging.getLogger("lokixai.main")
    logger.info("Starting LokiXAI Desktop Assistant...")

    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication
    from src.lokixai.ui.main_window import MainWindow

    # Configure High-DPI scaling for Windows 11
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("LokiXAI")
    app.setOrganizationName("LokiXAI")

    window = MainWindow()
    window.show()

    logger.info("LokiXAI Desktop Assistant GUI initialized and active.")
    exit_code = app.exec()

    # Graceful shutdown
    from src.lokixai.monitoring.system_monitor import get_system_monitor
    from src.lokixai.voice.tts_engine import get_tts_engine
    get_system_monitor().stop()
    get_tts_engine().stop()

    logger.info("LokiXAI shutdown complete.")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
