"""Tests for preflight_check.check_garbled_text (AI-figure-slop Track B, §3).

The #1 categorical AI tell: lexically-void glyph strings in <text>/<tspan>
("Tramioncatiion", mixed-script runs, consonant scrambles). Void tokens emit
severity "categorical" (dominant); ambiguous tokens emit "warn"; clean tokens
(genes, units, p-values, Greek, real sentences) pass. Thresholds are
PROVISIONAL/UNCALIBRATED.
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# The check lives in the sibling script preflight_check.py (one dir up).
SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from preflight_check import check_garbled_text  # noqa: E402

WRAP = '<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">{}</svg>'


def _run(inner):
    root = ET.fromstring(WRAP.format(inner))
    return check_garbled_text(root)


def test_void_frontiers_token_is_categorical():
    # "Tramioncatiion" — letter-pileup + consonant patterns
    f = _run("<text>Tramioncatiion of cells</text>")
    assert any(x["severity"] == "categorical" for x in f)


def test_mixed_script_is_categorical():
    # Latin 'dis' + Cyrillic 'о' lookalikes inside one token
    f = _run("<text>diѕlоsttal</text>")  # ѕ + о (Cyrillic) in a Latin run
    assert any(
        x["severity"] == "categorical" and "mixed-script" in x["message"] for x in f
    )


def test_gene_symbols_and_pvalues_pass():
    f = _run("<text>TP53</text><text>JAK2</text><text>p&lt;0.05</text><text>CD4</text>")
    assert all(x["severity"] == "pass" for x in f)


def test_units_and_ranges_pass():
    f = _run(
        "<text>60%</text><text>0-100</text><text>kDa</text>"
        "<text>µL</text><text>1.2e-3</text>"
    )
    assert all(x["severity"] == "pass" for x in f)


def test_greek_and_short_ticks_pass():
    f = _run("<text>α</text><text>ΔΔCt</text><text>log</text><text>A</text>")
    assert all(x["severity"] == "pass" for x in f)


def test_consonant_scramble_is_categorical():
    f = _run("<text>dssilcedwxz</text>")  # no-vowels + consonant-run
    assert any(x["severity"] == "categorical" for x in f)


def test_real_sentence_passes():
    f = _run("<text>Treatment reduced tumor volume by 60 percent</text>")
    assert all(x["severity"] == "pass" for x in f)
