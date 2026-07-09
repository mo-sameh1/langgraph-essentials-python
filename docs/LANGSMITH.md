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

## 5. What this repo sends to LangSmith

- tracing LangGraph workflow runs
- debugging run trees in Studio
- seeding evaluation datasets
- running deterministic offline evaluations
- attaching structured review feedback

The application continues to run normally when LangSmith is unconfigured.

### Trace structure

The email agent keeps the graph topology unchanged and adds tracing around the
existing workflow semantics:

- root runs:
  - `email_workflow.start`
  - `email_workflow.resume_review`
- child runs:
  - `knowledge_base.search`
  - `bug_ticket.create`
  - `email_reply.persist`

Each traced run is enriched with consistent metadata and tags so you can filter
by workflow phase, source, intent, urgency, review requirement, bug-ticket
creation, and review outcome.

### Human review feedback

When a paused review is resumed, the repository logs one structured feedback
record with the key `human_review_outcome`.

- `approved` means the draft was accepted as-is
- `edited` means the draft was changed before sending
- `rejected` means the reply was not sent

Edited reviews also attach a correction payload containing the final reply that
was sent.

## 6. LangSmith UI workflows

These workflows are mostly configured in the LangSmith product UI. The code in
this repo supplies the trace structure and metadata they depend on.

### Studio debugging

1. Open your project in [LangSmith Studio](https://smith.langchain.com/).
2. Filter on metadata such as:
   - `workflow_name = email-agent`
   - `source = notebook`
   - `human_review_required = true`
   - `bug_ticket_created = true`
   - `review_outcome = rejected`
3. Open a trace to inspect the LangGraph run tree, model calls, and tool spans.

Reference: [View traces and observability docs](https://docs.langchain.com/langsmith/observability)

### Create a dataset from traces

Once you have a useful filtered set of traces, export them into a dataset from
the LangSmith UI. This works well for:

- tricky billing emails
- rejected or heavily edited review outcomes
- critical bug reports that should keep creating tickets

Reference: [Dataset workflows](https://docs.langchain.com/langsmith/dataset-transformations)

### Create an annotation queue

If you want a reviewer workflow in LangSmith itself:

1. Create a single-run annotation queue.
2. Set the default dataset if you want reviewed traces to export cleanly later.
3. Add rubric items such as:
   - `response_quality`
   - `policy_compliance`
   - `needs_follow_up`
   - `human_review_outcome`

Reference: [Annotation queues](https://docs.langchain.com/langsmith/annotation-queues)

### Build a dashboard

The easiest starting point is the project’s prebuilt dashboard. After that, add
custom charts grouped by metadata fields such as:

- interrupt / review-required rate
- bug-ticket creation rate
- approval vs. rejection vs. edited review outcomes
- intent distribution across traced emails

Reference: [Dashboards](https://docs.langchain.com/langsmith/dashboards)

### Suggested automation rules

Good first automations for this repository are:

- send traces with `review_outcome = rejected` to an annotation queue
- sample a small percentage of `human_review_required = true` traces for spot checks
- add `urgency = critical` bug traces to a dataset for regression coverage

Reference: [Automation rules](https://docs.langchain.com/langsmith/rules)
