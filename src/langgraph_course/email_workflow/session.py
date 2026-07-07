"""Session wrapper for the email workflow graph."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import cast

from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command

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
    ) -> EmailWorkflowState:
        """Start a new workflow run for one email."""

        initial_state: EmailInput = {
            "email_content": email_content,
            "sender_email": sender_email,
            "email_id": email_id or f"email-{uuid.uuid4().hex[:8]}",
        }
        result = self.graph.invoke(initial_state, self.config)
        return cast(EmailWorkflowState, result)

    def resume_review(
        self,
        *,
        approved: bool,
        edited_response: str | None = None,
    ) -> EmailWorkflowState:
        """Resume an interrupted review step."""

        decision: ReviewDecision = {"approved": approved}
        if edited_response:
            decision["edited_response"] = edited_response
        result = self.graph.invoke(Command(resume=decision), self.config)
        return cast(EmailWorkflowState, result)


__all__ = ["EmailWorkflowSession"]
