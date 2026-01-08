"""
Input validation utilities for statistical analysis.

This module provides validation functions for structured inputs to the
statistical analysis utilities, ensuring data quality before processing.

Example usage:
    >>> from scripts.validators import validate_test_selection_input
    >>> errors = validate_test_selection_input({
    ...     "outcome_type": "continuous",
    ...     "distribution": "normal",
    ...     "design": "independent",
    ...     "n_groups": 2
    ... })
    >>> print(errors)
    []
"""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ValidationResult:
    """Result of input validation."""

    valid: bool
    errors: list[str]
    warnings: list[str]
    normalized_input: dict[str, Any]


# =============================================================================
# Valid Values for Enums
# =============================================================================

VALID_OUTCOME_TYPES = {
    "continuous",
    "categorical",
    "ordinal",
    "count",
    "time_to_event",
    "proportion",
}

VALID_DISTRIBUTIONS = {"normal", "non_normal", "unknown"}

VALID_DESIGNS = {"independent", "paired", "repeated_measures"}

VALID_MTC_METHODS = {
    "bh_fdr",
    "bonferroni",
    "holm",
    "hochberg",
    "by_fdr",
    "sidak",
    "holm_sidak",
    "fdr_tsbh",
    "fdr_tsbky",
}

VALID_POWER_TEST_TYPES = {
    "t_test",
    "paired_t_test",
    "one_sample_t",
    "anova",
    "correlation",
    "chi_square",
    "proportion",
}

VALID_EFFECT_METRICS = {
    "cohens_d",
    "hedges_g",
    "pearsons_r",
    "spearmans_rho",
    "eta_squared",
    "partial_eta_squared",
    "omega_squared",
    "r_squared",
    "odds_ratio",
    "risk_ratio",
    "hazard_ratio",
    "cramers_v",
    "phi",
    "log2_fold_change",
    "cohens_h",
    "number_needed_to_treat",
}


# =============================================================================
# Test Selection Validation
# =============================================================================


def validate_test_selection_input(
    input_data: dict[str, Any],
) -> ValidationResult:
    """
    Validate input for test selection.

    Parameters
    ----------
    input_data : dict
        Dictionary with keys:
        - outcome_type: str (required)
        - distribution: str (required for continuous/ordinal)
        - design: str (required)
        - n_groups: int (required)
        - variance_equal: bool (optional)
        - expected_counts_sufficient: bool (optional, for categorical)

    Returns
    -------
    ValidationResult
        Validation result with errors, warnings, and normalized input

    Examples
    --------
    >>> result = validate_test_selection_input({
    ...     "outcome_type": "continuous",
    ...     "distribution": "normal",
    ...     "design": "independent",
    ...     "n_groups": 2
    ... })
    >>> result.valid
    True
    """
    errors = []
    warnings = []
    normalized = {}

    # Required fields
    required_fields = ["outcome_type", "design", "n_groups"]
    for field in required_fields:
        if field not in input_data:
            errors.append(f"Missing required field: '{field}'")

    if errors:
        return ValidationResult(
            valid=False, errors=errors, warnings=warnings, normalized_input={}
        )

    # Validate outcome_type
    outcome_type = str(input_data["outcome_type"]).lower().strip()
    if outcome_type not in VALID_OUTCOME_TYPES:
        errors.append(
            f"Invalid outcome_type: '{outcome_type}'. "
            f"Valid values: {sorted(VALID_OUTCOME_TYPES)}"
        )
    normalized["outcome_type"] = outcome_type

    # Validate distribution (required for continuous/ordinal)
    if outcome_type in ("continuous", "ordinal"):
        if "distribution" not in input_data:
            errors.append(
                f"'distribution' is required for outcome_type='{outcome_type}'"
            )
        else:
            distribution = str(input_data["distribution"]).lower().strip()
            if distribution not in VALID_DISTRIBUTIONS:
                errors.append(
                    f"Invalid distribution: '{distribution}'. "
                    f"Valid values: {sorted(VALID_DISTRIBUTIONS)}"
                )
            normalized["distribution"] = distribution
    elif "distribution" in input_data:
        distribution = str(input_data["distribution"]).lower().strip()
        normalized["distribution"] = distribution
        if outcome_type == "categorical":
            warnings.append("distribution is not used for categorical outcomes")

    # Validate design
    design = str(input_data["design"]).lower().strip()
    if design not in VALID_DESIGNS:
        errors.append(
            f"Invalid design: '{design}'. Valid values: {sorted(VALID_DESIGNS)}"
        )
    normalized["design"] = design

    # Validate n_groups
    try:
        n_groups = int(input_data["n_groups"])
        if n_groups < 1:
            errors.append(f"n_groups must be >= 1, got {n_groups}")
        elif n_groups == 1 and design != "independent":
            warnings.append(f"n_groups=1 with design='{design}' may not be meaningful")
        normalized["n_groups"] = n_groups
    except (ValueError, TypeError):
        errors.append(f"n_groups must be an integer, got '{input_data['n_groups']}'")

    # Optional: variance_equal
    if "variance_equal" in input_data:
        val = input_data["variance_equal"]
        if isinstance(val, bool):
            normalized["variance_equal"] = val
        elif isinstance(val, str):
            normalized["variance_equal"] = val.lower() in ("true", "yes", "1")
        elif val is None:
            normalized["variance_equal"] = None
        else:
            warnings.append(f"variance_equal should be boolean, got '{val}'")

    # Optional: expected_counts_sufficient
    if "expected_counts_sufficient" in input_data:
        val = input_data["expected_counts_sufficient"]
        if isinstance(val, bool):
            normalized["expected_counts_sufficient"] = val
        elif isinstance(val, str):
            normalized["expected_counts_sufficient"] = val.lower() in (
                "true",
                "yes",
                "1",
            )
        else:
            warnings.append(
                f"expected_counts_sufficient should be boolean, got '{val}'"
            )

    # Cross-validation
    if not errors:
        # Check for common issues
        if (
            normalized.get("design") == "repeated_measures"
            and normalized.get("n_groups", 0) == 2
        ):
            warnings.append(
                "repeated_measures with 2 groups is typically analyzed as paired design"
            )

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        normalized_input=normalized,
    )


# =============================================================================
# Multiple Testing Correction Validation
# =============================================================================


def validate_mtc_input(
    input_data: dict[str, Any],
) -> ValidationResult:
    """
    Validate input for multiple testing correction.

    Parameters
    ----------
    input_data : dict
        Dictionary with keys:
        - pvalues: list of float (required)
        - method: str (optional, default "bh_fdr")
        - alpha: float (optional, default 0.05)

    Returns
    -------
    ValidationResult
        Validation result with errors, warnings, and normalized input
    """
    errors = []
    warnings = []
    normalized = {}

    # Required: pvalues
    if "pvalues" not in input_data:
        errors.append("Missing required field: 'pvalues'")
        return ValidationResult(
            valid=False, errors=errors, warnings=warnings, normalized_input={}
        )

    # Validate pvalues
    pvalues = input_data["pvalues"]
    if not isinstance(pvalues, (list, tuple)):
        errors.append("pvalues must be a list")
    elif len(pvalues) == 0:
        errors.append("pvalues cannot be empty")
    else:
        validated_pvalues = []
        for i, p in enumerate(pvalues):
            try:
                p_float = float(p)
                if p_float < 0 or p_float > 1:
                    errors.append(f"pvalues[{i}] = {p_float} is not in range [0, 1]")
                validated_pvalues.append(p_float)
            except (ValueError, TypeError):
                errors.append(f"pvalues[{i}] = '{p}' is not a valid number")

        if not errors:
            normalized["pvalues"] = validated_pvalues

            # Warnings for suspicious p-value patterns
            if all(p == validated_pvalues[0] for p in validated_pvalues):
                warnings.append("All p-values are identical - verify test results")

            n_significant = sum(1 for p in validated_pvalues if p < 0.05)
            if n_significant == 0 and len(validated_pvalues) > 10:
                warnings.append("No p-values < 0.05 before correction")

    # Validate method
    method = input_data.get("method", "bh_fdr")
    method = str(method).lower().strip()
    if method not in VALID_MTC_METHODS:
        errors.append(
            f"Invalid method: '{method}'. Valid values: {sorted(VALID_MTC_METHODS)}"
        )
    normalized["method"] = method

    # Validate alpha
    alpha = input_data.get("alpha", 0.05)
    try:
        alpha = float(alpha)
        if alpha <= 0 or alpha >= 1:
            errors.append(f"alpha must be in (0, 1), got {alpha}")
        normalized["alpha"] = alpha
    except (ValueError, TypeError):
        errors.append(f"alpha must be a number, got '{input_data.get('alpha')}'")

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        normalized_input=normalized,
    )


# =============================================================================
# Power Analysis Validation
# =============================================================================


def validate_power_analysis_input(
    input_data: dict[str, Any],
) -> ValidationResult:
    """
    Validate input for power analysis.

    Parameters
    ----------
    input_data : dict
        Dictionary with keys:
        - test_type: str (required)
        - effect_size: float (optional, one of three must be None)
        - power: float (optional, one of three must be None)
        - n_per_group: int (optional, one of three must be None)
        - alpha: float (optional, default 0.05)
        - n_groups: int (optional, for ANOVA)
        - df: int (optional, for chi_square)

    Returns
    -------
    ValidationResult
        Validation result with errors, warnings, and normalized input
    """
    errors = []
    warnings = []
    normalized = {}

    # Required: test_type
    if "test_type" not in input_data:
        errors.append("Missing required field: 'test_type'")
        return ValidationResult(
            valid=False, errors=errors, warnings=warnings, normalized_input={}
        )

    # Validate test_type
    test_type = str(input_data["test_type"]).lower().strip()
    if test_type not in VALID_POWER_TEST_TYPES:
        errors.append(
            f"Invalid test_type: '{test_type}'. "
            f"Valid values: {sorted(VALID_POWER_TEST_TYPES)}"
        )
    normalized["test_type"] = test_type

    # Validate effect_size, power, n_per_group (exactly one must be None)
    effect_size = input_data.get("effect_size")
    power = input_data.get("power")
    n_per_group = input_data.get("n_per_group")

    none_count = sum(x is None for x in [effect_size, power, n_per_group])

    if none_count != 1:
        errors.append(
            "Exactly one of (effect_size, power, n_per_group) must be None "
            f"to be calculated. Got {none_count} None values."
        )

    # Validate effect_size
    if effect_size is not None:
        try:
            effect_size = float(effect_size)
            if effect_size <= 0:
                errors.append(f"effect_size must be positive, got {effect_size}")
            normalized["effect_size"] = effect_size
        except (ValueError, TypeError):
            errors.append(f"effect_size must be a number, got '{effect_size}'")
    else:
        normalized["effect_size"] = None

    # Validate power
    if power is not None:
        try:
            power = float(power)
            if power <= 0 or power >= 1:
                errors.append(f"power must be in (0, 1), got {power}")
            normalized["power"] = power

            if power < 0.8:
                warnings.append(f"Power {power} is below recommended 0.8")
        except (ValueError, TypeError):
            errors.append(f"power must be a number, got '{power}'")
    else:
        normalized["power"] = None

    # Validate n_per_group
    if n_per_group is not None:
        try:
            n_per_group = int(n_per_group)
            if n_per_group < 2:
                errors.append(f"n_per_group must be >= 2, got {n_per_group}")
            normalized["n_per_group"] = n_per_group

            if n_per_group < 10:
                warnings.append(f"n_per_group = {n_per_group} is very small")
        except (ValueError, TypeError):
            errors.append(f"n_per_group must be an integer, got '{n_per_group}'")
    else:
        normalized["n_per_group"] = None

    # Validate alpha
    alpha = input_data.get("alpha", 0.05)
    try:
        alpha = float(alpha)
        if alpha <= 0 or alpha >= 1:
            errors.append(f"alpha must be in (0, 1), got {alpha}")
        normalized["alpha"] = alpha
    except (ValueError, TypeError):
        errors.append(f"alpha must be a number, got '{input_data.get('alpha')}'")

    # Validate n_groups (for ANOVA)
    if test_type == "anova":
        n_groups = input_data.get("n_groups", 2)
        try:
            n_groups = int(n_groups)
            if n_groups < 2:
                errors.append(f"n_groups must be >= 2 for ANOVA, got {n_groups}")
            normalized["n_groups"] = n_groups
        except (ValueError, TypeError):
            errors.append(f"n_groups must be an integer, got '{n_groups}'")

    # Validate df (for chi_square)
    if test_type == "chi_square":
        if "df" not in input_data:
            errors.append("df (degrees of freedom) is required for chi_square test")
        else:
            try:
                df = int(input_data["df"])
                if df < 1:
                    errors.append(f"df must be >= 1, got {df}")
                normalized["df"] = df
            except (ValueError, TypeError):
                errors.append(f"df must be an integer, got '{input_data['df']}'")

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        normalized_input=normalized,
    )


# =============================================================================
# Effect Size Interpretation Validation
# =============================================================================


def validate_effect_size_input(
    input_data: dict[str, Any],
) -> ValidationResult:
    """
    Validate input for effect size interpretation.

    Parameters
    ----------
    input_data : dict
        Dictionary with keys:
        - value: float (required)
        - metric: str (required)

    Returns
    -------
    ValidationResult
        Validation result with errors, warnings, and normalized input
    """
    errors = []
    warnings = []
    normalized = {}

    # Required: value
    if "value" not in input_data:
        errors.append("Missing required field: 'value'")
    else:
        try:
            value = float(input_data["value"])
            normalized["value"] = value

            # Warnings for extreme values
            if abs(value) > 10:
                warnings.append(
                    f"Effect size value {value} is unusually large - verify calculation"
                )
        except (ValueError, TypeError):
            errors.append(f"value must be a number, got '{input_data['value']}'")

    # Required: metric
    if "metric" not in input_data:
        errors.append("Missing required field: 'metric'")
    else:
        metric = str(input_data["metric"]).lower().strip()
        if metric not in VALID_EFFECT_METRICS:
            errors.append(
                f"Invalid metric: '{metric}'. "
                f"Valid values: {sorted(VALID_EFFECT_METRICS)}"
            )
        normalized["metric"] = metric

        # Metric-specific validation
        if not errors and "value" in normalized:
            value = normalized["value"]

            if metric in ("pearsons_r", "spearmans_rho"):
                if abs(value) > 1:
                    errors.append(f"Correlation value must be in [-1, 1], got {value}")

            if metric in (
                "eta_squared",
                "partial_eta_squared",
                "omega_squared",
                "r_squared",
            ):
                if value < 0:
                    errors.append(f"{metric} cannot be negative, got {value}")
                if value > 1:
                    errors.append(f"{metric} cannot exceed 1, got {value}")

            if metric in ("odds_ratio", "risk_ratio", "hazard_ratio"):
                if value <= 0:
                    errors.append(f"{metric} must be positive, got {value}")

            if metric == "cramers_v":
                if value < 0 or value > 1:
                    errors.append(f"Cramer's V must be in [0, 1], got {value}")

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        normalized_input=normalized,
    )


# =============================================================================
# Utility Functions
# =============================================================================


def validate_numeric_range(
    value: Any,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
    exclusive_min: bool = False,
    exclusive_max: bool = False,
    param_name: str = "value",
) -> tuple[Optional[float], Optional[str]]:
    """
    Validate that a value is numeric and within range.

    Parameters
    ----------
    value : Any
        Value to validate
    min_val : float, optional
        Minimum allowed value
    max_val : float, optional
        Maximum allowed value
    exclusive_min : bool
        If True, value must be > min_val (not >=)
    exclusive_max : bool
        If True, value must be < max_val (not <=)
    param_name : str
        Name for error messages

    Returns
    -------
    tuple of (float or None, str or None)
        (validated_value, error_message)
    """
    try:
        num_value = float(value)
    except (ValueError, TypeError):
        return None, f"{param_name} must be a number, got '{value}'"

    if min_val is not None:
        if exclusive_min and num_value <= min_val:
            return None, f"{param_name} must be > {min_val}, got {num_value}"
        elif not exclusive_min and num_value < min_val:
            return None, f"{param_name} must be >= {min_val}, got {num_value}"

    if max_val is not None:
        if exclusive_max and num_value >= max_val:
            return None, f"{param_name} must be < {max_val}, got {num_value}"
        elif not exclusive_max and num_value > max_val:
            return None, f"{param_name} must be <= {max_val}, got {num_value}"

    return num_value, None


def validate_enum(
    value: Any,
    valid_values: set[str],
    param_name: str = "value",
) -> tuple[Optional[str], Optional[str]]:
    """
    Validate that a value is one of the allowed enum values.

    Parameters
    ----------
    value : Any
        Value to validate
    valid_values : set of str
        Allowed values
    param_name : str
        Name for error messages

    Returns
    -------
    tuple of (str or None, str or None)
        (normalized_value, error_message)
    """
    str_value = str(value).lower().strip()

    if str_value not in valid_values:
        return None, (
            f"Invalid {param_name}: '{value}'. Valid values: {sorted(valid_values)}"
        )

    return str_value, None


if __name__ == "__main__":
    # Example usage
    print("=== Validation Examples ===\n")

    # Test selection validation
    result = validate_test_selection_input(
        {
            "outcome_type": "continuous",
            "distribution": "normal",
            "design": "independent",
            "n_groups": 2,
        }
    )
    print(f"Test selection: valid={result.valid}, errors={result.errors}")

    # Invalid input
    result = validate_test_selection_input(
        {
            "outcome_type": "invalid",
            "design": "independent",
        }
    )
    print(f"Invalid input: valid={result.valid}, errors={result.errors}")

    # MTC validation
    result = validate_mtc_input(
        {
            "pvalues": [0.001, 0.01, 0.05, 0.1],
            "method": "bh_fdr",
        }
    )
    print(f"MTC: valid={result.valid}, warnings={result.warnings}")

    # Power analysis validation
    result = validate_power_analysis_input(
        {
            "test_type": "t_test",
            "effect_size": 0.5,
            "power": 0.8,
        }
    )
    print(f"Power: valid={result.valid}, errors={result.errors}")
