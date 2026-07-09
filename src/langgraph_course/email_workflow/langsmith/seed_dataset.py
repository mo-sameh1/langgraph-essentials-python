"""CLI entrypoint for seeding the canonical email-agent dataset."""

from __future__ import annotations

import argparse

from .datasets import DATASET_NAME, sync_canonical_dataset


def main() -> int:
    """Seed or refresh the canonical LangSmith dataset."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-name", default=DATASET_NAME)
    parser.add_argument(
        "--preserve-existing",
        action="store_true",
        help="Abort instead of replacing an existing canonical dataset.",
    )
    args = parser.parse_args()
    dataset_id = sync_canonical_dataset(
        dataset_name=args.dataset_name,
        replace_existing=not args.preserve_existing,
    )
    print(f"Seeded dataset '{args.dataset_name}' ({dataset_id}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
