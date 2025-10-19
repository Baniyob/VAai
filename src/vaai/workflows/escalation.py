"""Utilities for escalating cases to human agents."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict

from ..intents.base import IntentResponse, ResponseType
from ..monitoring.observability import ObservabilityContext
from ..utils.context import ConversationContext


@dataclass
class EscalationTicket:
    """Structured payload for handing off to human agents."""

    client_id: str
    case_id: str
    issue_type: str
    urgency: str
    created_at: datetime
    metadata: Dict[str, str]

    def to_json(self) -> Dict[str, object]:
        return {
            "clientId": self.client_id,
            "caseId": self.case_id,
            "issueType": self.issue_type,
            "urgencyLevel": self.urgency,
            "createdAt": self.created_at.isoformat(),
            "metadata": self.metadata,
        }


def escalate_to_human(
    *,
    context: ConversationContext,
    intent: str,
    reason: str | None,
    observability: ObservabilityContext,
    urgency: str = "high",
) -> IntentResponse:
    """Build an escalation response and ticket payload."""

    context.case_id = context.case_id or f"CASE-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    context.add_note(f"Escalated intent {intent}: {reason}")

    ticket = EscalationTicket(
        client_id=context.client_id,
        case_id=context.case_id,
        issue_type=intent,
        urgency=urgency,
        created_at=datetime.utcnow(),
        metadata={"reason": reason or "unspecified", "trace_id": observability.trace_id},
    )

    return IntentResponse(
        message="I'll bring a specialist to assist you further. Please stay on the line while I connect you.",
        response_type=ResponseType.CASE_ESCALATION,
        data={"ticket": ticket.to_json()},
        requires_follow_up=True,
    )
