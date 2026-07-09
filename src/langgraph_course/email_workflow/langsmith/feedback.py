"""Helpers for attaching human review feedback to LangSmith traces."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol
from uuid import UUID

from ..types import ReviewDecision
from .client import build_langsmith_client
from .config import EmailWorkflowLangSmithConfig, get_langsmith_config
from .metadata import WORKFLOW_NAME

REVIEW_FEEDBACK_KEY = "human_review_outcome"

RunIdentifier = str | UUID


@dataclass(frozen=True)
class LangSmithRunReference:
    """Trace identifiers needed to attach feedback to a recorded run."""

    run_id: RunIdentifier | None
    trace_id: RunIdentifier | None

    @property
    def ready(self) -> bool:
        """Return whether both identifiers are available."""

        return self.run_id is not None and self.trace_id is not None


@dataclass(frozen=True)
class ReviewFeedbackPayload:
    """Structured feedback fields sent to LangSmith."""

    key: str
    score: bool
    value: str
    comment: str
    correction: dict[str, Any] | None
    source_info: dict[str, Any]
    extra: dict[str, Any]


class FeedbackClientLike(Protocol):
    """Minimal client surface needed for posting feedback."""

    def create_feedback(self, **kwargs: Any) -> Any:
        """Create one feedback record in LangSmith."""
        ...


def build_review_feedback_payload(
    *,
    state: Mapping[str, Any],
    decision: ReviewDecision,
    review_outcome: str,
    thread_id: str,
) -> ReviewFeedbackPayload:
    """Build a stable feedback payload for a human review decision."""

    classification = state.get("classification")
    edited_response = decision.get("edited_response")
    correction: dict[str, Any] | None = None
    if edited_response:
        correction = {"sent_reply": edited_response}
    return ReviewFeedbackPayload(
        key=REVIEW_FEEDBACK_KEY,
        score=review_outcome != "rejected",
        value=review_outcome,
        comment=_review_comment(review_outcome),
        correction=correction,
        source_info={
            "workflow_name": WORKFLOW_NAME,
            "decision_source": "human_review",
            "phase": "resume_review",
            "thread_id": thread_id,
        },
        extra={
            "email_id": state.get("email_id"),
            "intent": _lookup_nested_value(classification, "intent"),
            "urgency": _lookup_nested_value(classification, "urgency"),
            "final_status": state.get("sent_status"),
            "bug_ticket_created": state.get("ticket_id") is not None,
            "approved": decision.get("approved", False),
            "edited_response_present": edited_response is not None,
        },
    )


def log_review_feedback(
    *,
    run_reference: LangSmithRunReference,
    state: Mapping[str, Any],
    decision: ReviewDecision,
    review_outcome: str,
    thread_id: str,
    config: EmailWorkflowLangSmithConfig | None = None,
    enabled: bool | None = None,
    client: FeedbackClientLike | None = None,
) -> bool:
    """Attach review feedback when LangSmith tracing is active."""

    resolved_config = config or get_langsmith_config()
    if enabled is None:
        feedback_enabled = resolved_config.tracing_active
    else:
        feedback_enabled = enabled and resolved_config.api_key_present
    if not feedback_enabled or not run_reference.ready:
        return False
    resolved_client = client or build_langsmith_client(resolved_config)
    if resolved_client is None:
        return False
    payload = build_review_feedback_payload(
        state=state,
        decision=decision,
        review_outcome=review_outcome,
        thread_id=thread_id,
    )
    try:
        resolved_client.create_feedback(
            run_id=run_reference.run_id,
            trace_id=run_reference.trace_id,
            key=payload.key,
            score=payload.score,
            value=payload.value,
            correction=payload.correction,
            comment=payload.comment,
            source_info=payload.source_info,
            extra=payload.extra,
        )
    except Exception:
        return False
    return True


def _review_comment(review_outcome: str) -> str:
    if review_outcome == "edited":
        return "Human reviewer edited the drafted response before it was sent."
    if review_outcome == "rejected":
        return "Human reviewer rejected the drafted response."
    return "Human reviewer approved the drafted response."


def _lookup_nested_value(
    mapping: Mapping[str, Any] | Any,
    key: str,
) -> Any:
    if isinstance(mapping, Mapping):
        return mapping.get(key)
    return None


__all__ = [
    "REVIEW_FEEDBACK_KEY",
    "LangSmithRunReference",
    "ReviewFeedbackPayload",
    "build_review_feedback_payload",
    "log_review_feedback",
]
