# LangSmith setup for the email agent

This repository keeps Ollama local and uses LangSmith only for tracing,
debugging, and evaluation workflows. You do not need OpenAI credentials.

## No-cost setup path

Use the free LangSmith Developer plan:

- 1 free seat
- 5k base traces/month included
- keep Ollama local so model usage stays free

Do not add a payment method unless you intentionally want to exceed the free
tier. Keep `LANGSMITH_TRACING=false` when you are not actively tracing.

## 1. Create a free account and API key

1. Sign up at [smith.langchain.com](https://smith.langchain.com/).
2. Open the API keys page and create a personal API key.
3. Copy the key into your local `.env` file.

## 2. Configure `.env`

Start from the repo template:

```bash
cp -n .env.example .env
```

Then set the LangSmith values you want:

```dotenv
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=lsv2_pt_your_key_here
LANGSMITH_PROJECT=langgraph-essentials-email-agent
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_WORKSPACE_ID=
```

Notes:

- `LANGSMITH_PROJECT` defaults to `langgraph-essentials-email-agent`.
- `LANGSMITH_WORKSPACE_ID` is only needed when your API key can access more than
  one workspace.
- leaving `LANGSMITH_TRACING=false` keeps the repository in local-only mode.

## 3. Verify the integration

Run the verification module:

```bash
uv run python -m langgraph_course.email_workflow.langsmith.verify
```

Possible outcomes:

- tracing disabled: local-only mode is working
- tracing requested but key missing: fix `.env`
- authenticated successfully: traces can be sent

## 4. Stay inside the free tier

- Turn tracing on only when you are actively debugging or evaluating.
- Use the local evaluation dry-run mode later in this repo when you do not need
  uploaded LangSmith experiments.
- Keep notebook demos small and intentional.
- Reuse one project instead of creating many throwaway projects.

## 5. What this repo will use LangSmith for

- tracing LangGraph workflow runs
- debugging run trees in Studio
- seeding evaluation datasets
- running deterministic offline evaluations
- attaching structured review feedback

The application continues to run normally when LangSmith is unconfigured.
