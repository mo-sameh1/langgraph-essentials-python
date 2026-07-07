"""Graph assembly and default application factories for the email workflow."""

from __future__ import annotations

from typing import cast

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from langgraph_course.models import get_chat_model

from .nodes import (
    BugTrackingNode,
    DocumentationSearchNode,
    HumanReviewNode,
    IntentClassifierNode,
    ReadEmailNode,
    ResponseWriterNode,
    SendReplyNode,
    needs_human_review,
)
from .services import (
    EmailWorkflowServices,
    KnowledgeBase,
    default_customer_profiles,
    default_documents,
)
from .types import ChatModelLike, EmailWorkflowState


def build_email_workflow(
    services: EmailWorkflowServices,
    *,
    checkpointer: BaseCheckpointSaver | None = None,
) -> CompiledStateGraph:
    """Build the email workflow graph."""

    builder = StateGraph(EmailWorkflowState)
    builder.add_node("read_email", ReadEmailNode())
    builder.add_node("classify_intent", IntentClassifierNode(services))
    builder.add_node("search_documentation", DocumentationSearchNode(services))
    builder.add_node("bug_tracking", BugTrackingNode(services))
    builder.add_node("write_response", ResponseWriterNode(services))
    builder.add_node("human_review", HumanReviewNode())
    builder.add_node("send_reply", SendReplyNode(services))

    builder.add_edge(START, "read_email")
    builder.add_edge("read_email", "classify_intent")
    builder.add_edge("classify_intent", "search_documentation")
    builder.add_edge("classify_intent", "bug_tracking")
    builder.add_edge("search_documentation", "write_response")
    builder.add_edge("bug_tracking", "write_response")
    builder.add_edge("send_reply", END)

    return builder.compile(checkpointer=checkpointer)


def create_default_services(
    *, model: ChatModelLike | None = None
) -> EmailWorkflowServices:
    """Create the default local-Ollama services used by the course app."""

    llm = model or cast(ChatModelLike, get_chat_model())
    return EmailWorkflowServices(
        llm=llm,
        knowledge_base=KnowledgeBase(documents=default_documents()),
        customer_profiles=default_customer_profiles(),
    )


def create_default_app() -> CompiledStateGraph:
    """Create a runnable application graph with in-memory persistence."""

    services = create_default_services()
    return build_email_workflow(services, checkpointer=InMemorySaver())


__all__ = [
    "build_email_workflow",
    "create_default_app",
    "create_default_services",
    "needs_human_review",
]
