"""Session wrapper for the email workflow graph."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import cast

from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command

from .langsmith import (
    LangSmithRunReference,
    build_workflow_metadata,
    build_workflow_tags,
    log_review_feedback,
    summarize_workflow_outputs,
    workflow_root_trace,
)
from .types import EmailInput, EmailWorkflowState, ReviewDecision


@dataclass(frozen=True)
class EmailWorkflowSession:
    """Small session wrapper that keeps the thread id attached to the graph."""

    graph: CompiledStateGraph
    thread_id: str

    @property
    def config(self) -> RunnableConfig:
        return {"configurable": {"thread_id": self.thread_id}}

    def start(
        self,
        *,
        email_content: str,
        sender_email: str,
        email_id: str | None = None,
        source: str = "manual",
        trace_enabled: bool | None = None,
    ) -> EmailWorkflowState:
        """Start a new workflow run for one email."""

        initial_state: EmailInput = {
            "email_content": email_content,
            "sender_email": sender_email,
            "email_id": email_id or f"email-{uuid.uuid4().hex[:8]}",
        }
        with workflow_root_trace(
            name="email_workflow.start",
            inputs=initial_state,
            metadata=build_workflow_metadata(
                state=initial_state,
                thread_id=self.thread_id,
                source=source,
                phase="start",
            ),
            tags=build_workflow_tags(
                state=initial_state,
                source=source,
                phase="start",
            ),
            enabled=trace_enabled,
        ) as run:
            result = self.graph.invoke(initial_state, self.config)
            run.add_metadata(
                build_workflow_metadata(
                    state=result,
                    thread_id=self.thread_id,
                    source=source,
                    phase="start",
                )
            )
            run.add_tags(
                build_workflow_tags(
                    state=result,
                    source=source,
                    phase="start",
                )
            )
            run.end(outputs=summarize_workflow_outputs(result))
            return cast(EmailWorkflowState, result)

    def resume_review(
        self,
        *,
        approved: bool,
        edited_response: str | None = None,
        source: str = "manual",
        trace_enabled: bool | None = None,
    ) -> EmailWorkflowState:
        """Resume an interrupted review step."""

        decision: ReviewDecision = {"approved": approved}
        if edited_response:
            decision["edited_response"] = edited_response
        review_outcome = _determine_review_outcome(
            approved=approved,
            edited_response=edited_response,
        )
        with workflow_root_trace(
            name="email_workflow.resume_review",
            inputs=decision,
            metadata=build_workflow_metadata(
                state=decision,
                thread_id=self.thread_id,
                source=source,
                phase="resume_review",
                review_outcome=review_outcome,
            ),
            tags=build_workflow_tags(
                state=decision,
                source=source,
                phase="resume_review",
                review_outcome=review_outcome,
            ),
            enabled=trace_enabled,
        ) as run:
            result = self.graph.invoke(Command(resume=decision), self.config)
            run.add_metadata(
                build_workflow_metadata(
                    state=result,
                    thread_id=self.thread_id,
                    source=source,
                    phase="resume_review",
                    review_outcome=review_outcome,
                )
            )
            run.add_tags(
                build_workflow_tags(
                    state=result,
                    source=source,
                    phase="resume_review",
                    review_outcome=review_outcome,
                )
            )
            run.end(outputs=summarize_workflow_outputs(result))
            run_reference = LangSmithRunReference(
                run_id=run.id,
                trace_id=run.trace_id,
            )
        typed_result = cast(EmailWorkflowState, result)
        log_review_feedback(
            run_reference=run_reference,
            state=typed_result,
            decision=decision,
            review_outcome=review_outcome,
            thread_id=self.thread_id,
            enabled=trace_enabled,
        )
        return typed_result


def _determine_review_outcome(
    *,
    approved: bool,
    edited_response: str | None,
) -> str:
    if not approved:
        return "rejected"
    if edited_response:
        return "edited"
    return "approved"


__all__ = ["EmailWorkflowSession"]
