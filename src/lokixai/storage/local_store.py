"""Persistent local storage for conversation sessions, routines, and workspaces."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.lokixai.ai.conversation import ConversationSession

logger = logging.getLogger("lokixai.storage")


class LocalStore:
    """Handles local disk serialization of user sessions and automation data."""

    def __init__(self, base_dir: str = "data"):
        self.base_dir = Path(base_dir)
        self.sessions_dir = self.base_dir / "sessions"
        self.routines_file = self.base_dir / "routines.json"
        self.workspaces_file = self.base_dir / "workspaces.json"

        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def save_session(self, session: ConversationSession) -> None:
        target = self.sessions_dir / f"{session.id}.json"
        try:
            with open(target, "w", encoding="utf-8") as f:
                f.write(session.model_dump_json(indent=2))
        except Exception as e:
            logger.error(f"Failed to save session {session.id}: {e}")

    def load_session(self, session_id: str) -> Optional[ConversationSession]:
        target = self.sessions_dir / f"{session_id}.json"
        if not target.exists():
            return None
        try:
            with open(target, "r", encoding="utf-8") as f:
                data = json.load(f)
            return ConversationSession(**data)
        except Exception as e:
            logger.error(f"Failed to load session {session_id}: {e}")
            return None

    def list_sessions(self) -> List[Dict[str, str]]:
        """List summary of saved sessions (id, title, created_at)."""
        results = []
        for file in sorted(self.sessions_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    results.append({
                        "id": data.get("id", file.stem),
                        "title": data.get("title", "Untitled Session"),
                        "created_at": data.get("created_at", ""),
                    })
            except Exception:
                continue
        return results

    def delete_session(self, session_id: str) -> bool:
        target = self.sessions_dir / f"{session_id}.json"
        if target.exists():
            try:
                target.unlink()
                return True
            except Exception:
                return False
        return False

    def load_routines(self) -> List[Dict[str, Any]]:
        if not self.routines_file.exists():
            return []
        try:
            with open(self.routines_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def save_routines(self, routines: List[Dict[str, Any]]) -> None:
        try:
            with open(self.routines_file, "w", encoding="utf-8") as f:
                json.dump(routines, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save routines: {e}")


_global_store: Optional[LocalStore] = None


def get_local_store() -> LocalStore:
    global _global_store
    if _global_store is None:
        _global_store = LocalStore()
    return _global_store
