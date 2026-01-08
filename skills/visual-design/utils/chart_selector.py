"""Chart type recommendation based on data characteristics.

Provides deterministic chart selection logic based on established visualization
principles. Eliminates LLM variance by encoding decision matrices as code.
"""

from typing import Dict, Any, Optional


CHART_RECOMMENDATIONS: Dict[str, Dict[str, Any]] = {
    "comparison_few_categories": {
        "recommended": ["bar", "dot_plot"],
        "acceptable": ["grouped_bar", "lollipop"],
        "avoid": ["pie", "3d_bar"],
        "reason": "Bar charts enable precise comparison; pie charts make comparisons difficult",
    },
    "comparison_many_categories": {
        "recommended": ["horizontal_bar", "heatmap"],
        "acceptable": ["dot_plot", "cleveland_dot"],
        "avoid": ["3d_bar", "pie", "vertical_bar"],
        "reason": "Horizontal bars accommodate labels; heatmaps show patterns in large datasets",
    },
    "time_series": {
        "recommended": ["line", "area"],
        "acceptable": ["step", "connected_scatter"],
        "avoid": ["bar", "pie"],
        "reason": "Line charts imply continuity; bar charts imply discrete measurements",
    },
    "time_series_multiple": {
        "recommended": ["multi_line", "small_multiples"],
        "acceptable": ["stacked_area", "ridgeline"],
        "avoid": ["pie", "3d"],
        "reason": "Multiple lines allow comparison; facets prevent overplotting",
    },
    "distribution": {
        "recommended": ["histogram", "violin", "box_plot"],
        "acceptable": ["density", "strip_plot", "swarm"],
        "avoid": ["bar_of_means", "pie"],
        "reason": "Distribution plots show spread and shape; bar of means hides variation",
    },
    "distribution_comparison": {
        "recommended": ["violin", "box_plot", "ridgeline"],
        "acceptable": ["overlapping_histogram", "strip_plot"],
        "avoid": ["bar_of_means", "pie"],
        "reason": "Side-by-side distributions enable direct comparison",
    },
    "relationship_2var": {
        "recommended": ["scatter"],
        "acceptable": ["hexbin", "contour"],
        "avoid": ["connected_scatter", "line"],
        "reason": "Scatter shows correlation; connected scatter implies ordered sequence",
    },
    "relationship_3var": {
        "recommended": ["scatter_with_color", "scatter_with_size"],
        "acceptable": ["bubble", "faceted_scatter"],
        "avoid": ["3d_scatter"],
        "reason": "Color/size encoding works well; 3D depth perception is poor",
    },
    "relationship_many_var": {
        "recommended": ["pairplot", "parallel_coordinates"],
        "acceptable": ["heatmap_correlation"],
        "avoid": ["3d", "pie"],
        "reason": "Pairplots show all relationships; parallel coordinates reveal patterns",
    },
    "part_to_whole": {
        "recommended": ["stacked_bar", "treemap"],
        "acceptable": ["waffle", "stacked_area"],
        "avoid": ["pie_many_segments", "3d_pie"],
        "reason": "Stacked bars enable comparison; pie charts fail with >5 segments",
    },
    "part_to_whole_simple": {
        "recommended": ["stacked_bar", "pie"],
        "acceptable": ["donut", "waffle"],
        "avoid": ["3d_pie"],
        "reason": "Pie acceptable for 2-5 categories; stacked bar preferred for precision",
    },
    "flow_network": {
        "recommended": ["sankey", "network_graph"],
        "acceptable": ["chord", "arc_diagram"],
        "avoid": ["table", "pie"],
        "reason": "Flow diagrams show relationships; tables obscure connections",
    },
    "ranking": {
        "recommended": ["horizontal_bar", "slope"],
        "acceptable": ["dot_plot", "bump_chart"],
        "avoid": ["pie", "scatter"],
        "reason": "Horizontal bars ordered by value; slope charts show rank changes",
    },
    "geospatial": {
        "recommended": ["choropleth", "point_map"],
        "acceptable": ["cartogram", "hex_map"],
        "avoid": ["pie_map", "3d_map"],
        "reason": "Choropleths show regional patterns; avoid 3D for accuracy",
    },
    "uncertainty": {
        "recommended": ["error_bar", "confidence_band"],
        "acceptable": ["gradient_interval", "violin"],
        "avoid": ["bar_without_error", "pie"],
        "reason": "Error bars/bands show uncertainty; hiding it is misleading",
    },
}


def recommend_chart_type(
    data_type: str,
    n_categories: Optional[int] = None,
    n_time_points: Optional[int] = None,
    n_groups: Optional[int] = None,
) -> Dict[str, Any]:
    """Recommend chart type based on data characteristics.

    Args:
        data_type: Type of data comparison. Supported types:
            - comparison: Comparing values across categories
            - time_series: Values over time
            - distribution: Shape of data spread
            - relationship: Correlation between variables
            - part_to_whole: Proportions of a whole
            - flow_network: Connections between entities
            - ranking: Ordered values
            - geospatial: Geographic data
            - uncertainty: Data with error/confidence
        n_categories: Number of categories (for comparison)
        n_time_points: Number of time points (for time series)
        n_groups: Number of groups being compared

    Returns:
        Dict with:
            - data_type: Original data type
            - recommended: List of recommended chart types
            - acceptable: List of acceptable alternatives
            - avoid: List of chart types to avoid
            - reason: Explanation for recommendation
    """
    # Normalize input
    normalized = data_type.lower().replace(" ", "_").replace("-", "_")

    # Handle category count thresholds for comparisons
    if normalized == "comparison":
        if n_categories is not None and n_categories > 7:
            normalized = "comparison_many_categories"
        else:
            normalized = "comparison_few_categories"

    # Handle multiple time series
    if normalized == "time_series" and n_groups is not None and n_groups > 1:
        normalized = "time_series_multiple"

    # Handle distribution comparisons
    if normalized == "distribution" and n_groups is not None and n_groups > 1:
        normalized = "distribution_comparison"

    # Handle relationship dimensionality
    if normalized == "relationship":
        if n_categories is not None and n_categories > 2:
            normalized = "relationship_many_var"
        elif n_groups is not None and n_groups > 0:
            normalized = "relationship_3var"
        else:
            normalized = "relationship_2var"

    # Handle part-to-whole with few vs many segments
    if normalized in ("part_to_whole", "proportion", "percentage"):
        if n_categories is not None and n_categories <= 5:
            normalized = "part_to_whole_simple"
        else:
            normalized = "part_to_whole"

    # Lookup in recommendations
    if normalized in CHART_RECOMMENDATIONS:
        return {
            "data_type": data_type,
            "resolved_type": normalized,
            **CHART_RECOMMENDATIONS[normalized],
        }

    # Default recommendation for unknown types
    return {
        "data_type": data_type,
        "resolved_type": "unknown",
        "recommended": ["bar", "scatter"],
        "acceptable": ["line", "dot_plot"],
        "avoid": ["3d", "pie"],
        "reason": "Safe defaults for unknown data type; consider data characteristics",
    }


def get_chart_description(chart_type: str) -> str:
    """Get description of a chart type and when to use it.

    Args:
        chart_type: Name of chart type

    Returns:
        Description string
    """
    descriptions = {
        "bar": "Vertical bars comparing discrete categories. Best for few categories with short labels.",
        "horizontal_bar": "Horizontal bars. Better for many categories or long labels.",
        "line": "Connected points showing trends. Implies continuity over ordered dimension.",
        "scatter": "Points showing relationship between two variables. No implied connection.",
        "histogram": "Bars showing frequency distribution. Bin width affects interpretation.",
        "box_plot": "Shows median, quartiles, and outliers. Compact distribution summary.",
        "violin": "Distribution shape with density curve. More detail than box plot.",
        "heatmap": "Color-encoded matrix. Good for patterns in many categories.",
        "pie": "Proportions of whole. Limited to 2-5 segments maximum.",
        "stacked_bar": "Proportions that sum to total. Better than pie for comparison.",
        "area": "Filled line chart. Shows magnitude and trend.",
        "sankey": "Flow between nodes. Shows transfers, conversions, paths.",
        "treemap": "Nested rectangles by size. Good for hierarchical part-to-whole.",
    }

    return descriptions.get(
        chart_type.lower(), f"No description available for '{chart_type}'."
    )


def list_data_types() -> list[str]:
    """Return list of supported data types for chart selection."""
    return [
        "comparison",
        "time_series",
        "distribution",
        "relationship",
        "part_to_whole",
        "flow_network",
        "ranking",
        "geospatial",
        "uncertainty",
    ]
