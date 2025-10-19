"""Transaction data service integration."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Money:
    currency: str
    amount: int

    @property
    def display_value(self) -> str:
        return f"{self.currency} {self.amount / 100:.2f}"


@dataclass
class Transaction:
    transaction_id: str
    posted_at: datetime
    merchant_name: str
    amount: Money
    category: str

    def model_dump(self) -> dict:
        return {
            "transactionId": self.transaction_id,
            "postedAt": self.posted_at.isoformat(),
            "merchantName": self.merchant_name,
            "amount": self.amount.display_value,
            "category": self.category,
        }


class TransactionAPI:
    """Client for retrieving card transaction history."""

    def list_recent(self, *, card_id: str | None, limit: int) -> List[Transaction]:
        now = datetime.utcnow()
        return [
            Transaction(
                transaction_id=f"TXN-{i}",
                posted_at=now,
                merchant_name=f"Merchant {i}",
                amount=Money(currency="USD", amount=1000 * (i + 1)),
                category="general",
            )
            for i in range(limit)
        ]

    def get_transaction(self, *, transaction_id: str) -> Transaction:
        return Transaction(
            transaction_id=transaction_id,
            posted_at=datetime.utcnow(),
            merchant_name="Example Merchant",
            amount=Money(currency="USD", amount=3299),
            category="shopping",
        )
