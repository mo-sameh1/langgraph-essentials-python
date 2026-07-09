"""Canonical evaluation cases for the email workflow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypedDict
from uuid import UUID, uuid5

from langsmith.schemas import Example

from ..types import EmailClassificationData

DATASET_NAME = "email-agent-canonical-cases"
DATASET_NAMESPACE = UUID("0d6f8cf3-7d83-42b4-a40b-528fdf57e6bf")


class EvaluationExampleInputs(TypedDict):
    """Typed input payload for canonical email-agent examples."""

    case_id: str
    email_id: str
    sender_email: str
    email_content: str


class EvaluationExampleOutputs(TypedDict):
    """Typed expected-output payload for canonical email-agent examples."""

    expected_intent: str
    expected_urgency: str
    expected_requires_review: bool
    expected_interrupt: bool
    expected_bug_ticket: bool
    expected_approved_status: str
    expected_rejected_status: str
    expected_draft_nonempty: bool
    expected_sent_reply_nonempty_if_sent: bool


class EvaluationExamplePayload(TypedDict):
    """Typed LangSmith example payload used for dataset seeding."""

    inputs: EvaluationExampleInputs
    outputs: EvaluationExampleOutputs
    metadata: dict[str, str]


@dataclass(frozen=True)
class EmailWorkflowEvaluationCase:
    """Canonical evaluation case used for dataset seeding and offline evaluation."""

    case_id: str
    sender_email: str
    email_content: str
    classification: EmailClassificationData
    draft_response: str
    requires_review: bool
    expects_bug_ticket: bool
    approved_response: str | None = None
    approved_final_status: Literal["sent", "cancelled"] = "sent"
    rejected_final_status: Literal["sent", "cancelled"] = "cancelled"

    @property
    def email_id(self) -> str:
        return f"eval-{self.case_id}"

    def to_example(self) -> EvaluationExamplePayload:
        """Return a LangSmith-compatible example payload."""

        payload: EvaluationExamplePayload = {
            "inputs": {
                "case_id": self.case_id,
                "email_id": self.email_id,
                "sender_email": self.sender_email,
                "email_content": self.email_content,
            },
            "outputs": {
                "expected_intent": self.classification["intent"],
                "expected_urgency": self.classification["urgency"],
                "expected_requires_review": self.requires_review,
                "expected_interrupt": self.requires_review,
                "expected_bug_ticket": self.expects_bug_ticket,
                "expected_approved_status": self.approved_final_status,
                "expected_rejected_status": self.rejected_final_status,
                "expected_draft_nonempty": True,
                "expected_sent_reply_nonempty_if_sent": True,
            },
            "metadata": {"case_id": self.case_id},
        }
        return payload

    def to_local_example(self) -> Example:
        """Return an in-memory Example object for local-only evaluation."""

        payload = self.to_example()
        return Example(
            id=uuid5(DATASET_NAMESPACE, f"{DATASET_NAME}:{self.case_id}"),
            dataset_id=DATASET_NAMESPACE,
            inputs=payload["inputs"],
            outputs=payload["outputs"],
            metadata=payload["metadata"],
        )


def canonical_evaluation_cases() -> list[EmailWorkflowEvaluationCase]:
    """Return the curated email-agent evaluation set."""

    return [
        EmailWorkflowEvaluationCase(
            case_id="question_sale",
            sender_email="customer@example.com",
            email_content="Can you tell me how long the sale is on?",
            classification={
                "intent": "question",
                "urgency": "low",
                "topic": "sale/promotion inquiry",
                "summary": "Customer wants to know when the current sale ends.",
            },
            draft_response=(
                "Thanks for reaching out. The current promotion is scheduled through "
                "the weekend, though sale windows may vary by region."
            ),
            requires_review=False,
            expects_bug_ticket=False,
            approved_final_status="sent",
            rejected_final_status="sent",
        ),
        EmailWorkflowEvaluationCase(
            case_id="billing_duplicate_charge",
            sender_email="customer@example.com",
            email_content="I was charged twice for my subscription and need help today.",
            classification={
                "intent": "billing",
                "urgency": "high",
                "topic": "duplicate subscription charge",
                "summary": (
                    "Customer reports a duplicate subscription charge and wants "
                    "urgent help."
                ),
            },
            draft_response=(
                "Thank you for flagging this. We are reviewing the duplicate charge now "
                "and will update you shortly."
            ),
            approved_response=(
                "We reviewed the duplicate charge, escalated it to billing, and will "
                "update you shortly."
            ),
            requires_review=True,
            expects_bug_ticket=False,
        ),
        EmailWorkflowEvaluationCase(
            case_id="bug_tire_failure",
            sender_email="customer@example.com",
            email_content="The tire will not stay attached to the car after the update.",
            classification={
                "intent": "bug",
                "urgency": "critical",
                "topic": "tire attachment system failure after update",
                "summary": "Vehicle tire does not remain attached after a software update.",
            },
            draft_response=(
                "We opened a priority defect ticket and escalated your safety issue "
                "immediately."
            ),
            approved_response=(
                "We opened a priority defect ticket and escalated your safety issue "
                "immediately."
            ),
            requires_review=True,
            expects_bug_ticket=True,
        ),
        EmailWorkflowEvaluationCase(
            case_id="feature_color_request",
            sender_email="vip@example.com",
            email_content="Do you have the product in green yet?",
            classification={
                "intent": "feature",
                "urgency": "low",
                "topic": "product color availability",
                "summary": "Customer asks whether a new product color is available.",
            },
            draft_response=(
                "We recommend checking live inventory before we promise color "
                "availability, and we can notify you if green returns."
            ),
            requires_review=False,
            expects_bug_ticket=False,
            approved_final_status="sent",
            rejected_final_status="sent",
        ),
        EmailWorkflowEvaluationCase(
            case_id="complex_enterprise_escalation",
            sender_email="vip@example.com",
            email_content="We need a custom enterprise arrangement for our renewal.",
            classification={
                "intent": "complex",
                "urgency": "medium",
                "topic": "enterprise renewal arrangement",
                "summary": "Customer requests a custom enterprise renewal arrangement.",
            },
            draft_response=(
                "Thanks for outlining your renewal needs. We are routing this to a "
                "specialist so we can respond with the right enterprise guidance."
            ),
            approved_response=(
                "We reviewed your renewal request and are routing it to a specialist "
                "for enterprise-specific follow-up."
            ),
            requires_review=True,
            expects_bug_ticket=False,
        ),
    ]


def case_lookup() -> dict[str, EmailWorkflowEvaluationCase]:
    """Return the canonical cases keyed by case id."""

    return {case.case_id: case for case in canonical_evaluation_cases()}


def local_examples() -> list[Example]:
    """Return canonical examples as in-memory LangSmith Example objects."""

    return [case.to_local_example() for case in canonical_evaluation_cases()]


__all__ = [
    "DATASET_NAME",
    "EmailWorkflowEvaluationCase",
    "canonical_evaluation_cases",
    "case_lookup",
    "local_examples",
]
