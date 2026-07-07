"""Service objects and in-memory stores for the email workflow application."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from itertools import count

from .types import ChatModelLike, CustomerHistoryData


@dataclass(frozen=True)
class KnowledgeDocument:
    """Simple in-memory knowledge base document."""

    title: str
    content: str
    tags: tuple[str, ...]


@dataclass(frozen=True)
class SentReplyRecord:
    """A record of a sent customer reply."""

    email_id: str
    sender_email: str
    response: str


@dataclass
class KnowledgeBase:
    """Small searchable document store for the course project."""

    documents: list[KnowledgeDocument]

    def search(self, query: str, *, limit: int = 3) -> list[str]:
        """Return the best-matching document snippets for a query."""

        query_terms = set(_tokenize(query))
        if not query_terms:
            return [
                self._format_document(document) for document in self.documents[:limit]
            ]

        scored_documents: list[tuple[int, KnowledgeDocument]] = []
        for document in self.documents:
            haystack = " ".join((document.title, document.content, *document.tags))
            document_terms = set(_tokenize(haystack))
            score = len(query_terms & document_terms)
            if score > 0:
                scored_documents.append((score, document))

        scored_documents.sort(key=lambda item: item[0], reverse=True)
        best_documents = [document for _, document in scored_documents[:limit]]
        if not best_documents:
            best_documents = self.documents[:limit]

        return [self._format_document(document) for document in best_documents]

    @staticmethod
    def _format_document(document: KnowledgeDocument) -> str:
        return f"{document.title}: {document.content}"


@dataclass
class TicketRegistry:
    """Tiny in-memory bug tracker used by the workflow."""

    _counter: count = field(default_factory=lambda: count(start=1))
    tickets: dict[str, str] = field(default_factory=dict)

    def create_ticket(self, summary: str) -> str:
        """Create a new bug ticket and return its identifier."""

        ticket_id = f"BUG-{next(self._counter):04d}"
        self.tickets[ticket_id] = summary
        return ticket_id


@dataclass
class EmailWorkflowServices:
    """External dependencies and stores used by the graph nodes."""

    llm: ChatModelLike
    knowledge_base: KnowledgeBase
    ticket_registry: TicketRegistry = field(default_factory=TicketRegistry)
    customer_profiles: dict[str, CustomerHistoryData] = field(default_factory=dict)
    sent_replies: list[SentReplyRecord] = field(default_factory=list)

    def get_customer_history(self, sender_email: str) -> CustomerHistoryData:
        """Return known customer history or a safe default profile."""

        return self.customer_profiles.get(
            sender_email,
            {"tier": "standard", "region": "global", "previous_tickets": 0},
        )


def default_documents() -> list[KnowledgeDocument]:
    """Return the default knowledge base content used by the app."""

    return [
        KnowledgeDocument(
            title="Billing duplicate charges",
            content=(
                "Apologize, confirm the duplicate charge review, and explain that "
                "billing corrections usually complete in 3-5 business days."
            ),
            tags=("billing", "duplicate", "refund", "subscription"),
        ),
        KnowledgeDocument(
            title="Product color availability",
            content=(
                "Check live inventory before promising color availability. If a "
                "color is unavailable, offer to notify the customer when it returns."
            ),
            tags=("feature", "product", "color", "inventory"),
        ),
        KnowledgeDocument(
            title="Promotion and sale timing",
            content=(
                "Sales windows may vary by region. Share the public end date only "
                "if it is listed in policy, otherwise explain that pricing can "
                "change without notice."
            ),
            tags=("question", "sale", "pricing", "promotion"),
        ),
        KnowledgeDocument(
            title="Product defect escalation",
            content=(
                "For a broken or unsafe product, create a bug or defect ticket and "
                "reassure the customer that support is escalating the issue "
                "immediately."
            ),
            tags=("bug", "defect", "broken", "unsafe"),
        ),
        KnowledgeDocument(
            title="Subscription renewal pricing",
            content=(
                "Renewal pricing depends on the customer tier and current plan. "
                "Avoid quoting a rate unless the pricing policy is available."
            ),
            tags=("billing", "renewal", "pricing", "subscription"),
        ),
    ]


def default_customer_profiles() -> dict[str, CustomerHistoryData]:
    """Return the seeded customer profiles used by the course app."""

    return {
        "customer@example.com": {
            "tier": "priority",
            "region": "us",
            "previous_tickets": 2,
        },
        "vip@example.com": {
            "tier": "enterprise",
            "region": "eu",
            "previous_tickets": 5,
        },
    }


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9_]+", text.lower())


__all__ = [
    "EmailWorkflowServices",
    "KnowledgeBase",
    "KnowledgeDocument",
    "SentReplyRecord",
    "TicketRegistry",
    "default_customer_profiles",
    "default_documents",
]
