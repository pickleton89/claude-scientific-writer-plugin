"""
Data validation for plotting inputs.

Provides deterministic checks before plotting to catch common errors
and warn about potential issues.

Usage:
    from scripts.validate_data import (
        validate_volcano_data,
        validate_heatmap_data,
        check_continuous_as_bars,
        check_riskratio_as_bars,
        check_encoding_value_fidelity,
        check_closure,
        check_default_palette,
        print_validation,
    )
"""

import math
import re
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd


@dataclass
class ValidationResult:
    """Result of data validation."""

    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        """Allow using result directly in if statements."""
        return self.valid

    def add_error(self, message: str) -> None:
        """Add an error message."""
        self.errors.append(message)
        self.valid = False

    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)


def validate_volcano_data(
    df: pd.DataFrame,
    log2fc_col: str = "log2FoldChange",
    pvalue_col: str = "padj",
    gene_col: Optional[str] = "gene_symbol",
) -> ValidationResult:
    """
    Validate DataFrame for volcano plot.

    Checks:
    - Required columns exist
    - P-values in [0, 1] range
    - No NaN in critical columns
    - Log2FC is numeric

    Parameters
    ----------
    df : pd.DataFrame
        Differential expression results
    log2fc_col : str
        Column name for log2 fold change (default: "log2FoldChange")
    pvalue_col : str
        Column name for p-value (default: "padj")
    gene_col : str, optional
        Column name for gene identifiers (default: "gene_symbol")

    Returns
    -------
    ValidationResult
        Result with valid flag, errors list, and warnings list

    Examples
    --------
    >>> df = pd.DataFrame({
    ...     'gene_symbol': ['A', 'B', 'C'],
    ...     'log2FoldChange': [1.5, -2.0, 0.1],
    ...     'padj': [0.001, 0.01, 0.5],
    ... })
    >>> result = validate_volcano_data(df)
    >>> result.valid
    True
    """
    result = ValidationResult(valid=True)

    # Check required columns
    if log2fc_col not in df.columns:
        result.add_error(
            f"Column '{log2fc_col}' not found. Available: {list(df.columns)}"
        )
    if pvalue_col not in df.columns:
        result.add_error(
            f"Column '{pvalue_col}' not found. Available: {list(df.columns)}"
        )

    if not result.valid:
        return result

    # Check p-value range
    pvals = df[pvalue_col]
    pval_min = pvals.min()
    pval_max = pvals.max()

    if pval_min < 0 or pval_max > 1:
        result.add_error(
            f"P-values in '{pvalue_col}' must be in [0, 1]. "
            f"Found range: [{pval_min:.2e}, {pval_max:.2e}]"
        )

    # Check for NaN
    nan_pval = pvals.isna().sum()
    nan_fc = df[log2fc_col].isna().sum()
    if nan_pval > 0:
        result.add_warning(f"{nan_pval} NaN values in '{pvalue_col}' will be excluded")
    if nan_fc > 0:
        result.add_warning(f"{nan_fc} NaN values in '{log2fc_col}' will be excluded")

    # Check log2FC is numeric
    if not pd.api.types.is_numeric_dtype(df[log2fc_col]):
        result.add_error(f"Column '{log2fc_col}' must be numeric")

    # Check gene column
    if gene_col and gene_col not in df.columns:
        result.add_warning(
            f"Gene column '{gene_col}' not found; gene labeling disabled"
        )

    # Check for adjusted p-values
    if "pvalue" in pvalue_col.lower() and "adj" not in pvalue_col.lower():
        result.add_warning(
            "Using unadjusted p-values? Consider 'padj' for multiple testing correction"
        )

    # Check for zero p-values (common in DESeq2)
    zero_pvals = (pvals == 0).sum()
    if zero_pvals > 0:
        result.add_warning(
            f"{zero_pvals} genes have p-value = 0 (will be capped at 1e-300 in -log10)"
        )

    # Check data size
    n_rows = len(df)
    if n_rows > 50000:
        result.add_warning(
            f"{n_rows} genes may slow rendering; consider filtering to significant genes"
        )

    return result


def validate_heatmap_data(
    df: pd.DataFrame,
    expected_rows: Optional[int] = None,
    expected_cols: Optional[int] = None,
) -> ValidationResult:
    """
    Validate DataFrame/matrix for heatmap.

    Checks:
    - Data is numeric
    - No infinite values
    - Reasonable dimensions
    - Variance is non-zero (for z-scoring)

    Parameters
    ----------
    df : pd.DataFrame
        Expression matrix (genes x samples)
    expected_rows : int, optional
        Expected number of rows (genes)
    expected_cols : int, optional
        Expected number of columns (samples)

    Returns
    -------
    ValidationResult
        Result with valid flag, errors list, and warnings list

    Examples
    --------
    >>> df = pd.DataFrame(np.random.randn(100, 10))
    >>> result = validate_heatmap_data(df)
    >>> result.valid
    True
    """
    result = ValidationResult(valid=True)

    # Check numeric
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) != len(df.columns):
        non_numeric = set(df.columns) - set(numeric_cols)
        result.add_error(f"Non-numeric columns found: {non_numeric}")

    if not result.valid:
        return result

    # Check for infinite values
    if np.isinf(df.select_dtypes(include=[np.number]).values).any():
        result.add_error("Infinite values found in data")

    # Check dimensions
    n_rows, n_cols = df.shape

    if expected_rows is not None and n_rows != expected_rows:
        result.add_warning(f"Expected {expected_rows} rows, got {n_rows}")
    if expected_cols is not None and n_cols != expected_cols:
        result.add_warning(f"Expected {expected_cols} columns, got {n_cols}")

    if n_rows > 500:
        result.add_warning(
            f"{n_rows} rows may be too many for readable heatmap; "
            "consider filtering to top variable genes"
        )
    if n_cols > 100:
        result.add_warning(
            f"{n_cols} columns may be too many; consider sample subsetting"
        )
    if n_rows < 2:
        result.add_error("Need at least 2 rows for clustering")
    if n_cols < 2:
        result.add_error("Need at least 2 columns for clustering")

    # Check for NaN values
    nan_count = df.isna().sum().sum()
    if nan_count > 0:
        nan_pct = 100 * nan_count / (n_rows * n_cols)
        if nan_pct > 10:
            result.add_error(
                f"{nan_pct:.1f}% NaN values; imputation or filtering required"
            )
        else:
            result.add_warning(
                f"{nan_count} NaN values ({nan_pct:.1f}%); consider imputation"
            )

    # Check for constant rows (zero variance)
    try:
        variances = df.var(axis=1)
        zero_var = (variances == 0).sum()
        if zero_var > 0:
            result.add_warning(
                f"{zero_var} rows have zero variance (will cause NaN after z-scoring)"
            )
    except TypeError:
        # Non-numeric data
        pass

    return result


def validate_survival_data(
    df: pd.DataFrame,
    time_col: str = "time",
    event_col: str = "event",
    group_col: Optional[str] = None,
) -> ValidationResult:
    """
    Validate DataFrame for survival analysis.

    Checks:
    - Required columns exist
    - Time values are positive
    - Event values are binary (0/1)
    - No NaN in critical columns

    Parameters
    ----------
    df : pd.DataFrame
        Survival data
    time_col : str
        Column name for time-to-event (default: "time")
    event_col : str
        Column name for event indicator (default: "event")
    group_col : str, optional
        Column name for group/strata

    Returns
    -------
    ValidationResult
        Result with valid flag, errors list, and warnings list
    """
    result = ValidationResult(valid=True)

    # Check required columns
    if time_col not in df.columns:
        result.add_error(
            f"Time column '{time_col}' not found. Available: {list(df.columns)}"
        )
    if event_col not in df.columns:
        result.add_error(
            f"Event column '{event_col}' not found. Available: {list(df.columns)}"
        )

    if not result.valid:
        return result

    # Check time values
    times = df[time_col]
    if (times < 0).any():
        result.add_error("Time values must be non-negative")
    if times.isna().any():
        result.add_warning(
            f"{times.isna().sum()} NaN values in time column will be excluded"
        )

    # Check event values
    events = df[event_col]
    unique_events = events.dropna().unique()
    if not set(unique_events).issubset({0, 1, True, False}):
        result.add_error(
            f"Event column should be binary (0/1). Found values: {unique_events}"
        )

    # Check group column
    if group_col:
        if group_col not in df.columns:
            result.add_warning(f"Group column '{group_col}' not found")
        else:
            n_groups = df[group_col].nunique()
            if n_groups > 10:
                result.add_warning(
                    f"{n_groups} groups may make survival plot difficult to read"
                )

    # Check sample size
    n_samples = len(df)
    if n_samples < 10:
        result.add_warning(
            f"Only {n_samples} samples; survival estimates may be unreliable"
        )

    # Check event rate
    event_rate = events.mean()
    if event_rate < 0.1:
        result.add_warning(
            f"Low event rate ({event_rate:.1%}); consider longer follow-up"
        )
    if event_rate > 0.9:
        result.add_warning(
            f"High event rate ({event_rate:.1%}); most subjects experienced event"
        )

    return result


def print_validation(result: ValidationResult) -> None:
    """
    Print validation result in human-readable format.

    Parameters
    ----------
    result : ValidationResult
        Validation result to print
    """
    if result.valid:
        print("Validation passed")
    else:
        print("Validation failed")

    for error in result.errors:
        print(f"  ERROR: {error}")
    for warning in result.warnings:
        print(f"  WARNING: {warning}")


# CLI interface
if __name__ == "__main__":
    import sys

    # Simple test
    print("Running validation module tests...")

    # Test volcano validation
    df_volcano = pd.DataFrame(
        {
            "gene_symbol": ["A", "B", "C"],
            "log2FoldChange": [1.5, -2.0, 0.1],
            "padj": [0.001, 0.01, 0.5],
        }
    )
    result = validate_volcano_data(df_volcano)
    print("\nVolcano data validation:")
    print_validation(result)
    assert result.valid, "Valid volcano data should pass"

    # Test heatmap validation
    df_heatmap = pd.DataFrame(np.random.randn(50, 8))
    result = validate_heatmap_data(df_heatmap)
    print("\nHeatmap data validation:")
    print_validation(result)
    assert result.valid, "Valid heatmap data should pass"

    # Test survival validation
    df_survival = pd.DataFrame(
        {
            "time": [10, 20, 30, 40, 50],
            "event": [1, 0, 1, 0, 1],
            "group": ["A", "A", "B", "B", "A"],
        }
    )
    result = validate_survival_data(df_survival, group_col="group")
    print("\nSurvival data validation:")
    print_validation(result)
    assert result.valid, "Valid survival data should pass"

    print("\nAll tests passed!")
    sys.exit(0)


# =============================================================================
# CHART-DESIGN VALIDATORS (Fujii 2026, Weissgerber 2015, Fujii 2023)
# =============================================================================
#
# These validators check semantic plot-design choices, not file properties.
# They flag known anti-patterns:
#
#   check_continuous_as_bars  -- Weissgerber 2015 PLoS Biol: bar charts of
#                                continuous data hide the underlying distribution.
#   check_riskratio_as_bars   -- Fujii 2023 J Epidemiol: risk ratios / odds
#                                ratios / hazard ratios should be drawn as
#                                points + 95% CI, not as bars.
#   check_encoding_value_fidelity -- AI-figure-slop dim 2.1: bar/pie/point
#                                geometry must reconcile to printed value-labels.
#   check_closure             -- dim 2.2: parts-of-whole must sum to the whole
#                                (pie ~100%, stacked-bar to declared total).
#   check_default_palette     -- dim 6.2 (two-sided, advisory): flags literal
#                                matplotlib tab10 / seaborn-deep default cycles.
#
# The latter three are GENERATION-time exact checks against data we already
# hold (the plotted values + chosen encoding + palette) -- no OCR, no forensic
# CV, no image->data recovery. They honor two guardrails: (1) each returns an
# independent ValidationResult so the orchestrator collects a vector of
# (check, severity, message), never a composite "slop score"; every threshold is
# documented PROVISIONAL / UNCALIBRATED in-docstring. (2) Categorical tells
# DOMINATE (add_error / valid=False) for encoding-value and closure failures,
# while the weak, two-sided aesthetic palette signal is warning-only and never
# instructs stripping decoration / minimizing ink (Bateman CHI2010:
# over-minimization is itself regression-to-mean).
#
# All functions are pure / side-effect-free; they return ValidationResult and
# never raise. Wire them into figure pre-flight before saving.


def _is_continuous_data(data: object) -> bool:
    """Heuristic: is `data` a continuous numerical sample (per group), not a discrete count?

    Accepts: numpy arrays, pandas Series, lists/tuples of numbers, or a dict /
    DataFrame keyed by group name with numerical values per group.

    Returns True if the underlying values are real-valued and have variance
    that suggests an empirical distribution rather than a single count per group.
    """
    if isinstance(data, pd.DataFrame):
        # Treat each non-grouping column as a candidate continuous sample
        numeric_cols = data.select_dtypes(include=[np.number])
        if numeric_cols.empty:
            return False
        # If any numeric column has more than one unique value per group-block,
        # treat as continuous.
        for col in numeric_cols.columns:
            values = numeric_cols[col].dropna().to_numpy()
            if len(values) > 5 and len(np.unique(values)) > 3:
                return True
        return False

    if isinstance(data, dict):
        for group_values in data.values():
            if _is_continuous_data(group_values):
                return True
        return False

    if isinstance(data, (list, tuple, np.ndarray, pd.Series)):
        try:
            arr = np.asarray(data, dtype=float)
        except (TypeError, ValueError):
            return False
        finite = arr[np.isfinite(arr)]
        if len(finite) <= 5:
            return False
        # Continuous if it has more than ~3 unique values
        return len(np.unique(finite)) > 3

    return False


def check_continuous_as_bars(
    data: object,
    plot_type: str,
) -> ValidationResult:
    """
    Check whether continuous data is being drawn as a bar chart (Weissgerber 2015 anti-pattern).

    Bar charts of continuous data hide the underlying distribution. Two datasets
    with identical means but radically different distributions produce identical-
    looking bars. Use box+jitter, violin+jitter, or strip plots instead.

    Parameters
    ----------
    data : array-like, dict, or DataFrame
        The data to be plotted. If a dict / DataFrame, each value / column
        per group is checked for continuity.
    plot_type : str
        The intended plot type. Bar / barplot / column trigger the warning.

    Returns
    -------
    ValidationResult
        `valid=True` always (this is advisory, not blocking).
        `warnings` populated if a bar chart is being applied to continuous data.

    Examples
    --------
    >>> import numpy as np
    >>> data = {"control": np.random.normal(0, 1, 50), "treated": np.random.normal(1, 1, 50)}
    >>> r = check_continuous_as_bars(data, "bar")
    >>> bool(r.warnings)
    True
    >>> r = check_continuous_as_bars({"a": [10], "b": [12]}, "bar")  # discrete counts
    >>> bool(r.warnings)
    False
    """
    result = ValidationResult(valid=True)

    plot_type_lower = (plot_type or "").lower().strip()
    bar_aliases = {"bar", "barplot", "bar chart", "barchart", "column"}

    if plot_type_lower not in bar_aliases:
        return result

    if not _is_continuous_data(data):
        return result

    result.add_warning(
        "check_continuous_as_bars: bar chart applied to continuous data. "
        "Bar charts hide the underlying distribution; identical-looking bars "
        "can come from radically different distributions. "
        "Use box+jitter, violin+jitter, or strip plot instead "
        "(Weissgerber et al. 2015 PLoS Biol, doi:10.1371/journal.pbio.1002128). "
        "See plotting-libraries/references/plot_selection_guide.md for code recipes."
    )
    return result


_RISKRATIO_PATTERNS = (
    r"\bodds[\s_-]?ratio",
    r"\brisk[\s_-]?ratio",
    r"\bhazard[\s_-]?ratio",
    r"\brate[\s_-]?ratio",
    r"\bincidence[\s_-]?rate[\s_-]?ratio",
    r"\bincidence[\s_-]?ratio",
    r"\brelative[\s_-]?risk",
    r"\b(or)\b\s*\(",  # "OR (95% CI..."
    r"\b(rr)\b\s*\(",
    r"\b(hr)\b\s*\(",
)


def check_riskratio_as_bars(
    plot_type: str,
    data_label: str,
) -> ValidationResult:
    """
    Check whether a risk ratio / odds ratio / hazard ratio is being drawn as bars (Fujii 2023 anti-pattern).

    Bars exaggerate the visual weight of the point estimate at the expense of
    the confidence interval; a wide-CI estimate looks deceptively confident as
    a bar. Use `pointrange` (point + horizontal CI line) or a forest plot.

    Parameters
    ----------
    plot_type : str
        The intended plot type. Bar / barplot / column trigger the check.
    data_label : str
        The y-axis label or data description string. Patterns like
        "Odds ratio (95% CI)", "Hazard ratio", "OR (95% CI)" trigger the warning.

    Returns
    -------
    ValidationResult
        `valid=True` always (advisory).
        `warnings` populated if bar chart + ratio-with-CI label match.

    Examples
    --------
    >>> r = check_riskratio_as_bars("bar", "Odds ratio (95% CI)")
    >>> bool(r.warnings)
    True
    >>> r = check_riskratio_as_bars("bar", "Sample size")
    >>> bool(r.warnings)
    False
    >>> r = check_riskratio_as_bars("pointrange", "Hazard ratio (95% CI)")
    >>> bool(r.warnings)
    False
    """
    result = ValidationResult(valid=True)

    plot_type_lower = (plot_type or "").lower().strip()
    bar_aliases = {"bar", "barplot", "bar chart", "barchart", "column"}

    if plot_type_lower not in bar_aliases:
        return result

    label_lower = (data_label or "").lower()
    matched = any(re.search(pattern, label_lower) for pattern in _RISKRATIO_PATTERNS)
    if not matched:
        return result

    result.add_warning(
        "check_riskratio_as_bars: bar chart applied to a ratio-with-CI estimate. "
        "Bars exaggerate the point estimate at the expense of the CI; "
        "wide-CI estimates look deceptively confident as bars. "
        "Use pointrange (point + horizontal CI line) or a forest plot "
        "(Fujii 2023 J Epidemiol 33:487-488). "
        "See plotting-libraries/references/plot_selection_guide.md §Risk-ratio recipe."
    )
    return result


# =============================================================================
# AI-FIGURE-SLOP VALIDATORS (generation-time exact checks; ai_figure_slop.md)
# =============================================================================
#
# We GENERATE the figures, so we hold ground-truth data + the chosen encoding +
# the palette. These three checks reconcile that held data deterministically;
# they never OCR, never run forensic CV, never recover data from pixels (that
# stack is inbound-only / advisory). Thresholds below are PROVISIONAL /
# UNCALIBRATED -- a constructed instrument that still needs calibration.

# Bar/column/stacked aliases reused by the fidelity + closure checks.
_BAR_ENCODINGS = {"bar", "barplot", "bar chart", "barchart", "column"}
_STACKED_ENCODINGS = {
    "stacked_bar",
    "stacked bar",
    "stacked_column",
    "stacked column",
    "100_stacked_bar",
    "100% stacked bar",
    "100_stacked_column",
}
_PIE_ENCODINGS = {"pie", "donut", "doughnut"}
_POINT_ENCODINGS = {"scatter", "point", "line"}


def _coerce_keyed_floats(values: object) -> tuple[list, list[float], int]:
    """Coerce a values container to ordered (keys, floats), dropping NaN.

    Accepts dict[str, number] (insertion order), pandas Series (index order),
    or list/tuple/np.ndarray (positional index). Returns (keys, floats,
    n_dropped_nan). Non-coercible entries are dropped and counted as NaN.
    """
    keys: list = []
    raw: list = []
    if isinstance(values, dict):
        for k, v in values.items():
            keys.append(k)
            raw.append(v)
    elif isinstance(values, pd.Series):
        for k, v in values.items():
            keys.append(k)
            raw.append(v)
    elif isinstance(values, (list, tuple, np.ndarray)):
        seq = list(values)
        keys = list(range(len(seq)))
        raw = seq
    else:
        # Single scalar -> one positional entry.
        keys = [0]
        raw = [values]

    out_keys: list = []
    out_vals: list[float] = []
    n_dropped = 0
    for k, v in zip(keys, raw):
        try:
            fv = float(v)
        except (TypeError, ValueError):
            n_dropped += 1
            continue
        if math.isnan(fv):
            n_dropped += 1
            continue
        out_keys.append(k)
        out_vals.append(fv)
    return out_keys, out_vals, n_dropped


def _coerce_parallel_floats(obj: object, keys: list) -> Optional[list[Optional[float]]]:
    """Coerce a parallel container (geometry / printed_labels) to floats aligned
    to ``keys``.

    Returns a list the same length as ``keys`` (None per unparseable entry), or
    None if the container length / keys don't align (caller emits a warning).
    Numeric strings are parsed by stripping %, ',', '$', and whitespace.
    """
    if obj is None:
        return None

    if isinstance(obj, dict):
        try:
            ordered = [obj[k] for k in keys]
        except (KeyError, TypeError):
            return None
    elif isinstance(obj, pd.Series):
        ordered = list(obj.values)
    elif isinstance(obj, (list, tuple, np.ndarray)):
        ordered = list(obj)
    else:
        ordered = [obj]

    if len(ordered) != len(keys):
        return None

    out: list[Optional[float]] = []
    for v in ordered:
        out.append(_parse_label_number(v))
    return out


def _parse_label_number(v: object) -> Optional[float]:
    """Parse a printed label / geometry entry into a float, or None.

    Strips '%', ',', '$', and surrounding whitespace from strings. Returns None
    for unparseable / NaN entries (caller decides whether that is a warning).
    """
    if v is None:
        return None
    if isinstance(v, (int, float, np.integer, np.floating)):
        fv = float(v)
        return None if math.isnan(fv) else fv
    if isinstance(v, str):
        cleaned = v.strip().replace("%", "").replace(",", "").replace("$", "").strip()
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None
    try:
        fv = float(v)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(fv) else fv


def check_encoding_value_fidelity(
    values: object,
    encoding: str,
    *,
    printed_labels: object = None,
    geometry: object = None,
    rel_tol: float = 0.01,
    abs_tol: float = 1e-9,
    axis_is_log: bool = False,
    axis_baseline: float = 0.0,
) -> ValidationResult:
    """Reconcile geometry / printed value-labels against the encoded values
    (AI-figure-slop dimension 2.1, a *categorical* tell).

    Because we generate the figure we hold both the true data values and the
    labels/geometry we are about to stamp. The geometric measure of each mark
    must be a consistent linear transform of the value it encodes, and any
    printed value-label must equal the value the geometry encodes. A mismatch
    beyond tolerance is a dominating categorical tell -> ``add_error``
    (``valid=False``). Soft / inconclusive conditions -> ``add_warning``.

    Geometry law by encoding:
      - bar/column/stacked_bar: length linear in ``(value - axis_baseline)``;
        on a log axis, linear in ``log10(value) - log10(axis_min)``.
      - pie/donut: wedge angle (deg) linear in value, total = 360 deg.
      - scatter/point/line: position linear in value (identity).

    Parameters
    ----------
    values : array-like or dict[str, number]
        The numeric series being encoded geometrically (the ground truth).
    encoding : str
        One of bar/column/stacked_bar/pie/donut/scatter/point/line
        (case-insensitive; bar aliases normalized). Unknown -> warning, no-op.
    printed_labels : array-like or dict, optional
        The literal value-labels the caller will stamp, parallel to ``values``.
        Each may be a number or numeric string ("42", "3.0%", "1,250").
        ``None`` skips the label-fidelity branch.
    geometry : array-like or dict, optional
        The actual rendered measure per mark (bar height, wedge degrees, point
        coord), parallel to ``values``. When supplied the check verifies it is
        the correct monotone transform of ``values``. ``None`` assumes the
        canonical law for ``encoding``.
    rel_tol, abs_tol : float
        Reconciliation tolerance (``math.isclose`` semantics). Defaults
        (1% relative) are **PROVISIONAL / UNCALIBRATED**.
    axis_is_log : bool
        Bar length is measured in log10-space; any ``value <= 0`` -> error.
    axis_baseline : float
        Non-zero bar baseline (truncated axis). Honored in the geometry law,
        but the *printed label* must still equal the full value, not
        ``value - baseline``.

    Returns
    -------
    ValidationResult
        ``valid=False`` on any reconciliation failure beyond tolerance.

    Examples
    --------
    >>> check_encoding_value_fidelity([10, 20, 30], "bar",
    ...                               geometry=[1.0, 2.0, 3.0]).valid
    True
    >>> check_encoding_value_fidelity([42.0], "bar",
    ...                               printed_labels=["57"]).valid
    False
    """
    result = ValidationResult(valid=True)

    enc = (encoding or "").lower().strip()
    if enc in _BAR_ENCODINGS:
        enc = "bar"
    elif enc in _STACKED_ENCODINGS:
        enc = "bar"  # stacked bars share the linear-length law per segment

    known = {"bar", "pie", "donut", "scatter", "point", "line"}
    if enc not in known:
        result.add_warning(
            f"[check_encoding_value_fidelity/warn] unknown encoding "
            f"'{encoding}'; fidelity not checked."
        )
        return result

    keys, vals, n_nan = _coerce_keyed_floats(values)
    if n_nan:
        result.add_warning(
            f"[check_encoding_value_fidelity/warn] {n_nan} NaN/non-numeric "
            "values excluded from fidelity check."
        )
    if not vals:
        result.add_warning(
            "[check_encoding_value_fidelity/warn] no numeric values to check."
        )
        return result

    geom = _coerce_parallel_floats(geometry, keys) if geometry is not None else None
    if geometry is not None and geom is None:
        result.add_warning(
            "[check_encoding_value_fidelity/warn] geometry length/keys differ "
            "from values; geometry fidelity check incomplete."
        )

    labels = (
        _coerce_parallel_floats(printed_labels, keys)
        if printed_labels is not None
        else None
    )
    if printed_labels is not None and labels is None:
        result.add_warning(
            "[check_encoding_value_fidelity/warn] printed_labels length/keys "
            "differ from values; label fidelity check incomplete."
        )

    isclose = lambda a, b: math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)

    # ---- PIE / DONUT: angle proportionality ----------------------------------
    expected_angle: Optional[list[float]] = None
    if enc in ("pie", "donut"):
        if any(v < 0 for v in vals):
            result.add_error(
                "[check_encoding_value_fidelity/error] pie/donut cannot encode "
                "negative values."
            )
            return result
        total = sum(vals)
        if total <= 0:
            result.add_error(
                "[check_encoding_value_fidelity/error] non-positive total; "
                "wedge angles undefined."
            )
            return result
        expected_angle = [360.0 * v / total for v in vals]
        if geom is not None:
            for k, g, ea in zip(keys, geom, expected_angle):
                if g is None:
                    continue
                if not isclose(g, ea):
                    result.add_error(
                        f"[check_encoding_value_fidelity/error] wedge for '{k}' "
                        f"renders {g:.4g} deg but value implies {ea:.4g} deg "
                        "(geometry-vs-value mismatch, dimension 2.1)."
                    )

    # ---- BAR / COLUMN / STACKED: proportional-consistency of geometry --------
    elif enc == "bar":
        if axis_is_log:
            if any(v <= 0 for v in vals):
                result.add_error(
                    "[check_encoding_value_fidelity/error] non-positive value "
                    "on log axis; length undefined (log geometry desync)."
                )
                return result
            positive = [v for v in vals if v > 0]
            axis_min = min(positive)
            encoded = [math.log10(v) - math.log10(axis_min) for v in vals]
        else:
            encoded = [v - axis_baseline for v in vals]

        if geom is not None:
            ratios: list[float] = []
            for g, e in zip(geom, encoded):
                if g is None:
                    continue
                if abs(e) <= abs_tol:
                    continue  # zero-magnitude bar: ratio undefined, skip
                ratios.append(g / e)
            if not ratios:
                result.add_warning(
                    "[check_encoding_value_fidelity/warn] all encoded "
                    "magnitudes zero; proportionality not checked."
                )
            else:
                k0 = ratios[0]
                if k0 <= 0:
                    result.add_error(
                        "[check_encoding_value_fidelity/error] geometry scale is "
                        "non-positive (inverted axis?); label/height desync."
                    )
                elif not all(isclose(r, k0) for r in ratios):
                    result.add_error(
                        "[check_encoding_value_fidelity/error] geometry is not a "
                        "consistent linear transform of values; label/height "
                        "desync (dimension 2.1 categorical tell)."
                    )

    # ---- SCATTER / POINT / LINE: identity ------------------------------------
    else:  # scatter / point / line
        if geom is not None:
            for k, g, v in zip(keys, geom, vals):
                if g is None:
                    continue
                if not isclose(g, v):
                    result.add_error(
                        f"[check_encoding_value_fidelity/error] point '{k}' "
                        f"renders at {g:.4g} but value is {v:.4g} "
                        "(position-vs-value mismatch, dimension 2.1)."
                    )

    # ---- PRINTED-LABEL branch (all encodings) --------------------------------
    if labels is not None:
        total = sum(vals) if enc in ("pie", "donut") else None
        for i, (k, v) in enumerate(zip(keys, vals)):
            lab = labels[i]
            if lab is None:
                result.add_warning(
                    f"[check_encoding_value_fidelity/warn] printed label for "
                    f"'{k}' is missing/garbled; not reconciled."
                )
                continue
            if enc in ("pie", "donut") and total:
                pct = 100.0 * v / total
                ea = expected_angle[i] if expected_angle else None
                ok = (
                    isclose(lab, v)
                    or isclose(lab, pct)
                    or (ea is not None and isclose(lab, ea))
                )
            else:
                ok = isclose(lab, v)
            if not ok:
                result.add_error(
                    f"[check_encoding_value_fidelity/error] printed label "
                    f"{lab:.4g} does not match encoded value {v:.4g} for "
                    f"'{k}' (encoding-vs-printed-value mismatch, dimension 2.1 "
                    "categorical tell)."
                )

    return result


# Closure within this many percentage points is treated as exact (floating-point
# noise), and emits no message. Above it, a rounding gap warns up to abs_tol_pct,
# then errors. PROVISIONAL / UNCALIBRATED.
_CLOSURE_EXACT_EPS_PCT = 1e-6


def check_closure(
    parts: object,
    encoding: str,
    *,
    declared_total: Optional[float] = None,
    expect_percent: Optional[bool] = None,
    abs_tol_pct: float = 0.5,
    abs_tol_total: Optional[float] = None,
    rel_tol_total: float = 0.005,
) -> ValidationResult:
    """Check that parts-of-whole segments sum to the whole (AI-figure-slop
    dimension 2.2, conservation / closure).

    Two-band tolerance encodes the report's 1-vs-2 anchor: a rounding-level gap
    is advisory (``add_warning``), but a true conservation failure is a
    dominating categorical tell (``add_error`` / ``valid=False``). NAMED
    ``check_closure`` (spec C4), not ``check_parts_sum_to_whole``.

    Parameters
    ----------
    parts : array-like or dict[str, number]
        The parts-of-whole series (pie wedges, stacked-bar segments).
    encoding : str
        One of pie/donut/stacked_bar/stacked_column/100_stacked_bar
        (case-insensitive). Any other encoding -> no-op valid result.
    declared_total : float, optional
        The stated whole the segments must reconcile to. For percent pies the
        implied whole is 100. ``None`` + absolute-mode -> nothing to reconcile
        against (only internal impossibilities flagged).
    expect_percent : bool, optional
        Force percent interpretation. ``None`` auto-detects (all parts in
        [0, 100] and sum within 1.0 pp of 100, with no declared_total).
    abs_tol_pct : float
        Warn/error boundary in percentage points for the sum-to-100% test.
        Default **0.5 pp** is **PROVISIONAL / UNCALIBRATED**. A visible
        rounding gap (e.g. 33.3*3 = 99.9, gap 0.1 pp) <= abs_tol_pct -> advisory
        WARNING (anchor "1"); a gap > abs_tol_pct (e.g. 92%) -> ERROR
        (anchor "2"). Only an essentially exact closure (gap within
        floating-point noise, ``_CLOSURE_EXACT_EPS_PCT``) is silent. (This
        resolves an internal spec contradiction in favor of the documented test
        cases + the dimension-2.2 anchor; see the inline note at the band
        logic.)
    abs_tol_total, rel_tol_total : float
        Tolerance for reconciling against an absolute ``declared_total``
        (default 0.5% relative). **PROVISIONAL / UNCALIBRATED.**

    Returns
    -------
    ValidationResult
        ``valid=False`` on a true conservation failure; warning on a
        rounding-band gap or structural advisory.

    Examples
    --------
    >>> check_closure({"A": 25, "B": 25, "C": 50}, "pie").valid
    True
    >>> check_closure([20, 30, 42], "pie", expect_percent=True).valid  # 92%
    False
    """
    result = ValidationResult(valid=True)

    enc = (encoding or "").lower().strip()
    partsofwhole = (
        enc in _PIE_ENCODINGS
        or enc in _STACKED_ENCODINGS
        or enc in {"stacked_bar", "stacked_column", "100_stacked_bar"}
    )
    is_strict_whole = (
        enc in _PIE_ENCODINGS or enc in {"100_stacked_bar"} or ("100" in enc)
    )
    if not partsofwhole:
        return result

    keys, vals, n_nan = _coerce_keyed_floats(parts)
    if n_nan:
        result.add_warning(
            f"[check_closure/warn] {n_nan} NaN/non-numeric parts excluded."
        )
    if not vals:
        result.add_warning("[check_closure/warn] no numeric parts to reconcile.")
        return result

    # Negatives: strict wholes cannot contain a negative segment; diverging
    # stacked bars legitimately can (two-sided -> warning only).
    if any(v < 0 for v in vals):
        if is_strict_whole:
            result.add_error(
                "[check_closure/error] negative segment cannot be part of a "
                "whole (pie/donut/100%-stacked conservation failure)."
            )
            return result
        else:
            result.add_warning(
                "[check_closure/warn] negative segment present; assuming a "
                "diverging stacked bar (closure not enforced)."
            )

    s = sum(vals)

    # Determine reconciliation mode.
    if expect_percent is True:
        mode = "percent"
        whole: float = 100.0
    elif (
        expect_percent is None
        and declared_total is None
        and all(0.0 <= p <= 100.0 for p in vals)
        and abs(s - 100.0) <= 1.0
    ):
        mode = "percent"
        whole = 100.0
    elif declared_total is not None:
        if declared_total == 0:
            result.add_error(
                "[check_closure/error] declared total is zero; cannot reconcile."
            )
            return result
        mode = "absolute"
        whole = float(declared_total)
    else:
        # No whole to reconcile against; only internal checks ran.
        return result

    gap = abs(s - whole)

    if mode == "percent":
        # Two-band tolerance. NOTE (deviation from spec prose): the spec text
        # made the silent band `gap <= abs_tol_pct (0.5pp)`, but its own pytest
        # case (33.3*3 = 99.9, gap 0.1pp) expects a *warning*, matching the
        # dimension-2.2 anchor "1 = rounding-level gap is advisory". We resolve
        # that contradiction in favor of the test + anchor: only an essentially
        # exact closure (gap within floating-point noise) is silent; any visible
        # rounding gap up to abs_tol_pct warns; a true conservation failure
        # (gap > abs_tol_pct, e.g. 92%) errors. abs_tol_pct (default 0.5pp)
        # remains the configurable warn/error boundary and is
        # PROVISIONAL / UNCALIBRATED.
        if gap <= _CLOSURE_EXACT_EPS_PCT:
            return result  # closure is exact (rounding-clean), no message
        elif gap <= abs_tol_pct:
            result.add_warning(
                f"[check_closure/warn] parts sum to {s:.4g}% but whole is 100% "
                f"(gap {gap:.4g} pp); rounding-level gap (dimension 2.2 anchor "
                "'1', advisory -- slices were probably independently rounded)."
            )
        else:
            result.add_error(
                f"[check_closure/error] parts sum to {s:.4g}% but whole is 100% "
                f"(gap {gap:.4g} pp); fails to close (dimension 2.2 conservation "
                "categorical tell)."
            )
    else:  # absolute
        tol = max(abs_tol_total or 0.0, rel_tol_total * abs(whole))
        if gap <= tol:
            return result
        elif gap <= 2.0 * tol:
            result.add_warning(
                f"[check_closure/warn] parts sum to {s:.4g} but declared total "
                f"is {whole:.4g} (gap {gap:.4g}); rounding-level gap "
                "(dimension 2.2 anchor '1', advisory)."
            )
        else:
            result.add_error(
                f"[check_closure/error] parts sum to {s:.4g} but declared total "
                f"is {whole:.4g} (gap {gap:.4g}); fails to close (dimension 2.2 "
                "conservation categorical tell)."
            )

    return result


# Literal tool-default color cycles, lowercased hex. Flagged (advisory) when
# passed verbatim as a series palette. TWO-SIDED: we flag the *literal default*
# only; any bespoke / brand / CVD-safe palette never warns. We never instruct
# stripping color or minimizing ink (Bateman CHI2010: over-minimization is
# itself a regression-to-mean failure).
_MPL_TAB10 = (
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
)
# seaborn "deep" default (sns.color_palette() with no args, mpl>=2 cycle variant)
_SEABORN_DEEP = (
    "#4c72b0",
    "#dd8452",
    "#55a868",
    "#c44e52",
    "#8172b3",
    "#937860",
    "#da8bc3",
    "#8c8c8c",
    "#ccb974",
    "#64b5cd",
)
# Recommended replacements (names from plotting_params.PALETTES).
_DEFAULT_PALETTE_REPLACEMENTS = "Oligon, Okabe-Ito, Paul-Tol Categorical 8, or viridis"

# Named sentinels indicating an unmodified tool default was requested by name.
_DEFAULT_PALETTE_NAMES = {
    "tab10",
    "c0",
    "default",
    "matplotlib",
    "seaborn",
    "deep",
}


def _to_hex(entry: object) -> Optional[str]:
    """Normalize a color entry to lowercase '#rrggbb', or None if unparseable.

    Accepts '#RRGGBB' / '#RGB' hex strings and (r, g, b) float tuples in 0..1.
    """
    if isinstance(entry, str):
        s = entry.strip().lower()
        if re.fullmatch(r"#[0-9a-f]{6}", s):
            return s
        if re.fullmatch(r"#[0-9a-f]{3}", s):
            return "#" + "".join(c * 2 for c in s[1:])
        return None
    if isinstance(entry, (tuple, list, np.ndarray)) and len(entry) >= 3:
        try:
            r, g, b = (float(entry[0]), float(entry[1]), float(entry[2]))
        except (TypeError, ValueError):
            return None
        if all(0.0 <= c <= 1.0 for c in (r, g, b)):
            return "#{:02x}{:02x}{:02x}".format(
                round(r * 255), round(g * 255), round(b * 255)
            )
        return None
    return None


def check_default_palette(
    palette: object,
    *,
    match_threshold: float = 0.6,
    require_prefix_run: int = 3,
) -> ValidationResult:
    """Flag a literal tool-default color cycle (AI-figure-slop dimension 6.2,
    the template / default-distribution look).

    WARNING-ONLY, never blocks. The palette axis is the weak, two-sided
    aesthetic signal (guardrail 2): a literal default is *flagged* but it is not
    a lie. ``valid`` stays ``True`` always. The message never instructs
    stripping color or minimizing ink -- over-minimization is itself a
    regression-to-mean failure (Bateman CHI2010). Bespoke / brand / CVD-safe
    palettes (Oligon, Okabe-Ito, viridis, Paul Tol categorical 8) are verified
    to pass clean.

    Parameters
    ----------
    palette : list/tuple of hex strings or RGB float tuples, or a named sentinel
        The color sequence the caller is about to pass as the series palette.
        Named sentinels ({"tab10", "C0", "default", "matplotlib", "seaborn",
        "deep"}) indicate an unmodified default requested by name. ``None`` /
        empty -> no-op (caller did not pin colors).
    match_threshold : float
        Fraction of the supplied palette that must coincide (order-aligned)
        with a known default to flag. Default 0.6 is **PROVISIONAL /
        UNCALIBRATED** -- prevents flagging a bespoke palette that merely reuses
        one tab10 blue.
    require_prefix_run : int
        Minimum aligned leading run matching a default that also triggers a
        flag even if the tail diverges (the recognizable tab10 *opening* is the
        documented fingerprint). Default 3 is **PROVISIONAL / UNCALIBRATED** --
        a lone C0-blue (run of 1) does not false-flag.

    Returns
    -------
    ValidationResult
        ``valid=True`` always; ``warnings`` populated on a default match.

    Examples
    --------
    >>> check_default_palette(["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]).warnings
    [...]
    >>> check_default_palette(["#e69f00", "#56b4e9", "#009e73"]).warnings
    []
    """
    result = ValidationResult(valid=True)

    if palette is None:
        return result

    # Named-default-by-name sentinel.
    if isinstance(palette, str):
        if palette.strip().lower() in _DEFAULT_PALETTE_NAMES:
            result.add_warning(
                f"[check_default_palette/warn] palette '{palette}' is a named "
                "tool default (template/default-distribution look, dimension "
                "6.2). TWO-SIDED: a default is not an error; if a default look "
                f"is intended, ignore. Otherwise prefer a bespoke/brand CVD-safe "
                f"palette: {_DEFAULT_PALETTE_REPLACEMENTS}. "
                "See plotting_params.recommend_palette()."
            )
        return result

    if not isinstance(palette, (list, tuple, np.ndarray)) or len(palette) == 0:
        return result

    # Normalize to a list of lowercase hex strings (skip unparseable).
    hexes: list[str] = []
    for entry in palette:
        h = _to_hex(entry)
        if h is not None:
            hexes.append(h)
    if not hexes:
        return result

    for name, default in (
        ("matplotlib tab10", _MPL_TAB10),
        ("seaborn deep", _SEABORN_DEEP),
    ):
        span = min(len(hexes), len(default))
        aligned_matches = sum(1 for i in range(span) if hexes[i] == default[i])
        frac = aligned_matches / len(hexes)

        leading_run = 0
        for i in range(span):
            if hexes[i] == default[i]:
                leading_run += 1
            else:
                break

        # A genuine fingerprint needs enough aligned hits that it cannot be a
        # coincidence: gate the fraction branch behind require_prefix_run aligned
        # matches so a lone C0-blue (1 match, frac=100%) never false-flags
        # (spec edge case), while a full tab10 opening still trips it.
        frac_hit = frac >= match_threshold and aligned_matches >= require_prefix_run
        run_hit = leading_run >= require_prefix_run
        if frac_hit or run_hit:
            result.add_warning(
                f"[check_default_palette/warn] palette matches the {name} tool "
                f"default (frac={frac:.0%}, leading run={leading_run}). This is "
                "a generative-slop fingerprint (template/default-distribution "
                "look, dimension 6.2). TWO-SIDED: a default is not an error; if "
                "a default look is intended, ignore. Otherwise prefer a "
                f"bespoke/brand CVD-safe palette: {_DEFAULT_PALETTE_REPLACEMENTS}. "
                "See plotting_params.recommend_palette()."
            )
            break  # one match is enough; don't double-warn

    return result
