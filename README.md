# LangGraph Essentials — Python (Local Ollama)

Professional course workspace for
[Quickstart: LangGraph Essentials - Python](https://academy.langchain.com/courses/langgraph-essentials-python).
The exercises use a local Ollama model instead of the OpenAI API.

## Ready-to-use stack

- Python 3.12 managed with `uv`
- LangGraph and LangChain
- `langchain-ollama` with the local `langgraph-coder` model
- optional LangSmith tracing/evaluation support
- JupyterLab/IPython kernel for course notebooks
- Ruff, Pyright, and Pytest for quality checks
- A separate local Codex launcher (`codex-local`) for agentic repository work

## Start a course session

```bash
cd ~/Documents/GitHub/langgraph-essentials-python
cp -n .env.example .env
uv sync
uv run jupyter lab
```

To work with the local coding agent in this repository:

```bash
cd ~/Documents/GitHub/langgraph-essentials-python
codex-local
```

To chat with the underlying model without an agent:

```bash
ollama run langgraph-coder
```

## Use Ollama in course code

Where a lesson constructs an OpenAI chat model, use the shared factory:

```python
from langgraph_course.models import get_chat_model

llm = get_chat_model()
```

Or construct it directly:

```python
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="langgraph-coder",
    base_url="http://127.0.0.1:11434",
    temperature=0.2,
    num_ctx=32768,
)
```

## Quality commands

```bash
uv run ruff format .
uv run ruff check .
uv run pyright
uv run pytest
```

## Optional LangSmith setup

LangSmith is opt-in in this repository. The local/default path stays free and
uses Ollama only.

```bash
uv run python -m langgraph_course.email_workflow.langsmith.verify
```

See [docs/LANGSMITH.md](docs/LANGSMITH.md) for the free-tier setup path and
[docs/OLLAMA.md](docs/OLLAMA.md) for local model operations.
