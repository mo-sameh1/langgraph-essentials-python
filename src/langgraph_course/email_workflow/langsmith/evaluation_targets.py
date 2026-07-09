"""Reusable evaluation targets for the email workflow."""

from __future__ import annotations

from typing import Any, Literal

from langgraph.checkpoint.memory import InMemorySaver

from .. import build_email_workflow, create_default_services
from ..helpers import require_classification
from ..services import EmailWorkflowServices
from ..session import EmailWorkflowSession
from .evaluation_cases import EmailWorkflowEvaluationCase, case_lookup


def build_evaluation_services() -> EmailWorkflowServices:
    """Create the real application services used for evaluation runs."""

    return create_default_services()


def evaluate_pre_review_case(
    inputs: dict[str, Any],
    *,
    trace_enabled: bool | None = None,
) -> dict[str, Any]:
    """Evaluate classification and routing behavior before review decisions."""

    case = _case_from_inputs(inputs)
    session = _build_evaluation_session(thread_id=f"{case.case_id}-pre-review")
    result = session.start(
        email_content=case.email_content,
        sender_email=case.sender_email,
        email_id=case.email_id,
        source="eval",
        trace_enabled=trace_enabled,
    )
    classification = require_classification(result)
    return {
        "intent": classification["intent"],
        "urgency": classification["urgency"],
        "interrupted": "__interrupt__" in result,
        "requires_review": "__interrupt__" in result,
        "bug_ticket_created": bool(result.get("ticket_id")),
        "draft_response_nonempty": bool(result.get("draft_response")),
        "final_status": result.get("sent_status"),
        "sent_reply_nonempty": bool(result.get("sent_reply")),
    }


def evaluate_end_to_end_case(
    inputs: dict[str, Any],
    *,
    decision: Literal["approved", "rejected"],
    trace_enabled: bool | None = None,
) -> dict[str, Any]:
    """Evaluate the workflow through auto-resume policies."""

    case = _case_from_inputs(inputs)
    session = _build_evaluation_session(thread_id=f"{case.case_id}-{decision}")
    first_result = session.start(
        email_content=case.email_content,
        sender_email=case.sender_email,
        email_id=case.email_id,
        source="eval",
        trace_enabled=trace_enabled,
    )
    final_result = first_result
    if "__interrupt__" in first_result:
        final_result = session.resume_review(
            approved=decision == "approved",
            edited_response=_edited_response_for(case, decision),
            source="eval",
            trace_enabled=trace_enabled,
        )
    classification = require_classification(first_result)
    return {
        "intent": classification["intent"],
        "urgency": classification["urgency"],
        "interrupted": "__interrupt__" in first_result,
        "requires_review": "__interrupt__" in first_result,
        "bug_ticket_created": bool(first_result.get("ticket_id")),
        "draft_response_nonempty": bool(first_result.get("draft_response")),
        "final_status": final_result.get("sent_status"),
        "sent_reply_nonempty": bool(final_result.get("sent_reply")),
    }


def _build_evaluation_session(*, thread_id: str) -> EmailWorkflowSession:
    services = build_evaluation_services()
    graph = build_email_workflow(services, checkpointer=InMemorySaver())
    return EmailWorkflowSession(graph, thread_id=thread_id)


def _case_from_inputs(inputs: dict[str, Any]) -> EmailWorkflowEvaluationCase:
    case_id = str(inputs["case_id"])
    return case_lookup()[case_id]


def _edited_response_for(
    case: EmailWorkflowEvaluationCase,
    decision: Literal["approved", "rejected"],
) -> str | None:
    if decision == "approved":
        return case.approved_response
    return None


__all__ = [
    "build_evaluation_services",
    "evaluate_end_to_end_case",
    "evaluate_pre_review_case",
]
