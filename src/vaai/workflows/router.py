"""Workflow routing utilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from ..agent import EscalationRequired
from ..intents.base import IntentHandler


@dataclass
class WorkflowRouter:
    """Maps intents to their handlers with validation."""

    handlers: Dict[str, IntentHandler]

    def route(self, intent_name: str) -> IntentHandler:
        try:
            return self.handlers[intent_name]
        except KeyError as exc:  # noqa: B902
            raise EscalationRequired(f"No handler registered for intent: {intent_name}") from exc

    def register(self, handler: IntentHandler) -> None:
        self.handlers[handler.name] = handler
