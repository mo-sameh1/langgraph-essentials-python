"""Trace metadata helpers for the email workflow."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

WORKFLOW_NAME = "email-agent"


def build_workflow_metadata(
    *,
    state: Mapping[str, Any],
    thread_id: str,
    source: str,
    phase: str,
    review_outcome: str | None = None,
) -> dict[str, Any]:
    """Build normalized metadata for root workflow traces."""

    metadata: dict[str, Any] = {
        "workflow_name": WORKFLOW_NAME,
        "workflow_source": source,
        "workflow_phase": phase,
        "thread_id": thread_id,
        "email_id": state.get("email_id"),
        "sender_email": state.get("sender_email"),
    }
    classification = state.get("classification")
    if isinstance(classification, Mapping):
        intent = _optional_text(classification.get("intent"))
        urgency = _optional_text(classification.get("urgency"))
        topic = _optional_text(classification.get("topic"))
        if intent is not None:
            metadata["intent"] = intent
        if urgency is not None:
            metadata["urgency"] = urgency
        if topic is not None:
            metadata["topic"] = topic
        if intent is not None and urgency is not None:
            metadata["human_review_required"] = _needs_human_review(
                intent=intent,
                urgency=urgency,
            )
    if review_outcome is not None:
        metadata["review_outcome"] = review_outcome
    if "ticket_id" in state:
        metadata["bug_ticket_created"] = bool(state.get("ticket_id"))
    if "sent_status" in state:
        metadata["sent_status"] = state.get("sent_status")
    if "__interrupt__" in state:
        metadata["interrupted"] = bool(state.get("__interrupt__"))
    return {key: value for key, value in metadata.items() if value is not None}


def build_workflow_tags(
    *,
    state: Mapping[str, Any],
    source: str,
    phase: str,
    review_outcome: str | None = None,
) -> list[str]:
    """Build trace tags for workflow filtering in LangSmith."""

    tags = [
        f"workflow:{WORKFLOW_NAME}",
        f"source:{source}",
        f"phase:{phase}",
    ]
    classification = state.get("classification")
    if isinstance(classification, Mapping):
        intent = _optional_text(classification.get("intent"))
        urgency = _optional_text(classification.get("urgency"))
        if intent is not None:
            tags.append(f"intent:{intent}")
        if urgency is not None:
            tags.append(f"urgency:{urgency}")
        if intent is not None and urgency is not None:
            review_required = _needs_human_review(intent=intent, urgency=urgency)
            tags.append(f"review-required:{str(review_required).lower()}")
    if "ticket_id" in state:
        tags.append(f"bug-ticket:{str(bool(state.get('ticket_id'))).lower()}")
    if review_outcome is not None:
        tags.append(f"review-outcome:{review_outcome}")
    if "sent_status" in state and state.get("sent_status") is not None:
        tags.append(f"sent-status:{state['sent_status']}")
    if "__interrupt__" in state:
        tags.append(f"interrupted:{str(bool(state.get('__interrupt__'))).lower()}")
    return sorted(set(tags))


def summarize_workflow_outputs(state: Mapping[str, Any]) -> dict[str, Any]:
    """Return a compact output payload for root trace visualization."""

    summary = {
        "email_id": state.get("email_id"),
        "intent": None,
        "urgency": None,
        "ticket_id": state.get("ticket_id"),
        "sent_status": state.get("sent_status"),
        "interrupted": bool(state.get("__interrupt__")),
    }
    classification = state.get("classification")
    if isinstance(classification, Mapping):
        summary["intent"] = classification.get("intent")
        summary["urgency"] = classification.get("urgency")
    return summary


def _optional_text(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized or None


def _needs_human_review(*, intent: str, urgency: str) -> bool:
    return urgency in {"high", "critical"} or intent in {"complex", "billing"}


__all__ = [
    "WORKFLOW_NAME",
    "build_workflow_metadata",
    "build_workflow_tags",
    "summarize_workflow_outputs",
]
