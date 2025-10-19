"""Verification-related intent handlers."""
from __future__ import annotations

from dataclasses import dataclass

from .base import IntentHandler, IntentRequest, IntentResponse, ResponseType
from ..monitoring.observability import ObservabilityContext
from ..utils.context import ConversationContext
from ..utils.security import VerificationService


@dataclass
class VerifyClientHandler:
    """Handle the client verification workflow."""

    verification_service: VerificationService
    name: str = "verify_client"
    requires_verification: bool = False

    def handle(
        self,
        request: IntentRequest,
        context: ConversationContext,
        observability: ObservabilityContext,
    ) -> IntentResponse:
        verification_status = self.verification_service.verify(context=context, parameters=request.parameters)
        context.is_verified = verification_status.passed
        context.verification_attempts += 1

        if verification_status.passed:
            message = "Thank you. I've verified your identity. How can I assist you with your card today?"
        else:
            message = (
                "I couldn't complete the verification just yet. Let's try again or I can connect you with a specialist."
            )

        return IntentResponse(
            message=message,
            response_type=ResponseType.TEXT,
            data={"verification_passed": verification_status.passed},
            requires_follow_up=not verification_status.passed,
        )
