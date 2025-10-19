"""Analytics and metrics collection."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..utils.context import ConversationContext


def default_events() -> List[Dict[str, object]]:
    return []


@dataclass
class AnalyticsCollector:
    """Captures conversational analytics for dashboards and training."""

    events: List[Dict[str, object]] = field(default_factory=default_events)
    trace_id: Optional[str] = None

    def bind_trace(self, trace_id: str) -> None:
        self.trace_id = trace_id

    def record_event(self, name: str, *, context: ConversationContext, metadata: Optional[Dict[str, object]] = None) -> None:
        self.events.append(
            {
                "event": name,
                "client_id": context.client_id,
                "case_id": context.case_id,
                "metadata": metadata or {},
            }
        )

    def record_error(self, error: Exception, *, context: ConversationContext, metadata: Optional[Dict[str, object]] = None) -> None:
        self.events.append(
            {
                "event": "error",
                "client_id": context.client_id,
                "case_id": context.case_id,
                "error": str(error),
                "metadata": metadata or {},
            }
        )

    def flush(self) -> List[Dict[str, object]]:
        """Return recorded events for downstream processing."""

        events, self.events = self.events, []
        return events
