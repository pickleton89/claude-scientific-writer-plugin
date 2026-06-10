"""Tests for Fujii (2026) intent classifier, chart recommender, palette
recommender, and chart-design validators (Weissgerber 2015, Fujii 2023).
"""

import logging
import sys
from pathlib import Path

import numpy as np
import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from plotting_params import (  # noqa: E402
    ChartRecommendation,
    classify_figure_intent,
    recommend_chart,
    recommend_palette,
)
from validate_data import (  # noqa: E402
    check_closure,
    check_continuous_as_bars,
    check_default_palette,
    check_encoding_value_fidelity,
    check_riskratio_as_bars,
)


# ---------------------------------------------------------------------------
# Fujii intent classifier
# ---------------------------------------------------------------------------


class TestClassifyFigureIntent:
    """Fujii 2026 §"Identify the key message" — Description / Difference / Association."""

    @pytest.mark.parametrize(
        "phrase",
        [
            "compare gene expression between treated and control",
            "treatment vs placebo group difference",
        ],
    )
    def test_difference_phrases(self, phrase: str) -> None:
        assert classify_figure_intent(phrase) == "difference"

    @pytest.mark.parametrize(
        "phrase",
        [
            "show the distribution of patient ages",
            "describe the spread of expression values",
        ],
    )
    def test_description_phrases(self, phrase: str) -> None:
        assert classify_figure_intent(phrase) == "description"

    @pytest.mark.parametrize(
        "phrase",
        [
            "does dose predict response?",
            "correlation between biomarker and outcome",
        ],
    )
    def test_association_phrases(self, phrase: str) -> None:
        assert classify_figure_intent(phrase) == "association"

    def test_unknown_phrase_returns_general(self) -> None:
        assert classify_figure_intent("make a chart") == "general"


# ---------------------------------------------------------------------------
# recommend_chart
# ---------------------------------------------------------------------------


class TestRecommendChart:
    """Encodes Weissgerber 2015, Fujii 2023, Cleveland-McGill 1984 anti-patterns."""

    def test_difference_continuous_unpaired_prefers_box_jitter(self) -> None:
        recs = recommend_chart(
            "difference", x_type="categorical", y_type="continuous", n_groups=2
        )
        assert recs[0].plot_type == "box+jitter"

    def test_difference_continuous_unpaired_flags_bar_as_discouraged(self) -> None:
        recs = recommend_chart(
            "difference", x_type="categorical", y_type="continuous", n_groups=2
        )
        bar_recs = [r for r in recs if r.plot_type == "bar"]
        assert len(bar_recs) == 1
        assert bar_recs[0].discouraged is True
        assert "Weissgerber" in (bar_recs[0].citation or "")

    def test_difference_paired_prefers_paired_points(self) -> None:
        recs = recommend_chart(
            "difference",
            x_type="categorical",
            y_type="continuous",
            n_groups=2,
            paired=True,
        )
        assert recs[0].plot_type == "paired_points_lines"

    def test_riskratio_prefers_pointrange_flags_bar(self) -> None:
        recs = recommend_chart("difference", y_type="point_estimate_ci")
        assert recs[0].plot_type == "pointrange"
        bar_recs = [r for r in recs if r.plot_type == "bar"]
        assert len(bar_recs) == 1
        assert bar_recs[0].discouraged is True
        assert "Fujii 2023" in (bar_recs[0].citation or "")

    def test_description_continuous_returns_distribution_plots(self) -> None:
        recs = recommend_chart("description", y_type="continuous")
        plot_types = {r.plot_type for r in recs}
        assert plot_types == {"histogram", "kde", "ecdf"}

    def test_description_many_categorical_pie_discouraged(self) -> None:
        recs = recommend_chart(
            "description", x_type="categorical", y_type=None, n_groups=8
        )
        pie_recs = [r for r in recs if r.plot_type == "pie"]
        assert len(pie_recs) == 1
        assert pie_recs[0].discouraged is True
        assert "Cleveland" in (pie_recs[0].citation or "")

    def test_description_few_categorical_pie_not_discouraged(self) -> None:
        recs = recommend_chart(
            "description", x_type="categorical", y_type=None, n_groups=3
        )
        pie_recs = [r for r in recs if r.plot_type == "pie"]
        assert len(pie_recs) == 1
        assert pie_recs[0].discouraged is False

    def test_association_continuous_continuous_returns_scatter(self) -> None:
        recs = recommend_chart("association", x_type="continuous", y_type="continuous")
        plot_types = [r.plot_type for r in recs]
        assert plot_types[0] == "scatter"

    def test_unknown_intent_returns_general(self) -> None:
        recs = recommend_chart("nonsense_intent")
        assert len(recs) == 1
        assert recs[0].plot_type == "general"

    def test_chart_recommendation_dataclass_fields(self) -> None:
        r = ChartRecommendation("box+jitter", "rationale", citation="Weissgerber 2015")
        assert r.plot_type == "box+jitter"
        assert r.discouraged is False
        assert r.citation == "Weissgerber 2015"


# ---------------------------------------------------------------------------
# recommend_palette
# ---------------------------------------------------------------------------


class TestRecommendPalette:
    """Cowan 2010 working-memory cap; Crameri 2020 CVD safety."""

    def test_categorical_few_levels_returns_okabe_ito(self) -> None:
        p = recommend_palette("categorical", n_levels=4)
        assert p.name == "Okabe-Ito"
        assert p.colorblind_safe is True

    def test_categorical_eight_levels_returns_categorical_8(self) -> None:
        p = recommend_palette("categorical", n_levels=8)
        assert p.name == "Categorical 8"

    def test_categorical_too_many_warns_via_logging(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        with caplog.at_level(logging.WARNING):
            p = recommend_palette("categorical", n_levels=12)
        assert any("exceeds the 8-level" in record.message for record in caplog.records)
        # Still returns a categorical palette as best-effort
        assert p.colorblind_safe is True

    def test_diverging_returns_diverging_palette(self) -> None:
        p = recommend_palette("diverging")
        assert p.name == "Heatmap Diverging"

    def test_sequential_returns_viridis_sample(self) -> None:
        p = recommend_palette("sequential")
        assert p.name == "Viridis (7-stop)"
        assert p.colorblind_safe is True
        assert len(p.colors) == 7

    def test_sequential_too_many_levels_warns(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        with caplog.at_level(logging.WARNING):
            p = recommend_palette("sequential", n_levels=20)
        assert any("exceeds the 7-stop" in record.message for record in caplog.records)
        # Still returns the discrete sample (caller can switch to continuous cmap)
        assert p.name == "Viridis (7-stop)"

    def test_unknown_scale_type_raises(self) -> None:
        with pytest.raises(ValueError):
            recommend_palette("nonsense")


# ---------------------------------------------------------------------------
# Chart-design validators (Weissgerber 2015, Fujii 2023)
# ---------------------------------------------------------------------------


class TestCheckContinuousAsBars:
    """Weissgerber 2015 PLoS Biol bar-chart anti-pattern."""

    def setup_method(self) -> None:
        np.random.seed(42)

    def test_continuous_data_with_bar_warns(self) -> None:
        data = {
            "control": np.random.normal(0, 1, 50),
            "treated": np.random.normal(1, 1, 50),
        }
        result = check_continuous_as_bars(data, "bar")
        assert result.valid is True  # advisory only
        assert len(result.warnings) == 1
        assert "Weissgerber" in result.warnings[0]
        assert "box+jitter" in result.warnings[0]

    def test_discrete_counts_with_bar_no_warning(self) -> None:
        # Single integer count per category — no continuous distribution
        result = check_continuous_as_bars({"a": [10], "b": [12]}, "bar")
        assert len(result.warnings) == 0

    def test_continuous_data_with_box_no_warning(self) -> None:
        data = {
            "control": np.random.normal(0, 1, 50),
            "treated": np.random.normal(1, 1, 50),
        }
        result = check_continuous_as_bars(data, "box+jitter")
        assert len(result.warnings) == 0

    def test_continuous_data_with_violin_no_warning(self) -> None:
        data = np.random.normal(0, 1, 50)
        result = check_continuous_as_bars(data, "violin+jitter")
        assert len(result.warnings) == 0

    @pytest.mark.parametrize("alias", ["barplot", "bar chart", "BarPlot", "column"])
    def test_bar_aliases_trigger_check(self, alias: str) -> None:
        data = np.random.normal(0, 1, 50)
        result = check_continuous_as_bars(data, alias)
        assert len(result.warnings) == 1


class TestCheckRiskratioAsBars:
    """Fujii 2023 J Epidemiol points + 95% CI rule."""

    @pytest.mark.parametrize(
        "label",
        [
            "Odds ratio (95% CI)",
            "Hazard ratio for death",
            "OR (95% CI: 1.2-2.5)",
            "HR (95% CI)",
            "Relative risk",
            "Incidence rate ratio",
        ],
    )
    def test_bar_with_ratio_label_warns(self, label: str) -> None:
        result = check_riskratio_as_bars("bar", label)
        assert result.valid is True
        assert len(result.warnings) == 1
        assert "Fujii 2023" in result.warnings[0]
        assert "pointrange" in result.warnings[0]

    @pytest.mark.parametrize("label", ["Sample size", "Mean expression", "n / N"])
    def test_bar_with_unrelated_label_no_warning(self, label: str) -> None:
        result = check_riskratio_as_bars("bar", label)
        assert len(result.warnings) == 0

    def test_pointrange_with_ratio_label_no_warning(self) -> None:
        result = check_riskratio_as_bars("pointrange", "Hazard ratio (95% CI)")
        assert len(result.warnings) == 0

    def test_forest_plot_with_ratio_label_no_warning(self) -> None:
        # Forest plots are not in the bar_aliases set; they're not flagged.
        result = check_riskratio_as_bars("forest_plot", "Odds ratio (95% CI)")
        assert len(result.warnings) == 0

    def test_empty_label_no_warning(self) -> None:
        result = check_riskratio_as_bars("bar", "")
        assert len(result.warnings) == 0


# ---------------------------------------------------------------------------
# AI-figure-slop validators (encoding fidelity, closure, default palette)
# ---------------------------------------------------------------------------


class TestCheckEncodingValueFidelity:
    """Report dimension 2.1 (encoding-value fidelity), categorical tell."""

    def test_bar_geometry_matches_values_passes(self) -> None:
        r = check_encoding_value_fidelity(
            [10, 20, 30],
            "bar",
            geometry=[1.0, 2.0, 3.0],  # consistent k=0.1
        )
        assert r.valid is True
        assert len(r.errors) == 0

    def test_bar_geometry_desync_errors(self) -> None:
        # third bar scaled by a different factor -> height/label desync
        r = check_encoding_value_fidelity([10, 20, 30], "bar", geometry=[1.0, 2.0, 9.0])
        assert r.valid is False
        assert any("desync" in e or "linear transform" in e for e in r.errors)

    def test_printed_label_mismatch_errors(self) -> None:
        r = check_encoding_value_fidelity([42.0], "bar", printed_labels=["57"])
        assert r.valid is False
        assert any("does not match" in e for e in r.errors)

    def test_pie_angles_proportional_passes(self) -> None:
        r = check_encoding_value_fidelity(
            {"A": 25, "B": 25, "C": 50},
            "pie",
            geometry=[90.0, 90.0, 180.0],  # degrees sum 360
            printed_labels=["25%", "25%", "50%"],
        )
        assert r.valid is True

    def test_pie_negative_value_errors(self) -> None:
        r = check_encoding_value_fidelity({"A": -5, "B": 10}, "pie")
        assert r.valid is False
        assert any("negative" in e.lower() for e in r.errors)

    def test_log_axis_nonpositive_value_errors(self) -> None:
        r = check_encoding_value_fidelity(
            [0.0, 10.0], "bar", geometry=[0.0, 1.0], axis_is_log=True
        )
        assert r.valid is False
        assert any("log" in e.lower() for e in r.errors)

    def test_nan_excluded_warns_not_errors(self) -> None:
        r = check_encoding_value_fidelity(
            [10.0, np.nan, 30.0], "bar", geometry=[1.0, 0.0, 3.0]
        )
        assert r.valid is True
        assert any("NaN" in w for w in r.warnings)


class TestCheckClosure:
    """Report dimension 2.2 (closure / conservation)."""

    def test_pie_sums_to_100_passes(self) -> None:
        r = check_closure({"A": 25, "B": 25, "C": 50}, "pie")
        assert r.valid is True
        assert len(r.errors) == 0

    def test_pie_rounding_gap_warns_not_errors(self) -> None:
        # 33.3*3 = 99.9 -> within the rounding band (>0.5pp, <=1.0pp)
        r = check_closure([33.3, 33.3, 33.3], "pie", expect_percent=True)
        assert r.valid is True
        assert any("gap" in w for w in r.warnings)

    def test_pie_fails_to_sum_errors(self) -> None:
        r = check_closure([20, 30, 42], "pie", expect_percent=True)  # 92%
        assert r.valid is False
        assert any("conservation" in e or "whole" in e for e in r.errors)

    def test_stacked_bar_reconciles_to_declared_total(self) -> None:
        r = check_closure([400, 350, 500], "stacked_bar", declared_total=1250)
        assert r.valid is True

    def test_stacked_bar_total_mismatch_errors(self) -> None:
        r = check_closure([400, 350, 500], "stacked_bar", declared_total=2000)
        assert r.valid is False

    def test_negative_pie_segment_errors(self) -> None:
        r = check_closure({"A": -10, "B": 110}, "pie")
        assert r.valid is False
        assert any("negative" in e.lower() for e in r.errors)

    def test_non_partsofwhole_encoding_is_noop(self) -> None:
        r = check_closure([20, 30, 42], "scatter")
        assert r.valid is True
        assert len(r.errors) == 0 and len(r.warnings) == 0


class TestCheckDefaultPalette:
    """Report dimension 6.2 (template/default-distribution look), two-sided weak signal."""

    def test_tab10_palette_warns(self) -> None:
        r = check_default_palette(["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"])
        assert r.valid is True  # never blocks
        assert len(r.warnings) == 1
        assert "default" in r.warnings[0].lower()

    def test_named_default_sentinel_warns(self) -> None:
        r = check_default_palette("tab10")
        assert r.valid is True
        assert any("default" in w.lower() for w in r.warnings)

    def test_okabe_ito_palette_no_warning(self) -> None:
        r = check_default_palette(
            ["#e69f00", "#56b4e9", "#009e73", "#f0e442", "#0072b2"]
        )
        assert len(r.warnings) == 0  # recommended palette is clean (two-sided)

    def test_oligon_brand_palette_no_warning(self) -> None:
        r = check_default_palette(["#222222", "#2db2e8", "#666666", "#e8622d"])
        assert len(r.warnings) == 0

    def test_single_c0_blue_does_not_false_flag(self) -> None:
        r = check_default_palette(["#1f77b4"])  # one blue is not a fingerprint
        assert len(r.warnings) == 0

    def test_seaborn_deep_palette_warns(self) -> None:
        r = check_default_palette(["#4c72b0", "#dd8452", "#55a868", "#c44e52"])
        assert len(r.warnings) == 1

    def test_rgb_float_tuples_normalized_and_flagged(self) -> None:
        # tab10 C0/C1/C2 as 0..1 RGB floats
        r = check_default_palette(
            [(0.121, 0.466, 0.705), (1.0, 0.498, 0.054), (0.172, 0.627, 0.172)]
        )
        assert len(r.warnings) == 1

    def test_none_palette_is_noop(self) -> None:
        r = check_default_palette(None)
        assert r.valid is True
        assert len(r.warnings) == 0
