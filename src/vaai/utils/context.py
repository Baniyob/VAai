"""Conversation context state management."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


def default_case_notes() -> List[str]:
    return []


def default_metadata() -> Dict[str, str]:
    return {}


@dataclass
class ConversationContext:
    """Mutable state that persists across conversational turns."""

    client_id: str
    channel: str
    locale: str = "en-US"
    loyalty_tier: Optional[str] = None
    is_verified: bool = False
    verification_attempts: int = 0
    active_card_id: Optional[str] = None
    case_id: Optional[str] = None
    case_notes: List[str] = field(default_factory=default_case_notes)
    session_metadata: Dict[str, str] = field(default_factory=default_metadata)
    started_at: datetime = field(default_factory=datetime.utcnow)

    def add_note(self, note: str) -> None:
        timestamp = datetime.utcnow().isoformat()
        self.case_notes.append(f"[{timestamp}] {note}")

    def set_metadata(self, key: str, value: str) -> None:
        self.session_metadata[key] = value

    def get_metadata(self, key: str, default: Optional[str] = None) -> Optional[str]:
        return self.session_metadata.get(key, default)
