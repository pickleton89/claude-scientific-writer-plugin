"""Tests for data validation utilities."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from validate_data import (  # noqa: E402
    ValidationResult,
    validate_heatmap_data,
    validate_survival_data,
    validate_volcano_data,
)


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_valid_result_is_truthy(self):
        """Valid result should be truthy in boolean context."""
        result = ValidationResult(valid=True)
        assert result
        assert bool(result) is True

    def test_invalid_result_is_falsy(self):
        """Invalid result should be falsy in boolean context."""
        result = ValidationResult(valid=False)
        assert not result
        assert bool(result) is False

    def test_add_error(self):
        """add_error should add message and set valid to False."""
        result = ValidationResult(valid=True)
        result.add_error("test error")
        assert not result.valid
        assert "test error" in result.errors

    def test_add_warning(self):
        """add_warning should add message but keep valid status."""
        result = ValidationResult(valid=True)
        result.add_warning("test warning")
        assert result.valid
        assert "test warning" in result.warnings


class TestVolcanoValidation:
    """Tests for volcano plot data validation."""

    @pytest.fixture
    def valid_df(self):
        """Create a valid volcano plot DataFrame."""
        return pd.DataFrame(
            {
                "gene_symbol": ["A", "B", "C", "D", "E"],
                "log2FoldChange": [1.5, -2.0, 0.1, 3.0, -0.5],
                "padj": [0.001, 0.01, 0.5, 0.0001, 0.8],
            }
        )

    def test_valid_data_passes(self, valid_df):
        """Valid data should pass validation."""
        result = validate_volcano_data(valid_df)
        assert result.valid
        assert len(result.errors) == 0

    def test_missing_log2fc_column_fails(self, valid_df):
        """Missing log2FC column should fail."""
        result = validate_volcano_data(valid_df, log2fc_col="missing")
        assert not result.valid
        assert any("not found" in e for e in result.errors)

    def test_missing_pvalue_column_fails(self, valid_df):
        """Missing p-value column should fail."""
        result = validate_volcano_data(valid_df, pvalue_col="missing")
        assert not result.valid
        assert any("not found" in e for e in result.errors)

    def test_invalid_pvalue_range_fails(self, valid_df):
        """P-values outside [0,1] should fail."""
        valid_df["padj"] = [0.01, 1.5, 0.5, 0.001, 0.1]  # 1.5 is invalid
        result = validate_volcano_data(valid_df)
        assert not result.valid
        assert any("must be in [0, 1]" in e for e in result.errors)

    def test_negative_pvalue_fails(self, valid_df):
        """Negative p-values should fail."""
        valid_df["padj"] = [0.01, -0.5, 0.5, 0.001, 0.1]
        result = validate_volcano_data(valid_df)
        assert not result.valid

    def test_nan_pvalue_warning(self, valid_df):
        """NaN p-values should generate warning."""
        valid_df.loc[0, "padj"] = np.nan
        result = validate_volcano_data(valid_df)
        assert result.valid  # Still valid, just warning
        assert any("NaN" in w for w in result.warnings)

    def test_nan_log2fc_warning(self, valid_df):
        """NaN log2FC values should generate warning."""
        valid_df.loc[0, "log2FoldChange"] = np.nan
        result = validate_volcano_data(valid_df)
        assert result.valid
        assert any("NaN" in w for w in result.warnings)

    def test_missing_gene_column_warning(self, valid_df):
        """Missing gene column should generate warning."""
        result = validate_volcano_data(valid_df, gene_col="missing_col")
        assert result.valid
        assert any("gene" in w.lower() for w in result.warnings)

    def test_unadjusted_pvalue_warning(self, valid_df):
        """Using unadjusted p-values should generate warning."""
        result = validate_volcano_data(valid_df, pvalue_col="padj")
        # padj contains 'adj', so no warning
        valid_df["pvalue"] = valid_df["padj"]
        result = validate_volcano_data(valid_df, pvalue_col="pvalue")
        assert any("unadjusted" in w.lower() for w in result.warnings)

    def test_zero_pvalue_warning(self, valid_df):
        """Zero p-values should generate warning."""
        valid_df.loc[0, "padj"] = 0.0
        result = validate_volcano_data(valid_df)
        assert result.valid
        assert any("p-value = 0" in w for w in result.warnings)

    def test_custom_column_names(self):
        """Custom column names should work."""
        df = pd.DataFrame(
            {
                "gene": ["A", "B"],
                "FC": [1.0, -1.0],
                "p": [0.01, 0.05],
            }
        )
        result = validate_volcano_data(
            df, log2fc_col="FC", pvalue_col="p", gene_col="gene"
        )
        assert result.valid


class TestHeatmapValidation:
    """Tests for heatmap data validation."""

    @pytest.fixture
    def valid_matrix(self):
        """Create a valid heatmap matrix."""
        np.random.seed(42)
        return pd.DataFrame(
            np.random.randn(100, 10),
            index=[f"Gene_{i}" for i in range(100)],
            columns=[f"Sample_{i}" for i in range(10)],
        )

    def test_valid_data_passes(self, valid_matrix):
        """Valid data should pass validation."""
        result = validate_heatmap_data(valid_matrix)
        assert result.valid
        assert len(result.errors) == 0

    def test_non_numeric_column_fails(self, valid_matrix):
        """Non-numeric columns should fail."""
        valid_matrix["text_col"] = "text"
        result = validate_heatmap_data(valid_matrix)
        assert not result.valid
        assert any("Non-numeric" in e for e in result.errors)

    def test_infinite_values_fail(self, valid_matrix):
        """Infinite values should fail."""
        valid_matrix.iloc[0, 0] = np.inf
        result = validate_heatmap_data(valid_matrix)
        assert not result.valid
        assert any("Infinite" in e for e in result.errors)

    def test_large_matrix_warning(self):
        """Large matrix should generate warning."""
        large = pd.DataFrame(np.random.randn(600, 10))
        result = validate_heatmap_data(large)
        assert result.valid  # Still valid, just warning
        assert any("too many" in w for w in result.warnings)

    def test_wide_matrix_warning(self):
        """Wide matrix should generate warning."""
        wide = pd.DataFrame(np.random.randn(50, 150))
        result = validate_heatmap_data(wide)
        assert result.valid
        assert any("too many" in w for w in result.warnings)

    def test_too_few_rows_fails(self):
        """Matrix with < 2 rows should fail."""
        small = pd.DataFrame(np.random.randn(1, 5))
        result = validate_heatmap_data(small)
        assert not result.valid
        assert any("at least 2 rows" in e for e in result.errors)

    def test_too_few_cols_fails(self):
        """Matrix with < 2 columns should fail."""
        small = pd.DataFrame(np.random.randn(5, 1))
        result = validate_heatmap_data(small)
        assert not result.valid
        assert any("at least 2 columns" in e for e in result.errors)

    def test_nan_values_warning(self, valid_matrix):
        """NaN values should generate warning."""
        valid_matrix.iloc[0, 0] = np.nan
        result = validate_heatmap_data(valid_matrix)
        assert result.valid
        assert any("NaN" in w for w in result.warnings)

    def test_high_nan_percentage_fails(self, valid_matrix):
        """High percentage of NaN values should fail."""
        valid_matrix.iloc[:20, :] = np.nan  # 20% NaN
        result = validate_heatmap_data(valid_matrix)
        assert not result.valid

    def test_zero_variance_warning(self):
        """Rows with zero variance should generate warning."""
        # Create a matrix where some rows have zero variance (constant values)
        df = pd.DataFrame(
            {
                "S1": [1.0, 2.0, 3.0, 5.0, 5.0],
                "S2": [1.0, 3.0, 4.0, 5.0, 5.0],  # Rows 3 and 4 have same values
                "S3": [1.0, 4.0, 5.0, 5.0, 5.0],
            }
        )
        # Row 0 has all 1.0 values - zero variance
        result = validate_heatmap_data(df)
        assert result.valid
        # Row 0 has zero variance across samples
        assert any("zero variance" in w for w in result.warnings)

    def test_expected_dimensions_warning(self, valid_matrix):
        """Unexpected dimensions should generate warning."""
        result = validate_heatmap_data(valid_matrix, expected_rows=50)
        assert result.valid
        assert any("Expected 50 rows" in w for w in result.warnings)


class TestSurvivalValidation:
    """Tests for survival data validation."""

    @pytest.fixture
    def valid_df(self):
        """Create valid survival data."""
        return pd.DataFrame(
            {
                "time": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
                "event": [1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
                "group": ["A", "A", "A", "A", "A", "B", "B", "B", "B", "B"],
            }
        )

    def test_valid_data_passes(self, valid_df):
        """Valid survival data should pass."""
        result = validate_survival_data(valid_df, group_col="group")
        assert result.valid

    def test_missing_time_column_fails(self, valid_df):
        """Missing time column should fail."""
        result = validate_survival_data(valid_df, time_col="missing")
        assert not result.valid
        assert any("Time column" in e for e in result.errors)

    def test_missing_event_column_fails(self, valid_df):
        """Missing event column should fail."""
        result = validate_survival_data(valid_df, event_col="missing")
        assert not result.valid
        assert any("Event column" in e for e in result.errors)

    def test_negative_time_fails(self, valid_df):
        """Negative time values should fail."""
        valid_df.loc[0, "time"] = -5
        result = validate_survival_data(valid_df)
        assert not result.valid
        assert any("non-negative" in e for e in result.errors)

    def test_non_binary_event_fails(self, valid_df):
        """Non-binary event values should fail."""
        valid_df["event"] = [1, 2, 3, 0, 1, 0, 1, 0, 1, 0]
        result = validate_survival_data(valid_df)
        assert not result.valid
        assert any("binary" in e for e in result.errors)

    def test_missing_group_column_warning(self, valid_df):
        """Missing group column should generate warning."""
        result = validate_survival_data(valid_df, group_col="nonexistent")
        assert result.valid
        assert any("not found" in w for w in result.warnings)

    def test_many_groups_warning(self):
        """Many groups should generate warning."""
        # Need >10 groups to trigger warning
        df = pd.DataFrame({
            "time": list(range(1, 13)),
            "event": [1, 0] * 6,
            "group": list(range(12)),  # 12 unique groups
        })
        result = validate_survival_data(df, group_col="group")
        assert result.valid
        assert any("groups" in w for w in result.warnings)

    def test_small_sample_warning(self):
        """Small sample size should generate warning."""
        df = pd.DataFrame({"time": [1, 2, 3], "event": [1, 0, 1]})
        result = validate_survival_data(df)
        assert result.valid
        assert any("samples" in w.lower() for w in result.warnings)

    def test_low_event_rate_warning(self):
        """Low event rate should generate warning."""
        # Need <10% event rate (e.g., 5%)
        df = pd.DataFrame({
            "time": list(range(1, 21)),
            "event": [1] + [0] * 19,  # 5% event rate
        })
        result = validate_survival_data(df)
        assert result.valid
        assert any("event rate" in w.lower() for w in result.warnings)

    def test_high_event_rate_warning(self):
        """High event rate should generate warning."""
        # Need >90% event rate (e.g., 95%)
        df = pd.DataFrame({
            "time": list(range(1, 21)),
            "event": [1] * 19 + [0],  # 95% event rate
        })
        result = validate_survival_data(df)
        assert result.valid
        assert any("event rate" in w.lower() for w in result.warnings)

    def test_boolean_events_accepted(self, valid_df):
        """Boolean event values should be accepted."""
        valid_df["event"] = [True, False, True, False, True, False, True, False, True, False]
        result = validate_survival_data(valid_df)
        assert result.valid


class TestIntegration:
    """Integration tests for combined validation workflows."""

    def test_volcano_to_heatmap_workflow(self):
        """Test typical workflow: validate DE results, then expression matrix."""
        # Step 1: Validate DE results
        de_results = pd.DataFrame(
            {
                "gene_symbol": [f"Gene_{i}" for i in range(100)],
                "log2FoldChange": np.random.randn(100),
                "padj": np.random.uniform(0, 1, 100),
            }
        )
        volcano_result = validate_volcano_data(de_results)
        assert volcano_result.valid

        # Step 2: Filter significant genes
        sig_genes = de_results[de_results["padj"] < 0.05]["gene_symbol"].tolist()

        # Step 3: Validate expression matrix
        np.random.seed(42)
        expr_matrix = pd.DataFrame(
            np.random.randn(len(sig_genes), 10),
            index=sig_genes,
            columns=[f"Sample_{i}" for i in range(10)],
        )
        heatmap_result = validate_heatmap_data(expr_matrix)
        assert heatmap_result.valid

    def test_all_validators_deterministic(self):
        """All validators should produce same results on same input."""
        np.random.seed(42)
        df = pd.DataFrame(
            {
                "gene_symbol": ["A", "B", "C"],
                "log2FoldChange": [1.5, -2.0, 0.1],
                "padj": [0.001, 0.01, 0.5],
            }
        )

        results = [validate_volcano_data(df) for _ in range(10)]
        assert all(r.valid == results[0].valid for r in results)
        assert all(r.errors == results[0].errors for r in results)
        assert all(r.warnings == results[0].warnings for r in results)
