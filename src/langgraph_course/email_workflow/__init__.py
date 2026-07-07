"""Email workflow application for the LangGraph Essentials course."""

from .graph import (
    build_email_workflow,
    create_default_app,
    create_default_services,
    needs_human_review,
)
from .services import (
    EmailWorkflowServices,
    KnowledgeBase,
    KnowledgeDocument,
    SentReplyRecord,
    TicketRegistry,
)
from .session import EmailWorkflowSession
from .types import (
    ChatModelLike,
    CustomerHistoryData,
    EmailClassificationData,
    EmailClassificationModel,
    EmailInput,
    EmailWorkflowState,
    ReviewDecision,
    ReviewRequest,
    StructuredOutputRunnable,
)

__all__ = [
    "ChatModelLike",
    "CustomerHistoryData",
    "EmailClassificationData",
    "EmailClassificationModel",
    "EmailInput",
    "EmailWorkflowServices",
    "EmailWorkflowSession",
    "EmailWorkflowState",
    "KnowledgeBase",
    "KnowledgeDocument",
    "ReviewDecision",
    "ReviewRequest",
    "SentReplyRecord",
    "StructuredOutputRunnable",
    "TicketRegistry",
    "build_email_workflow",
    "create_default_app",
    "create_default_services",
    "needs_human_review",
]
