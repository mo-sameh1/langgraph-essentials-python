"""Tracing context helpers for opt-in LangSmith instrumentation."""

from __future__ import annotations

from contextlib import nullcontext
from typing import Any

from langsmith import tracing_context

from .client import build_langsmith_client
from .config import EmailWorkflowLangSmithConfig, get_langsmith_config


def langsmith_tracing_context(
    *,
    config: EmailWorkflowLangSmithConfig | None = None,
    project_name: str | None = None,
    enabled: bool | None = None,
) -> Any:
    """Return a safe tracing context manager for workflow entrypoints."""

    resolved_config = config or get_langsmith_config()
    if enabled is None:
        tracing_enabled = resolved_config.tracing_active
    else:
        tracing_enabled = enabled and resolved_config.api_key_present
    if not tracing_enabled:
        return nullcontext()
    client = build_langsmith_client(resolved_config)
    if client is None:
        return nullcontext()
    return tracing_context(
        enabled=True,
        client=client,
        project_name=project_name or resolved_config.project,
    )


__all__ = ["langsmith_tracing_context"]
