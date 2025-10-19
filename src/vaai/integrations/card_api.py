"""Integrations with the card management system."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class CardOperationResult:
    """Return type for card management actions."""

    success: bool
    reference_id: Optional[str] = None
    failure_reason: Optional[str] = None


class CardManagementAPI:
    """Client for interacting with card management microservices."""

    def freeze_card(self, *, card_id: str, reason: Optional[str]) -> CardOperationResult:
        """Freeze the card and optionally trigger replacement."""

        if not card_id:
            return CardOperationResult(success=False, failure_reason="card_id_required")
        reference = f"FRZ-{card_id}" if reason else f"FRZ-{card_id}-AUTO"
        return CardOperationResult(success=True, reference_id=reference)

    def activate_card(self, *, card_id: str | None) -> CardOperationResult:
        if not card_id:
            return CardOperationResult(success=False, failure_reason="card_id_required")
        return CardOperationResult(success=True, reference_id=f"ACT-{card_id}")
