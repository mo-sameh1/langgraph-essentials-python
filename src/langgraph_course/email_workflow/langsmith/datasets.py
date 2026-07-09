"""Dataset seeding helpers for the email workflow LangSmith integration."""

from __future__ import annotations

from typing import cast

from langsmith import Client

from .client import build_langsmith_client
from .evaluation_cases import DATASET_NAME, canonical_evaluation_cases


def sync_canonical_dataset(
    *,
    dataset_name: str = DATASET_NAME,
    replace_existing: bool = True,
    client: Client | None = None,
) -> str:
    """Create or refresh the canonical LangSmith dataset for this workflow."""

    resolved_client = client or build_langsmith_client()
    if resolved_client is None:
        raise RuntimeError("LangSmith client is unavailable. Configure LANGSMITH_API_KEY first.")
    if _dataset_exists(resolved_client, dataset_name):
        if not replace_existing:
            raise RuntimeError(
                f"Dataset '{dataset_name}' already exists. "
                "Pass replace_existing=True to refresh it."
            )
        resolved_client.delete_dataset(dataset_name=dataset_name)
    dataset = resolved_client.create_dataset(
        dataset_name,
        description="Canonical evaluation cases for the LangGraph Essentials email agent.",
        metadata={"workflow_name": "email-agent"},
    )
    examples = [cast(dict[str, object], case.to_example()) for case in canonical_evaluation_cases()]
    resolved_client.create_examples(
        dataset_id=dataset.id,
        examples=examples,
    )
    return str(dataset.id)


def _dataset_exists(client: Client, dataset_name: str) -> bool:
    try:
        client.read_dataset(dataset_name=dataset_name)
    except Exception:
        return False
    return True


__all__ = ["DATASET_NAME", "sync_canonical_dataset"]
