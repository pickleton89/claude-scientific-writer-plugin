"""Tests for chart_selector module."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.chart_selector import (
    recommend_chart_type,
    get_chart_description,
    list_data_types,
    CHART_RECOMMENDATIONS,
)


class TestRecommendChartType:
    """Tests for chart type recommendations."""

    def test_comparison_few_categories(self):
        """Few categories should recommend bar charts."""
        result = recommend_chart_type("comparison", n_categories=3)
        assert "bar" in result["recommended"]
        assert "pie" in result["avoid"]

    def test_comparison_many_categories(self):
        """Many categories should recommend horizontal bar."""
        result = recommend_chart_type("comparison", n_categories=15)
        assert "horizontal_bar" in result["recommended"]
        assert "resolved_type" == "comparison_many_categories" or \
               result["resolved_type"] == "comparison_many_categories"

    def test_time_series(self):
        """Time series should recommend line charts."""
        result = recommend_chart_type("time_series")
        assert "line" in result["recommended"]
        assert "bar" in result["avoid"]

    def test_time_series_multiple_groups(self):
        """Multiple time series should handle groups."""
        result = recommend_chart_type("time_series", n_groups=3)
        # Should get multi_line or small_multiples
        assert any(x in result["recommended"] for x in ["multi_line", "small_multiples", "line"])

    def test_distribution(self):
        """Distribution data should recommend histograms/violins."""
        result = recommend_chart_type("distribution")
        assert any(x in result["recommended"] for x in ["histogram", "violin", "box_plot"])
        assert "bar_of_means" in result["avoid"]

    def test_relationship_2var(self):
        """Two-variable relationships should recommend scatter."""
        result = recommend_chart_type("relationship")
        assert "scatter" in result["recommended"]

    def test_relationship_3var(self):
        """Three-variable relationships should use color/size encoding."""
        result = recommend_chart_type("relationship", n_groups=1)
        assert any(x in result["recommended"] for x in ["scatter_with_color", "scatter_with_size", "scatter"])

    def test_part_to_whole_few(self):
        """Part-to-whole with few segments can use pie."""
        result = recommend_chart_type("part_to_whole", n_categories=3)
        # Either pie is acceptable or stacked_bar recommended
        assert "stacked_bar" in result["recommended"] or "pie" in result["recommended"]

    def test_part_to_whole_many(self):
        """Part-to-whole with many segments should avoid pie."""
        result = recommend_chart_type("part_to_whole", n_categories=10)
        assert "stacked_bar" in result["recommended"] or "treemap" in result["recommended"]

    def test_flow_network(self):
        """Flow data should recommend sankey/network."""
        result = recommend_chart_type("flow_network")
        assert "sankey" in result["recommended"]

    def test_ranking(self):
        """Ranking data should use horizontal bars."""
        result = recommend_chart_type("ranking")
        assert "horizontal_bar" in result["recommended"]

    def test_unknown_data_type_returns_safe_defaults(self):
        """Unknown data types should return safe defaults."""
        result = recommend_chart_type("unknown_type")
        assert "recommended" in result
        assert "avoid" in result
        assert result["resolved_type"] == "unknown"

    def test_case_insensitive(self):
        """Data type matching should be case-insensitive."""
        result1 = recommend_chart_type("TIME_SERIES")
        result2 = recommend_chart_type("time_series")
        assert result1["recommended"] == result2["recommended"]

    def test_underscore_and_hyphen_equivalent(self):
        """Underscores and hyphens should be equivalent."""
        result1 = recommend_chart_type("time_series")
        result2 = recommend_chart_type("time-series")
        assert result1["recommended"] == result2["recommended"]

    def test_returns_reason(self):
        """All recommendations should include a reason."""
        for data_type in list_data_types():
            result = recommend_chart_type(data_type)
            assert "reason" in result
            assert len(result["reason"]) > 0


class TestGetChartDescription:
    """Tests for chart descriptions."""

    def test_known_charts_have_descriptions(self):
        """Common chart types should have descriptions."""
        known_charts = ["bar", "line", "scatter", "histogram", "pie"]
        for chart in known_charts:
            desc = get_chart_description(chart)
            assert len(desc) > 10  # Meaningful description

    def test_unknown_chart_returns_message(self):
        """Unknown charts should return informative message."""
        desc = get_chart_description("nonexistent_chart")
        assert "no description" in desc.lower()

    def test_case_insensitive(self):
        """Chart lookup should be case-insensitive."""
        desc1 = get_chart_description("BAR")
        desc2 = get_chart_description("bar")
        assert desc1 == desc2


class TestListDataTypes:
    """Tests for data type listing."""

    def test_returns_list(self):
        """Should return a list of strings."""
        types = list_data_types()
        assert isinstance(types, list)
        assert all(isinstance(t, str) for t in types)

    def test_contains_common_types(self):
        """Should include common data visualization types."""
        types = list_data_types()
        expected = ["comparison", "time_series", "distribution", "relationship", "part_to_whole"]
        for exp in expected:
            assert exp in types


class TestChartRecommendationsIntegrity:
    """Tests for chart recommendations data integrity."""

    def test_all_entries_have_required_fields(self):
        """All chart recommendations should have required fields."""
        required = ["recommended", "avoid", "reason"]
        for data_type, rec in CHART_RECOMMENDATIONS.items():
            for field in required:
                assert field in rec, f"{data_type} missing {field}"

    def test_recommended_is_list(self):
        """Recommended charts should be lists."""
        for data_type, rec in CHART_RECOMMENDATIONS.items():
            assert isinstance(rec["recommended"], list), \
                f"{data_type} recommended is not a list"
            assert len(rec["recommended"]) > 0, \
                f"{data_type} has no recommendations"

    def test_avoid_is_list(self):
        """Avoid list should be a list."""
        for data_type, rec in CHART_RECOMMENDATIONS.items():
            assert isinstance(rec["avoid"], list), \
                f"{data_type} avoid is not a list"

    def test_no_overlap_between_recommended_and_avoid(self):
        """Recommended and avoid lists should not overlap."""
        for data_type, rec in CHART_RECOMMENDATIONS.items():
            overlap = set(rec["recommended"]) & set(rec["avoid"])
            assert len(overlap) == 0, \
                f"{data_type} has overlap: {overlap}"
