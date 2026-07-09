from langgraph_course.email_workflow.langsmith.datasets import DATASET_NAME
from langgraph_course.email_workflow.langsmith.evaluation_cases import (
    canonical_evaluation_cases,
    case_lookup,
)
from langgraph_course.email_workflow.langsmith.evaluation_targets import (
    evaluate_end_to_end_case,
    evaluate_pre_review_case,
)


def test_canonical_cases_seed_expected_dataset_shape() -> None:
    cases = canonical_evaluation_cases()

    assert DATASET_NAME == "email-agent-canonical-cases"
    assert len(cases) >= 5
    assert {case.case_id for case in cases} == set(case_lookup())

    example = cases[0].to_example()
    assert "inputs" in example
    assert "outputs" in example
    outputs = example["outputs"]
    assert outputs["expected_draft_nonempty"] is True


def test_pre_review_evaluation_target_reports_bug_ticket_behavior() -> None:
    result = evaluate_pre_review_case(
        {"case_id": "bug_tire_failure"},
        trace_enabled=False,
    )

    assert result["intent"] == "bug"
    assert result["urgency"] == "critical"
    assert result["interrupted"] is True
    assert result["bug_ticket_created"] is True
    assert result["draft_response_nonempty"] is True


def test_end_to_end_evaluation_targets_support_approved_and_rejected_paths() -> None:
    approved = evaluate_end_to_end_case(
        {"case_id": "billing_duplicate_charge"},
        decision="approved",
        trace_enabled=False,
    )
    rejected = evaluate_end_to_end_case(
        {"case_id": "billing_duplicate_charge"},
        decision="rejected",
        trace_enabled=False,
    )

    assert approved["final_status"] == "sent"
    assert approved["sent_reply_nonempty"] is True
    assert rejected["final_status"] == "cancelled"
    assert rejected["sent_reply_nonempty"] is False
