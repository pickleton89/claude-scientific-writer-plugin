#!/usr/bin/env python3
"""
Oligon Scientific Brand — Matplotlib Setup (v5.0 / Style Guide v2.3)
====================================================================

Thin wrapper that installs `oligon_color_brand.mplstyle` into matplotlib's
stylelib and re-exports the canonical tokens, cycles, and helpers from
`adapters/matplotlib_adapter.py`. Nothing is duplicated — the adapter is
the single source of truth.

Usage:
    # Install stylesheet once:
    $ python scripts/matplotlib_brand_setup.py

    # Then in any script:
    import matplotlib.pyplot as plt
    plt.style.use('oligon_color_brand')

    # For full v5.0 token + cycle access, import the adapter:
    from matplotlib_adapter import (
        set_brand_style, select_cycle,
        BRAND_BLUE, BLUE_600, ORANGE_500, ORANGE_600, NEUTRAL_900,
        CYCLE_TREATMENT_CONTROL, CYCLE_PEER_4, CYCLE_FOCUS,
        CYCLE_OPPOSING, CYCLE_MULTI_CATEGORY,
        get_divergent_cmap, run_preflight, validate_palette,
    )

Running this module directly (`python matplotlib_brand_setup.py`) copies
the `.mplstyle` file into `matplotlib.get_configdir()/stylelib/` so
`plt.style.use('oligon_color_brand')` works without an absolute path.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import matplotlib

# Re-export v5.0 tokens + cycles + validators from the adapter so
# callers that do `from matplotlib_brand_setup import *` continue to
# work but always get current values.
_ADAPTER_DIR = Path(__file__).resolve().parent.parent / "adapters"
sys.path.insert(0, str(_ADAPTER_DIR))


_STYLE_FILE = (
    Path(__file__).resolve().parent.parent / "assets" / "oligon_color_brand.mplstyle"
)


def install_stylesheet(dest_dir: Path | None = None) -> Path:
    """
    Copy `oligon_color_brand.mplstyle` into matplotlib's stylelib so it's
    discoverable by `plt.style.use('oligon_color_brand')`.

    Parameters
    ----------
    dest_dir : Path, optional
        Target stylelib directory. Defaults to
        `matplotlib.get_configdir() / 'stylelib'`.

    Returns
    -------
    Path
        The installed file's path.
    """
    if not _STYLE_FILE.exists():
        raise FileNotFoundError(f"Style file not found: {_STYLE_FILE}")

    if dest_dir is None:
        dest_dir = Path(matplotlib.get_configdir()) / "stylelib"

    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / _STYLE_FILE.name
    shutil.copy2(_STYLE_FILE, dest)
    return dest


if __name__ == "__main__":
    installed = install_stylesheet()
    print(f"Installed Oligon brand style: {installed}")
    print("In matplotlib scripts:  plt.style.use('oligon_color_brand')")
