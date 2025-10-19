# VAai Architecture Overview

## Vision

VAai is a bank-grade conversational AI designed to resolve payment-card enquiries autonomously
while adhering to stringent security and regulatory requirements. The solution targets >80%
first-contact resolution across card lifecycle, transaction support, and fraud scenarios.

## System Layers

### 1. Omni-Channel Front-End
- **Channels:** Voice (SIP/Twilio/Genesys), Web chat, Mobile in-app chat.
- **Responsibilities:** Speech-to-text, text-to-speech, intent invocation, fallback to live agent.
- **Security:** PCI-DSS masking, TLS encryption, configurable session timeouts.

### 2. Agent Orchestration Engine
- **Intent Understanding:** NLU + prompt-engineered LLM orchestrator with guardrails.
- **State Management:** Maintains `ConversationContext` per session, including verification status,
  card focus, and case metadata.
- **Policy Enforcement:** Verifies identity before sensitive intents, applies compliance guardrails,
  triggers fraud workflows.
- **Observability:** Emits structured traces and analytics events for dashboards and RLHF feedback.

### 3. Domain Intents & Workflows
- **Verification:** OTP, knowledge-based questions, voice biometrics.
- **Card Management:** Activation, freeze/reissue, limit adjustments, travel notifications.
- **Transaction Support:** Recent activity, charge explanations, dispute initiation, refund tracking.
- **Personalized Offers:** Loyalty upgrades, card recommendations, limit increase suggestions.
- **Escalation:** Prioritised routing to human teams with case summaries.

### 4. Back-End Integrations
- Card Management API (freeze, activate, replace)
- Transaction Services (history, disputes, refunds)
- CRM (client tier, preferences, VIP flags)
- Authentication Service (OTP, KYC)
- Fraud Detection Engine (risk scores, behaviour anomalies)
- Knowledge Base (policy updates via RAG)
- Ticketing/Case Management (ServiceNow, Salesforce)

## Data Flow

1. Client joins via voice/text channel; channel adapter creates session and collects identifiers.
2. `VAaiAgent` authenticates using configured `AuthenticationProvider` before privileged intents.
3. Agent routes intents through `WorkflowRouter` to domain handlers.
4. Handlers call integration clients to perform actions or retrieve data.
5. Responses are formatted with redaction rules and delivered to the client.
6. Observability layer logs every turn, feeding analytics dashboards, fraud monitors, and RL loops.
7. When escalation is required, `escalate_to_human` creates a structured ticket for human agents.

## Security & Compliance

- Tokenized storage of card identifiers; transcripts auto-redacted before persistence.
- Role-based access between microservices; least privilege enforced via OAuth scopes.
- Continuous verification (device fingerprint, behaviour analytics) to detect suspicious activity.
- Audit-ready logging aligned with PCI-DSS, GDPR, and KYC guidelines.

## Learning & Improvement

- RLHF feedback loops capture human agent corrections and customer surveys.
- Intent misclassification tracker prompts retraining when thresholds exceed tolerance.
- A/B experimentation harness for testing prompt templates and workflow variants.

## Deployment

- Containerised microservices deployed on Kubernetes with blue/green rollouts.
- Edge nodes handle telephony and STT/TTS to maintain low latency.
- Dedicated vault for secrets and encryption keys.

## Metrics & Monitoring

- **Average Handle Time (AHT):** measured per channel and intent.
- **First Contact Resolution (FCR):** tracked via CRM disposition codes.
- **Client Satisfaction (CSAT):** collected post-interaction surveys.
- **Escalation Rate:** monitored to identify automation gaps.
- **Compliance Accuracy:** spot-checked via automated policy audits.
- **Latency:** SLO of <1.5s for text responses, <400ms streaming for voice segments.

## Roadmap Highlights

- Integrate adaptive authentication scoring.
- Launch proactive fraud alerts with conversational outreach.
- Expand multilingual support with locale-specific compliance prompts.
- Deploy agent-assist hybrid mode for complex corporate accounts.
