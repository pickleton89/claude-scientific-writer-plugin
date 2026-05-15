"""
Oligon Brand Adapter for Matplotlib/Seaborn

This module provides functions and constants for applying Oligon scientific
brand identity to matplotlib and seaborn visualizations.

Usage:
    from oligon_brand.adapters.matplotlib_adapter import (
        set_brand_style,
        select_cycle,
        run_preflight,
        validate_palette,
        count_brand_blue,
        get_brand_compliance_report,
        BRAND_COLORS,
        CYCLE_TREATMENT_CONTROL,
    )

    # Deterministically select color cycle
    cycle_name, colors = select_cycle(n_series=2, context='comparison')

    # Apply brand style
    set_brand_style(cycle_name)

    # Create your plot...
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])

    # Validate brand compliance (full validation)
    preflight = run_preflight(fig)
    palette = validate_palette(fig)
    brand_blue = count_brand_blue(fig)

    assert all(preflight.values()), "Preflight failed"
    assert palette['valid'], f"Non-brand colors: {palette['violations']}"
    assert brand_blue['compliant'], "Too many Brand Blue elements"

    # Or use the comprehensive report
    print(get_brand_compliance_report(fig))
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
    else:
        # Fallback to embedded defaults
        return _get_default_tokens()

def _get_default_tokens() -> dict:
    """Fallback brand tokens if JSON not available."""
    return {
        "colors": {
            "primary": {"brand_blue": {"hex": "#2DB2E8"}},
            "contrast": {"contrast_orange": {"hex": "#E8622D"}, "dark_warm": {"hex": "#7D250F"}},
            "neutrals": {
                "dark_gray": {"hex": "#222222"},
                "medium_gray": {"hex": "#666666"},
                "muted_gray": {"hex": "#999999"},
                "light_gray": {"hex": "#BDBDBD"}
            },
            "supporting_blues": {
                "medium_blue": {"hex": "#158BBB"},
                "dark_teal": {"hex": "#0F5D7D"}
            },
            "structure": {
                "white": {"hex": "#FFFFFF"},
                "black": {"hex": "#000000"},
                "gridline": {"hex": "#E5E5E5"}
            }
        }
    }

_TOKENS = _load_brand_tokens()

# =============================================================================
# COLOR CONSTANTS
# =============================================================================

BRAND_COLORS = {
    # Primary highlight
    'brand_blue': '#2DB2E8',

    # Neutrals (for data)
    'dark_gray': '#222222',
    'medium_gray': '#666666',
    'muted_gray': '#999999',
    'light_gray': '#BDBDBD',  # annotations only

    # Contrast
    'contrast_orange': '#E8622D',
    'dark_warm': '#7D250F',

    # Supporting blues
    'medium_blue': '#158BBB',
    'dark_teal': '#0F5D7D',

    # Structure
    'black': '#000000',
    'white': '#FFFFFF',
    'gridline': '#E5E5E5',
}

# =============================================================================
# COLOR CYCLES
# =============================================================================

# Cycle 1: Control vs Treatment (most common)
CYCLE_TREATMENT_CONTROL = ['#222222', '#2DB2E8', '#666666']

# Cycle 2: Neutrals only (no designated highlight)
CYCLE_NEUTRALS_ONLY = ['#222222', '#666666', '#999999']

# Cycle 3: Opposing effects (blue vs orange)
CYCLE_OPPOSING = ['#2DB2E8', '#E8622D', '#222222']

# Cycle 4: Multiple categories (use sparingly, add shapes!)
CYCLE_MULTI_CATEGORY = ['#222222', '#2DB2E8', '#666666', '#158BBB']

# Volcano plot specific
VOLCANO_COLORS = {
    'nonsig': '#BDBDBD',
    'up': '#E8622D',
    'down': '#2DB2E8',
}

# Marker shapes for multi-category (accessibility)
MARKER_SHAPES = ['o', 's', '^', 'D']  # circle, square, triangle, diamond

# =============================================================================
# STYLE CONFIGURATION
# =============================================================================

CycleType = Literal['treatment_control', 'neutrals_only', 'opposing', 'multi_category']

def set_brand_style(cycle: CycleType = 'treatment_control') -> None:
    """
    Apply Oligon brand visual standards to matplotlib.

    Parameters
    ----------
    cycle : str
        Which color cycle to use as default:
        - 'treatment_control' (default): Control vs experimental
        - 'neutrals_only': All groups equal weight
        - 'opposing': Bidirectional effects (up/down)
        - 'multi_category': 4 categories (use with marker shapes)

    Examples
    --------
    >>> set_brand_style('treatment_control')
    >>> plt.plot([1, 2, 3], [1, 4, 9])  # Uses brand colors automatically
    """
    cycle_map = {
        'treatment_control': CYCLE_TREATMENT_CONTROL,
        'neutrals_only': CYCLE_NEUTRALS_ONLY,
        'opposing': CYCLE_OPPOSING,
        'multi_category': CYCLE_MULTI_CATEGORY,
    }

    selected_cycle = cycle_map.get(cycle, CYCLE_TREATMENT_CONTROL)

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

        # Axes
        'axes.facecolor': 'white',
        'axes.edgecolor': 'black',
        'axes.linewidth': 0.8,
        'axes.grid': False,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.labelcolor': 'black',
        'axes.labelsize': 12,
        'axes.titlesize': 16,
        'axes.titleweight': 'normal',
        'axes.prop_cycle': plt.cycler(color=selected_cycle),

        # Ticks
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'xtick.color': 'black',
        'ytick.color': 'black',
        'xtick.direction': 'out',
        'ytick.direction': 'out',

        # Grid (off by default)
        'grid.color': '#E5E5E5',
        'grid.linewidth': 0.5,
        'grid.alpha': 1.0,

        # Legend
        'legend.fontsize': 12,
        'legend.title_fontsize': 12,
        'legend.frameon': False,
        'legend.loc': 'best',

        # Font (10pt floor, 12pt base — see brand-tokens.json typography.figures)
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
        'font.size': 12,

        # SVG/PDF font handling — keep text as text (not glyph paths) so
        # brand grep-checks find font-family/font-size attributes and so
        # downstream editors (Inkscape, Illustrator) can edit the text.
        'svg.fonttype': 'none',
        'pdf.fonttype': 42,
        'ps.fonttype': 42,

        # Lines
        'lines.linewidth': 1.25,
        'lines.markersize': 5,

        # Patches (bars, etc.)
        'patch.edgecolor': 'none',
    })

# =============================================================================
# DETERMINISTIC SELECTORS
# =============================================================================

ContextType = Literal['comparison', 'equal_weight', 'bidirectional']


def select_cycle(
    n_series: int,
    context: ContextType = 'comparison',
    has_highlight: bool = True
) -> tuple[str, list[str]]:
    """
    Deterministically select color cycle based on data characteristics.

    This function eliminates LLM interpretation by providing explicit logic
    for cycle selection based on the number of data series and scientific context.

    Parameters
    ----------
    n_series : int
        Number of data series to be plotted (1-4 supported)
    context : str
        Scientific context of the visualization:
        - 'comparison': Control vs treatment (default)
        - 'equal_weight': All groups have equal importance
        - 'bidirectional': Opposing effects (up/down, gain/loss)
    has_highlight : bool
        Whether one series should be highlighted (default True)

    Returns
    -------
    tuple[str, list[str]]
        (cycle_name, color_list) - The cycle name and list of hex colors

    Raises
    ------
    ValueError
        If n_series > 4 (redesign with faceting recommended)

    Examples
    --------
    >>> cycle_name, colors = select_cycle(2, context='comparison')
    >>> print(cycle_name)  # 'treatment_control'
    >>> print(colors)  # ['#222222', '#2DB2E8']

    >>> cycle_name, colors = select_cycle(2, context='bidirectional')
    >>> print(cycle_name)  # 'opposing'
    >>> print(colors)  # ['#2DB2E8', '#E8622D']
    """
    if n_series < 1:
        raise ValueError(f"n_series must be >= 1, got {n_series}")

    if n_series == 1:
        return 'single', [BRAND_COLORS['dark_gray']]

    if n_series == 2:
        if context == 'bidirectional':
            return 'opposing', CYCLE_OPPOSING[:2]
        return 'treatment_control', CYCLE_TREATMENT_CONTROL[:2]

    if n_series == 3:
        if context == 'equal_weight' or not has_highlight:
            return 'neutrals_only', CYCLE_NEUTRALS_ONLY
        if context == 'bidirectional':
            return 'opposing', CYCLE_OPPOSING
        return 'treatment_control', CYCLE_TREATMENT_CONTROL

    if n_series == 4:
        return 'multi_category', CYCLE_MULTI_CATEGORY

    # 5+ series: signal redesign needed
    raise ValueError(
        f"Too many series ({n_series}). Maximum 4 supported. "
        "Redesign using faceting or small multiples."
    )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_divergent_cmap(name: str = 'brand_divergent') -> LinearSegmentedColormap:
    """
    Create a perceptually uniform divergent colormap for heatmaps.

    Centered at white: dark teal (neg) -> brand blue -> white -> orange -> dark warm (pos)

    Returns
    -------
    LinearSegmentedColormap
        Colormap suitable for data centered around zero.

    Examples
    --------
    >>> cmap = get_divergent_cmap()
    >>> plt.imshow(data, cmap=cmap, vmin=-3, vmax=3)
    """
    colors = [
        BRAND_COLORS['dark_teal'],
        BRAND_COLORS['brand_blue'],
        BRAND_COLORS['white'],
        BRAND_COLORS['contrast_orange'],
        BRAND_COLORS['dark_warm'],
    ]

    positions = [0.0, 0.25, 0.5, 0.75, 1.0]

    return LinearSegmentedColormap.from_list(
        name,
        list(zip(positions, colors))
    )


def add_panel_label(
    ax: plt.Axes,
    label: str,
    offset: tuple = (-0.12, 1.05),
    fontsize: int = 14,
    fontweight: str = 'bold'
) -> None:
    """
    Add a panel label (A, B, C, etc.) to an axes.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to label
    label : str
        The label text (e.g., 'A', 'B', 'C')
    offset : tuple
        (x, y) offset in axes coordinates
    fontsize : int
        Font size in points
    fontweight : str
        Font weight ('bold', 'normal', etc.)

    Examples
    --------
    >>> fig, axes = plt.subplots(1, 2)
    >>> add_panel_label(axes[0], 'A')
    >>> add_panel_label(axes[1], 'B')
    """
    ax.text(
        offset[0], offset[1],
        label,
        transform=ax.transAxes,
        fontsize=fontsize,
        fontweight=fontweight,
        va='top',
        ha='left',
        color='black'
    )


def add_error_band(
    ax: plt.Axes,
    x: np.ndarray,
    y: np.ndarray,
    yerr: np.ndarray,
    color: str,
    alpha: float = 0.25,
    label: Optional[str] = None
) -> plt.Line2D:
    """
    Add a semi-transparent error band around a line.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to plot on
    x : array-like
        X values
    y : array-like
        Y values (center line)
    yerr : array-like or tuple
        Error values. If tuple, (lower, upper) errors.
    color : str
        Color for both line and band
    alpha : float
        Opacity of the error band (0.2-0.3 recommended)
    label : str, optional
        Label for legend

    Returns
    -------
    matplotlib.lines.Line2D
        The line object

    Examples
    --------
    >>> line = add_error_band(ax, time, survival, ci, BRAND_COLORS['brand_blue'], label='Treatment')
    """
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
    n_labels: int = 10
) -> plt.Axes:
    """
    Create a volcano plot with brand colors.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes to plot on
    log2fc : array-like
        Log2 fold change values
    pval : array-like
        P-values (will be -log10 transformed)
    fc_thresh : float
        Fold change threshold (absolute log2)
    p_thresh : float
        P-value threshold
    gene_labels : array-like, optional
        Gene names for labeling top hits
    n_labels : int
        Number of top genes to label

    Returns
    -------
    matplotlib.axes.Axes
        The axes with volcano plot

    Examples
    --------
    >>> fig, ax = plt.subplots()
    >>> plot_volcano(ax, log2fc, pvalues, fc_thresh=1.5, p_thresh=0.01)
    """
    neg_log_p = -np.log10(pval)

    # Classify points
    nonsig = (np.abs(log2fc) < fc_thresh) | (pval >= p_thresh)
    sig_up = (log2fc >= fc_thresh) & (pval < p_thresh)
    sig_down = (log2fc <= -fc_thresh) & (pval < p_thresh)

    # Plot
    ax.scatter(log2fc[nonsig], neg_log_p[nonsig],
               c=VOLCANO_COLORS['nonsig'], s=12, alpha=0.6, label='NS')
    ax.scatter(log2fc[sig_up], neg_log_p[sig_up],
               c=VOLCANO_COLORS['up'], s=20, alpha=0.8, label='Up')
    ax.scatter(log2fc[sig_down], neg_log_p[sig_down],
               c=VOLCANO_COLORS['down'], s=20, alpha=0.8, label='Down')

    # Threshold lines
    ax.axhline(-np.log10(p_thresh), color='#666666', linestyle='--', linewidth=0.5)
    ax.axvline(-fc_thresh, color='#666666', linestyle='--', linewidth=0.5)
    ax.axvline(fc_thresh, color='#666666', linestyle='--', linewidth=0.5)

    ax.set_xlabel('log₂(Fold Change)')
    ax.set_ylabel('-log₁₀(p-value)')

    return ax


# =============================================================================
# PREFLIGHT VALIDATORS
# =============================================================================

# Set of all allowed brand colors (uppercase hex)
ALLOWED_COLORS = {c.upper() for c in BRAND_COLORS.values()}


def run_preflight(fig: plt.Figure) -> dict[str, bool]:
    """
    Automated preflight validation for brand compliance.

    Checks the figure against Oligon brand standards and returns
    a dictionary with pass/fail status for each check.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure to validate

    Returns
    -------
    dict[str, bool]
        Dictionary mapping check names to pass/fail status:
        - 'white_background': Figure has white background
        - 'spines_removed': Top/right spines are hidden
        - 'grid_off': Grid is disabled (or properly styled)
        - 'axes_black': Axis lines and ticks are black

    Examples
    --------
    >>> fig, ax = plt.subplots()
    >>> set_brand_style('treatment_control')
    >>> ax.plot([1, 2, 3], [1, 4, 9])
    >>> results = run_preflight(fig)
    >>> all(results.values())  # True if compliant
    True
    """
    results = {}

    # Check 1: White background
    facecolor = fig.get_facecolor()
    # Compare RGB values (ignore alpha)
    results['white_background'] = (
        abs(facecolor[0] - 1.0) < 0.01 and
        abs(facecolor[1] - 1.0) < 0.01 and
        abs(facecolor[2] - 1.0) < 0.01
    )

    # Check 2: Top/right spines removed (check all axes)
    spines_ok = True
    for ax in fig.axes:
        if ax.spines['top'].get_visible() or ax.spines['right'].get_visible():
            spines_ok = False
            break
    results['spines_removed'] = spines_ok

    # Check 3: Grid off (or if on, properly styled)
    grid_ok = True
    for ax in fig.axes:
        # Check if grid is visible by examining gridlines
        x_gridlines = ax.xaxis.get_gridlines()
        y_gridlines = ax.yaxis.get_gridlines()

        x_grid_visible = any(line.get_visible() for line in x_gridlines) if x_gridlines else False
        y_grid_visible = any(line.get_visible() for line in y_gridlines) if y_gridlines else False

        if x_grid_visible or y_grid_visible:
            # Grid is on - check if it's properly styled (light gray)
            for line in x_gridlines + y_gridlines:
                if line.get_visible():
                    color = line.get_color()
                    # Accept gridline gray (#E5E5E5) or similar light grays
                    if isinstance(color, str):
                        color_upper = color.upper()
                        if color_upper not in {'#E5E5E5', '#E0E0E0', '#EEEEEE', 'LIGHTGRAY', 'LIGHTGREY'}:
                            grid_ok = False
                            break
    results['grid_off'] = grid_ok

    # Check 4: Axes lines are black
    axes_black = True
    for ax in fig.axes:
        for spine in ['left', 'bottom']:
            if ax.spines[spine].get_visible():
                ec = ax.spines[spine].get_edgecolor()
                # Check if color is black (RGB close to 0)
                if not (ec[0] < 0.1 and ec[1] < 0.1 and ec[2] < 0.1):
                    axes_black = False
                    break
    results['axes_black'] = axes_black

    return results


def extract_figure_colors(fig: plt.Figure) -> set[str]:
    """
    Extract all colors used in a figure for validation.

    Examines lines, scatter plots, bars, and other elements to
    compile a set of all colors used in the visualization.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure to analyze

    Returns
    -------
    set[str]
        Set of uppercase hex color strings (e.g., {'#2DB2E8', '#222222'})

    Examples
    --------
    >>> fig, ax = plt.subplots()
    >>> ax.plot([1, 2], [1, 2], color='#2DB2E8')
    >>> colors = extract_figure_colors(fig)
    >>> '#2DB2E8' in colors
    True
    """
    colors = set()

    def _color_to_hex(color) -> Optional[str]:
        """Convert various color formats to hex string."""
        if color is None:
            return None
        if isinstance(color, str):
            if color.startswith('#'):
                return color.upper()
            # Named colors - try to convert
            try:
                rgb = mpl.colors.to_rgb(color)
                return '#{:02X}{:02X}{:02X}'.format(
                    int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
                )
            except ValueError:
                return None
        if hasattr(color, '__len__') and len(color) >= 3:
            # RGBA or RGB tuple
            return '#{:02X}{:02X}{:02X}'.format(
                int(color[0] * 255), int(color[1] * 255), int(color[2] * 255)
            )
        return None

    for ax in fig.axes:
        # Lines
        for line in ax.get_lines():
            hex_color = _color_to_hex(line.get_color())
            if hex_color:
                colors.add(hex_color)

        # Collections (scatter, etc.)
        for coll in ax.collections:
            facecolors = coll.get_facecolor()
            if len(facecolors) > 0:
                for fc in facecolors:
                    hex_color = _color_to_hex(fc)
                    if hex_color:
                        colors.add(hex_color)

            edgecolors = coll.get_edgecolor()
            if len(edgecolors) > 0:
                for ec in edgecolors:
                    hex_color = _color_to_hex(ec)
                    if hex_color:
                        colors.add(hex_color)

        # Patches (bars, etc.)
        for patch in ax.patches:
            fc = patch.get_facecolor()
            hex_color = _color_to_hex(fc)
            if hex_color:
                colors.add(hex_color)

    return colors


def get_preflight_report(fig: plt.Figure) -> str:
    """
    Generate a human-readable preflight report.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure to validate

    Returns
    -------
    str
        Formatted report string with pass/fail indicators

    Examples
    --------
    >>> fig, ax = plt.subplots()
    >>> set_brand_style('treatment_control')
    >>> print(get_preflight_report(fig))
    Oligon Brand Preflight Check
    ============================
    ✓ white_background
    ✓ spines_removed
    ✓ grid_off
    ✓ axes_black

    Result: PASS (4/4 checks passed)
    """
    results = run_preflight(fig)

    lines = ["Oligon Brand Preflight Check", "=" * 28]
    for check, passed in results.items():
        symbol = "✓" if passed else "✗"
        lines.append(f"{symbol} {check}")

    passed_count = sum(results.values())
    total_count = len(results)
    status = "PASS" if passed_count == total_count else "FAIL"
    lines.append("")
    lines.append(f"Result: {status} ({passed_count}/{total_count} checks passed)")

    return "\n".join(lines)


def validate_palette(fig: plt.Figure) -> dict:
    """
    Validate that all colors in a figure are from the brand palette.

    Extracts colors from the figure and compares against the allowed
    brand colors. Reports any violations (non-brand colors used).

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure to validate

    Returns
    -------
    dict
        Validation results containing:
        - 'valid': bool - True if all colors are brand-compliant
        - 'used_colors': set[str] - All colors found in the figure
        - 'violations': set[str] - Colors not in the brand palette
        - 'allowed_colors': set[str] - Reference set of allowed colors

    Examples
    --------
    >>> set_brand_style('treatment_control')
    >>> fig, ax = plt.subplots()
    >>> ax.plot([1, 2, 3], [1, 4, 9])
    >>> result = validate_palette(fig)
    >>> result['valid']
    True

    >>> fig2, ax2 = plt.subplots()
    >>> ax2.plot([1, 2, 3], [1, 4, 9], color='red')  # Non-brand color
    >>> result2 = validate_palette(fig2)
    >>> result2['valid']
    False
    >>> '#FF0000' in result2['violations']
    True
    """
    used_colors = extract_figure_colors(fig)

    # Structural colors (white/black) are always allowed
    structural_colors = {'#FFFFFF', '#000000'}

    # Find violations: colors used that aren't in brand palette or structural
    violations = used_colors - ALLOWED_COLORS - structural_colors

    return {
        'valid': len(violations) == 0,
        'used_colors': used_colors,
        'violations': violations,
        'allowed_colors': ALLOWED_COLORS.copy(),
    }


def count_brand_blue(fig: plt.Figure) -> dict:
    """
    Count Brand Blue (#2DB2E8) usage in a figure.

    Brand guidelines specify that Brand Blue should be limited to
    1-2 elements per panel to maintain its impact as a highlight color.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure to analyze

    Returns
    -------
    dict
        Analysis results containing:
        - 'total_count': int - Total Brand Blue elements across all axes
        - 'per_axes': dict[int, int] - Count per axes index
        - 'compliant': bool - True if all axes have <= 2 Brand Blue elements
        - 'violations': list[int] - Axes indices exceeding the limit

    Examples
    --------
    >>> set_brand_style('treatment_control')
    >>> fig, ax = plt.subplots()
    >>> ax.plot([1, 2, 3], [1, 4, 9])  # One Brand Blue line
    >>> result = count_brand_blue(fig)
    >>> result['compliant']
    True
    >>> result['total_count']
    1
    """
    BRAND_BLUE = '#2DB2E8'
    BRAND_BLUE_UPPER = BRAND_BLUE.upper()

    per_axes = {}
    violations = []

    def _is_brand_blue(color) -> bool:
        """Check if a color matches Brand Blue."""
        if color is None:
            return False
        if isinstance(color, str):
            if color.upper() == BRAND_BLUE_UPPER:
                return True
            if color.startswith('#'):
                return color.upper() == BRAND_BLUE_UPPER
            # Try converting named color
            try:
                rgb = mpl.colors.to_rgb(color)
                hex_color = '#{:02X}{:02X}{:02X}'.format(
                    int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
                )
                return hex_color == BRAND_BLUE_UPPER
            except ValueError:
                return False
        if hasattr(color, '__len__') and len(color) >= 3:
            hex_color = '#{:02X}{:02X}{:02X}'.format(
                int(color[0] * 255), int(color[1] * 255), int(color[2] * 255)
            )
            return hex_color == BRAND_BLUE_UPPER
        return False

    for ax_idx, ax in enumerate(fig.axes):
        count = 0

        # Check lines
        for line in ax.get_lines():
            if _is_brand_blue(line.get_color()):
                count += 1

        # Check collections (scatter plots, etc.)
        for coll in ax.collections:
            facecolors = coll.get_facecolor()
            if len(facecolors) > 0:
                # For scatter with single color, count as 1 element
                unique_blues = set()
                for fc in facecolors:
                    if _is_brand_blue(fc):
                        unique_blues.add(tuple(fc))
                if unique_blues:
                    count += 1  # Count collection as single element

        # Check patches (bars, etc.)
        for patch in ax.patches:
            if _is_brand_blue(patch.get_facecolor()):
                count += 1

        per_axes[ax_idx] = count

        # Check compliance (max 2 Brand Blue elements per axes)
        if count > 2:
            violations.append(ax_idx)

    total_count = sum(per_axes.values())

    return {
        'total_count': total_count,
        'per_axes': per_axes,
        'compliant': len(violations) == 0,
        'violations': violations,
    }


def get_brand_compliance_report(fig: plt.Figure) -> str:
    """
    Generate a comprehensive brand compliance report.

    Combines preflight checks, palette validation, and Brand Blue usage
    into a single human-readable report.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure to validate

    Returns
    -------
    str
        Formatted compliance report

    Examples
    --------
    >>> set_brand_style('treatment_control')
    >>> fig, ax = plt.subplots()
    >>> ax.plot([1, 2, 3], [1, 4, 9])
    >>> print(get_brand_compliance_report(fig))
    """
    lines = ["Oligon Brand Compliance Report", "=" * 31, ""]

    # Preflight checks
    preflight = run_preflight(fig)
    lines.append("PREFLIGHT CHECKS:")
    for check, passed in preflight.items():
        symbol = "✓" if passed else "✗"
        lines.append(f"  {symbol} {check}")

    lines.append("")

    # Palette validation
    palette = validate_palette(fig)
    lines.append("PALETTE VALIDATION:")
    if palette['valid']:
        lines.append("  ✓ All colors are brand-compliant")
    else:
        lines.append("  ✗ Non-brand colors detected:")
        for violation in sorted(palette['violations']):
            lines.append(f"    - {violation}")

    lines.append("")

    # Brand Blue usage
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

    # Overall result
    all_passed = (
        all(preflight.values()) and
        palette['valid'] and
        brand_blue['compliant']
    )
    status = "PASS" if all_passed else "FAIL"
    lines.append(f"OVERALL: {status}")

    return "\n".join(lines)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_color(name: str) -> str:
    """Get a brand color by name."""
    return BRAND_COLORS.get(name, '#000000')


def get_cycle(name: CycleType) -> list:
    """Get a color cycle by name."""
    cycles = {
        'treatment_control': CYCLE_TREATMENT_CONTROL,
        'neutrals_only': CYCLE_NEUTRALS_ONLY,
        'opposing': CYCLE_OPPOSING,
        'multi_category': CYCLE_MULTI_CATEGORY,
    }
    return cycles.get(name, CYCLE_TREATMENT_CONTROL)


# =============================================================================
# AUTO-APPLY ON IMPORT (Optional)
# =============================================================================

# Uncomment to apply brand style automatically when module is imported:
# set_brand_style('treatment_control')
