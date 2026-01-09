"""
Plotting-libraries deterministic utilities.

This package provides deterministic parameter lookups and validation
for scientific visualizations.

Modules
-------
plotting_params
    Parameter lookup tables for thresholds, journal specs, colors, clustering
validate_data
    Input data validation for volcano plots, heatmaps, etc.
validate_figure
    Output figure validation for format, DPI, dimensions
"""

try:
    from .plotting_params import (
        get_volcano_thresholds,
        get_journal_spec,
        get_figsize_for_journal,
        get_palette,
        get_volcano_colors,
        get_clustering_params,
        classify_plot_type,
        classify_ecosystem,
        mm_to_inches,
        get_random_seed,
        RANDOM_SEED,
        VolcanoThresholds,
        JournalFigureSpec,
        ColorPalette,
        ClusteringParams,
        ThresholdPreset,
    )
    from .validate_data import (
        validate_volcano_data,
        validate_heatmap_data,
        validate_survival_data,
        ValidationResult,
        print_validation,
    )
    from .validate_figure import (
        validate_figure,
        validate_figure_for_journal,
        FigureValidation,
        print_validation as print_figure_validation,
    )
except ImportError:
    # Fallback for direct script execution
    from plotting_params import (  # noqa: F401
        get_volcano_thresholds,
        get_journal_spec,
        get_figsize_for_journal,
        get_palette,
        get_volcano_colors,
        get_clustering_params,
        classify_plot_type,
        classify_ecosystem,
        mm_to_inches,
        get_random_seed,
        RANDOM_SEED,
        VolcanoThresholds,
        JournalFigureSpec,
        ColorPalette,
        ClusteringParams,
        ThresholdPreset,
    )
    from validate_data import (  # noqa: F401
        validate_volcano_data,
        validate_heatmap_data,
        validate_survival_data,
        ValidationResult,
        print_validation,
    )
    from validate_figure import (  # noqa: F401
        validate_figure,
        validate_figure_for_journal,
        FigureValidation,
        print_validation as print_figure_validation,
    )

__all__ = [
    # plotting_params
    "get_volcano_thresholds",
    "get_journal_spec",
    "get_figsize_for_journal",
    "get_palette",
    "get_volcano_colors",
    "get_clustering_params",
    "classify_plot_type",
    "classify_ecosystem",
    "mm_to_inches",
    "get_random_seed",
    "RANDOM_SEED",
    "VolcanoThresholds",
    "JournalFigureSpec",
    "ColorPalette",
    "ClusteringParams",
    "ThresholdPreset",
    # validate_data
    "validate_volcano_data",
    "validate_heatmap_data",
    "validate_survival_data",
    "ValidationResult",
    "print_validation",
    # validate_figure
    "validate_figure",
    "validate_figure_for_journal",
    "FigureValidation",
    "print_figure_validation",
]
