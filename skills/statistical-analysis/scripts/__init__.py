"""
Statistical Analysis Deterministic Utilities.

This package provides deterministic implementations of statistical analysis
functions, eliminating LLM interpretation variance from core analytical tasks.

Modules:
    test_selector: Deterministic statistical test selection from data characteristics
    mtc_corrector: Multiple testing correction wrapper
    effect_interpreter: Effect size interpretation via lookup tables
    power_calculator: Power analysis wrapper
    validators: Input validation utilities
"""

from .test_selector import (
    select_test,
    select_correlation_test,
    OutcomeType,
    Distribution,
    Design,
    TestRecommendation,
)
from .mtc_corrector import correct_pvalues, MTCResult
from .effect_interpreter import interpret_effect_size, EffectInterpretation
from .power_calculator import power_analysis, PowerResult
from .validators import (
    validate_test_selection_input,
    validate_power_analysis_input,
    validate_mtc_input,
)

__all__ = [
    # Test selection
    "select_test",
    "select_correlation_test",
    "OutcomeType",
    "Distribution",
    "Design",
    "TestRecommendation",
    # Multiple testing correction
    "correct_pvalues",
    "MTCResult",
    # Effect size interpretation
    "interpret_effect_size",
    "EffectInterpretation",
    # Power analysis
    "power_analysis",
    "PowerResult",
    # Validators
    "validate_test_selection_input",
    "validate_power_analysis_input",
    "validate_mtc_input",
]
