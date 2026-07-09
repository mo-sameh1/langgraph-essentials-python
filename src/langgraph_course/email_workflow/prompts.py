"""Prompt builders for the email workflow application."""

from __future__ import annotations

from .types import EmailClassificationData


def build_classification_prompt(*, email: str, sender_email: str) -> str:
    """Build the classification prompt for the inbound email."""

    return (
        "Analyze the customer email and classify it.\n"
        "Return exactly one intent and one urgency label.\n\n"
        "Intent definitions:\n"
        "- question: a straightforward information request that support can answer directly\n"
        "- bug: the customer reports something broken, malfunctioning, unsafe, or not working\n"
        "- billing: the customer reports charges, refunds, invoices, payments, "
        "or subscription billing issues\n"
        "- feature: the customer asks whether a product capability, option, "
        "variant, or availability exists\n"
        "- complex: the request needs specialist handling, custom arrangements, "
        "escalation, or non-standard business discussion\n\n"
        "Urgency definitions:\n"
        "- low: general question or non-urgent request\n"
        "- medium: important request, but not time-sensitive or harmful right now\n"
        "- high: urgent issue that should be handled quickly, such as account or billing impact\n"
        "- critical: safety issue, severe malfunction, or major production-blocking failure\n\n"
        "Classification guidance:\n"
        "- If the email asks whether a product color, option, or capability exists, "
        "choose feature, not question.\n"
        "- If the email is about custom enterprise terms, renewal arrangements, "
        "or specialist follow-up, choose complex, not billing.\n"
        "- If the email reports a dangerous or safety-related defect, choose bug "
        "with critical urgency.\n"
        "- If the email reports a duplicate charge that is urgent but not dangerous, "
        "choose billing with high urgency.\n\n"
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
