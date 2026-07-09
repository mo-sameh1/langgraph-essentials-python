"""Typed LangSmith configuration helpers for the email workflow."""

from __future__ import annotations

from dataclasses import dataclass

from langgraph_course.settings import Settings, get_settings


@dataclass(frozen=True)
class EmailWorkflowLangSmithConfig:
    """Resolved LangSmith settings used by the email workflow package."""

    tracing_enabled: bool
    api_key: str | None
    project: str
    endpoint: str
    workspace_id: str | None

    @property
    def api_key_present(self) -> bool:
        """Return whether an API key is available for authenticated operations."""

        return bool(self.api_key)

    @property
    def tracing_active(self) -> bool:
        """Return whether tracing can be enabled safely for this process."""

        return self.tracing_enabled and self.api_key_present

    @property
    def missing_configuration(self) -> list[str]:
        """Return missing configuration items that block authenticated tracing."""

        missing: list[str] = []
        if self.tracing_enabled and not self.api_key_present:
            missing.append("LANGSMITH_API_KEY")
        return missing

    @property
    def summary(self) -> str:
        """Return a short human-readable status line."""

        if self.tracing_active:
            return f"LangSmith tracing enabled for project '{self.project}'."
        if self.tracing_enabled:
            return "LangSmith tracing requested, but configuration is incomplete."
        return "LangSmith tracing disabled; local-only workflow is active."


def get_langsmith_config(
    settings: Settings | None = None,
) -> EmailWorkflowLangSmithConfig:
    """Return normalized LangSmith configuration for this repository."""

    resolved_settings = settings or get_settings()
    api_key = _normalize_optional_text(resolved_settings.langsmith_api_key)
    workspace_id = _normalize_optional_text(resolved_settings.langsmith_workspace_id)
    return EmailWorkflowLangSmithConfig(
        tracing_enabled=resolved_settings.langsmith_tracing,
        api_key=api_key,
        project=resolved_settings.langsmith_project.strip(),
        endpoint=resolved_settings.langsmith_endpoint.strip(),
        workspace_id=workspace_id,
    )


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


__all__ = ["EmailWorkflowLangSmithConfig", "get_langsmith_config"]
