"""Deterministic model stubs used for LangSmith evaluation workflows."""

from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage

from .evaluation_cases import EmailWorkflowEvaluationCase, case_lookup


class ScriptedStructuredRunnable:
    """Return a structured classification for the matched evaluation case."""

    def __init__(self, cases: dict[str, EmailWorkflowEvaluationCase], schema: type) -> None:
        self.cases = cases
        self.schema = schema

    def invoke(self, input: str) -> Any:
        case = _match_case(input, self.cases)
        return self.schema(**case.classification)


class ScriptedEmailWorkflowModel:
    """Deterministic chat model for cheap, stable evaluation runs."""

    def __init__(self, cases: dict[str, EmailWorkflowEvaluationCase] | None = None) -> None:
        self.cases = cases or case_lookup()

    def with_structured_output(
        self,
        schema: type,
        *,
        method: str = "json_schema",
        include_raw: bool = False,
        **kwargs: Any,
    ) -> ScriptedStructuredRunnable:
        del method, include_raw, kwargs
        return ScriptedStructuredRunnable(self.cases, schema)

    def invoke(self, input: str) -> AIMessage:
        case = _match_case(input, self.cases)
        return AIMessage(content=case.draft_response)


def _match_case(
    prompt: str,
    cases: dict[str, EmailWorkflowEvaluationCase],
) -> EmailWorkflowEvaluationCase:
    for case in cases.values():
        if case.email_content in prompt:
            return case
    raise ValueError("Could not map prompt to a canonical evaluation case.")


__all__ = ["ScriptedEmailWorkflowModel", "ScriptedStructuredRunnable"]
