# Repository guidance

This repository contains the user's own work for the LangChain Academy course
"Quickstart: LangGraph Essentials - Python."

## Working conventions

- Use Python 3.12 and `uv`; do not install project packages globally.
- Use `langchain-ollama` and the local `langgraph-coder` model by default.
- Do not add or request OpenAI API credentials.
- Keep course exercises in `notebooks/` unless a lesson requires another layout.
- Do not solve future course exercises unless the user explicitly asks.
- Never commit `.env`, credentials, generated caches, or notebook checkpoints.
- Before finishing code changes, run Ruff, Pyright, and relevant Pytest tests.
- Prefer small, typed functions and explicit LangGraph state schemas.

