from langgraph_course.settings import Settings


def test_local_ollama_defaults() -> None:
    settings = Settings()

    assert settings.ollama_base_url == "http://127.0.0.1:11434"
    assert settings.ollama_model == "langgraph-coder"
    assert settings.ollama_num_ctx == 32768
