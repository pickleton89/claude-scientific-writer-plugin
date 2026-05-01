"""
Deterministic parameter lookup for plotting-libraries skill.

Converts prose decision tables to executable code for reproducible
parameter selection in scientific visualizations.

Usage:
    from scripts.plotting_params import (
        get_volcano_thresholds,
        get_journal_spec,
        get_palette,
        classify_plot_type,
        mm_to_inches,
    )
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


# =============================================================================
# THRESHOLD PRESETS (from volcano_plots.md)
# =============================================================================


class ThresholdPreset(Enum):
    """Predefined threshold stringency levels for volcano plots."""

    EXPLORATORY = "exploratory"
    STANDARD = "standard"
    STRINGENT = "stringent"
    VERY_STRINGENT = "very_stringent"


@dataclass(frozen=True)
class VolcanoThresholds:
    """Threshold parameters for volcano plots."""

    pvalue: float
    log2fc: float
    label: str


VOLCANO_THRESHOLDS: dict[ThresholdPreset, VolcanoThresholds] = {
    ThresholdPreset.EXPLORATORY: VolcanoThresholds(
        pvalue=0.05, log2fc=0.585, label="Exploratory (1.5-fold)"
    ),
    ThresholdPreset.STANDARD: VolcanoThresholds(
        pvalue=0.05, log2fc=1.0, label="Standard (2-fold, FDR)"
    ),
    ThresholdPreset.STRINGENT: VolcanoThresholds(
        pvalue=0.01, log2fc=1.5, label="Stringent (2.8-fold)"
    ),
    ThresholdPreset.VERY_STRINGENT: VolcanoThresholds(
        pvalue=0.001, log2fc=2.0, label="Very Stringent (4-fold)"
    ),
}


def get_volcano_thresholds(preset: str = "standard") -> VolcanoThresholds:
    """
    Get volcano plot thresholds by preset name.

    Parameters
    ----------
    preset : str
        One of: "exploratory", "standard", "stringent", "very_stringent"
        Default: "standard"

    Returns
    -------
    VolcanoThresholds
        Dataclass with pvalue, log2fc, and label fields

    Examples
    --------
    >>> t = get_volcano_thresholds("stringent")
    >>> t.pvalue
    0.01
    >>> t.log2fc
    1.5
    """
    try:
        return VOLCANO_THRESHOLDS[ThresholdPreset(preset)]
    except (ValueError, KeyError):
        return VOLCANO_THRESHOLDS[ThresholdPreset.STANDARD]


# =============================================================================
# JOURNAL FIGURE SPECIFICATIONS
# =============================================================================


@dataclass(frozen=True)
class JournalFigureSpec:
    """Figure specifications for a journal."""

    single_column_mm: float
    double_column_mm: float
    max_height_mm: float
    min_dpi: int
    preferred_format: str
    font_size_min_pt: int


JOURNAL_SPECS: dict[str, JournalFigureSpec] = {
    "nature": JournalFigureSpec(
        single_column_mm=89,
        double_column_mm=183,
        max_height_mm=247,
        min_dpi=300,
        preferred_format="pdf",
        font_size_min_pt=7,
    ),
    "cell": JournalFigureSpec(
        single_column_mm=85,
        double_column_mm=174,
        max_height_mm=230,
        min_dpi=300,
        preferred_format="pdf",
        font_size_min_pt=6,
    ),
    "science": JournalFigureSpec(
        single_column_mm=90,
        double_column_mm=180,
        max_height_mm=230,
        min_dpi=300,
        preferred_format="eps",
        font_size_min_pt=7,
    ),
    "plos": JournalFigureSpec(
        single_column_mm=83,
        double_column_mm=173,
        max_height_mm=230,
        min_dpi=300,
        preferred_format="tiff",
        font_size_min_pt=8,
    ),
    "elife": JournalFigureSpec(
        single_column_mm=88,
        double_column_mm=180,
        max_height_mm=240,
        min_dpi=300,
        preferred_format="pdf",
        font_size_min_pt=7,
    ),
    "default": JournalFigureSpec(
        single_column_mm=89,
        double_column_mm=183,
        max_height_mm=247,
        min_dpi=300,
        preferred_format="pdf",
        font_size_min_pt=7,
    ),
}


def get_journal_spec(journal: str) -> JournalFigureSpec:
    """
    Get figure specifications for a journal.

    Parameters
    ----------
    journal : str
        Journal name (case-insensitive): "nature", "cell", "science", "plos", "elife"

    Returns
    -------
    JournalFigureSpec
        Dataclass with dimension and format specifications

    Examples
    --------
    >>> spec = get_journal_spec("nature")
    >>> spec.single_column_mm
    89
    >>> spec.min_dpi
    300
    """
    return JOURNAL_SPECS.get(journal.lower(), JOURNAL_SPECS["default"])


def mm_to_inches(mm: float) -> float:
    """
    Convert millimeters to inches for matplotlib.

    Parameters
    ----------
    mm : float
        Measurement in millimeters

    Returns
    -------
    float
        Measurement in inches

    Examples
    --------
    >>> round(mm_to_inches(89), 4)  # Nature single-column
    3.5039
    """
    return mm / 25.4


def get_figsize_for_journal(
    journal: str, column_type: str = "single", height_mm: Optional[float] = None
) -> tuple[float, float]:
    """
    Get matplotlib figsize tuple for a journal.

    Parameters
    ----------
    journal : str
        Journal name
    column_type : str
        "single" or "double" column width
    height_mm : float, optional
        Height in mm. If None, uses golden ratio from width.

    Returns
    -------
    tuple[float, float]
        (width, height) in inches for matplotlib figsize

    Examples
    --------
    >>> w, h = get_figsize_for_journal("nature", "single")
    >>> round(w, 4), round(h, 4)
    (3.5039, 2.1656)
    """
    spec = get_journal_spec(journal)

    if column_type == "double":
        width_mm = spec.double_column_mm
    else:
        width_mm = spec.single_column_mm

    if height_mm is None:
        # Golden ratio
        height_mm = width_mm / 1.618

    width_in = mm_to_inches(width_mm)
    height_in = mm_to_inches(height_mm)

    return (width_in, height_in)


# =============================================================================
# COLOR PALETTES
# =============================================================================


@dataclass(frozen=True)
class ColorPalette:
    """Color palette with named colors."""

    name: str
    colors: tuple[str, ...]
    colorblind_safe: bool
    description: str


PALETTES: dict[str, ColorPalette] = {
    # Oligon brand (default)
    "oligon": ColorPalette(
        name="Oligon Brand",
        colors=("#222222", "#2DB2E8", "#666666", "#E8622D", "#999999"),
        colorblind_safe=True,
        description="Oligon Scientific brand colors",
    ),
    # Colorblind-safe palettes
    "okabe_ito": ColorPalette(
        name="Okabe-Ito",
        colors=(
            "#E69F00",
            "#56B4E9",
            "#009E73",
            "#F0E442",
            "#0072B2",
            "#D55E00",
            "#CC79A7",
        ),
        colorblind_safe=True,
        description="Colorblind-safe qualitative palette",
    ),
    "volcano": ColorPalette(
        name="Volcano Plot",
        colors=("#D55E00", "#0072B2", "#999999"),  # Up, Down, NS
        colorblind_safe=True,
        description="Up/Down/NS for volcano plots",
    ),
    "heatmap_diverging": ColorPalette(
        name="Heatmap Diverging",
        colors=("#2166AC", "#F7F7F7", "#B2182B"),  # Blue-White-Red
        colorblind_safe=True,
        description="Diverging colormap for z-scored data",
    ),
    # Sequential — viridis 7-stop sample (perceptually uniform, CVD-safe)
    # Use as discrete fallback; for continuous heatmaps prefer matplotlib's
    # 'viridis' / 'cividis' / Crameri 'batlow' colormaps directly.
    "viridis_7": ColorPalette(
        name="Viridis (7-stop)",
        colors=(
            "#440154",  # dark purple
            "#443983",
            "#31688E",
            "#21908C",
            "#35B779",
            "#8FD744",
            "#FDE725",  # bright yellow
        ),
        colorblind_safe=True,
        description="Perceptually uniform sequential palette (viridis sampled at 7 stops). Crameri 2020 / Smith & van der Walt 2015.",
    ),
    "categorical_8": ColorPalette(
        name="Categorical 8",
        colors=(
            "#4477AA",
            "#EE6677",
            "#228833",
            "#CCBB44",
            "#66CCEE",
            "#AA3377",
            "#BBBBBB",
            "#000000",
        ),
        colorblind_safe=True,
        description="Paul Tol's colorblind-safe categorical palette",
    ),
}


def get_palette(name: str = "oligon") -> ColorPalette:
    """
    Get color palette by name.

    Parameters
    ----------
    name : str
        Palette name: "oligon", "okabe_ito", "volcano", "heatmap_diverging", "categorical_8"

    Returns
    -------
    ColorPalette
        Dataclass with name, colors tuple, colorblind_safe flag, and description

    Examples
    --------
    >>> p = get_palette("volcano")
    >>> p.colors
    ('#D55E00', '#0072B2', '#999999')
    """
    return PALETTES.get(name.lower(), PALETTES["oligon"])


def get_volcano_colors() -> dict[str, str]:
    """
    Get standard volcano plot colors (colorblind-safe).

    Returns
    -------
    dict[str, str]
        Mapping of regulation status to hex color

    Examples
    --------
    >>> colors = get_volcano_colors()
    >>> colors["Up"]
    '#D55E00'
    """
    return {
        "Up": "#D55E00",  # Vermillion
        "Down": "#0072B2",  # Blue
        "NS": "#999999",  # Gray
    }


# =============================================================================
# CLUSTERING PARAMETERS
# =============================================================================


@dataclass(frozen=True)
class ClusteringParams:
    """Clustering parameters for heatmaps."""

    method: str
    metric: str
    description: str


CLUSTERING_DEFAULTS: dict[str, ClusteringParams] = {
    "expression": ClusteringParams(
        method="ward",
        metric="correlation",
        description="Gene expression (pattern similarity)",
    ),
    "euclidean": ClusteringParams(
        method="ward",
        metric="euclidean",
        description="Absolute differences (default)",
    ),
    "robust": ClusteringParams(
        method="average",
        metric="manhattan",
        description="Robust to outliers",
    ),
}


def get_clustering_params(data_type: str = "expression") -> ClusteringParams:
    """
    Get clustering parameters for data type.

    Parameters
    ----------
    data_type : str
        One of: "expression", "euclidean", "robust"

    Returns
    -------
    ClusteringParams
        Dataclass with method and metric fields

    Examples
    --------
    >>> params = get_clustering_params("expression")
    >>> params.method
    'ward'
    >>> params.metric
    'correlation'
    """
    return CLUSTERING_DEFAULTS.get(data_type, CLUSTERING_DEFAULTS["expression"])


# =============================================================================
# PLOT TYPE CLASSIFIER
# =============================================================================

PLOT_TYPE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "volcano": (
        "volcano",
        "differential expression",
        "fold change",
        "deseq",
        "edger",
        "limma",
        "de genes",
        "log2fc",
        "deseq2",
    ),
    "heatmap": (
        "heatmap",
        "expression matrix",
        "clustering",
        "clustermap",
        "pheatmap",
        "complexheatmap",
        "gene expression",
    ),
    "survival": (
        "kaplan",
        "survival",
        "km curve",
        "censoring",
        "cox",
        "survminer",
        "lifelines",
        "hazard",
    ),
    "genome_tracks": (
        "genome",
        "track",
        "chromosome",
        "genomic",
        "gviz",
        "pygenometracks",
        "igv",
        "coverage",
    ),
    "statistical": (
        "boxplot",
        "violin",
        "scatter",
        "correlation",
        "regression",
        "q-q",
        "qqplot",
        "forest plot",
        "anova",
        "t-test",
    ),
    "pca_umap": (
        "pca",
        "umap",
        "tsne",
        "dimensionality reduction",
        "embedding",
        "scanpy",
    ),
}


def classify_plot_type(user_request: str) -> str:
    """
    Classify user request to plot type.

    Returns the most likely plot type based on keyword matching.

    Parameters
    ----------
    user_request : str
        Natural language description of desired plot

    Returns
    -------
    str
        Plot type: "volcano", "heatmap", "survival", "genome_tracks",
        "statistical", "pca_umap", or "general"

    Examples
    --------
    >>> classify_plot_type("create a volcano plot for my DESeq2 results")
    'volcano'
    >>> classify_plot_type("heatmap with hierarchical clustering")
    'heatmap'
    >>> classify_plot_type("make a chart")
    'general'
    """
    request_lower = user_request.lower()

    scores: dict[str, int] = {}
    for plot_type, keywords in PLOT_TYPE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in request_lower)
        if score > 0:
            scores[plot_type] = score

    if scores:
        return max(scores, key=lambda k: scores[k])
    return "general"


# =============================================================================
# FIGURE INTENT CLASSIFIER (Fujii 2026 §"Identify the key message")
# =============================================================================
#
# Classifies the user's described intent into one of three Fujii categories:
#   description  -- showing distribution, overview, "what does the data look like"
#   difference   -- comparing groups (treated vs control, before vs after)
#   association  -- relationship between variables (predicts, correlates, scales with)
#
# This is the figure-design pre-step: Fujii (2026) argues intent should be
# identified BEFORE plot type, so that plot type follows from intent.

INTENT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "description": (
        "show",
        "distribution",
        "overview",
        "what does the data look like",
        "describe",
        "summarize",
        "summarise",
        "characterize",
        "characterise",
        "spread",
        "range of",
        "histogram of",
    ),
    "difference": (
        "compare",
        "comparison",
        "difference between",
        "differ between",
        "vs ",
        "vs.",
        "versus",
        "before and after",
        "treated vs control",
        "treatment vs",
        "case vs control",
        "knockout vs",
        "different",
        "differ",
    ),
    "association": (
        "predict",
        "correlate",
        "correlation",
        "scales with",
        "depends on",
        "relationship between",
        "association",
        "regression",
        "linked to",
        "varies with",
        "as a function of",
    ),
}


def classify_figure_intent(user_request: str) -> str:
    """
    Classify the figure's communicative intent (Fujii 2026).

    Returns one of: "description", "difference", "association", or "general".

    Parameters
    ----------
    user_request : str
        Natural language description of what the figure should show.

    Returns
    -------
    str
        Intent category. "general" if no keywords matched.

    Examples
    --------
    >>> classify_figure_intent("compare gene expression between treated and control")
    'difference'
    >>> classify_figure_intent("show the distribution of patient ages")
    'description'
    >>> classify_figure_intent("does dose predict response?")
    'association'
    >>> classify_figure_intent("make a chart")
    'general'
    """
    request_lower = user_request.lower()

    scores: dict[str, int] = {}
    for intent, keywords in INTENT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in request_lower)
        if score > 0:
            scores[intent] = score

    if scores:
        return max(scores, key=lambda k: scores[k])
    return "general"


# =============================================================================
# CHART RECOMMENDATIONS (intent + data shape -> ranked plot types)
# =============================================================================


@dataclass(frozen=True)
class ChartRecommendation:
    """A recommended (or discouraged) chart type with rationale and citation.

    Attributes
    ----------
    plot_type : str
        Plot identifier (e.g., "box+jitter", "scatter", "bar").
    rationale : str
        One-line rationale explaining why this is preferred / discouraged.
    discouraged : bool
        If True, the plot type is technically possible but actively discouraged
        (e.g., bar chart for continuous data per Weissgerber 2015).
    citation : Optional[str]
        Primary literature citation supporting the recommendation, when applicable.
    """

    plot_type: str
    rationale: str
    discouraged: bool = False
    citation: Optional[str] = None


def recommend_chart(
    intent: str,
    x_type: Optional[str] = None,
    y_type: Optional[str] = None,
    n_groups: Optional[int] = None,
    paired: bool = False,
) -> list[ChartRecommendation]:
    """
    Recommend ranked plot types for a given intent and data shape.

    Encodes Fujii (2026) §"Choose the right graph and colour" + Weissgerber 2015
    bar-chart anti-pattern + Fujii 2023 risk-ratio recommendation.

    Parameters
    ----------
    intent : str
        Figure intent: "description", "difference", or "association".
        Other strings return a permissive default list.
    x_type : str, optional
        "continuous", "categorical", or None.
    y_type : str, optional
        "continuous", "categorical", "point_estimate_ci", or None.
        "point_estimate_ci" indicates risk ratios / odds ratios / hazard ratios
        with confidence intervals (Fujii 2023).
    n_groups : int, optional
        Number of groups (for categorical comparisons).
    paired : bool
        Whether observations are paired across groups.

    Returns
    -------
    list[ChartRecommendation]
        Recommendations ordered with preferred plots first, discouraged last.

    Examples
    --------
    >>> recs = recommend_chart("difference", x_type="categorical", y_type="continuous", n_groups=2)
    >>> recs[0].plot_type
    'box+jitter'
    >>> any(r.plot_type == 'bar' and r.discouraged for r in recs)
    True
    """
    if intent == "description":
        if y_type == "continuous" or x_type == "continuous":
            return [
                ChartRecommendation(
                    "histogram",
                    "Shows distribution shape; minimal cognitive load.",
                ),
                ChartRecommendation(
                    "kde",
                    "Smooth distribution; useful when sample size > ~30.",
                ),
                ChartRecommendation(
                    "ecdf",
                    "No binning artefacts; preserves every data point.",
                ),
            ]
        if x_type == "categorical" or y_type == "categorical":
            return [
                ChartRecommendation(
                    "count_bar",
                    "Counts per category — bar chart is acceptable here (data are inherently discrete).",
                ),
                ChartRecommendation(
                    "pie",
                    "Acceptable for ≤3 categories; discouraged for more (Cleveland-McGill 1984: angle is a weak channel).",
                    discouraged=(n_groups is not None and n_groups > 3),
                    citation="Cleveland & McGill 1984",
                ),
            ]

    if intent == "difference":
        if y_type == "point_estimate_ci":
            return [
                ChartRecommendation(
                    "pointrange",
                    "Points with horizontal 95% CI lines; correct for risk ratios / odds ratios / hazard ratios.",
                    citation="Fujii 2023",
                ),
                ChartRecommendation(
                    "forest_plot",
                    "Multi-row pointrange variant; standard for meta-analyses and subgroup forest plots.",
                    citation="Fujii 2023",
                ),
                ChartRecommendation(
                    "bar",
                    "Bars exaggerate the point estimate at the expense of the CI; a wide-CI estimate looks deceptively confident.",
                    discouraged=True,
                    citation="Fujii 2023",
                ),
            ]
        if x_type == "categorical" and y_type == "continuous":
            if paired:
                return [
                    ChartRecommendation(
                        "paired_points_lines",
                        "Paired points connected by lines; preserves within-subject change (Fujii 2026 Fig. 1 §3.i).",
                        citation="Fujii 2026",
                    ),
                    ChartRecommendation(
                        "parallel_coordinates",
                        "Multi-condition extension of paired points.",
                        citation="Fujii 2026",
                    ),
                    ChartRecommendation(
                        "bar",
                        "Bars hide individual responses and the pairing structure.",
                        discouraged=True,
                        citation="Weissgerber 2015",
                    ),
                ]
            return [
                ChartRecommendation(
                    "box+jitter",
                    "Box summary + individual data points; preserves distribution.",
                    citation="Weissgerber 2015",
                ),
                ChartRecommendation(
                    "violin+jitter",
                    "Density estimate + individual points; useful when n is large.",
                    citation="Weissgerber 2015",
                ),
                ChartRecommendation(
                    "strip",
                    "Plain individual points; minimal ink.",
                    citation="Weissgerber 2015",
                ),
                ChartRecommendation(
                    "bar",
                    "Bar charts of continuous data hide the underlying distribution; identical-looking bars can come from radically different distributions.",
                    discouraged=True,
                    citation="Weissgerber 2015",
                ),
            ]

    if intent == "association":
        if x_type == "continuous" and y_type == "continuous":
            return [
                ChartRecommendation(
                    "scatter",
                    "Each point shows the (x, y) pair; relationship visible directly.",
                ),
                ChartRecommendation(
                    "scatter_with_regression",
                    "Scatter + regression line with CI band; useful when association is the main message.",
                ),
                ChartRecommendation(
                    "hexbin",
                    "For high-density scatter where overplotting obscures pattern.",
                ),
            ]

    # Permissive default
    return [
        ChartRecommendation(
            "general",
            "No specific recommendation; consult plot_selection_guide.md.",
        ),
    ]


# =============================================================================
# PALETTE RECOMMENDATIONS BY SCALE TYPE
# =============================================================================


def recommend_palette(
    scale_type: str,
    n_levels: Optional[int] = None,
) -> ColorPalette:
    """
    Recommend a palette matched to the data's scale type.

    Fujii (2026) §"Choose the right graph and colour":
    - categorical -> distinguish groups
    - sequential  -> increasing magnitude (low to high)
    - diverging   -> deviation from a reference point (negative / zero / positive)

    For categorical data with n_levels > 8, emits a `logging.warning` per Cowan
    2010 working-memory limit (~4 chunks; 8 is a soft upper bound for figure
    legibility). For sequential data with n_levels > 7, warns that the discrete
    viridis sample is exceeded and recommends the continuous matplotlib colormap.

    Parameters
    ----------
    scale_type : str
        One of: "categorical", "sequential", "diverging".
    n_levels : int, optional
        Number of distinct levels in the data. Only used for warnings.

    Returns
    -------
    ColorPalette
        Recommended palette from PALETTES.

    Examples
    --------
    >>> p = recommend_palette("categorical", n_levels=4)
    >>> p.name
    'Okabe-Ito'
    >>> p = recommend_palette("sequential", n_levels=5)
    >>> p.name
    'Viridis (7-stop)'
    >>> p = recommend_palette("diverging")
    >>> p.name
    'Heatmap Diverging'
    """
    import logging

    scale_type = scale_type.lower().strip()

    if scale_type == "categorical":
        if n_levels is not None and n_levels > 8:
            logging.warning(
                "recommend_palette: %d categorical levels exceeds the 8-level "
                "soft upper bound (Cowan 2010 working-memory ~4 chunks). "
                "Consider faceting / small multiples or collapsing categories.",
                n_levels,
            )
        if n_levels is not None and n_levels <= 7:
            return PALETTES["okabe_ito"]
        return PALETTES["categorical_8"]

    if scale_type == "sequential":
        # Discrete viridis sample. For continuous heatmaps, callers should use
        # matplotlib's 'viridis' / 'cividis' / Crameri colormaps directly via
        # cmap=, not this discrete palette.
        if n_levels is not None and n_levels > 7:
            logging.warning(
                "recommend_palette: %d sequential levels exceeds the 7-stop "
                "discrete viridis sample. For finer granularity use a continuous "
                "matplotlib colormap (cmap='viridis' / 'cividis' / Crameri 'batlow').",
                n_levels,
            )
        return PALETTES["viridis_7"]

    if scale_type == "diverging":
        return PALETTES["heatmap_diverging"]

    raise ValueError(
        f"recommend_palette: unknown scale_type {scale_type!r}; "
        "expected 'categorical', 'sequential', or 'diverging'."
    )


# =============================================================================
# ECOSYSTEM CLASSIFIER
# =============================================================================

ECOSYSTEM_KEYWORDS: dict[str, tuple[str, ...]] = {
    "python": (
        "python",
        "matplotlib",
        "seaborn",
        "pandas",
        "numpy",
        "jupyter",
        "scanpy",
        "lifelines",
        "pygenometracks",
    ),
    "r": (
        "ggplot",
        "ggplot2",
        "bioconductor",
        "complexheatmap",
        "enhancedvolcano",
        "survminer",
        "gviz",
        "deseq2",
        "edger",
        "pheatmap",
    ),
}


def classify_ecosystem(
    user_request: str, data_context: Optional[str] = None
) -> str:
    """
    Classify preferred ecosystem (python/r) from request.

    Parameters
    ----------
    user_request : str
        Natural language description
    data_context : str, optional
        Additional context about data sources

    Returns
    -------
    str
        "python", "r", or "auto" if unclear

    Examples
    --------
    >>> classify_ecosystem("use matplotlib")
    'python'
    >>> classify_ecosystem("ggplot2 figure")
    'r'
    >>> classify_ecosystem("make a bar chart")
    'auto'
    """
    request_lower = user_request.lower()
    if data_context:
        request_lower += " " + data_context.lower()

    python_score = sum(1 for kw in ECOSYSTEM_KEYWORDS["python"] if kw in request_lower)
    r_score = sum(1 for kw in ECOSYSTEM_KEYWORDS["r"] if kw in request_lower)

    if python_score > r_score:
        return "python"
    elif r_score > python_score:
        return "r"
    return "auto"


# =============================================================================
# RANDOM SEED CONSTANT
# =============================================================================

# Standard random seed for reproducible clustering
RANDOM_SEED = 42


def get_random_seed() -> int:
    """
    Get the standard random seed for reproducible computations.

    Returns
    -------
    int
        Random seed (42)

    Examples
    --------
    >>> import numpy as np
    >>> np.random.seed(get_random_seed())
    """
    return RANDOM_SEED
