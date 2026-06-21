"""Tests for merge_sources.py (Phase-3 partial-sidecar merge).

Covers dedup by paper_id, search-log union, provenance (merged_from), and that
the merged record is a schema-valid sources.json (validate_sidecar --kind sources).
"""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

from merge_sources import merge_partials  # noqa: E402
from validate_sidecar import SidecarValidator  # noqa: E402


def _source(pid: str, title: str, source: str = "PubMed") -> dict:
    return {
        "paper_id": pid,
        "doi": pid,
        "pmid": None,
        "pmcid": None,
        "title": title,
        "authors": ["Doe J"],
        "year": 2024,
        "venue": "Journal",
        "source": source,
        "study_design": "RCT",
        "key_findings": "Finding.",
        "relevance": "High",
        "limitations": None,
        "reception": None,
        "grey_lit_note": None,
    }


def _log(database: str, query: str) -> dict:
    return {
        "database": database,
        "date": "2026-06-21",
        "query": query,
        "filters": None,
        "results": 10,
        "after_dedup": 8,
        "trace_id": None,
    }


def _partial(sqid: str, sources: list[dict], log: list[dict]) -> dict:
    return {
        "schema_version": "1.0",
        "metadata": {
            "frozen_at": "2026-06-21T18:00:00Z",
            "mode": "full",
            "topic_slug": "kras",
            "sub_question_id": sqid,
            "rq": "What drives resistance to KRAS G12C inhibitors?",
        },
        "sources": sources,
        "search_log": log,
    }


def test_merge_dedups_by_paper_id():
    p1 = _partial(
        "SQ1", [_source("10.1/a", "A"), _source("10.1/b", "B")], [_log("PubMed", "q1")]
    )
    p2 = _partial(
        "SQ2",
        [_source("10.1/b", "B again"), _source("10.1/c", "C")],
        [_log("OpenAlex", "q2")],
    )
    result = merge_partials(
        [p1, p2], mode="full", topic_slug="kras", frozen_at="2026-06-21T19:00:00Z"
    )
    assert result.total_in == 4
    assert result.unique == 3  # 10.1/b deduped
    assert result.duplicates == 1
    pids = [s["paper_id"] for s in result.merged["sources"]]
    assert pids == ["10.1/a", "10.1/b", "10.1/c"]
    # first occurrence wins
    assert result.merged["sources"][1]["title"] == "B"


def test_merge_unions_search_log_and_databases():
    p1 = _partial("SQ1", [_source("10.1/a", "A")], [_log("PubMed", "q1")])
    p2 = _partial("SQ2", [_source("10.1/b", "B", "OpenAlex")], [_log("OpenAlex", "q2")])
    result = merge_partials([p1, p2], mode="full", topic_slug="kras")
    assert len(result.merged["search_log"]) == 2
    assert set(result.databases) == {"PubMed", "OpenAlex"}


def test_merge_records_provenance():
    p1 = _partial("SQ1", [_source("10.1/a", "A")], [])
    p2 = _partial("SQ2", [_source("10.1/b", "B", "OpenAlex")], [])
    result = merge_partials([p1, p2], mode="full", topic_slug="kras")
    assert result.sub_question_ids == ["SQ1", "SQ2"]
    assert result.merged["metadata"]["merged_from"] == ["SQ1", "SQ2"]
    # rq inherited from first partial
    assert result.merged["metadata"]["rq"].startswith("What drives resistance")


def test_merge_empty():
    result = merge_partials([], mode="full", topic_slug="kras")
    assert result.unique == 0
    assert result.merged["metadata"]["merged_from"] is None
    assert result.merged["sources"] == []


def test_merged_record_is_schema_valid():
    p1 = _partial("SQ1", [_source("10.1/a", "A")], [_log("PubMed", "q1")])
    p2 = _partial(
        "SQ2",
        [_source("10.1/a", "A dup"), _source("10.1/b", "B", "OpenAlex")],
        [_log("OpenAlex", "q2")],
    )
    result = merge_partials(
        [p1, p2], mode="full", topic_slug="kras", frozen_at="2026-06-21T19:00:00Z"
    )
    ok, errors, _ = SidecarValidator("sources").validate(result.merged)
    assert ok, errors
    # S1 (unique paper_id) holds after dedup
    assert len({s["paper_id"] for s in result.merged["sources"]}) == result.unique
