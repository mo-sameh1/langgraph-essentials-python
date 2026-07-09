"""LangSmith client helpers for the email workflow package."""

from __future__ import annotations

from langsmith import Client

from .config import EmailWorkflowLangSmithConfig, get_langsmith_config


def build_langsmith_client(
    config: EmailWorkflowLangSmithConfig | None = None,
) -> Client | None:
    """Build a LangSmith client when credentials are available."""

    resolved_config = config or get_langsmith_config()
    if not resolved_config.api_key_present:
        return None
    return Client(
        api_key=resolved_config.api_key,
        api_url=resolved_config.endpoint,
        workspace_id=resolved_config.workspace_id,
    )


def get_langsmith_client() -> Client | None:
    """Return a LangSmith client for the configured environment."""

    return build_langsmith_client()


__all__ = ["build_langsmith_client", "get_langsmith_client"]
