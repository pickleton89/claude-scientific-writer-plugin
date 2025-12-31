#!/usr/bin/env python3
"""
Oligon Scientific Brand - Matplotlib Helpers
=============================================
Companion module for oligon_color_brand.mplstyle.

The .mplstyle file handles rcParams; this module provides:
- Color constants for direct use in code
- Scenario-specific color cycles  
- Divergent colormap for heatmaps
- Helper functions (panel labels, etc.)

Usage:
    import matplotlib.pyplot as plt
    
    # Option 1: Use the .mplstyle file (recommended)
    plt.style.use('oligon_color_brand')  # if installed in stylelib
    # OR
    plt.style.use('/path/to/oligon_color_brand.mplstyle')
    
    # Option 2: Import this module for colors + helpers
    from matplotlib_brand_setup import *
    
    # Use color constants directly
    ax.plot(x, y, color=BRAND_BLUE)
    ax.scatter(x, y, c=DARK_GRAY)
    
    # Use cycle lists for manual color assignment
    for i, group in enumerate(groups):
        ax.plot(x, y[i], color=CYCLE_OPPOSING[i])
    
    # Add panel labels
    add_panel_label(ax, 'A')
    
    # Use divergent colormap for heatmaps
    im = ax.imshow(data, cmap=get_divergent_cmap())
"""

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# =============================================================================
# BRAND COLOR DEFINITIONS
# =============================================================================

BRAND_COLORS = {
    # Primary brand color
    'brand_blue': '#2DB2E8',
    
    # Neutral data colors
    'dark_gray': '#222222',
    'medium_gray': '#666666',
    'muted_gray': '#999999',
    'light_gray': '#BDBDBD',  # Annotations only, not for data
    
    # Contrast color
    'contrast_orange': '#E8622D',
    
    # Supporting colors
    'medium_blue': '#158BBB',
    'dark_teal': '#0F5D7D',
    'dark_warm': '#7D250F',
    
    # Structure
    'black': '#000000',
    'white': '#FFFFFF',
    'gridline': '#E5E5E5',
}

# Convenience aliases for direct use
BRAND_BLUE = '#2DB2E8'
DARK_GRAY = '#222222'
MEDIUM_GRAY = '#666666'
MUTED_GRAY = '#999999'
LIGHT_GRAY = '#BDBDBD'
CONTRAST_ORANGE = '#E8622D'
MEDIUM_BLUE = '#158BBB'
DARK_TEAL = '#0F5D7D'
DARK_WARM = '#7D250F'

# =============================================================================
# SCENARIO-SPECIFIC COLOR CYCLES
# =============================================================================

# Cycle 1: Control vs. Treatment (most common)
# Use when comparing experimental condition against baseline
CYCLE_TREATMENT_CONTROL = ['#222222', '#2DB2E8', '#666666']

# Cycle 2: Neutrals only (no designated highlight)
# Use when all groups are peers, no single condition deserves emphasis
CYCLE_NEUTRALS_ONLY = ['#222222', '#666666', '#999999']

# Cycle 3: Opposing effects (up vs. down, gain vs. loss)
# Use for bidirectional changes (e.g., differential expression)
CYCLE_OPPOSING = ['#2DB2E8', '#E8622D', '#222222']

# Cycle 4: Multiple categories (≤4 groups, use with marker shapes)
CYCLE_MULTI_CATEGORY = ['#222222', '#2DB2E8', '#666666', '#158BBB']

# Volcano plot specific (dict for easy mapping)
COLORS_VOLCANO = {
    'NS': '#BDBDBD',
    'Up': '#E8622D',
    'Down': '#2DB2E8',
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def add_panel_label(ax, label, x=-0.1, y=1.05, fontsize=10, fontweight='bold'):
    """
    Add a panel label (A, B, C, etc.) to an axes.
    
    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to label
    label : str
        The label text (e.g., 'A', 'B', 'C')
    x, y : float
        Position in axes coordinates (default: top-left)
    fontsize : int
        Font size (default: 10)
    fontweight : str
        Font weight (default: 'bold')
    """
    ax.text(x, y, label, transform=ax.transAxes,
            fontsize=fontsize, fontweight=fontweight,
            va='bottom', ha='right')


def get_divergent_cmap(name='OligonDivergent'):
    """
    Create a divergent colormap for heatmaps (teal-blue-white-orange-red).
    
    Centered at zero, suitable for z-scores and log2 fold changes.
    
    Returns
    -------
    LinearSegmentedColormap
        Use with imshow, pcolormesh, etc.
    
    Example
    -------
    >>> im = ax.imshow(data, cmap=get_divergent_cmap(), vmin=-3, vmax=3)
    >>> plt.colorbar(im)
    """
    colors = ['#0F5D7D', '#2DB2E8', '#FFFFFF', '#E8622D', '#7D250F']
    positions = [0.0, 0.25, 0.5, 0.75, 1.0]
    
    # Convert hex to RGB tuples
    rgb_colors = []
    for hex_color in colors:
        h = hex_color.lstrip('#')
        rgb_colors.append(tuple(int(h[i:i+2], 16)/255 for i in (0, 2, 4)))
    
    return LinearSegmentedColormap.from_list(name, list(zip(positions, rgb_colors)))


def set_cycle(ax, cycle='treatment_control'):
    """
    Set the color cycle for a specific axes.
    
    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to modify
    cycle : str
        Which cycle to use:
        - 'treatment_control': Control vs. treatment (default)
        - 'neutrals': All groups equal weight
        - 'opposing': Up vs. down / bidirectional
        - 'multi': 4-category comparisons
    """
    from cycler import cycler
    
    cycles = {
        'treatment_control': CYCLE_TREATMENT_CONTROL,
        'neutrals': CYCLE_NEUTRALS_ONLY,
        'opposing': CYCLE_OPPOSING,
        'multi': CYCLE_MULTI_CATEGORY,
    }
    
    selected = cycles.get(cycle, CYCLE_TREATMENT_CONTROL)
    ax.set_prop_cycle(cycler('color', selected))


# =============================================================================
# DEMO
# =============================================================================

if __name__ == '__main__':
    import numpy as np
    import os
    
    # Try to use the .mplstyle file if available
    style_path = os.path.join(os.path.dirname(__file__), 
                               '..', 'assets', 'oligon_color_brand.mplstyle')
    if os.path.exists(style_path):
        plt.style.use(style_path)
        print(f"Using style file: {style_path}")
    
    fig, ax = plt.subplots(figsize=(5, 4))
    
    x = np.linspace(0, 10, 50)
    ax.plot(x, np.sin(x), label='Control')
    ax.plot(x, np.sin(x) + 0.5, label='Treatment')
    ax.plot(x, np.sin(x) - 0.3, label='Vehicle')
    
    ax.set_xlabel('Time (hours)')
    ax.set_ylabel('Response')
    ax.legend()
    add_panel_label(ax, 'A')
    
    plt.tight_layout()
    plt.savefig('brand_demo.png', dpi=300)
    print("Demo saved to brand_demo.png")
