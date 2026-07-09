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

## Email agent workflows

### Local-only path

This is the default and lowest-cost path. Keep `LANGSMITH_TRACING=false` in
`.env`, then open the application notebook:

```bash
uv run jupyter lab
```

Open `labs/lab6_application.ipynb` and run it normally. The email agent will
use Ollama only and will not upload traces.

### LangSmith-enabled tracing path

LangSmith is opt-in. After adding your free-tier API key to `.env`, verify the
setup before running the notebook or scripts:

```bash
uv run python -m langgraph_course.email_workflow.langsmith.verify
```

If tracing is active, the application notebook will tag runs with
`source="notebook"` so they are easy to find in LangSmith Studio.

### Dataset seeding and evaluation commands

Seed or refresh the canonical LangSmith dataset:

```bash
uv run python -m langgraph_course.email_workflow.langsmith.seed_dataset
```

Run local evaluations against the real Ollama-backed workflow without uploading results:

```bash
uv run python -m langgraph_course.email_workflow.langsmith.run_evaluations --mode all
```

For a faster iteration loop, start with:

```bash
uv run python -m langgraph_course.email_workflow.langsmith.run_evaluations --mode pre-review
```

Upload one evaluation experiment to LangSmith when you want a tracked run:

```bash
uv run python -m langgraph_course.email_workflow.langsmith.run_evaluations --mode all --upload-results
```

See [docs/LANGSMITH.md](docs/LANGSMITH.md) for the free-tier LangSmith setup
and UI workflow guide, and [docs/OLLAMA.md](docs/OLLAMA.md) for local model
operations.
