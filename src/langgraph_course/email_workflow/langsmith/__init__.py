"""LangSmith support helpers for the email workflow package."""

from .client import build_langsmith_client, get_langsmith_client
from .config import EmailWorkflowLangSmithConfig, get_langsmith_config
from .metadata import (
    WORKFLOW_NAME,
    build_workflow_metadata,
    build_workflow_tags,
    summarize_workflow_outputs,
)
from .tracing import langsmith_tracing_context, workflow_root_trace, workflow_span

__all__ = [
    "WORKFLOW_NAME",
    "EmailWorkflowLangSmithConfig",
    "build_langsmith_client",
    "build_workflow_metadata",
    "build_workflow_tags",
    "get_langsmith_client",
    "get_langsmith_config",
    "langsmith_tracing_context",
    "summarize_workflow_outputs",
    "workflow_root_trace",
    "workflow_span",
]
