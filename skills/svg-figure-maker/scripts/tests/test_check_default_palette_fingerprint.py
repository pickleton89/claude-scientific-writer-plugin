"""Tests for preflight_check.check_default_palette_fingerprint (Track B, §4).

A SOFT, two-sided regression-to-mean tell: tool-default colour sequences
(matplotlib tab10, Excel, seaborn deep) used as data colours read as untouched
defaults. Fires "warn" only, and only on a >=3-hex default run; brand-palette
matches are exempt (no double-report with check_palette_compliance). Thresholds
are PROVISIONAL/UNCALIBRATED.
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from preflight_check import check_default_palette_fingerprint  # noqa: E402

WRAP = '<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">{}</svg>'


def _runp(inner, palette=None):
    root = ET.fromstring(WRAP.format(inner))
    return check_default_palette_fingerprint(root, palette)


def test_three_tab10_hexes_warn():
    inner = '<rect fill="#1f77b4"/><rect fill="#ff7f0e"/><rect fill="#2ca02c"/>'
    f = _runp(inner)
    assert any(x["severity"] == "warn" and "tab10" in x["message"] for x in f)


def test_two_tab10_hexes_pass():
    inner = '<rect fill="#1f77b4"/><rect fill="#ff7f0e"/>'
    f = _runp(inner)
    assert all(x["severity"] == "pass" for x in f)  # below 3-hit floor


def test_tab10_hexes_in_brand_palette_are_exempt():
    inner = '<rect fill="#1f77b4"/><rect fill="#ff7f0e"/><rect fill="#2ca02c"/>'
    # All three declared as brand colours -> not a fingerprint.
    f = _runp(inner, palette={"#1F77B4", "#FF7F0E", "#2CA02C"})
    assert all(x["severity"] == "pass" for x in f)


def test_excel_default_run_warns():
    inner = '<rect fill="#4472C4"/><rect fill="#ED7D31"/><rect fill="#A5A5A5"/>'
    f = _runp(inner)
    assert any(x["severity"] == "warn" and "excel" in x["message"].lower() for x in f)


def test_clean_brand_only_passes():
    inner = '<rect fill="#2DB2E8"/><rect fill="#E8622D"/><rect fill="#1B2A4A"/>'
    f = _runp(inner)
    assert all(x["severity"] == "pass" for x in f)
