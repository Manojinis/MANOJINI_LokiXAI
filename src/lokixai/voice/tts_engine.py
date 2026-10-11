"""Text-to-speech engine running asynchronously without blocking UI."""

from __future__ import annotations

import logging
import queue
import threading
from typing import List, Optional

logger = logging.getLogger("lokixai.voice.tts")


class TTSEngine:
    """Asynchronous speech synthesizer using pyttsx3."""

    def __init__(self, rate: int = 175, volume: float = 1.0):
        self.rate = rate
        self.volume = volume
        self.is_enabled = True
        self._queue: queue.Queue = queue.Queue()
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._worker_loop, daemon=True, name="LokiTTSWorker")
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        self._queue.put(None)

    def speak(self, text: str) -> None:
        """Enqueue text for speech playback."""
        if not self.is_enabled or not text.strip():
            return
        if not self._running:
            self.start()
        self._queue.put(text)

    def _worker_loop(self) -> None:
        import comtypes
        comtypes.CoInitialize()
        import pyttsx3

        engine = None
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", self.rate)
            engine.setProperty("volume", self.volume)
        except Exception as e:
            logger.warning(f"Could not initialize pyttsx3 engine: {e}")

        while self._running:
            try:
                item = self._queue.get()
                if item is None:
                    break
                if engine and self.is_enabled:
                    engine.say(item)
                    engine.runAndWait()
                self._queue.task_done()
            except Exception as e:
                logger.error(f"TTS playback error: {e}")


_global_tts: Optional[TTSEngine] = None


def get_tts_engine() -> TTSEngine:
    global _global_tts
    if _global_tts is None:
        _global_tts = TTSEngine()
        _global_tts.start()
    return _global_tts
