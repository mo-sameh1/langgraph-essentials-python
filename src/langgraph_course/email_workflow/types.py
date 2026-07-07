"""Shared types and model contracts for the email workflow application."""

from __future__ import annotations

from typing import Any, Literal, NotRequired, Protocol, Required, TypedDict, cast

from langchain_core.messages import AIMessage
from pydantic import BaseModel, Field


class EmailClassificationData(TypedDict):
    """State-friendly email classification payload."""

    intent: Literal["question", "bug", "billing", "feature", "complex"]
    urgency: Literal["low", "medium", "high", "critical"]
    topic: str
    summary: str


class CustomerHistoryData(TypedDict):
    """Minimal customer profile used during drafting."""

    tier: str
    region: str
    previous_tickets: int


class ReviewDecision(TypedDict, total=False):
    """Human review payload used to resume interrupted runs."""

    approved: bool
    edited_response: str


class ReviewRequest(TypedDict):
    """Interrupt payload shown to the human reviewer."""

    email_id: str
    original_email: str
    draft_response: str
    urgency: str
    intent: str
    action: str


class EmailWorkflowState(TypedDict, total=False):
    """Shared LangGraph state for the email workflow."""

    email_content: Required[str]
    sender_email: Required[str]
    email_id: Required[str]
    normalized_email: NotRequired[str]
    classification: NotRequired[EmailClassificationData]
    ticket_id: NotRequired[str]
    search_results: NotRequired[list[str]]
    draft_response: NotRequired[str]
    sent_reply: NotRequired[str]
    sent_status: NotRequired[str]


class EmailInput(TypedDict):
    """Required inputs when starting a new workflow thread."""

    email_content: str
    sender_email: str
    email_id: str


class EmailClassificationModel(BaseModel):
    """Structured output schema used by the LLM."""

    intent: Literal["question", "bug", "billing", "feature", "complex"]
    urgency: Literal["low", "medium", "high", "critical"]
    topic: str = Field(min_length=1)
    summary: str = Field(min_length=1)

    def to_state(self) -> EmailClassificationData:
        """Return a TypedDict-shaped payload for graph state."""

        return cast(EmailClassificationData, self.model_dump())


class StructuredOutputRunnable(Protocol):
    """Subset of the structured-output runnable API used by this app."""

    def invoke(self, input: str) -> BaseModel | dict[str, Any]:
        """Execute the structured output call."""
        ...


class ChatModelLike(Protocol):
    """Subset of the chat model API used by the app."""

    def invoke(self, input: str) -> AIMessage:
        """Generate a chat response."""
        ...

    def with_structured_output(
        self,
        schema: type[BaseModel],
        *,
        method: str = "json_schema",
        include_raw: bool = False,
        **kwargs: Any,
    ) -> StructuredOutputRunnable:
        """Return a runnable that yields structured data."""
        ...


__all__ = [
    "ChatModelLike",
    "CustomerHistoryData",
    "EmailClassificationData",
    "EmailClassificationModel",
    "EmailInput",
    "EmailWorkflowState",
    "ReviewDecision",
    "ReviewRequest",
    "StructuredOutputRunnable",
]
