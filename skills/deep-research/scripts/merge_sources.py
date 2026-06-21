#!/usr/bin/env python3
"""
Merge partial sources sidecars from the Phase-3 parallel sub-question fan-out.

In fan-out modes (``thresholds.FANOUT_MODES``), the deep-research orchestrator
spawns one researcher subagent per decomposition sub-question. Each writes a
PARTIAL sources sidecar — the same schema as a full ``sources.json``, tagged with
its ``metadata.sub_question_id`` and named ``..._sources.sub{N}.json``. This
module merges those partials into the single canonical ``sources.json`` the
verification / synthesis / compiler stages consume: deduplicating sources by
``paper_id`` and unioning the per-database search logs.

Downstream is unchanged — the merged sidecar is an ordinary ``sources.json``,
validated by ``validate_sidecar.py --kind sources``, and the merged search log
feeds ``search_audit.py`` exactly as a single-context run would.

Usage:
    python merge_sources.py --mode full --topic-slug kras --out merged.json \\
        part_sub1.json part_sub2.json part_sub3.json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

SCHEMA_VERSION = "1.0"


@dataclass
class MergeResult:
    """Outcome of merging partial sources sidecars."""

    merged: dict
    total_in: int
    unique: int
    duplicates: int
    databases: list[str] = field(default_factory=list)
    sub_question_ids: list[str] = field(default_factory=list)


def merge_partials(
    partials: list[dict],
    mode: str,
    topic_slug: str,
    frozen_at: str = "",
    rq: str | None = None,
    search_contract_version: str | None = None,
) -> MergeResult:
    """
    Merge partial sources records into one canonical sources record.

    Dedup is by ``paper_id`` (first occurrence wins — partials are produced
    concurrently, so order is by argument position). The per-database search
    logs are concatenated verbatim (each sub-question issues distinct queries,
    so rows are genuinely distinct and reproducibility-critical).

    Args:
        partials: Parsed partial sources records (each a valid sources.json).
        mode: deep-research mode for the merged metadata.
        topic_slug: Topic slug for the merged metadata.
        frozen_at: ISO-8601 timestamp for the merged sidecar (set when the
            bibliography phase completes).
        rq: Research question; pulled from the first partial when None.
        search_contract_version: Pulled from the first partial when None.

    Returns:
        MergeResult with the merged record and dedup/coverage stats.
    """
    seen: set[str] = set()
    merged_sources: list[dict] = []
    search_log: list[dict] = []
    sub_question_ids: list[str] = []
    total_in = 0
    duplicates = 0

    for partial in partials:
        meta = partial.get("metadata") or {}
        sqid = meta.get("sub_question_id")
        if sqid and sqid not in sub_question_ids:
            sub_question_ids.append(sqid)

        for src in partial.get("sources") or []:
            total_in += 1
            pid = src.get("paper_id")
            if pid and pid in seen:
                duplicates += 1
                continue
            if pid:
                seen.add(pid)
            merged_sources.append(src)

        for row in partial.get("search_log") or []:
            search_log.append(row)

    # Inherit rq / contract version from the first partial unless overridden.
    if partials:
        first_meta = partials[0].get("metadata") or {}
        if rq is None:
            rq = first_meta.get("rq")
        if search_contract_version is None:
            search_contract_version = first_meta.get("search_contract_version")

    databases: list[str] = []
    for row in search_log:
        db = row.get("database")
        if db and db not in databases:
            databases.append(db)

    merged = {
        "schema_version": SCHEMA_VERSION,
        "metadata": {
            "frozen_at": frozen_at,
            "mode": mode,
            "topic_slug": topic_slug,
            "search_contract_version": search_contract_version,
            "rq": rq,
            "merged_from": sub_question_ids or None,
        },
        "sources": merged_sources,
        "search_log": search_log,
    }
    return MergeResult(
        merged=merged,
        total_in=total_in,
        unique=len(merged_sources),
        duplicates=duplicates,
        databases=databases,
        sub_question_ids=sub_question_ids,
    )


def _load(path: str) -> dict:
    return json.loads(Path(path).read_text())


def main() -> None:
    """CLI entry point. Merges partial sidecars and writes a sources.json."""
    ap = argparse.ArgumentParser(
        description="Merge partial sources sidecars into one canonical sources.json"
    )
    ap.add_argument("partials", nargs="+", help="Partial sources sidecar JSON files")
    ap.add_argument("--mode", required=True, help="deep-research mode")
    ap.add_argument("--topic-slug", required=True, dest="topic_slug")
    ap.add_argument(
        "--out", required=True, help="Path to write the merged sources.json"
    )
    ap.add_argument(
        "--frozen-at", default="", dest="frozen_at", help="ISO-8601 timestamp"
    )
    ap.add_argument(
        "--rq",
        default=None,
        help="Research question (else inherited from first partial)",
    )
    args = ap.parse_args()

    partials = [_load(p) for p in args.partials]
    result = merge_partials(
        partials, args.mode, args.topic_slug, args.frozen_at, args.rq
    )
    Path(args.out).write_text(
        json.dumps(result.merged, indent=2) + "\n", encoding="utf-8"
    )

    sys.stdout.write(
        f"merged {len(partials)} partial(s): {result.total_in} sources in -> "
        f"{result.unique} unique ({result.duplicates} duplicate(s) dropped); "
        f"{len(result.databases)} database(s); sub-questions {result.sub_question_ids}\n"
    )
    sys.stdout.write(f"wrote {args.out}\n")
    sys.stdout.write(
        f"Next: `validate_sidecar.py --kind sources --file {args.out}` before Checkpoint 2.\n"
    )


if __name__ == "__main__":
    main()
