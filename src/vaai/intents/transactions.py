"""Transaction inquiry intents."""
from __future__ import annotations

from dataclasses import dataclass

from .base import IntentRequest, IntentResponse, ResponseType
from ..integrations.transaction_api import TransactionAPI
from ..monitoring.observability import ObservabilityContext
from ..utils.context import ConversationContext


@dataclass
class ListRecentTransactionsHandler:
    """Fetch recent transactions for a card."""

    transaction_api: TransactionAPI
    name: str = "list_recent_transactions"
    requires_verification: bool = True

    def handle(
        self,
        request: IntentRequest,
        context: ConversationContext,
        observability: ObservabilityContext,
    ) -> IntentResponse:
        card_id = request.parameters.get("card_id") or context.active_card_id
        transactions = self.transaction_api.list_recent(card_id=card_id, limit=10)
        message = "Here are the last transactions on your card. Let me know if you need more detail on any of them."
        return IntentResponse(
            message=message,
            response_type=ResponseType.TRANSACTION_LIST,
            data={"transactions": [txn.model_dump() for txn in transactions]},
            requires_follow_up=True,
        )


@dataclass
class ExplainChargeHandler:
    """Provide details about a specific transaction."""

    transaction_api: TransactionAPI
    name: str = "explain_charge"
    requires_verification: bool = True

    def handle(
        self,
        request: IntentRequest,
        context: ConversationContext,
        observability: ObservabilityContext,
    ) -> IntentResponse:
        transaction_id = request.parameters["transaction_id"]
        details = self.transaction_api.get_transaction(transaction_id=transaction_id)
        message = (
            "This charge was processed by {merchant} on {date} for {amount}. Let me know if you would like to dispute it."
        ).format(
            merchant=details.merchant_name,
            date=details.posted_at.strftime("%d %b %Y"),
            amount=details.amount.display_value,
        )
        return IntentResponse(
            message=message,
            response_type=ResponseType.TEXT,
            data={"transaction": details.model_dump()},
            requires_follow_up=True,
        )
