"""Observability helpers for tracing and logging."""
from __future__ import annotations

import uuid
from dataclasses import dataclass

from ..intents.base import IntentRequest
from ..utils.context import ConversationContext


@dataclass
class ObservabilityContext:
    """Metadata captured for distributed tracing and logging."""

    trace_id: str
    span_id: str
    client_id: str
    intent: str

    @classmethod
    def from_context(cls, context: ConversationContext, request: IntentRequest) -> "ObservabilityContext":
        trace_id = context.get_metadata("trace_id") or uuid.uuid4().hex
        context.set_metadata("trace_id", trace_id)
        span_id = uuid.uuid4().hex
        return cls(trace_id=trace_id, span_id=span_id, client_id=context.client_id, intent=request.intent_name)
