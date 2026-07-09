from langgraph_course.email_workflow.langsmith import (
    EmailWorkflowLangSmithConfig,
    get_langsmith_config,
    langsmith_tracing_context,
)
from langgraph_course.settings import Settings


def make_settings(
    *,
    langsmith_tracing: bool = False,
    langsmith_api_key: str | None = None,
    langsmith_project: str = "langgraph-essentials-email-agent",
    langsmith_endpoint: str = "https://api.smith.langchain.com",
    langsmith_workspace_id: str | None = None,
) -> Settings:
    return Settings(
        ollama_base_url="http://127.0.0.1:11434",
        ollama_model="langgraph-coder",
        ollama_num_ctx=32768,
        ollama_temperature=0.2,
        langsmith_tracing=langsmith_tracing,
        langsmith_api_key=langsmith_api_key,
        langsmith_project=langsmith_project,
        langsmith_endpoint=langsmith_endpoint,
        langsmith_workspace_id=langsmith_workspace_id,
    )


def test_langsmith_config_defaults_are_safe() -> None:
    config = get_langsmith_config(make_settings())

    assert config.tracing_enabled is False
    assert config.api_key is None
    assert config.project == "langgraph-essentials-email-agent"
    assert config.endpoint == "https://api.smith.langchain.com"
    assert config.tracing_active is False
    assert config.missing_configuration == []


def test_langsmith_config_detects_missing_api_key() -> None:
    config = get_langsmith_config(make_settings(langsmith_tracing=True))

    assert config.tracing_enabled is True
    assert config.tracing_active is False
    assert config.missing_configuration == ["LANGSMITH_API_KEY"]


def test_langsmith_config_normalizes_blank_optional_values() -> None:
    config = get_langsmith_config(
        make_settings(
            langsmith_api_key="  ",
            langsmith_workspace_id="  ",
        )
    )

    assert config.api_key is None
    assert config.workspace_id is None


def test_langsmith_tracing_context_is_safe_when_disabled() -> None:
    config = EmailWorkflowLangSmithConfig(
        tracing_enabled=False,
        api_key=None,
        project="langgraph-essentials-email-agent",
        endpoint="https://api.smith.langchain.com",
        workspace_id=None,
    )

    with langsmith_tracing_context(config=config):
        assert True
