"""Prompt builders for the email workflow application."""

from __future__ import annotations

from .types import EmailClassificationData


def build_classification_prompt(*, email: str, sender_email: str) -> str:
    """Build the classification prompt for the inbound email."""

    return (
        "Analyze the customer email and classify it.\n"
        "Use one of these intents: question, bug, billing, feature, complex.\n"
        "Use one of these urgency levels: low, medium, high, critical.\n\n"
        f"Email: {email}\n"
        f"From: {sender_email}\n"
    )


def build_response_prompt(
    *,
    email: str,
    classification: EmailClassificationData,
    context_sections: str,
) -> str:
    """Build the drafting prompt for the support response."""

    return (
        "Draft a concise, professional customer support reply.\n\n"
        f"Original email:\n{email}\n\n"
        f"Intent: {classification['intent']}\n"
        f"Urgency: {classification['urgency']}\n"
        f"Topic: {classification['topic']}\n"
        f"Summary: {classification['summary']}\n\n"
        f"{context_sections}\n"
        "Requirements:\n"
        "- Be empathetic and direct.\n"
        "- Use the provided documentation if relevant.\n"
        "- Mention a bug ticket if one exists.\n"
        "- Do not promise anything unsupported by the context.\n"
    )


__all__ = ["build_classification_prompt", "build_response_prompt"]
