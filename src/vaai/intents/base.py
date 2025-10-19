"""Intent base classes and data models."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Protocol

from ..monitoring.observability import ObservabilityContext
from ..utils.context import ConversationContext


class ResponseType(str, Enum):
    """Enumerates the possible response payload types."""

    TEXT = "text"
    CARD_SUMMARY = "card_summary"
    TRANSACTION_LIST = "transaction_list"
    CASE_ESCALATION = "case_escalation"


@dataclass
class IntentRequest:
    """Normalized representation of an intent-triggered request."""

    intent_name: str
    utterance: str
    parameters: Dict[str, str] = field(default_factory=dict)


@dataclass
class IntentResponse:
    """Standard contract for responses produced by intent handlers."""

    message: str
    response_type: ResponseType = ResponseType.TEXT
    data: Optional[Dict[str, object]] = None
    requires_follow_up: bool = False
    terminate_session: bool = False


class IntentHandler(Protocol):
    """Interface implemented by all intent handlers."""

    name: str
    requires_verification: bool

    def handle(
        self,
        request: IntentRequest,
        context: ConversationContext,
        observability: ObservabilityContext,
    ) -> IntentResponse:
        """Process the request and return a response."""
