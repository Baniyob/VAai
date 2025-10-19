"""Core agent orchestration logic for VAai payment-card virtual assistant."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Protocol

from .intents.base import IntentHandler, IntentRequest, IntentResponse
from .monitoring.analytics import AnalyticsCollector
from .monitoring.observability import ObservabilityContext
from .utils.context import ConversationContext
from .workflows.router import WorkflowRouter


class EscalationRequired(Exception):
    """Raised when a request must be escalated to a human agent."""


@dataclass
class AgentConfig:
    """Configuration options for the conversational agent."""

    max_turns: int = 25
    enable_voice_biometrics: bool = True
    enable_rag: bool = True
    enable_fraud_checks: bool = True


class AuthenticationProvider(Protocol):
    """Defines the interface for authenticating callers."""

    def verify_identity(self, context: ConversationContext) -> bool:
        """Return ``True`` if the caller is authenticated."""


@dataclass
class VAaiAgent:
    """High-level orchestrator for handling multi-turn conversations."""

    router: WorkflowRouter
    analytics: AnalyticsCollector
    auth_provider: AuthenticationProvider
    config: AgentConfig = field(default_factory=AgentConfig)

    def handle_turn(self, request: IntentRequest, context: ConversationContext) -> IntentResponse:
        """Process a single conversational turn.

        The orchestrator performs authentication checks, routes the intent to a
        workflow, logs the interaction, and returns the generated response.
        """

        self.analytics.record_event("turn_start", context=context, metadata={"intent": request.intent_name})

        if not context.is_verified and request.intent_name != "verify_client":
            if not self.auth_provider.verify_identity(context):
                self.analytics.record_event("verification_failed", context=context)
                raise EscalationRequired("Unable to verify caller identity.")
            context.is_verified = True

        observability = ObservabilityContext.from_context(context, request)
        self.analytics.bind_trace(observability.trace_id)

        handler = self.router.route(request.intent_name)
        if handler.requires_verification and not context.is_verified:
            raise EscalationRequired("Intent requires verified identity.")

        try:
            response = handler.handle(request=request, context=context, observability=observability)
        except EscalationRequired:
            self.analytics.record_event("escalated", context=context, metadata={"intent": request.intent_name})
            raise
        except Exception as exc:  # noqa: BLE001
            self.analytics.record_error(exc, context=context, metadata={"intent": request.intent_name})
            raise

        self.analytics.record_event(
            "turn_complete",
            context=context,
            metadata={
                "intent": request.intent_name,
                "response_type": response.response_type,
                "requires_follow_up": response.requires_follow_up,
            },
        )

        return response

    def run_conversation(self, requests: List[IntentRequest], context: ConversationContext) -> List[IntentResponse]:
        """Execute a batch of conversational turns for testing or playback."""

        responses: List[IntentResponse] = []
        for turn, request in enumerate(requests, start=1):
            if turn > self.config.max_turns:
                self.analytics.record_event("max_turns_exceeded", context=context)
                break
            response = self.handle_turn(request=request, context=context)
            responses.append(response)
            if response.terminate_session:
                break
        return responses


def create_agent(
    handlers: Dict[str, IntentHandler],
    analytics: AnalyticsCollector,
    auth_provider: AuthenticationProvider,
    config: Optional[AgentConfig] = None,
) -> VAaiAgent:
    """Convenience factory for assembling the virtual agent."""

    router = WorkflowRouter(handlers=handlers)
    return VAaiAgent(router=router, analytics=analytics, auth_provider=auth_provider, config=config or AgentConfig())
