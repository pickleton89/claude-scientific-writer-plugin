"""Tests for scripts/parse_document.py."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

import parse_document as pd

SCHEMA = json.loads(
    (Path(__file__).parent.parent / "schemas" / "document_inventory.json").read_text()
)


def _validate(inv: dict) -> None:
    jsonschema.Draft7Validator(SCHEMA).validate(inv)


class TestNormalizeText:
    def test_crlf_to_lf(self) -> None:
        assert pd.normalize_text("a\r\nb\r\n") == "a\nb\n"

    def test_strips_trailing_whitespace(self) -> None:
        assert pd.normalize_text("a   \nb \t\n") == "a\nb\n"

    def test_strips_trailing_blank_lines(self) -> None:
        assert pd.normalize_text("a\n\n\n\n") == "a\n"

    def test_empty(self) -> None:
        assert pd.normalize_text("") == ""

    def test_nfc_normalization(self) -> None:
        # 'é' as combining sequence U+0065 U+0301 → U+00E9
        decomposed = "Née\n"
        normalized = pd.normalize_text(decomposed)
        assert "é" in normalized
        assert "́" not in normalized


class TestStripDocumentWrapper:
    def test_strips_wrapper(self) -> None:
        wrapped = "<document>\nInner content\nMore lines\n</document>\n"
        assert pd.strip_document_wrapper(wrapped) == "Inner content\nMore lines"

    def test_passthrough_when_no_wrapper(self) -> None:
        raw = "No wrapper here\n"
        assert pd.strip_document_wrapper(raw) == raw

    def test_handles_leading_whitespace(self) -> None:
        wrapped = "  <document>\nInner\n</document>\n"
        assert pd.strip_document_wrapper(wrapped) == "Inner"


class TestDetectHeading:
    @pytest.mark.parametrize(
        "line,expected_level,expected_name",
        [
            ("# Introduction", 1, "Introduction"),
            ("## Background", 2, "Background"),
            ("### Methods and Materials", 3, "Methods and Materials"),
            ("###### Deep Section", 6, "Deep Section"),
        ],
    )
    def test_markdown_heading(self, line: str, expected_level: int, expected_name: str) -> None:
        h = pd.detect_heading(line)
        assert h is not None
        assert h.level == expected_level
        assert h.name == expected_name

    def test_explicit_section_marker(self) -> None:
        h = pd.detect_heading("[Section: Introduction]")
        assert h is not None
        assert h.name == "Introduction"
        assert h.level == 1

    def test_plaintext_all_caps(self) -> None:
        h = pd.detect_heading("INTRODUCTION")
        assert h is not None
        assert h.level == 1
        assert h.name == "INTRODUCTION"

    def test_plaintext_rejects_sentences_in_caps(self) -> None:
        # Ends with period — should NOT be a heading.
        assert pd.detect_heading("THIS IS A SENTENCE.") is None

    def test_plaintext_rejects_mixed_case(self) -> None:
        assert pd.detect_heading("Introduction") is None

    def test_rejects_blank(self) -> None:
        assert pd.detect_heading("") is None
        assert pd.detect_heading("   ") is None

    def test_rejects_prose(self) -> None:
        assert pd.detect_heading("This is a regular sentence.") is None


class TestBuildInventory:
    def test_empty_document(self) -> None:
        inv = pd.build_inventory("", audit_slug="t")
        assert inv["sections"] == []
        assert inv["paragraphs"] == []
        # Empty SHA-256
        assert inv["metadata"]["source_sha256"] == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        _validate(inv)

    def test_no_headings_creates_preamble(self) -> None:
        inv = pd.build_inventory("First paragraph.\n\nSecond paragraph.\n", audit_slug="t")
        assert len(inv["sections"]) == 1
        assert inv["sections"][0]["name"] == "Preamble"
        assert inv["sections"][0]["id"] == "S001"
        assert len(inv["paragraphs"]) == 2
        _validate(inv)

    def test_skips_preamble_when_doc_starts_with_heading(self) -> None:
        inv = pd.build_inventory("# Intro\n\nbody.\n", audit_slug="t")
        assert len(inv["sections"]) == 1
        assert inv["sections"][0]["id"] == "S001"
        assert inv["sections"][0]["name"] == "Intro"

    def test_multi_section(self) -> None:
        text = "# A\n\npara1\n\npara2\n\n# B\n\npara3\n"
        inv = pd.build_inventory(text, audit_slug="t")
        assert [s["name"] for s in inv["sections"]] == ["A", "B"]
        assert len(inv["paragraphs"]) == 3
        # Section A has paragraphs P001, P002.
        section_a = inv["sections"][0]
        assert section_a["paragraph_ids"] == ["P001", "P002"]
        # Section B has paragraph P003.
        assert inv["sections"][1]["paragraph_ids"] == ["P003"]
        _validate(inv)

    def test_ordinals_restart_per_section(self) -> None:
        text = "# A\n\nx\n\ny\n\n# B\n\nz\n"
        inv = pd.build_inventory(text, audit_slug="t")
        section_to_ords = {}
        for p in inv["paragraphs"]:
            section_to_ords.setdefault(p["section_id"], []).append(p["ordinal"])
        # Each section's ordinals start at 1.
        for ords in section_to_ords.values():
            assert ords[0] == 1
            assert ords == sorted(ords)

    def test_sha256_stable_under_whitespace_jitter(self) -> None:
        a = pd.build_inventory("# A\n\nbody\n", audit_slug="t")
        b = pd.build_inventory("# A   \r\n\r\nbody  \n\n\n", audit_slug="t")
        assert a["metadata"]["source_sha256"] == b["metadata"]["source_sha256"]

    def test_sha256_changes_with_content(self) -> None:
        a = pd.build_inventory("body\n", audit_slug="t")
        b = pd.build_inventory("body!\n", audit_slug="t")
        assert a["metadata"]["source_sha256"] != b["metadata"]["source_sha256"]

    def test_strips_wrapper(self) -> None:
        wrapped = "<document>\n# A\n\nbody\n</document>\n"
        inv = pd.build_inventory(wrapped, audit_slug="t")
        assert inv["sections"][0]["name"] == "A"

    def test_id_pattern_compliant(self) -> None:
        text = "# A\n\nbody\n"
        inv = pd.build_inventory(text, audit_slug="t")
        for s in inv["sections"]:
            assert s["id"].startswith("S")
            assert len(s["id"]) >= 4
        for p in inv["paragraphs"]:
            assert p["id"].startswith("P")

    def test_overrides_initially_empty(self) -> None:
        inv = pd.build_inventory("body\n", audit_slug="t")
        assert inv["overrides"] == []


class TestResolveLocation:
    def test_no_override_returns_baseline(self) -> None:
        inv = pd.build_inventory("# A\n\nbody\n", audit_slug="t")
        sid = inv["sections"][0]["id"]
        pid = inv["paragraphs"][0]["id"]
        section, paragraph = pd.resolve_location(inv, section_id=sid, paragraph_id=pid)
        assert section["name"] == "A"
        assert paragraph["ordinal"] == 1

    def test_section_name_override_applied(self) -> None:
        inv = pd.build_inventory("# A\n\nbody\n", audit_slug="t")
        inv["overrides"].append(
            {
                "kind": "section_name",
                "path": "sections[0].name",
                "after": "Background",
                "reason": "merged subsection",
            }
        )
        sid = inv["sections"][0]["id"]
        pid = inv["paragraphs"][0]["id"]
        section, _ = pd.resolve_location(inv, section_id=sid, paragraph_id=pid)
        assert section["name"] == "Background"

    def test_unknown_path_silently_ignored(self) -> None:
        inv = pd.build_inventory("# A\n\nbody\n", audit_slug="t")
        inv["overrides"].append(
            {"kind": "section_name", "path": "bogus[99]", "after": "X", "reason": "test"}
        )
        sid = inv["sections"][0]["id"]
        pid = inv["paragraphs"][0]["id"]
        section, _ = pd.resolve_location(inv, section_id=sid, paragraph_id=pid)
        # Baseline name preserved (D3 catches the bad path at validate-time).
        assert section["name"] == "A"
