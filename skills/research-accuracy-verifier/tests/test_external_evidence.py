"""Tests for scripts/external_evidence.py (Phase 2 ledger)."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from external_evidence import (
    canonicalize_query,
    lookup_or_fetch,
    query_hash,
    record_consumption,
)


# ── canonicalize_query / query_hash ─────────────────────────────────────────


class TestCanonicalize:
    def test_key_order_does_not_affect_hash(self):
        a = {"doi": "10.1/x", "pmid": "123"}
        b = {"pmid": "123", "doi": "10.1/x"}
        assert query_hash(a) == query_hash(b)

    def test_string_value_case_does_not_affect_hash(self):
        a = {"doi": "10.1126/SCIENCE.1258096"}
        b = {"doi": "10.1126/science.1258096"}
        assert query_hash(a) == query_hash(b)

    def test_distinct_values_produce_distinct_hashes(self):
        a = {"doi": "10.1/x"}
        b = {"doi": "10.1/y"}
        assert query_hash(a) != query_hash(b)

    def test_hash_is_64_char_lowercase_hex(self):
        h = query_hash({"doi": "10.1/x"})
        assert len(h) == 64
        assert h == h.lower()
        assert all(c in "0123456789abcdef" for c in h)

    def test_nested_dict_canonicalization(self):
        a = {"q": {"nested": "VAL", "x": 1}}
        b = {"q": {"x": 1, "nested": "val"}}
        assert query_hash(a) == query_hash(b)


# ── lookup_or_fetch ─────────────────────────────────────────────────────────


class TestLookupOrFetch:
    @pytest.fixture
    def ledger_path(self, tmp_path: Path) -> Path:
        return tmp_path / "audit_X" / "external_evidence.json"

    def test_first_call_is_cache_miss_and_creates_ledger(self, ledger_path: Path):
        digest, cached = lookup_or_fetch(
            ledger_path,
            tool="scite",
            method="scite_context",
            query_params={"doi": "10.1/x"},
            paper_id="10.1/x",
            fetcher=lambda: "editorialNotices: NONE",
        )
        assert digest == "editorialNotices: NONE"
        assert cached is False
        assert ledger_path.exists()
        ledger = json.loads(ledger_path.read_text())
        assert ledger["schema_version"] == "1.0"
        assert ledger["metadata"]["audit_slug"] == "audit_X"
        assert len(ledger["entries"]) == 1
        assert ledger["entries"][0]["id"] == "E0001"

    def test_second_call_with_same_params_is_cache_hit(self, ledger_path: Path):
        calls = []
        def fetcher():
            calls.append(1)
            return "fresh"
        lookup_or_fetch(
            ledger_path, "scite", "scite_context",
            {"doi": "10.1/x"}, "10.1/x", fetcher,
        )
        d2, cached2 = lookup_or_fetch(
            ledger_path, "scite", "scite_context",
            {"doi": "10.1/x"}, "10.1/x", fetcher,
        )
        assert cached2 is True
        assert d2 == "fresh"
        assert len(calls) == 1

    def test_value_case_collapses_to_same_cache_entry(self, ledger_path: Path):
        calls = []
        def fetcher():
            calls.append(1)
            return "r"
        lookup_or_fetch(
            ledger_path, "scite", "scite_context",
            {"doi": "10.1/X"}, "10.1/x", fetcher,
        )
        _, cached = lookup_or_fetch(
            ledger_path, "scite", "scite_context",
            {"doi": "10.1/x"}, "10.1/x", fetcher,
        )
        assert cached is True
        assert len(calls) == 1

    def test_different_paper_id_scope_misses_cache(self, ledger_path: Path):
        calls = []
        def fetcher():
            calls.append(1)
            return "r"
        lookup_or_fetch(
            ledger_path, "scite", "scite_context",
            {"doi": "10.1/x"}, "10.1/x", fetcher,
        )
        lookup_or_fetch(
            ledger_path, "scite", "scite_context",
            {"doi": "10.1/x"}, "10.1/y", fetcher,
        )
        assert len(calls) == 2
        ledger = json.loads(ledger_path.read_text())
        assert {e["id"] for e in ledger["entries"]} == {"E0001", "E0002"}

    def test_sequential_ids(self, ledger_path: Path):
        for i in range(3):
            lookup_or_fetch(
                ledger_path, "scite", "scite_context",
                {"doi": f"10.1/{i}"}, f"10.1/{i}", lambda: "r",
            )
        ledger = json.loads(ledger_path.read_text())
        assert [e["id"] for e in ledger["entries"]] == ["E0001", "E0002", "E0003"]

    def test_stale_entry_triggers_refetch(self, ledger_path: Path):
        # Seed ledger with an entry whose fetched_at is older than TTL.
        old_ts = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        ledger = {
            "schema_version": "1.0",
            "metadata": {"audit_slug": "audit_X", "opened_at": "2026-01-01T00:00:00Z"},
            "entries": [
                {
                    "id": "E0001",
                    "tool": "scite",
                    "method": "scite_context",
                    "query_hash": query_hash({"doi": "10.1/x"}),
                    "query_params": {"doi": "10.1/x"},
                    "paper_id": "10.1/x",
                    "fetched_at": old_ts,
                    "response_digest": "stale",
                    "consumed_by_findings": [],
                }
            ],
        }
        ledger_path.parent.mkdir(parents=True)
        ledger_path.write_text(json.dumps(ledger))

        digest, cached = lookup_or_fetch(
            ledger_path, "scite", "scite_context",
            {"doi": "10.1/x"}, "10.1/x", lambda: "fresh",
            freshness_days=7,
        )
        assert cached is False
        assert digest == "fresh"
        # New entry appended (E0002), stale one preserved.
        led = json.loads(ledger_path.read_text())
        assert len(led["entries"]) == 2
        assert led["entries"][1]["response_digest"] == "fresh"

    def test_dict_response_serialized(self, ledger_path: Path):
        digest, _ = lookup_or_fetch(
            ledger_path, "scite", "scite_context",
            {"doi": "10.1/x"}, "10.1/x",
            lambda: {"a": 1, "b": "two"},
        )
        assert digest == '{"a":1,"b":"two"}'

    def test_oversize_response_truncated_to_512(self, ledger_path: Path):
        big = "x" * 1000
        digest, _ = lookup_or_fetch(
            ledger_path, "scite", "scite_context",
            {"doi": "10.1/x"}, "10.1/x",
            lambda: big,
        )
        assert len(digest) == 512
        assert digest.endswith("…")

    def test_unknown_tool_without_explicit_ttl_raises(self, ledger_path: Path):
        with pytest.raises(KeyError):
            lookup_or_fetch(
                ledger_path, "unknown_tool", "x",
                {"q": "1"}, None, lambda: "r",
            )

    def test_explicit_freshness_days_overrides_thresholds(self, ledger_path: Path):
        calls = []
        def fetcher():
            calls.append(1)
            return "r"
        lookup_or_fetch(
            ledger_path, "unknown_tool", "x",
            {"q": "1"}, None, fetcher,
            freshness_days=7,
        )
        assert len(calls) == 1

    def test_atomic_write_leaves_no_tempfile(self, ledger_path: Path):
        lookup_or_fetch(
            ledger_path, "scite", "scite_context",
            {"doi": "10.1/x"}, "10.1/x", lambda: "r",
        )
        # No stray .tmp files in the parent dir.
        tmps = list(ledger_path.parent.glob(".*tmp*"))
        assert tmps == []


# ── record_consumption ──────────────────────────────────────────────────────


class TestRecordConsumption:
    def test_appends_finding_to_existing_entry(self, tmp_path: Path):
        p = tmp_path / "audit_x" / "external_evidence.json"
        lookup_or_fetch(
            p, "scite", "scite_context",
            {"doi": "10.1/x"}, "10.1/x", lambda: "r",
        )
        assert record_consumption(p, "E0001", "F-001") is True
        led = json.loads(p.read_text())
        assert led["entries"][0]["consumed_by_findings"] == ["F-001"]

    def test_idempotent(self, tmp_path: Path):
        p = tmp_path / "audit_x" / "external_evidence.json"
        lookup_or_fetch(
            p, "scite", "scite_context",
            {"doi": "10.1/x"}, "10.1/x", lambda: "r",
        )
        record_consumption(p, "E0001", "F-001")
        assert record_consumption(p, "E0001", "F-001") is False
        led = json.loads(p.read_text())
        assert led["entries"][0]["consumed_by_findings"] == ["F-001"]

    def test_unknown_entry_returns_false(self, tmp_path: Path):
        p = tmp_path / "audit_x" / "external_evidence.json"
        lookup_or_fetch(
            p, "scite", "scite_context",
            {"doi": "10.1/x"}, "10.1/x", lambda: "r",
        )
        assert record_consumption(p, "E9999", "F-001") is False

    def test_missing_ledger_returns_false(self, tmp_path: Path):
        assert record_consumption(tmp_path / "nope.json", "E0001", "F-001") is False


def test_canonicalize_query_is_canonical_json():
    """Output is single-line JSON; round-trips through json.loads."""
    s = canonicalize_query({"b": 1, "a": "X"})
    assert json.loads(s) == {"a": "x", "b": 1}
    assert "\n" not in s
