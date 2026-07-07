"""Internal helper functions for node and session logic."""

from __future__ import annotations

from langchain_core.messages import AIMessage

from .types import CustomerHistoryData, EmailClassificationData, EmailWorkflowState


def message_to_text(message: AIMessage) -> str:
    """Normalize model output into plain text."""

    content = message.content
    if isinstance(content, str):
        return content
    return "\n".join(str(item) for item in content)


def require_classification(state: EmailWorkflowState) -> EmailClassificationData:
    """Read classification from state or fail fast."""

    classification = state.get("classification")
    if classification is None:
        raise ValueError("Missing email classification in workflow state.")
    return classification


def require_normalized_email(state: EmailWorkflowState) -> str:
    """Read normalized email content from state or fail fast."""

    normalized_email = state.get("normalized_email")
    if normalized_email is None:
        raise ValueError("Missing normalized email content in workflow state.")
    return normalized_email


def require_draft_response(state: EmailWorkflowState) -> str:
    """Read the drafted response from state or fail fast."""

    draft_response = state.get("draft_response")
    if draft_response is None:
        raise ValueError("Missing draft response in workflow state.")
    return draft_response


def build_context_sections(
    state: EmailWorkflowState,
    *,
    customer_history: CustomerHistoryData | None = None,
) -> str:
    """Assemble optional context blocks for the response-writing prompt."""

    sections: list[str] = []
    search_results = state.get("search_results")
    if search_results:
        formatted_results = "\n".join(f"- {item}" for item in search_results)
        sections.append(f"Relevant documentation:\n{formatted_results}")
    history = customer_history
    if history:
        sections.append(
            "Customer profile:\n"
            f"- Tier: {history['tier']}\n"
            f"- Region: {history['region']}\n"
            f"- Previous tickets: {history['previous_tickets']}"
        )
    ticket_id = state.get("ticket_id")
    if ticket_id:
        sections.append(f"Active bug ticket: {ticket_id}")
    return "\n\n".join(sections)


__all__ = [
    "build_context_sections",
    "message_to_text",
    "require_classification",
    "require_draft_response",
    "require_normalized_email",
]
