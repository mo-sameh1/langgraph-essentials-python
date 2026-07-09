from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from langgraph_course.email_workflow.langsmith import (
    REVIEW_FEEDBACK_KEY,
    EmailWorkflowLangSmithConfig,
    LangSmithRunReference,
    build_review_feedback_payload,
    log_review_feedback,
)
from langgraph_course.email_workflow.types import ReviewDecision


def test_build_review_feedback_payload_for_edited_review() -> None:
    payload = build_review_feedback_payload(
        state={
            "email_id": "email-123",
            "classification": {"intent": "billing", "urgency": "high"},
            "ticket_id": "ticket-9",
            "sent_status": "sent",
        },
        decision={"approved": True, "edited_response": "Updated response"},
        review_outcome="edited",
        thread_id="thread-123",
    )

    assert payload.key == REVIEW_FEEDBACK_KEY
    assert payload.score is True
    assert payload.value == "edited"
    assert payload.correction == {"sent_reply": "Updated response"}
    assert payload.source_info["thread_id"] == "thread-123"
    assert payload.extra["email_id"] == "email-123"
    assert payload.extra["intent"] == "billing"
    assert payload.extra["urgency"] == "high"
    assert payload.extra["bug_ticket_created"] is True
    assert payload.extra["edited_response_present"] is True


def test_log_review_feedback_is_noop_without_trace_identifiers() -> None:
    client = RecordingClient()

    logged = log_review_feedback(
        run_reference=LangSmithRunReference(run_id=None, trace_id=None),
        state={"email_id": "email-123"},
        decision={"approved": True},
        review_outcome="approved",
        thread_id="thread-123",
        config=make_config(),
        enabled=True,
        client=client,
    )

    assert logged is False
    assert client.calls == []


def test_log_review_feedback_posts_expected_payload() -> None:
    client = RecordingClient()
    decision: ReviewDecision = {"approved": False}

    logged = log_review_feedback(
        run_reference=LangSmithRunReference(
            run_id="run-123",
            trace_id="trace-123",
        ),
        state={
            "email_id": "email-123",
            "classification": {"intent": "bug", "urgency": "critical"},
            "sent_status": "cancelled",
        },
        decision=decision,
        review_outcome="rejected",
        thread_id="thread-123",
        config=make_config(),
        enabled=True,
        client=client,
    )

    assert logged is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert call["run_id"] == "run-123"
    assert call["trace_id"] == "trace-123"
    assert call["key"] == REVIEW_FEEDBACK_KEY
    assert call["score"] is False
    assert call["value"] == "rejected"
    assert call["extra"]["final_status"] == "cancelled"


def test_log_review_feedback_swallows_client_errors() -> None:
    client = FailingClient()

    logged = log_review_feedback(
        run_reference=LangSmithRunReference(
            run_id="run-123",
            trace_id="trace-123",
        ),
        state={"email_id": "email-123"},
        decision={"approved": True},
        review_outcome="approved",
        thread_id="thread-123",
        config=make_config(),
        enabled=True,
        client=client,
    )

    assert logged is False


def make_config() -> EmailWorkflowLangSmithConfig:
    return EmailWorkflowLangSmithConfig(
        tracing_enabled=True,
        api_key="test-key",
        project="langgraph-essentials-email-agent",
        endpoint="https://api.smith.langchain.com",
        workspace_id=None,
    )


@dataclass
class RecordingClient:
    calls: list[dict[str, Any]] = field(default_factory=list)

    def create_feedback(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(kwargs)
        return kwargs


class FailingClient:
    def create_feedback(self, **kwargs: Any) -> dict[str, Any]:
        raise RuntimeError("feedback unavailable")
