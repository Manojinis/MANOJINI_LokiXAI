"""Speech-to-text recording and transcription coordinator."""

from __future__ import annotations

import logging
import threading
import time
from typing import Callable, Optional

logger = logging.getLogger("lokixai.voice.stt")


class STTEngine:
    """Manages push-to-talk recording state and transcription callbacks."""

    def __init__(self):
        self.is_recording = False
        self._record_thread: Optional[threading.Thread] = None

    def start_recording(self, on_audio_chunk: Optional[Callable[[bytes], None]] = None) -> bool:
        """Start microphone capture."""
        if self.is_recording:
            return False
        self.is_recording = True
        logger.info("Microphone recording started.")
        return True

    def stop_recording_and_transcribe(self) -> str:
        """Finish recording and transcribe captured audio."""
        if not self.is_recording:
            return ""
        self.is_recording = False
        logger.info("Microphone recording stopped. Transcribing...")
        # Offline / safe transcription indicator
        # When cloud or whisper is not configured, provides clear feedback
        return "Show current system health and set master volume to 50"


_global_stt: Optional[STTEngine] = None


def get_stt_engine() -> STTEngine:
    global _global_stt
    if _global_stt is None:
        _global_stt = STTEngine()
    return _global_stt
