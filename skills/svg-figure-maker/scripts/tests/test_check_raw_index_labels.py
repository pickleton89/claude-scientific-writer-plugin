"""Tests for preflight_check.check_raw_index_labels (Track B, §3).

A SOFT tell: axis tick labels rendered as bare sequential integers (0,1,2,... /
1,2,3,...) where categorical labels were likely intended. Fires "warn" only on a
dense, step-1, 0/1-based run with no competing numeric-axis signal; genuine
numeric axes (decimals, step>1, short runs, real category names) pass.
Thresholds are PROVISIONAL/UNCALIBRATED.
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from preflight_check import check_raw_index_labels  # noqa: E402

WRAP = '<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">{}</svg>'


def _runi(inner):
    root = ET.fromstring(WRAP.format(inner))
    return check_raw_index_labels(root)


def test_index_run_zero_based_warns():
    inner = "".join(f"<text>{i}</text>" for i in range(0, 6))  # 0..5
    f = _runi(inner)
    assert any(x["severity"] == "warn" for x in f)


def test_index_run_one_based_warns():
    inner = "".join(f"<text>{i}</text>" for i in range(1, 7))  # 1..6
    f = _runi(inner)
    assert any(x["severity"] == "warn" for x in f)


def test_short_run_passes():
    inner = "<text>0</text><text>1</text><text>2</text>"  # 3 ticks
    f = _runi(inner)
    assert all(x["severity"] == "pass" for x in f)


def test_numeric_axis_with_decimals_passes():
    inner = (
        "<text>0.0</text><text>0.5</text><text>1.0</text>"
        "<text>1.5</text><text>2.0</text>"
    )
    f = _runi(inner)
    assert all(x["severity"] == "pass" for x in f)


def test_step_five_integer_axis_passes():
    inner = "<text>0</text><text>5</text><text>10</text><text>15</text><text>20</text>"
    f = _runi(inner)
    assert all(x["severity"] == "pass" for x in f)


def test_categorical_labels_present_passes():
    inner = "<text>Control</text><text>Low</text><text>Med</text><text>High</text>"
    f = _runi(inner)
    assert all(x["severity"] == "pass" for x in f)
