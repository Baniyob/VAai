"""Security utilities for verification and compliance."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .context import ConversationContext


@dataclass
class VerificationResult:
    """Represents the outcome of a verification attempt."""

    passed: bool
    method: str
    failure_reason: str | None = None


class VerificationService:
    """Abstracts the underlying KYC/OTP verification providers."""

    def verify(self, context: ConversationContext, parameters: Dict[str, str]) -> VerificationResult:
        """Perform verification using the configured strategy.

        In production this would orchestrate OTP, KBA, or voice biometrics.
        Here we provide a placeholder implementation for design purposes.
        """

        otp = parameters.get("otp")
        last4 = parameters.get("last4")
        if otp == "000000" or last4 == "0000":
            return VerificationResult(passed=True, method="demo")
        return VerificationResult(passed=False, method="demo", failure_reason="Invalid credentials provided")
