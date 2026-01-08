"""
Pytest configuration and shared fixtures for statistical analysis tests.
"""

import sys
from pathlib import Path

import pytest

# Add scripts directory to path for imports
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))


@pytest.fixture
def sample_pvalues():
    """Sample p-values for MTC testing."""
    return [0.001, 0.005, 0.01, 0.02, 0.03, 0.05, 0.10, 0.20, 0.50, 0.80]


@pytest.fixture
def small_pvalues():
    """All significant p-values."""
    return [0.001, 0.002, 0.003, 0.004, 0.005]


@pytest.fixture
def large_pvalues():
    """All non-significant p-values."""
    return [0.10, 0.20, 0.30, 0.50, 0.80]


@pytest.fixture
def test_selection_continuous_normal():
    """Valid input for continuous normal test selection."""
    return {
        "outcome_type": "continuous",
        "distribution": "normal",
        "design": "independent",
        "n_groups": 2,
    }


@pytest.fixture
def test_selection_continuous_nonnormal():
    """Valid input for continuous non-normal test selection."""
    return {
        "outcome_type": "continuous",
        "distribution": "non_normal",
        "design": "independent",
        "n_groups": 2,
    }


@pytest.fixture
def test_selection_categorical():
    """Valid input for categorical test selection."""
    return {
        "outcome_type": "categorical",
        "design": "independent",
        "n_groups": 2,
    }


@pytest.fixture
def power_analysis_input():
    """Valid input for power analysis."""
    return {
        "test_type": "t_test",
        "effect_size": 0.5,
        "power": 0.8,
        "alpha": 0.05,
    }
