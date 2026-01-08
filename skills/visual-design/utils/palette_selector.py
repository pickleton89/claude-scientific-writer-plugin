"""Color palette selection for scientific figures.

Provides deterministic palette selection based on data characteristics.
All palettes are colorblind-safe by default.
"""

from typing import Dict, Any, List, Optional


# Colorblind-safe categorical palettes
CATEGORICAL_PALETTES: Dict[str, Dict[str, Any]] = {
    "okabe_ito": {
        "colors": [
            "#E69F00",  # Orange
            "#56B4E9",  # Sky blue
            "#009E73",  # Bluish green
            "#F0E442",  # Yellow
            "#0072B2",  # Blue
            "#D55E00",  # Vermillion
            "#CC79A7",  # Reddish purple
            "#000000",  # Black
        ],
        "max_categories": 8,
        "colorblind_safe": True,
        "description": "Okabe-Ito palette, optimized for all CVD types",
    },
    "tableau10": {
        "colors": [
            "#4E79A7",  # Blue
            "#F28E2B",  # Orange
            "#E15759",  # Red
            "#76B7B2",  # Teal
            "#59A14F",  # Green
            "#EDC948",  # Yellow
            "#B07AA1",  # Purple
            "#FF9DA7",  # Pink
            "#9C755F",  # Brown
            "#BAB0AC",  # Gray
        ],
        "max_categories": 10,
        "colorblind_safe": True,
        "description": "Tableau 10, widely recognizable",
    },
    "wong": {
        "colors": [
            "#000000",  # Black
            "#E69F00",  # Orange
            "#56B4E9",  # Sky blue
            "#009E73",  # Bluish green
            "#F0E442",  # Yellow
            "#0072B2",  # Blue
            "#D55E00",  # Vermillion
            "#CC79A7",  # Reddish purple
        ],
        "max_categories": 8,
        "colorblind_safe": True,
        "description": "Wong palette, similar to Okabe-Ito with black first",
    },
    "tol_bright": {
        "colors": [
            "#4477AA",  # Blue
            "#EE6677",  # Red
            "#228833",  # Green
            "#CCBB44",  # Yellow
            "#66CCEE",  # Cyan
            "#AA3377",  # Purple
            "#BBBBBB",  # Gray
        ],
        "max_categories": 7,
        "colorblind_safe": True,
        "description": "Paul Tol bright palette, high contrast",
    },
}

# Sequential palettes (low to high)
SEQUENTIAL_PALETTES: Dict[str, Dict[str, Any]] = {
    "viridis": {
        "type": "sequential",
        "colorblind_safe": True,
        "matplotlib_name": "viridis",
        "description": "Perceptually uniform, colorblind-safe (yellow-green-blue)",
    },
    "plasma": {
        "type": "sequential",
        "colorblind_safe": True,
        "matplotlib_name": "plasma",
        "description": "Perceptually uniform, high contrast (yellow-pink-purple)",
    },
    "cividis": {
        "type": "sequential",
        "colorblind_safe": True,
        "matplotlib_name": "cividis",
        "description": "Optimized for deuteranomaly and protanomaly (yellow-blue)",
    },
    "inferno": {
        "type": "sequential",
        "colorblind_safe": True,
        "matplotlib_name": "inferno",
        "description": "High contrast, dark to light (black-red-yellow)",
    },
    "magma": {
        "type": "sequential",
        "colorblind_safe": True,
        "matplotlib_name": "magma",
        "description": "Similar to inferno, softer (black-purple-yellow)",
    },
    "blues": {
        "type": "sequential",
        "colorblind_safe": True,
        "matplotlib_name": "Blues",
        "description": "Single-hue blue gradient, good for heatmaps",
    },
    "greens": {
        "type": "sequential",
        "colorblind_safe": True,
        "matplotlib_name": "Greens",
        "description": "Single-hue green gradient",
    },
}

# Diverging palettes (has meaningful center)
DIVERGING_PALETTES: Dict[str, Dict[str, Any]] = {
    "rdbu": {
        "type": "diverging",
        "colorblind_safe": True,
        "matplotlib_name": "RdBu",
        "description": "Red-Blue, good for fold change and correlation",
    },
    "puor": {
        "type": "diverging",
        "colorblind_safe": True,
        "matplotlib_name": "PuOr",
        "description": "Purple-Orange, alternative diverging palette",
    },
    "prgn": {
        "type": "diverging",
        "colorblind_safe": True,
        "matplotlib_name": "PRGn",
        "description": "Purple-Green, good for +/- differences",
    },
    "brbg": {
        "type": "diverging",
        "colorblind_safe": True,
        "matplotlib_name": "BrBG",
        "description": "Brown-BlueGreen, nature-inspired diverging",
    },
    "coolwarm": {
        "type": "diverging",
        "colorblind_safe": True,
        "matplotlib_name": "coolwarm",
        "description": "Blue-Red with desaturated center, less harsh",
    },
}

# Binary comparison palettes
BINARY_PALETTES: Dict[str, Dict[str, Any]] = {
    "blue_orange": {
        "colors": ["#0072B2", "#E69F00"],
        "colorblind_safe": True,
        "description": "High contrast binary comparison (control/treatment)",
    },
    "magenta_green": {
        "colors": ["#CC79A7", "#009E73"],
        "colorblind_safe": True,
        "description": "Alternative to red-green for CVD accessibility",
    },
    "blue_vermillion": {
        "colors": ["#0072B2", "#D55E00"],
        "colorblind_safe": True,
        "description": "Strong contrast binary",
    },
    "purple_yellow": {
        "colors": ["#7B3294", "#FDB863"],
        "colorblind_safe": True,
        "description": "Diverging binary, good for before/after",
    },
}


def select_palette(
    data_type: str = "categorical",
    n_groups: int = 2,
    is_diverging: bool = False,
    require_colorblind_safe: bool = True,
    palette_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Select appropriate color palette based on data characteristics.

    Args:
        data_type: "categorical", "sequential", "diverging", or "binary"
        n_groups: Number of data groups/categories
        is_diverging: Whether data has meaningful center point (e.g., fold change)
        require_colorblind_safe: Filter for colorblind-safe only (default True)
        palette_name: Specific palette name to use (overrides auto-selection)

    Returns:
        Dict with:
            - palette_name: Name of selected palette
            - palette_type: Type of palette
            - colors: List of hex codes (for categorical/binary)
            - matplotlib_name: Name for matplotlib (for sequential/diverging)
            - colorblind_safe: Whether palette is CVD-safe
            - description: Palette description
            - warning: Optional warning if n_groups exceeds recommended max
    """
    # Override data_type if diverging flag set
    if is_diverging and data_type == "sequential":
        data_type = "diverging"

    # Allow specific palette override
    if palette_name:
        # Search all palette dictionaries
        for palettes in [
            CATEGORICAL_PALETTES,
            SEQUENTIAL_PALETTES,
            DIVERGING_PALETTES,
            BINARY_PALETTES,
        ]:
            if palette_name.lower() in palettes:
                palette_data = palettes[palette_name.lower()]
                return {
                    "palette_name": palette_name.lower(),
                    "palette_type": palette_data.get("type", "categorical"),
                    **palette_data,
                }

    # Sequential data - check before binary to respect explicit data_type
    if data_type == "sequential":
        return {
            "palette_name": "viridis",
            "palette_type": "sequential",
            **SEQUENTIAL_PALETTES["viridis"],
        }

    # Diverging data - check before binary to respect explicit data_type
    if data_type == "diverging":
        return {
            "palette_name": "rdbu",
            "palette_type": "diverging",
            **DIVERGING_PALETTES["rdbu"],
        }

    # Binary comparison (2 groups) - only when not sequential/diverging
    if n_groups == 2 or data_type == "binary":
        return {
            "palette_name": "blue_orange",
            "palette_type": "binary",
            **BINARY_PALETTES["blue_orange"],
        }

    # Categorical data
    if n_groups <= 8:
        palette = CATEGORICAL_PALETTES["okabe_ito"]
        return {
            "palette_name": "okabe_ito",
            "palette_type": "categorical",
            "colors": palette["colors"][:n_groups],
            "colorblind_safe": palette["colorblind_safe"],
            "description": palette["description"],
        }
    elif n_groups <= 10:
        palette = CATEGORICAL_PALETTES["tableau10"]
        return {
            "palette_name": "tableau10",
            "palette_type": "categorical",
            "colors": palette["colors"][:n_groups],
            "colorblind_safe": palette["colorblind_safe"],
            "description": palette["description"],
            "warning": f"n_groups={n_groups} is near maximum; consider faceting if adding more",
        }
    else:
        # Too many categories - warn and provide what we can
        return {
            "palette_name": "tableau10",
            "palette_type": "categorical",
            "colors": CATEGORICAL_PALETTES["tableau10"]["colors"],
            "colorblind_safe": True,
            "warning": f"n_groups={n_groups} exceeds recommended maximum of 7; "
            "strongly consider faceting, grouping, or using a sequential/heatmap approach",
            "description": "Extended palette with warning - consider redesign",
        }


def get_palette_colors(palette_name: str, n_colors: Optional[int] = None) -> List[str]:
    """Get hex color codes for a named palette.

    Args:
        palette_name: Name of palette
        n_colors: Number of colors to return (truncates if fewer needed)

    Returns:
        List of hex color codes
    """
    palette_name = palette_name.lower()

    # Check categorical palettes
    if palette_name in CATEGORICAL_PALETTES:
        colors = CATEGORICAL_PALETTES[palette_name]["colors"]
        if n_colors:
            return colors[:n_colors]
        return colors

    # Check binary palettes
    if palette_name in BINARY_PALETTES:
        return BINARY_PALETTES[palette_name]["colors"]

    # Sequential/diverging don't have discrete colors - return name for matplotlib
    if palette_name in SEQUENTIAL_PALETTES or palette_name in DIVERGING_PALETTES:
        raise ValueError(
            f"Palette '{palette_name}' is continuous. Use matplotlib_name for colormap."
        )

    raise ValueError(f"Unknown palette: {palette_name}")


def list_palettes(palette_type: Optional[str] = None) -> List[str]:
    """List available palette names.

    Args:
        palette_type: Filter by type ("categorical", "sequential", "diverging", "binary")
                     or None for all palettes

    Returns:
        List of palette names
    """
    if palette_type == "categorical":
        return list(CATEGORICAL_PALETTES.keys())
    elif palette_type == "sequential":
        return list(SEQUENTIAL_PALETTES.keys())
    elif palette_type == "diverging":
        return list(DIVERGING_PALETTES.keys())
    elif palette_type == "binary":
        return list(BINARY_PALETTES.keys())
    else:
        return (
            list(CATEGORICAL_PALETTES.keys())
            + list(SEQUENTIAL_PALETTES.keys())
            + list(DIVERGING_PALETTES.keys())
            + list(BINARY_PALETTES.keys())
        )
