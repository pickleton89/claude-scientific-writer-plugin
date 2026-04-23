"""
Oligon Brand Adapter for Matplotlib / Seaborn (v5.0 — Style Guide v2.3)

Applies the Oligon Digital Style Guide v2.3 (April 2026) to matplotlib figures:
Oklch tonal ramps (Blue/Orange/Neutral × 10 steps), same-hue treatment/control
cycle, peer-vs-focus cycle split, and divergent Blue 700 → white → Orange 700
colormap.

Usage:
    from matplotlib_adapter import (
        set_brand_style,
        select_cycle,
        run_preflight,
        validate_palette,
        count_brand_blue,
        get_brand_compliance_report,
        BRAND_COLORS,
        CYCLE_TREATMENT_CONTROL,
        CYCLE_PEER, CYCLE_FOCUS,
        CYCLE_OPPOSING,
        CYCLE_MULTI_CATEGORY,
    )

    cycle_name, colors = select_cycle(n_series=2, context='comparison')
    set_brand_style(cycle_name)

    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])

    print(get_brand_compliance_report(fig))

Breaking changes from v4 (#E8622D palette):
    * CYCLE_TREATMENT_CONTROL is a same-hue pair now (brand.blue + blue.300).
    * CYCLE_PEER and CYCLE_FOCUS replace the old single Cycle 2.
    * CYCLE_OPPOSING uses blue.600 + orange.600 instead of brand.blue + #E8622D.
    * VOLCANO_COLORS down/up = blue.600 / orange.600, ns = neutral.300.
    * Divergent colormap is a 3-stop blue.700 → white → orange.700.
    * Retired hexes (#E8622D, #7D250F, #0F5D7D, #158BBB, #222222 control) no
      longer appear in ALLOWED_COLORS.
"""

import json
from pathlib import Path
from typing import Optional, Literal

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap
import numpy as np


# =============================================================================
# LOAD BRAND TOKENS
# =============================================================================

def _load_brand_tokens() -> dict:
    """Load brand tokens from JSON file."""
    tokens_path = Path(__file__).parent.parent / "tokens" / "brand-tokens.json"
    if tokens_path.exists():
        with open(tokens_path, 'r') as f:
            return json.load(f)
    return _get_default_tokens()


def _get_default_tokens() -> dict:
    """Minimal fallback tokens if JSON not available."""
    return {
        "colors": {
            "brand_anchor": {"brand_blue": {"hex": "#2DB2E8"}},
            "ramps": {
                "blue": {
                    "50":  {"hex": "#EFFBFF"}, "100": {"hex": "#DBF3FF"},
                    "200": {"hex": "#B3E3FC"}, "300": {"hex": "#76CAF3"},
                    "400": {"hex": "#1FACE3"}, "500": {"hex": "#008ECB"},
                    "600": {"hex": "#006EA6"}, "700": {"hex": "#00507E"},
                    "800": {"hex": "#003454"}, "900": {"hex": "#001A2E"},
                },
                "orange": {
                    "50":  {"hex": "#FFF5F1"}, "100": {"hex": "#FFE8E0"},
                    "200": {"hex": "#FFCEBD"}, "300": {"hex": "#F0AA92"},
                    "400": {"hex": "#DD8363"}, "500": {"hex": "#C45E39"},
                    "600": {"hex": "#A0421D"}, "700": {"hex": "#772E11"},
                    "800": {"hex": "#4F1B06"}, "900": {"hex": "#2B0901"},
                },
                "neutral": {
                    "50":  {"hex": "#F3FAFD"}, "100": {"hex": "#E9F0F3"},
                    "200": {"hex": "#D6DCDF"}, "300": {"hex": "#B9BFC2"},
                    "400": {"hex": "#9A9FA2"}, "500": {"hex": "#7C8184"},
                    "600": {"hex": "#5F6467"}, "700": {"hex": "#44494B"},
                    "800": {"hex": "#2A2F31"}, "900": {"hex": "#121719"},
                },
            },
        }
    }


_TOKENS = _load_brand_tokens()


# =============================================================================
# COLOR CONSTANTS
# =============================================================================

# Brand anchor
BRAND_BLUE = '#2DB2E8'

# Blue ramp (10 steps)
BLUE_50   = '#EFFBFF'
BLUE_100  = '#DBF3FF'
BLUE_200  = '#B3E3FC'
BLUE_300  = '#76CAF3'
BLUE_400  = '#1FACE3'
BLUE_500  = '#008ECB'
BLUE_600  = '#006EA6'
BLUE_700  = '#00507E'
BLUE_800  = '#003454'
BLUE_900  = '#001A2E'

# Orange ramp (10 steps)
ORANGE_50   = '#FFF5F1'
ORANGE_100  = '#FFE8E0'
ORANGE_200  = '#FFCEBD'
ORANGE_300  = '#F0AA92'
ORANGE_400  = '#DD8363'
ORANGE_500  = '#C45E39'
ORANGE_600  = '#A0421D'
ORANGE_700  = '#772E11'
ORANGE_800  = '#4F1B06'
ORANGE_900  = '#2B0901'

# Neutral ramp (10 steps)
NEUTRAL_50   = '#F3FAFD'
NEUTRAL_100  = '#E9F0F3'
NEUTRAL_200  = '#D6DCDF'
NEUTRAL_300  = '#B9BFC2'
NEUTRAL_400  = '#9A9FA2'
NEUTRAL_500  = '#7C8184'
NEUTRAL_600  = '#5F6467'
NEUTRAL_700  = '#44494B'
NEUTRAL_800  = '#2A2F31'
NEUTRAL_900  = '#121719'

WHITE = '#FFFFFF'
BLACK = '#000000'

BRAND_COLORS = {
    # Brand anchor
    'brand_blue':  BRAND_BLUE,

    # Blue ramp
    'blue_50':   BLUE_50,  'blue_100': BLUE_100, 'blue_200': BLUE_200,
    'blue_300':  BLUE_300, 'blue_400': BLUE_400, 'blue_500': BLUE_500,
    'blue_600':  BLUE_600, 'blue_700': BLUE_700, 'blue_800': BLUE_800,
    'blue_900':  BLUE_900,

    # Orange ramp
    'orange_50':   ORANGE_50,  'orange_100': ORANGE_100, 'orange_200': ORANGE_200,
    'orange_300':  ORANGE_300, 'orange_400': ORANGE_400, 'orange_500': ORANGE_500,
    'orange_600':  ORANGE_600, 'orange_700': ORANGE_700, 'orange_800': ORANGE_800,
    'orange_900':  ORANGE_900,

    # Neutral ramp
    'neutral_50':   NEUTRAL_50,  'neutral_100': NEUTRAL_100, 'neutral_200': NEUTRAL_200,
    'neutral_300':  NEUTRAL_300, 'neutral_400': NEUTRAL_400, 'neutral_500': NEUTRAL_500,
    'neutral_600':  NEUTRAL_600, 'neutral_700': NEUTRAL_700, 'neutral_800': NEUTRAL_800,
    'neutral_900':  NEUTRAL_900,

    # Structure
    'white': WHITE,
    'black': BLACK,
}

# Semantic tokens (light theme) — prefer these in new code
SEMANTIC_LIGHT = {
    'page':       WHITE,
    'surface':    NEUTRAL_50,
    'border':     NEUTRAL_200,
    'text':       NEUTRAL_900,
    'text_muted': NEUTRAL_700,
    'accent':     BLUE_700,
    'brand':      BRAND_BLUE,
    'signal':     ORANGE_700,
}

SEMANTIC_DARK = {
    'page':    BLUE_900,
    'surface': BLUE_800,
    'text':    NEUTRAL_50,
    'accent':  BLUE_300,
    'brand':   BRAND_BLUE,
}


# =============================================================================
# COLOR CYCLES (Rule 1 — choose from data structure)
# =============================================================================

# Cycle 1 — Treatment / Control: same-hue pair, lightness hierarchy.
# Treatment in Brand Blue, control in Blue 300.
CYCLE_TREATMENT_CONTROL = [BRAND_BLUE, BLUE_300]

# Cycle 2 — Peer: N equal-weight arms, no promotion.
CYCLE_PEER_4 = [BLUE_800, BLUE_600, BLUE_400, BLUE_200]
CYCLE_PEER_3 = [BLUE_700, BLUE_500, BLUE_300]

# Cycle 2 — Focus: N arms with one promoted.
# Three background arms in receding Blue + one focus variant.
CYCLE_FOCUS_RECEDING = [BLUE_500, BLUE_300, BLUE_200]
FOCUS_VARIANTS = {
    'default':       ORANGE_500,  # Categorical focus (default)
    'soft':          ORANGE_400,  # Softer promotion
    'monochromatic': BLUE_800,    # More-of-the-same promotion
}
# Default focus cycle: 3 receding + orange focus
CYCLE_FOCUS = [*CYCLE_FOCUS_RECEDING, FOCUS_VARIANTS['default']]

# Cycle 3 — Opposing: signed/directional effects.
CYCLE_OPPOSING = [BLUE_600, ORANGE_600, NEUTRAL_300]

# Cycle 4 — Multi-Category: 3-4 categories with one conceptual outlier.
CYCLE_MULTI_CATEGORY = [BLUE_800, BLUE_500, BLUE_300, ORANGE_500]

# Volcano plot (Cycle 3 convention)
VOLCANO_COLORS = {
    'nonsig': NEUTRAL_300,   # neutral.300
    'up':     ORANGE_600,    # orange.600
    'down':   BLUE_600,      # blue.600
}

# Marker shapes mandatory under Cycle 4 for accessibility
MARKER_SHAPES = ['o', 's', '^', 'D']  # circle, square, triangle, diamond

# Back-compat alias: "neutrals_only" is superseded by Peer, but some callers may
# still ask for it. Route to the 3-arm Peer cycle.
CYCLE_NEUTRALS_ONLY = CYCLE_PEER_3


# =============================================================================
# STYLE CONFIGURATION
# =============================================================================

CycleType = Literal[
    'treatment_control',
    'peer', 'peer_3', 'peer_4',
    'focus',
    'opposing',
    'multi_category',
    'neutrals_only',  # deprecated alias for peer_3
]


def _resolve_cycle(cycle: CycleType) -> list:
    return {
        'treatment_control': CYCLE_TREATMENT_CONTROL,
        'peer':              CYCLE_PEER_4,
        'peer_3':            CYCLE_PEER_3,
        'peer_4':            CYCLE_PEER_4,
        'focus':             CYCLE_FOCUS,
        'opposing':          CYCLE_OPPOSING,
        'multi_category':    CYCLE_MULTI_CATEGORY,
        'neutrals_only':     CYCLE_PEER_3,
    }.get(cycle, CYCLE_TREATMENT_CONTROL)


def set_brand_style(cycle: CycleType = 'treatment_control') -> None:
    """
    Apply Oligon brand v5.0 / Style Guide v2.3 defaults to matplotlib.

    Type sizes follow the Figure Type Scale: title 12 pt, axis 10 pt,
    tick 9 pt, legend 8.5 pt. Axis furniture draws from neutral.900 so
    structure reads as structure, not as content.
    """
    selected_cycle = _resolve_cycle(cycle)

    plt.rcParams.update({
        # Figure
        'figure.facecolor': 'white',
        'figure.edgecolor': 'white',
        'figure.dpi': 150,
        'savefig.dpi': 300,
        'savefig.facecolor': 'white',
        'savefig.edgecolor': 'white',
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.1,

        # Axes (Figure Type Scale)
        'axes.facecolor': 'white',
        'axes.edgecolor': NEUTRAL_900,
        'axes.linewidth': 0.8,
        'axes.grid': False,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.labelcolor': NEUTRAL_900,
        'axes.labelsize': 10,   # axis labels
        'axes.labelweight': 'normal',
        'axes.titlesize': 12,   # figure title
        'axes.titleweight': 'bold',
        'axes.prop_cycle': plt.cycler(color=selected_cycle),

        # Ticks
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'xtick.color': NEUTRAL_900,
        'ytick.color': NEUTRAL_900,
        'xtick.direction': 'out',
        'ytick.direction': 'out',

        # Grid (off by default; neutral.200 when enabled)
        'grid.color': NEUTRAL_200,
        'grid.linewidth': 0.5,
        'grid.linestyle': '--',
        'grid.alpha': 1.0,

        # Legend
        'legend.fontsize': 8.5,
        'legend.frameon': False,
        'legend.loc': 'best',

        # Font
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
        'font.size': 9,

        # Lines / markers (v2.3: 1.8–2.2 pt primary, 5–6 pt markers)
        'lines.linewidth': 2.0,
        'lines.markersize': 5.5,

        # Patches: no outline
        'patch.edgecolor': 'none',
    })


# =============================================================================
# DETERMINISTIC SELECTORS
# =============================================================================

ContextType = Literal['comparison', 'equal_weight', 'bidirectional', 'focus']


def select_cycle(
    n_series: int,
    context: ContextType = 'comparison',
    has_highlight: bool = True,
) -> tuple[str, list[str]]:
    """
    Deterministically pick a v2.3 cycle from data characteristics (Rule 1).

    Decision logic:
        n=1                            → single stroke in brand.blue
        n=2 + bidirectional            → opposing (blue.600, orange.600)
        n=2 + focus                    → focus (1 receding + 1 focus arm)
        n=2 + comparison               → treatment_control (brand.blue, blue.300)
        n=3 + equal_weight             → peer_3
        n=3 + bidirectional            → opposing
        n=3 + focus or comparison      → focus (2 receding + 1 focus arm)
        n=4 + equal_weight             → peer_4
        n=4 + focus                    → focus (3 receding + 1 focus arm)
        n=4 + comparison               → multi_category
        n>=5                           → raise (redesign with faceting)

    Returns (cycle_name, ordered hex list). Focus cycles always end in
    the promoted focus arm (orange.500 by default).
    """
    if n_series < 1:
        raise ValueError(f"n_series must be >= 1, got {n_series}")

    if n_series == 1:
        return 'single', [BRAND_BLUE]

    if n_series == 2:
        if context == 'bidirectional':
            return 'opposing', CYCLE_OPPOSING[:2]
        if context == 'focus':
            return 'focus', [CYCLE_FOCUS_RECEDING[0], FOCUS_VARIANTS['default']]
        return 'treatment_control', CYCLE_TREATMENT_CONTROL[:2]

    if n_series == 3:
        if context == 'equal_weight' or not has_highlight:
            return 'peer_3', CYCLE_PEER_3
        if context == 'bidirectional':
            return 'opposing', CYCLE_OPPOSING
        # 'focus' or 'comparison' with a narrative arm → focus cycle
        return 'focus', [*CYCLE_FOCUS_RECEDING[:2], FOCUS_VARIANTS['default']]

    if n_series == 4:
        if context == 'equal_weight' or not has_highlight:
            return 'peer_4', CYCLE_PEER_4
        if context == 'focus':
            return 'focus', CYCLE_FOCUS
        return 'multi_category', CYCLE_MULTI_CATEGORY

    raise ValueError(
        f"Too many series ({n_series}). Maximum 4 supported. "
        "Redesign using faceting or small multiples."
    )


# =============================================================================
# COLORMAPS & HELPERS
# =============================================================================

def get_divergent_cmap(name: str = 'brand_divergent') -> LinearSegmentedColormap:
    """
    v2.3 divergent colormap for heatmaps centered at zero:
    Blue 700 → white → Orange 700 (symmetric lightness).
    """
    return LinearSegmentedColormap.from_list(
        name,
        [(0.0, BLUE_700), (0.5, WHITE), (1.0, ORANGE_700)],
    )


def add_panel_label(
    ax: plt.Axes,
    label: str,
    offset: tuple = (-0.12, 1.05),
    fontsize: int = 10,
    fontweight: str = 'bold',
) -> None:
    """Add a panel label (A, B, C, ...) at the top-left of an axes."""
    ax.text(
        offset[0], offset[1],
        label,
        transform=ax.transAxes,
        fontsize=fontsize,
        fontweight=fontweight,
        va='top',
        ha='left',
        color=NEUTRAL_900,
    )


def add_error_band(
    ax: plt.Axes,
    x: np.ndarray,
    y: np.ndarray,
    yerr: np.ndarray,
    color: str,
    alpha: float = 0.18,
    label: Optional[str] = None,
) -> plt.Line2D:
    """Semi-transparent error band around a line (v2.3: alpha ~0.18)."""
    if isinstance(yerr, tuple):
        lower, upper = y - yerr[0], y + yerr[1]
    else:
        lower, upper = y - yerr, y + yerr

    ax.fill_between(x, lower, upper, color=color, alpha=alpha, linewidth=0)
    line, = ax.plot(x, y, color=color, label=label)
    return line


def plot_volcano(
    ax: plt.Axes,
    log2fc: np.ndarray,
    pval: np.ndarray,
    fc_thresh: float = 1.0,
    p_thresh: float = 0.05,
    gene_labels: Optional[np.ndarray] = None,
    n_labels: int = 10,
) -> plt.Axes:
    """
    Volcano plot in v2.3 Cycle 3 opposing: down=blue.600, up=orange.600,
    non-significant=neutral.300.
    """
    neg_log_p = -np.log10(pval)

    nonsig = (np.abs(log2fc) < fc_thresh) | (pval >= p_thresh)
    sig_up = (log2fc >= fc_thresh) & (pval < p_thresh)
    sig_down = (log2fc <= -fc_thresh) & (pval < p_thresh)

    ax.scatter(log2fc[nonsig], neg_log_p[nonsig],
               c=VOLCANO_COLORS['nonsig'], s=12, alpha=0.6, label='NS')
    ax.scatter(log2fc[sig_up], neg_log_p[sig_up],
               c=VOLCANO_COLORS['up'], s=20, alpha=0.85, label='Up')
    ax.scatter(log2fc[sig_down], neg_log_p[sig_down],
               c=VOLCANO_COLORS['down'], s=20, alpha=0.85, label='Down')

    ax.axhline(-np.log10(p_thresh), color=NEUTRAL_500, linestyle='--', linewidth=0.5)
    ax.axvline(-fc_thresh, color=NEUTRAL_500, linestyle='--', linewidth=0.5)
    ax.axvline(fc_thresh, color=NEUTRAL_500, linestyle='--', linewidth=0.5)

    ax.set_xlabel('log₂(Fold Change)')
    ax.set_ylabel('-log₁₀(p-value)')
    return ax


# =============================================================================
# PREFLIGHT VALIDATORS
# =============================================================================

# Full v2.3 palette is the allow-set (primitives + semantic tokens all map to
# ramp steps already enumerated in BRAND_COLORS).
ALLOWED_COLORS = {c.upper() for c in BRAND_COLORS.values()}


def run_preflight(fig: plt.Figure) -> dict[str, bool]:
    """
    Automated preflight validation against v2.3 brand rules.

    Returns pass/fail for:
        white_background, spines_removed, grid_off, axes_dark_enough
    """
    results = {}

    facecolor = fig.get_facecolor()
    results['white_background'] = (
        abs(facecolor[0] - 1.0) < 0.01 and
        abs(facecolor[1] - 1.0) < 0.01 and
        abs(facecolor[2] - 1.0) < 0.01
    )

    spines_ok = True
    for ax in fig.axes:
        if ax.spines['top'].get_visible() or ax.spines['right'].get_visible():
            spines_ok = False
            break
    results['spines_removed'] = spines_ok

    grid_ok = True
    allowed_grid = {'#D6DCDF', '#E5E5E5', '#E0E0E0', '#EEEEEE', '#B9BFC2',
                    'LIGHTGRAY', 'LIGHTGREY'}
    for ax in fig.axes:
        x_gridlines = ax.xaxis.get_gridlines()
        y_gridlines = ax.yaxis.get_gridlines()
        x_grid_visible = any(line.get_visible() for line in x_gridlines) if x_gridlines else False
        y_grid_visible = any(line.get_visible() for line in y_gridlines) if y_gridlines else False
        if x_grid_visible or y_grid_visible:
            for line in list(x_gridlines) + list(y_gridlines):
                if line.get_visible():
                    color = line.get_color()
                    if isinstance(color, str) and color.upper() not in allowed_grid:
                        grid_ok = False
                        break
    results['grid_off'] = grid_ok

    # Axes spines should be dark (neutral.900 or black). Accept anything with
    # low luminance so legacy code using '#000000' still passes.
    axes_dark = True
    for ax in fig.axes:
        for spine in ('left', 'bottom'):
            if ax.spines[spine].get_visible():
                ec = ax.spines[spine].get_edgecolor()
                if not (ec[0] < 0.25 and ec[1] < 0.25 and ec[2] < 0.25):
                    axes_dark = False
                    break
    results['axes_black'] = axes_dark

    return results


def extract_figure_colors(fig: plt.Figure) -> set[str]:
    """Extract all hex colors used in lines, collections, and patches."""
    colors = set()

    def _to_hex(color) -> Optional[str]:
        if color is None:
            return None
        if isinstance(color, str):
            if color.startswith('#'):
                return color.upper()
            try:
                rgb = mpl.colors.to_rgb(color)
                return '#{:02X}{:02X}{:02X}'.format(
                    int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
            except ValueError:
                return None
        if hasattr(color, '__len__') and len(color) >= 3:
            return '#{:02X}{:02X}{:02X}'.format(
                int(color[0] * 255), int(color[1] * 255), int(color[2] * 255))
        return None

    for ax in fig.axes:
        for line in ax.get_lines():
            hx = _to_hex(line.get_color())
            if hx:
                colors.add(hx)
        for coll in ax.collections:
            for fc in coll.get_facecolor():
                hx = _to_hex(fc)
                if hx:
                    colors.add(hx)
            for ec in coll.get_edgecolor():
                hx = _to_hex(ec)
                if hx:
                    colors.add(hx)
        for patch in ax.patches:
            hx = _to_hex(patch.get_facecolor())
            if hx:
                colors.add(hx)

    return colors


def get_preflight_report(fig: plt.Figure) -> str:
    """Human-readable preflight report."""
    results = run_preflight(fig)
    lines = ["Oligon Brand Preflight Check (v2.3)", "=" * 35]
    for check, passed in results.items():
        lines.append(f"{'✓' if passed else '✗'} {check}")
    passed_count = sum(results.values())
    total = len(results)
    status = "PASS" if passed_count == total else "FAIL"
    lines += ["", f"Result: {status} ({passed_count}/{total} checks passed)"]
    return "\n".join(lines)


def validate_palette(fig: plt.Figure) -> dict:
    """Validate all figure colors are v2.3 brand-compliant."""
    used_colors = extract_figure_colors(fig)
    structural = {'#FFFFFF', '#000000'}
    violations = used_colors - ALLOWED_COLORS - structural
    return {
        'valid': len(violations) == 0,
        'used_colors': used_colors,
        'violations': violations,
        'allowed_colors': ALLOWED_COLORS.copy(),
    }


def count_brand_blue(fig: plt.Figure) -> dict:
    """
    Count Brand Blue (#2DB2E8) uses; v2.3 keeps the 1–2 per panel limit.
    """
    target = BRAND_BLUE.upper()
    per_axes = {}
    violations = []

    def _is_brand_blue(color) -> bool:
        if color is None:
            return False
        if isinstance(color, str):
            if color.upper() == target:
                return True
            if color.startswith('#'):
                return color.upper() == target
            try:
                rgb = mpl.colors.to_rgb(color)
                hx = '#{:02X}{:02X}{:02X}'.format(
                    int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
                return hx == target
            except ValueError:
                return False
        if hasattr(color, '__len__') and len(color) >= 3:
            hx = '#{:02X}{:02X}{:02X}'.format(
                int(color[0] * 255), int(color[1] * 255), int(color[2] * 255))
            return hx == target
        return False

    for ax_idx, ax in enumerate(fig.axes):
        count = 0
        for line in ax.get_lines():
            if _is_brand_blue(line.get_color()):
                count += 1
        for coll in ax.collections:
            facecolors = coll.get_facecolor()
            if len(facecolors) > 0:
                if any(_is_brand_blue(fc) for fc in facecolors):
                    count += 1
        for patch in ax.patches:
            if _is_brand_blue(patch.get_facecolor()):
                count += 1
        per_axes[ax_idx] = count
        if count > 2:
            violations.append(ax_idx)

    return {
        'total_count': sum(per_axes.values()),
        'per_axes': per_axes,
        'compliant': len(violations) == 0,
        'violations': violations,
    }


def get_brand_compliance_report(fig: plt.Figure) -> str:
    """Combined preflight + palette + brand-blue usage report."""
    lines = ["Oligon Brand Compliance Report (v2.3)", "=" * 37, ""]

    preflight = run_preflight(fig)
    lines.append("PREFLIGHT CHECKS:")
    for check, passed in preflight.items():
        lines.append(f"  {'✓' if passed else '✗'} {check}")
    lines.append("")

    palette = validate_palette(fig)
    lines.append("PALETTE VALIDATION:")
    if palette['valid']:
        lines.append("  ✓ All colors are brand-compliant")
    else:
        lines.append("  ✗ Non-brand colors detected:")
        for violation in sorted(palette['violations']):
            lines.append(f"    - {violation}")
    lines.append("")

    brand_blue = count_brand_blue(fig)
    lines.append("BRAND BLUE USAGE:")
    lines.append(f"  Total elements: {brand_blue['total_count']}")
    if brand_blue['compliant']:
        lines.append("  ✓ Within limit (≤2 per panel)")
    else:
        lines.append("  ✗ Exceeds limit in panels:")
        for ax_idx in brand_blue['violations']:
            lines.append(f"    - Axes {ax_idx}: {brand_blue['per_axes'][ax_idx]} elements")
    lines.append("")

    all_passed = all(preflight.values()) and palette['valid'] and brand_blue['compliant']
    lines.append(f"OVERALL: {'PASS' if all_passed else 'FAIL'}")
    return "\n".join(lines)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_color(name: str) -> str:
    """Look up a brand color by name (supports ramp-step and legacy keys)."""
    return BRAND_COLORS.get(name, '#000000')


def get_cycle(name: CycleType) -> list:
    """Look up a cycle by name."""
    return _resolve_cycle(name)


def get_semantic(token: str, theme: str = 'light') -> str:
    """Resolve a semantic token (page, surface, text, accent, brand, signal, border)."""
    if theme == 'dark':
        return SEMANTIC_DARK.get(token, SEMANTIC_LIGHT.get(token, '#000000'))
    return SEMANTIC_LIGHT.get(token, '#000000')
