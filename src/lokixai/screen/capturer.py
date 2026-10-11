"""Screen capture utility for explicit user-initiated screenshot analysis."""

from __future__ import annotations

import base64
import datetime
from io import BytesIO
import logging
from pathlib import Path
from typing import Optional
from PIL import ImageGrab

logger = logging.getLogger("lokixai.screen")


class ScreenCapturer:
    """Safely captures full or regional screenshots upon explicit user initiation."""

    def __init__(self, output_dir: str = "data/screenshots"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.last_capture_path: Optional[Path] = None

    def capture_full_screen(self) -> Path:
        """Capture display and persist to local screenshots cache."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        target_path = self.output_dir / f"screen_{timestamp}.png"
        
        screenshot = ImageGrab.grab()
        screenshot.save(str(target_path), "PNG")
        self.last_capture_path = target_path
        logger.info(f"Captured screenshot: {target_path}")
        return target_path

    def get_base64_image(self, path: Optional[Path] = None) -> str:
        """Encode image to base64 for vision models."""
        target = path or self.last_capture_path
        if not target or not target.exists():
            raise FileNotFoundError("No captured image available.")

        with open(target, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def discard_capture(self) -> None:
        """Delete last captured screenshot if user cancels."""
        if self.last_capture_path and self.last_capture_path.exists():
            try:
                self.last_capture_path.unlink()
                self.last_capture_path = None
            except Exception as e:
                logger.warning(f"Could not delete screenshot: {e}")


_global_capturer: Optional[ScreenCapturer] = None


def get_screen_capturer() -> ScreenCapturer:
    global _global_capturer
    if _global_capturer is None:
        _global_capturer = ScreenCapturer()
    return _global_capturer
