"""CLI entrypoint for real email-agent LangSmith evaluations."""

from __future__ import annotations

import argparse
from functools import partial
from typing import Any, Literal, cast

from langsmith import evaluate

from .client import build_langsmith_client
from .datasets import DATASET_NAME
from .evaluation_cases import local_examples
from .evaluation_targets import evaluate_end_to_end_case, evaluate_pre_review_case
from .evaluators import (
    bug_ticket_match,
    draft_response_nonempty,
    final_status_match,
    intent_match,
    interrupt_match,
    review_requirement_match,
    sent_reply_nonempty_if_sent,
    urgency_match,
)

EvaluationMode = Literal["pre-review", "approved", "rejected"]


def main() -> int:
    """Run LangSmith evaluations against the real email workflow."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("pre-review", "approved", "rejected", "all"),
        default="all",
    )
    parser.add_argument(
        "--upload-results",
        action="store_true",
        help="Upload the experiment to LangSmith instead of running locally only.",
    )
    parser.add_argument("--dataset-name", default=DATASET_NAME)
    args = parser.parse_args()

    jobs: list[EvaluationMode]
    if args.mode == "all":
        jobs = ["pre-review", "approved", "rejected"]
    else:
        jobs = [cast(EvaluationMode, args.mode)]
    for mode in jobs:
        _run_job(
            mode=mode,
            upload_results=args.upload_results,
            dataset_name=args.dataset_name,
        )
    return 0


def _run_job(
    *,
    mode: EvaluationMode,
    upload_results: bool,
    dataset_name: str,
) -> None:
    if mode == "pre-review":
        target = partial(evaluate_pre_review_case, trace_enabled=upload_results)
        evaluators = [
            intent_match,
            urgency_match,
            interrupt_match,
            review_requirement_match,
            bug_ticket_match,
            draft_response_nonempty,
        ]
    elif mode == "approved":
        target = partial(
            evaluate_end_to_end_case,
            decision="approved",
            trace_enabled=upload_results,
        )
        evaluators = [
            intent_match,
            urgency_match,
            interrupt_match,
            review_requirement_match,
            bug_ticket_match,
            draft_response_nonempty,
            partial(final_status_match, decision="approved"),
            sent_reply_nonempty_if_sent,
        ]
    else:
        target = partial(
            evaluate_end_to_end_case,
            decision="rejected",
            trace_enabled=upload_results,
        )
        evaluators = [
            intent_match,
            urgency_match,
            interrupt_match,
            review_requirement_match,
            bug_ticket_match,
            draft_response_nonempty,
            partial(final_status_match, decision="rejected"),
            sent_reply_nonempty_if_sent,
        ]

    data: Any
    client = None
    if upload_results:
        client = build_langsmith_client()
        if client is None:
            raise RuntimeError("LANGSMITH_API_KEY is required when --upload-results is enabled.")
        data = dataset_name
    else:
        data = local_examples()

    results = evaluate(
        cast(Any, target),
        data=data,
        evaluators=cast(Any, evaluators),
        metadata={
            "workflow_name": "email-agent",
            "evaluation_mode": mode,
            "upload_results": upload_results,
        },
        experiment_prefix=f"email-agent-{mode}",
        upload_results=upload_results,
        client=client,
        blocking=True,
    )
    print(f"Completed {mode} evaluation.")
    print(results)


if __name__ == "__main__":
    raise SystemExit(main())
