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
        print_validation,
    )
"""

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
        result.add_warning(f"Gene column '{gene_col}' not found; gene labeling disabled")

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
        result.add_warning(
            f"Expected {expected_rows} rows, got {n_rows}"
        )
    if expected_cols is not None and n_cols != expected_cols:
        result.add_warning(
            f"Expected {expected_cols} columns, got {n_cols}"
        )

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
#
# Both functions are pure / side-effect-free; they return ValidationResult and
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
