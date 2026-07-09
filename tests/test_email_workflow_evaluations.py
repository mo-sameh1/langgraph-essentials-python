from __future__ import annotations

from typing import Any

import pytest
from langchain_core.messages import AIMessage

from langgraph_course.email_workflow import EmailWorkflowServices, KnowledgeBase
from langgraph_course.email_workflow.langsmith.datasets import DATASET_NAME
from langgraph_course.email_workflow.langsmith.evaluation_cases import (
    canonical_evaluation_cases,
    case_lookup,
)
from langgraph_course.email_workflow.langsmith.evaluation_targets import (
    evaluate_end_to_end_case,
    evaluate_pre_review_case,
)
from langgraph_course.email_workflow.services import (
    default_customer_profiles,
    default_documents,
)


class RoutedScriptedEvaluationModel:
    def __init__(self, *, cases: dict[str, Any]) -> None:
        self.cases = cases

    def with_structured_output(
        self,
        schema: type,
        *,
        method: str = "json_schema",
        include_raw: bool = False,
        **kwargs: Any,
    ) -> Any:
        del method, include_raw, kwargs

        class _Runnable:
            def __init__(self, cases: dict[str, Any], schema: type) -> None:
                self.cases = cases
                self.schema = schema

            def invoke(self, input: str) -> Any:
                case = _match_case(input, self.cases)
                return self.schema(**case.classification)

        return _Runnable(self.cases, schema)

    def invoke(self, input: str) -> AIMessage:
        case = _match_case(input, self.cases)
        return AIMessage(content=case.draft_response)


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


def test_pre_review_evaluation_target_reports_bug_ticket_behavior(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_scripted_services(monkeypatch)
    result = evaluate_pre_review_case(
        {"case_id": "bug_tire_failure"},
        trace_enabled=False,
    )

    assert result["intent"] == "bug"
    assert result["urgency"] == "critical"
    assert result["interrupted"] is True
    assert result["bug_ticket_created"] is True
    assert result["draft_response_nonempty"] is True


def test_end_to_end_evaluation_targets_support_approved_and_rejected_paths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_scripted_services(monkeypatch)
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


def _patch_scripted_services(monkeypatch: pytest.MonkeyPatch) -> None:
    cases = case_lookup()

    def _factory() -> EmailWorkflowServices:
        return EmailWorkflowServices(
            llm=RoutedScriptedEvaluationModel(cases=cases),
            knowledge_base=KnowledgeBase(documents=default_documents()),
            customer_profiles=default_customer_profiles(),
        )

    monkeypatch.setattr(
        "langgraph_course.email_workflow.langsmith.evaluation_targets.build_evaluation_services",
        _factory,
    )


def _match_case(prompt: str, cases: dict[str, Any]) -> Any:
    for case in cases.values():
        if case.email_content in prompt:
            return case
    raise AssertionError("Could not map prompt to evaluation case.")
