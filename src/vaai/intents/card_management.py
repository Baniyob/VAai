"""Card management intents: activation, freeze, replacement."""
from __future__ import annotations

from dataclasses import dataclass

from .base import IntentRequest, IntentResponse, ResponseType
from ..monitoring.observability import ObservabilityContext
from ..utils.context import ConversationContext
from ..integrations.card_api import CardManagementAPI
from ..workflows.escalation import escalate_to_human


@dataclass
class FreezeCardHandler:
    """Freeze a lost or stolen card."""

    card_api: CardManagementAPI
    name: str = "freeze_card"
    requires_verification: bool = True

    def handle(
        self,
        request: IntentRequest,
        context: ConversationContext,
        observability: ObservabilityContext,
    ) -> IntentResponse:
        card_id = request.parameters.get("card_id") or context.active_card_id
        if not card_id:
            return IntentResponse(
                message="I can help with that. Which card would you like me to freeze?",
                requires_follow_up=True,
            )

        result = self.card_api.freeze_card(card_id=card_id, reason=request.parameters.get("reason"))
        if not result.success:
            return escalate_to_human(
                context=context,
                intent=request.intent_name,
                reason=result.failure_reason,
                observability=observability,
            )

        context.case_notes.append(f"Card {card_id} frozen: {result.reference_id}")
        return IntentResponse(
            message="The card is now frozen. I've ordered a replacement and will send updates to your email.",
            response_type=ResponseType.CARD_SUMMARY,
            data={"card_id": card_id, "status": "frozen", "replacement_case": result.reference_id},
            requires_follow_up=True,
        )


@dataclass
class ActivateCardHandler:
    """Activate a newly issued card."""

    card_api: CardManagementAPI
    name: str = "activate_card"
    requires_verification: bool = True

    def handle(
        self,
        request: IntentRequest,
        context: ConversationContext,
        observability: ObservabilityContext,
    ) -> IntentResponse:
        card_id = request.parameters.get("card_id") or context.active_card_id
        activation = self.card_api.activate_card(card_id=card_id)
        if activation.success:
            return IntentResponse(
                message="Your card is now active. Is there anything else I can help you with?",
                response_type=ResponseType.CARD_SUMMARY,
                data={"card_id": card_id, "status": "active"},
            )

        return escalate_to_human(
            context=context,
            intent=request.intent_name,
            reason=activation.failure_reason,
            observability=observability,
        )
