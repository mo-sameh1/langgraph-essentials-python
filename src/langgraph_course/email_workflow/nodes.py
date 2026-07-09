"""Node implementations for the email workflow application."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Literal, cast

from langgraph.graph import END
from langgraph.types import Command, interrupt
from pydantic import BaseModel

from .helpers import (
    build_context_sections,
    message_to_text,
    require_classification,
    require_draft_response,
    require_normalized_email,
)
from .prompts import build_classification_prompt, build_response_prompt
from .services import EmailWorkflowServices
from .types import (
    EmailClassificationData,
    EmailClassificationModel,
    EmailWorkflowState,
    ReviewDecision,
    ReviewRequest,
)


class ReadEmailNode:
    """Normalize raw inbound email text."""

    def __call__(self, state: EmailWorkflowState) -> EmailWorkflowState:
        email_content = " ".join(state["email_content"].split())
        email_id = state.get("email_id") or f"email-{uuid.uuid4().hex[:8]}"
        sender_email = state["sender_email"].strip().lower()
        return {
            "email_content": state["email_content"],
            "email_id": email_id,
            "normalized_email": email_content,
            "sender_email": sender_email,
        }


@dataclass(frozen=True)
class IntentClassifierNode:
    """Classify the email using structured output from the LLM."""

    services: EmailWorkflowServices

    def __call__(self, state: EmailWorkflowState) -> EmailWorkflowState:
        structured_llm = self.services.llm.with_structured_output(
            EmailClassificationModel,
            method="json_schema",
        )
        normalized_email = require_normalized_email(state)
        prompt = build_classification_prompt(
            email=normalized_email,
            sender_email=state["sender_email"],
        )
        classification = structured_llm.invoke(prompt)
        if isinstance(classification, EmailClassificationModel):
            payload = classification.to_state()
        elif isinstance(classification, BaseModel):
            payload = cast(EmailClassificationData, classification.model_dump())
        else:
            payload = cast(EmailClassificationData, classification)
        return cast(EmailWorkflowState, {"classification": payload})


@dataclass(frozen=True)
class DocumentationSearchNode:
    """Search course-local reference material for supporting context."""

    services: EmailWorkflowServices

    def __call__(self, state: EmailWorkflowState) -> EmailWorkflowState:
        classification = require_classification(state)
        normalized_email = require_normalized_email(state)
        query = (
            f"{classification['intent']} {classification['topic']} {normalized_email}"
        )
        results = self.services.knowledge_base.search(query)
        return cast(EmailWorkflowState, {"search_results": results})


@dataclass(frozen=True)
class BugTrackingNode:
    """Create a bug ticket only when the classified email describes a product issue."""

    services: EmailWorkflowServices

    def __call__(self, state: EmailWorkflowState) -> EmailWorkflowState:
        classification = require_classification(state)
        if classification["intent"] != "bug":
            return cast(EmailWorkflowState, {})
        summary = f"{classification['topic']}: {classification['summary']}"
        ticket_id = self.services.ticket_registry.create_ticket(summary)
        return cast(EmailWorkflowState, {"ticket_id": ticket_id})


@dataclass(frozen=True)
class ResponseWriterNode:
    """Draft a reply and route to review when the case is sensitive."""

    services: EmailWorkflowServices

    def __call__(
        self,
        state: EmailWorkflowState,
    ) -> Command[Literal["human_review", "send_reply"]]:
        classification = require_classification(state)
        customer_history = self.services.get_customer_history(state["sender_email"])
        context_sections = build_context_sections(
            state,
            customer_history=customer_history,
        )
        normalized_email = require_normalized_email(state)
        prompt = build_response_prompt(
            email=normalized_email,
            classification=classification,
            context_sections=context_sections,
        )
        response = self.services.llm.invoke(prompt)
        response_text = message_to_text(response)
        goto: Literal["human_review", "send_reply"]
        if needs_human_review(classification):
            goto = "human_review"
            print("Needs approval")
        else:
            goto = "send_reply"
        return Command(update={"draft_response": response_text}, goto=goto)


class HumanReviewNode:
    """Pause execution and wait for a human decision."""

    def __call__(
        self,
        state: EmailWorkflowState,
    ) -> Command[Literal["send_reply", "__end__"]]:
        classification = require_classification(state)
        normalized_email = require_normalized_email(state)
        draft_response = require_draft_response(state)
        review_request: ReviewRequest = {
            "email_id": state["email_id"],
            "original_email": normalized_email,
            "draft_response": draft_response,
            "urgency": classification["urgency"],
            "intent": classification["intent"],
            "action": "Review this draft. Approve as-is or provide an edited response.",
        }
        decision = cast(ReviewDecision, interrupt(review_request))
        if decision.get("approved", False):
            approved_response = decision.get("edited_response", draft_response)
            return Command(
                update={"draft_response": approved_response}, goto="send_reply"
            )
        return cast(
            Command[Literal["send_reply", "__end__"]],
            Command(update={"sent_status": "cancelled"}, goto=END),
        )


@dataclass(frozen=True)
class SendReplyNode:
    """Persist the sent response in an in-memory outbox."""

    services: EmailWorkflowServices

    def __call__(self, state: EmailWorkflowState) -> EmailWorkflowState:
        response = require_draft_response(state)
        self.services.record_sent_reply(
            email_id=state["email_id"],
            sender_email=state["sender_email"],
            response=response,
        )
        print(f"Sending reply: {response[:80]}...")
        return cast(
            EmailWorkflowState,
            {"sent_reply": response, "sent_status": "sent"},
        )


def needs_human_review(classification: EmailClassificationData) -> bool:
    """Return whether the case should pause for human review."""

    return classification["urgency"] in {"high", "critical"} or classification[
        "intent"
    ] in {"complex", "billing"}


__all__ = [
    "BugTrackingNode",
    "DocumentationSearchNode",
    "HumanReviewNode",
    "IntentClassifierNode",
    "ReadEmailNode",
    "ResponseWriterNode",
    "SendReplyNode",
    "needs_human_review",
]
