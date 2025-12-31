"""
Oligon Brand Adapter for Matplotlib/Seaborn

This module provides functions and constants for applying Oligon scientific
brand identity to matplotlib and seaborn visualizations.

Usage:
    from oligon_brand.adapters.matplotlib_adapter import (
        set_brand_style,
        BRAND_COLORS,
        CYCLE_TREATMENT_CONTROL,
        get_divergent_cmap,
        add_panel_label
    )

    # Apply brand style
    set_brand_style('treatment_control')

    # Create your plot...
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
        'axes.labelsize': 8,
        'axes.titlesize': 9,
        'axes.titleweight': 'normal',
        'axes.prop_cycle': plt.cycler(color=selected_cycle),

        # Ticks
        'xtick.labelsize': 7,
        'ytick.labelsize': 7,
        'xtick.color': 'black',
        'ytick.color': 'black',
        'xtick.direction': 'out',
        'ytick.direction': 'out',

        # Grid (off by default)
        'grid.color': '#E5E5E5',
        'grid.linewidth': 0.5,
        'grid.alpha': 1.0,

        # Legend
        'legend.fontsize': 7,
        'legend.frameon': False,
        'legend.loc': 'best',

        # Font
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
        'font.size': 8,

        # Lines
        'lines.linewidth': 1.25,
        'lines.markersize': 5,

        # Patches (bars, etc.)
        'patch.edgecolor': 'none',
    })

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
    fontsize: int = 10,
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
