"""Tests for the Phase 3 evidence-pinned marker on rendered audit reports.

Covers `render_report.generate_report()`'s `artifact_paths` kwarg:
  - marker is the first line of rendered output when artifact_paths supplied
  - marker is absent when artifact_paths is None (back-compat)
  - marker format matches plan §7.1 spec exactly
  - in required-enforcement mode, refuses to render with incomplete artifact set
  - `--no-enforce-artifacts` style override (enforcement="advisory" kwarg) allows
    incomplete artifact sets to render anyway
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

from render_report import (
    _ARTIFACT_FILENAMES,
    _ARTIFACT_KINDS,
    _MARKER_SCHEMA_VERSION,
    generate_report,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "audit_minimal"

_MARKER_RE = re.compile(
    r"^<!-- audit_evidence_pinned: true "
    r"artifacts: (?P<artifacts>[^ ]+) "
    r"audit_dir: (?P<audit_dir>[^ ]+) "
    r"schema_version: (?P<schema_version>[^ ]+) -->$"
)


def _audit_minimal_report() -> dict[str, Any]:
    return json.loads((FIXTURE_DIR / "audit_report.json").read_text())


def _all_artifact_paths(audit_dir: Path) -> dict[str, Path]:
    return {kind: audit_dir / fname for kind, fname in _ARTIFACT_FILENAMES.items()}


class TestMarkerPresence:
    def test_marker_absent_when_artifact_paths_none(self) -> None:
        md = generate_report(_audit_minimal_report())
        assert not md.startswith("<!-- audit_evidence_pinned")
        # First content should be the audit header.
        assert md.lstrip().startswith("# Accuracy Audit")

    def test_marker_present_when_artifact_paths_supplied(
        self, tmp_path: Path
    ) -> None:
        # Create stub files (presence is sufficient when enforcement is advisory).
        for fname in _ARTIFACT_FILENAMES.values():
            (tmp_path / fname).write_text("{}")
        md = generate_report(
            _audit_minimal_report(),
            artifact_paths=_all_artifact_paths(tmp_path),
            audit_dir=tmp_path,
            enforcement="advisory",
        )
        first_line = md.split("\n", 1)[0]
        assert first_line.startswith("<!-- audit_evidence_pinned: true ")
        assert first_line.endswith(" -->")


class TestMarkerFormat:
    def test_marker_matches_spec_regex(self, tmp_path: Path) -> None:
        for fname in _ARTIFACT_FILENAMES.values():
            (tmp_path / fname).write_text("{}")
        md = generate_report(
            _audit_minimal_report(),
            artifact_paths=_all_artifact_paths(tmp_path),
            audit_dir=tmp_path,
            enforcement="advisory",
        )
        first_line = md.split("\n", 1)[0]
        m = _MARKER_RE.match(first_line)
        assert m is not None, f"marker didn't match spec regex: {first_line!r}"

        # All 4 canonical artifact filenames listed in canonical order.
        artifacts_str = m.group("artifacts")
        assert artifacts_str.split(",") == [
            _ARTIFACT_FILENAMES[k] for k in _ARTIFACT_KINDS
        ]
        # audit_dir has trailing slash per plan §7.1.
        assert m.group("audit_dir").endswith("/")
        assert m.group("schema_version") == _MARKER_SCHEMA_VERSION

    def test_audit_dir_derived_from_paths_when_omitted(
        self, tmp_path: Path
    ) -> None:
        for fname in _ARTIFACT_FILENAMES.values():
            (tmp_path / fname).write_text("{}")
        md = generate_report(
            _audit_minimal_report(),
            artifact_paths=_all_artifact_paths(tmp_path),
            audit_dir=None,
            enforcement="advisory",
        )
        first_line = md.split("\n", 1)[0]
        m = _MARKER_RE.match(first_line)
        assert m is not None
        # Should be the tmp_path with trailing slash.
        assert m.group("audit_dir") == str(tmp_path) + "/"


class TestRequiredModeRefusesIncomplete:
    def test_required_refuses_when_path_missing(self) -> None:
        """All 4 paths omitted from the dict → all 4 are missing → raise."""
        with pytest.raises(ValueError, match="artifact set incomplete"):
            generate_report(
                _audit_minimal_report(),
                artifact_paths={},  # nothing supplied
                enforcement="required",
            )

    def test_required_refuses_when_file_nonexistent(self, tmp_path: Path) -> None:
        # Path supplied but the file doesn't exist on disk.
        paths = _all_artifact_paths(tmp_path)  # tmp_path is empty
        with pytest.raises(ValueError, match="not found"):
            generate_report(
                _audit_minimal_report(),
                artifact_paths=paths,
                enforcement="required",
            )

    def test_required_succeeds_when_all_files_present(self, tmp_path: Path) -> None:
        for fname in _ARTIFACT_FILENAMES.values():
            (tmp_path / fname).write_text("{}")
        md = generate_report(
            _audit_minimal_report(),
            artifact_paths=_all_artifact_paths(tmp_path),
            audit_dir=tmp_path,
            enforcement="required",
        )
        assert md.split("\n", 1)[0].startswith("<!-- audit_evidence_pinned: true ")


class TestEscapeHatch:
    def test_advisory_override_allows_incomplete_artifact_set(self) -> None:
        """`enforcement="advisory"` mirrors `--no-enforce-artifacts` and lets
        renders proceed with missing files (the marker still appears so
        downstream consumers know which artifacts were intended)."""
        md = generate_report(
            _audit_minimal_report(),
            artifact_paths={},  # no files
            enforcement="advisory",
        )
        # Still renders, still has the marker (even though files are missing).
        assert md.split("\n", 1)[0].startswith("<!-- audit_evidence_pinned: true ")
