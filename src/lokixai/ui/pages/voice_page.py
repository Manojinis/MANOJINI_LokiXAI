"""Voice assistant interface with push-to-talk recording and TTS speech controls."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from src.lokixai.voice.tts_engine import get_tts_engine
from src.lokixai.voice.stt_engine import get_stt_engine


class VoicePage(QWidget):
    """Voice Assistant Hub for audio recording and synthesis configuration."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tts = get_tts_engine()
        self.stt = get_stt_engine()
        self.is_recording = False
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Header Title
        title_box = QVBoxLayout()
        h = QLabel("🎙️ Voice Assistant & Audio Control")
        h.setStyleSheet("font-size: 18px; font-weight: 700; color: #00f2fe;")
        s = QLabel("Push-to-talk voice input, spoken responses, and microphone privacy status.")
        s.setStyleSheet("font-size: 12px; color: #94a3b8;")
        title_box.addWidget(h)
        title_box.addWidget(s)
        layout.addLayout(title_box)

        # Mic Recording Card
        mic_card = QFrame()
        mic_card.setObjectName("CardFrame")
        mic_layout = QVBoxLayout(mic_card)
        mic_layout.setAlignment(Qt.AlignCenter)
        mic_layout.setSpacing(16)
        mic_layout.setContentsMargins(24, 32, 24, 32)

        self.mic_btn = QPushButton("🎙️ Push to Talk")
        self.mic_btn.setObjectName("PrimaryButton")
        self.mic_btn.setFixedSize(220, 60)
        self.mic_btn.setStyleSheet("font-size: 16px; font-weight: 700; border-radius: 30px;")
        self.mic_btn.clicked.connect(self._toggle_recording)
        mic_layout.addWidget(self.mic_btn)

        self.status_lbl = QLabel("Status: Microphone Idle. Click to speak.")
        self.status_lbl.setStyleSheet("font-size: 13px; color: #94a3b8;")
        mic_layout.addWidget(self.status_lbl)

        # Privacy notice
        privacy_lbl = QLabel("🔒 Privacy Guarantee: Audio is only processed upon explicit click. No continuous background listening.")
        privacy_lbl.setStyleSheet("font-size: 11px; color: #64748b; font-style: italic;")
        mic_layout.addWidget(privacy_lbl)

        layout.addWidget(mic_card)

        # Live Transcript View
        trans_title = QLabel("TRANSCRIPTION PREVIEW")
        trans_title.setStyleSheet("font-size: 11px; font-weight: 700; color: #64748b; letter-spacing: 0.5px;")
        layout.addWidget(trans_title)

        self.trans_edit = QPlainTextEdit()
        self.trans_edit.setPlaceholderText("Spoken speech transcript will appear here...")
        self.trans_edit.setFixedHeight(100)
        layout.addWidget(self.trans_edit)

        # TTS Configuration Card
        tts_card = QFrame()
        tts_card.setObjectName("CardFrame")
        t_layout = QVBoxLayout(tts_card)
        t_layout.setSpacing(12)
        t_layout.setContentsMargins(16, 16, 16, 16)

        t_lbl = QLabel("TEXT-TO-SPEECH (TTS) PREFERENCES")
        t_lbl.setStyleSheet("font-size: 11px; font-weight: 700; color: #64748b;")
        t_layout.addWidget(t_lbl)

        # Speech rate
        rate_box = QHBoxLayout()
        r_lbl = QLabel("Speaking Rate (WPM):")
        self.rate_val_lbl = QLabel(f"{self.tts.rate}")
        self.rate_slider = QSlider(Qt.Horizontal)
        self.rate_slider.setRange(100, 280)
        self.rate_slider.setValue(self.tts.rate)
        self.rate_slider.valueChanged.connect(self._on_rate_change)
        rate_box.addWidget(r_lbl)
        rate_box.addWidget(self.rate_slider)
        rate_box.addWidget(self.rate_val_lbl)
        t_layout.addLayout(rate_box)

        # Volume slider
        vol_box = QHBoxLayout()
        v_lbl = QLabel("TTS Voice Volume:")
        self.tts_vol_lbl = QLabel("100%")
        self.tts_vol_slider = QSlider(Qt.Horizontal)
        self.tts_vol_slider.setRange(0, 100)
        self.tts_vol_slider.setValue(int(self.tts.volume * 100))
        self.tts_vol_slider.valueChanged.connect(self._on_volume_change)
        vol_box.addWidget(v_lbl)
        vol_box.addWidget(self.tts_vol_slider)
        vol_box.addWidget(self.tts_vol_lbl)
        t_layout.addLayout(vol_box)

        # Test Speak Button
        btn_box = QHBoxLayout()
        btn_box.addStretch()
        test_btn = QPushButton("🔊 Test Voice Synthesis")
        test_btn.clicked.connect(self._test_speech)
        btn_box.addWidget(test_btn)
        t_layout.addLayout(btn_box)

        layout.addWidget(tts_card)
        layout.addStretch()

    def _toggle_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.stt.start_recording()
            self.mic_btn.setText("⏹️ Stop Recording")
            self.mic_btn.setStyleSheet("background-color: #ef4444; color: white; font-size: 16px; font-weight: 700; border-radius: 30px;")
            self.status_lbl.setText("Status: Listening... Speak your command clearly.")
        else:
            self.is_recording = False
            transcript = self.stt.stop_recording_and_transcribe()
            self.mic_btn.setText("🎙️ Push to Talk")
            self.mic_btn.setStyleSheet("")
            self.mic_btn.setObjectName("PrimaryButton")
            self.status_lbl.setText("Status: Transcription complete.")
            self.trans_edit.setPlainText(transcript)

    def _on_rate_change(self, val: int):
        self.tts.rate = val
        self.rate_val_lbl.setText(str(val))

    def _on_volume_change(self, val: int):
        self.tts.volume = val / 100.0
        self.tts_vol_lbl.setText(f"{val}%")

    def _test_speech(self):
        self.tts.speak("Hello! This is LokiXAI voice synthesis test. Audio system operational.")
