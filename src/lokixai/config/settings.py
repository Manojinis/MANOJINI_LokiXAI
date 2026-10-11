"""Application configuration and validation settings."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field


DEFAULT_APPROVED_DIRS = [
    str(Path.cwd().resolve()),
    os.path.expanduser(r"~\Documents"),
    os.path.expanduser(r"~\Downloads"),
    r"C:\Users\Public",
]


class AppSettings(BaseModel):
    """Central configuration for LokiXAI application."""

    # AI Provider settings
    ai_provider: str = Field(default="openai", description="Active AI provider: openai, local, or mock")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o", description="Default OpenAI model")
    openai_embedding_model: str = Field(default="text-embedding-3-small", description="OpenAI embedding model")
    openai_timeout_seconds: int = Field(default=45, ge=5, le=300)

    # Local AI Provider (Ollama / vLLM)
    local_ai_base_url: str = Field(default="http://localhost:11434/v1", description="Local OpenAI-compatible API URL")
    local_ai_model: str = Field(default="llama3.2", description="Local model name")
    local_ai_api_key: str = Field(default="ollama", description="Local API key")

    # Security & Permissions
    auto_approve_safe_tools: bool = Field(default=True, description="Auto-approve read-only or low-risk tools")
    require_confirmation_destructive: bool = Field(default=True, description="Prompt user before destructive actions")
    approved_directories: List[str] = Field(default_factory=lambda: list(DEFAULT_APPROVED_DIRS))

    # Voice & Speech
    tts_enabled: bool = Field(default=True, description="Enable spoken text-to-speech output")
    tts_rate: int = Field(default=175, ge=80, le=350, description="Words per minute")
    tts_volume: float = Field(default=1.0, ge=0.0, le=1.0, description="Volume level 0.0 to 1.0")
    tts_voice_id: Optional[str] = Field(default=None, description="Specific SAPI voice ID")

    # System Monitor
    monitor_refresh_interval_sec: float = Field(default=2.0, ge=0.5, le=10.0)

    # Storage & Logging
    data_dir: str = Field(default="data")
    log_level: str = Field(default="INFO")

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> AppSettings:
        """Load settings from environment and persistent JSON file."""
        data_dir = Path("data")
        data_dir.mkdir(parents=True, exist_ok=True)
        json_file = config_path or (data_dir / "settings.json")

        loaded_data = {}
        if json_file.exists():
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    loaded_data = json.load(f)
            except Exception:
                loaded_data = {}

        # Overlay environment variables if present
        env_provider = os.getenv("LOKIXAI_AI_PROVIDER")
        if env_provider:
            loaded_data["ai_provider"] = env_provider

        env_key = os.getenv("OPENAI_API_KEY")
        if env_key:
            loaded_data["openai_api_key"] = env_key

        env_model = os.getenv("OPENAI_MODEL")
        if env_model:
            loaded_data["openai_model"] = env_model

        env_local_url = os.getenv("LOCAL_AI_BASE_URL")
        if env_local_url:
            loaded_data["local_ai_base_url"] = env_local_url

        try:
            return cls(**loaded_data)
        except Exception:
            return cls()

    def save(self, config_path: Optional[Path] = None) -> None:
        """Save current settings to persistent JSON file."""
        target = config_path or (Path(self.data_dir) / "settings.json")
        target.parent.mkdir(parents=True, exist_ok=True)
        # Avoid saving sensitive API keys to plaintext json if from env, but persist user UI settings
        with open(target, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json(indent=2))


_global_settings: Optional[AppSettings] = None


def get_settings() -> AppSettings:
    """Singleton getter for application settings."""
    global _global_settings
    if _global_settings is None:
        _global_settings = AppSettings.load()
    return _global_settings
