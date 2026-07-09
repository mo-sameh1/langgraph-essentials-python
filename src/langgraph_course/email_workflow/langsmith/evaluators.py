"""Deterministic evaluators for the email workflow LangSmith experiments."""

from __future__ import annotations

from typing import Any, Literal

from langsmith.schemas import Example, Run


def intent_match(run: Run, example: Example) -> dict[str, Any]:
    outputs = _require_run_outputs(run)
    reference_outputs = _require_example_outputs(example)
    return _boolean_score(
        key="intent_match",
        value=outputs["intent"] == reference_outputs["expected_intent"],
    )


def urgency_match(run: Run, example: Example) -> dict[str, Any]:
    outputs = _require_run_outputs(run)
    reference_outputs = _require_example_outputs(example)
    return _boolean_score(
        key="urgency_match",
        value=outputs["urgency"] == reference_outputs["expected_urgency"],
    )


def interrupt_match(run: Run, example: Example) -> dict[str, Any]:
    outputs = _require_run_outputs(run)
    reference_outputs = _require_example_outputs(example)
    return _boolean_score(
        key="interrupt_match",
        value=outputs["interrupted"] == reference_outputs["expected_interrupt"],
    )


def review_requirement_match(run: Run, example: Example) -> dict[str, Any]:
    outputs = _require_run_outputs(run)
    reference_outputs = _require_example_outputs(example)
    return _boolean_score(
        key="review_requirement_match",
        value=outputs["requires_review"] == reference_outputs["expected_requires_review"],
    )


def bug_ticket_match(run: Run, example: Example) -> dict[str, Any]:
    outputs = _require_run_outputs(run)
    reference_outputs = _require_example_outputs(example)
    return _boolean_score(
        key="bug_ticket_match",
        value=outputs["bug_ticket_created"] == reference_outputs["expected_bug_ticket"],
    )


def draft_response_nonempty(run: Run, example: Example) -> dict[str, Any]:
    outputs = _require_run_outputs(run)
    reference_outputs = _require_example_outputs(example)
    return _boolean_score(
        key="draft_response_nonempty",
        value=outputs["draft_response_nonempty"] == reference_outputs["expected_draft_nonempty"],
    )


def final_status_match(
    run: Run,
    example: Example,
    *,
    decision: Literal["approved", "rejected"],
) -> dict[str, Any]:
    outputs = _require_run_outputs(run)
    reference_outputs = _require_example_outputs(example)
    expected_key = (
        "expected_approved_status"
        if decision == "approved"
        else "expected_rejected_status"
    )
    return _boolean_score(
        key=f"final_status_match_{decision}",
        value=outputs["final_status"] == reference_outputs[expected_key],
    )


def sent_reply_nonempty_if_sent(run: Run, example: Example) -> dict[str, Any]:
    outputs = _require_run_outputs(run)
    reference_outputs = _require_example_outputs(example)
    expected = reference_outputs["expected_sent_reply_nonempty_if_sent"]
    if outputs["final_status"] != "sent":
        return _boolean_score(key="sent_reply_nonempty_if_sent", value=True)
    return _boolean_score(
        key="sent_reply_nonempty_if_sent",
        value=outputs["sent_reply_nonempty"] == expected,
    )


def _boolean_score(*, key: str, value: bool) -> dict[str, Any]:
    return {"key": key, "score": value}


def _require_run_outputs(run: Run) -> dict[str, Any]:
    if run.outputs is None:
        raise ValueError("Evaluation run outputs are missing.")
    return run.outputs


def _require_example_outputs(example: Example) -> dict[str, Any]:
    if example.outputs is None:
        raise ValueError("Evaluation reference outputs are missing.")
    return example.outputs


__all__ = [
    "bug_ticket_match",
    "draft_response_nonempty",
    "final_status_match",
    "intent_match",
    "interrupt_match",
    "review_requirement_match",
    "sent_reply_nonempty_if_sent",
    "urgency_match",
]
