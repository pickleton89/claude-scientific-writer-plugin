"""
Tests for oligon-brand matplotlib adapter deterministic functions.

Tests cover:
- select_cycle(): Deterministic color cycle selection
- run_preflight(): Automated brand compliance validation
- extract_figure_colors(): Color extraction from figures
- get_preflight_report(): Human-readable report generation
- validate_palette(): Color palette validation (Phase 2)
- count_brand_blue(): Brand Blue usage counting (Phase 2)
- get_brand_compliance_report(): Comprehensive compliance report (Phase 2)
"""

import pytest
import sys
from pathlib import Path

# Add adapters directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "adapters"))

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for testing
import matplotlib.pyplot as plt

from matplotlib_adapter import (
    select_cycle,
    run_preflight,
    extract_figure_colors,
    get_preflight_report,
    validate_palette,
    count_brand_blue,
    get_brand_compliance_report,
    set_brand_style,
    BRAND_COLORS,
    CYCLE_TREATMENT_CONTROL,
    CYCLE_NEUTRALS_ONLY,
    CYCLE_OPPOSING,
    CYCLE_MULTI_CATEGORY,
    ALLOWED_COLORS,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def brand_styled_figure():
    """Create a figure with brand style applied."""
    set_brand_style('treatment_control')
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])
    yield fig
    plt.close(fig)


@pytest.fixture
def default_figure():
    """Create a figure with matplotlib defaults (non-compliant)."""
    plt.rcdefaults()
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])
    yield fig
    plt.close(fig)


@pytest.fixture(autouse=True)
def cleanup_plots():
    """Ensure all plots are closed after each test."""
    yield
    plt.close('all')


# =============================================================================
# SELECT_CYCLE TESTS
# =============================================================================

class TestSelectCycle:
    """Tests for the select_cycle() function."""

    # --- Single series tests ---

    def test_single_series_returns_dark_gray(self):
        """Single series should return dark gray."""
        cycle_name, colors = select_cycle(n_series=1)
        assert cycle_name == 'single'
        assert colors == [BRAND_COLORS['dark_gray']]
        assert colors == ['#222222']

    def test_single_series_ignores_context(self):
        """Context should be ignored for single series."""
        for context in ['comparison', 'equal_weight', 'bidirectional']:
            cycle_name, colors = select_cycle(n_series=1, context=context)
            assert cycle_name == 'single'
            assert colors == ['#222222']

    # --- Two series tests ---

    def test_two_series_comparison_returns_treatment_control(self):
        """Two series with comparison context returns treatment_control cycle."""
        cycle_name, colors = select_cycle(n_series=2, context='comparison')
        assert cycle_name == 'treatment_control'
        assert colors == CYCLE_TREATMENT_CONTROL[:2]
        assert colors == ['#222222', '#2DB2E8']

    def test_two_series_default_is_comparison(self):
        """Default context is comparison."""
        cycle_name, colors = select_cycle(n_series=2)
        assert cycle_name == 'treatment_control'
        assert colors == ['#222222', '#2DB2E8']

    def test_two_series_bidirectional_returns_opposing(self):
        """Two series with bidirectional context returns opposing cycle."""
        cycle_name, colors = select_cycle(n_series=2, context='bidirectional')
        assert cycle_name == 'opposing'
        assert colors == CYCLE_OPPOSING[:2]
        assert colors == ['#2DB2E8', '#E8622D']

    def test_two_series_equal_weight_returns_treatment_control(self):
        """Two series with equal_weight still returns treatment_control (only affects 3 series)."""
        cycle_name, colors = select_cycle(n_series=2, context='equal_weight')
        assert cycle_name == 'treatment_control'
        assert colors == ['#222222', '#2DB2E8']

    # --- Three series tests ---

    def test_three_series_comparison_returns_treatment_control(self):
        """Three series with comparison context returns full treatment_control cycle."""
        cycle_name, colors = select_cycle(n_series=3, context='comparison')
        assert cycle_name == 'treatment_control'
        assert colors == CYCLE_TREATMENT_CONTROL
        assert len(colors) == 3

    def test_three_series_equal_weight_returns_neutrals_only(self):
        """Three series with equal_weight returns neutrals_only cycle."""
        cycle_name, colors = select_cycle(n_series=3, context='equal_weight')
        assert cycle_name == 'neutrals_only'
        assert colors == CYCLE_NEUTRALS_ONLY
        assert colors == ['#222222', '#666666', '#999999']

    def test_three_series_no_highlight_returns_neutrals_only(self):
        """Three series with has_highlight=False returns neutrals_only."""
        cycle_name, colors = select_cycle(n_series=3, has_highlight=False)
        assert cycle_name == 'neutrals_only'
        assert colors == CYCLE_NEUTRALS_ONLY

    def test_three_series_bidirectional_returns_opposing(self):
        """Three series with bidirectional context returns opposing cycle."""
        cycle_name, colors = select_cycle(n_series=3, context='bidirectional')
        assert cycle_name == 'opposing'
        assert colors == CYCLE_OPPOSING
        assert len(colors) == 3

    # --- Four series tests ---

    def test_four_series_returns_multi_category(self):
        """Four series always returns multi_category cycle."""
        cycle_name, colors = select_cycle(n_series=4)
        assert cycle_name == 'multi_category'
        assert colors == CYCLE_MULTI_CATEGORY
        assert len(colors) == 4

    def test_four_series_ignores_context(self):
        """Context is ignored for four series (always multi_category)."""
        for context in ['comparison', 'equal_weight', 'bidirectional']:
            cycle_name, colors = select_cycle(n_series=4, context=context)
            assert cycle_name == 'multi_category'

    # --- Edge cases and error handling ---

    def test_zero_series_raises_error(self):
        """Zero series should raise ValueError."""
        with pytest.raises(ValueError, match="n_series must be >= 1"):
            select_cycle(n_series=0)

    def test_negative_series_raises_error(self):
        """Negative series should raise ValueError."""
        with pytest.raises(ValueError, match="n_series must be >= 1"):
            select_cycle(n_series=-1)

    def test_five_series_raises_error(self):
        """Five or more series should raise ValueError with redesign suggestion."""
        with pytest.raises(ValueError, match="Too many series"):
            select_cycle(n_series=5)

    def test_five_series_error_suggests_faceting(self):
        """Error message for 5+ series should mention faceting."""
        with pytest.raises(ValueError, match="faceting"):
            select_cycle(n_series=5)

    def test_large_series_raises_error(self):
        """Large number of series should raise ValueError."""
        with pytest.raises(ValueError, match="Too many series"):
            select_cycle(n_series=10)

    # --- Determinism tests ---

    def test_determinism_same_inputs_same_outputs(self):
        """Same inputs should always produce same outputs."""
        for _ in range(10):
            result1 = select_cycle(n_series=2, context='comparison')
            result2 = select_cycle(n_series=2, context='comparison')
            assert result1 == result2

    def test_all_returned_colors_are_valid_hex(self):
        """All returned colors should be valid hex codes."""
        test_cases = [
            (1, 'comparison'),
            (2, 'comparison'),
            (2, 'bidirectional'),
            (3, 'comparison'),
            (3, 'equal_weight'),
            (3, 'bidirectional'),
            (4, 'comparison'),
        ]
        for n_series, context in test_cases:
            _, colors = select_cycle(n_series=n_series, context=context)
            for color in colors:
                assert color.startswith('#'), f"Color {color} doesn't start with #"
                assert len(color) == 7, f"Color {color} is not 7 characters"


# =============================================================================
# RUN_PREFLIGHT TESTS
# =============================================================================

class TestRunPreflight:
    """Tests for the run_preflight() function."""

    def test_brand_styled_figure_passes_all_checks(self, brand_styled_figure):
        """Figure with brand style should pass all preflight checks."""
        results = run_preflight(brand_styled_figure)
        assert all(results.values()), f"Failed checks: {[k for k, v in results.items() if not v]}"

    def test_returns_dict_with_expected_keys(self, brand_styled_figure):
        """Result should contain all expected check keys."""
        results = run_preflight(brand_styled_figure)
        expected_keys = {'white_background', 'spines_removed', 'grid_off', 'axes_black'}
        assert set(results.keys()) == expected_keys

    def test_all_values_are_boolean(self, brand_styled_figure):
        """All result values should be boolean."""
        results = run_preflight(brand_styled_figure)
        for key, value in results.items():
            assert isinstance(value, bool), f"{key} is not boolean: {type(value)}"

    def test_default_figure_fails_spines_check(self, default_figure):
        """Default matplotlib figure should fail spines check."""
        results = run_preflight(default_figure)
        assert not results['spines_removed']

    def test_white_background_check(self):
        """White background check should work correctly."""
        set_brand_style('treatment_control')

        # White background should pass
        fig1, ax1 = plt.subplots()
        fig1.set_facecolor('white')
        results1 = run_preflight(fig1)
        assert results1['white_background']
        plt.close(fig1)

        # Non-white background should fail
        fig2, ax2 = plt.subplots()
        fig2.set_facecolor('lightgray')
        results2 = run_preflight(fig2)
        assert not results2['white_background']
        plt.close(fig2)

    def test_spines_removed_check(self):
        """Spines removed check should detect visible top/right spines."""
        # Brand style removes spines
        set_brand_style('treatment_control')
        fig1, ax1 = plt.subplots()
        results1 = run_preflight(fig1)
        assert results1['spines_removed']
        plt.close(fig1)

        # Manually enable top spine
        set_brand_style('treatment_control')
        fig2, ax2 = plt.subplots()
        ax2.spines['top'].set_visible(True)
        results2 = run_preflight(fig2)
        assert not results2['spines_removed']
        plt.close(fig2)

    def test_axes_black_check(self):
        """Axes black check should verify spine colors."""
        set_brand_style('treatment_control')
        fig1, ax1 = plt.subplots()
        results1 = run_preflight(fig1)
        assert results1['axes_black']
        plt.close(fig1)

    def test_multi_axes_figure(self):
        """Preflight should check all axes in figure."""
        set_brand_style('treatment_control')
        fig, axes = plt.subplots(2, 2)

        # All axes should pass initially
        results = run_preflight(fig)
        assert results['spines_removed']

        # Enable one spine on one axes - should fail
        axes[0, 1].spines['top'].set_visible(True)
        results = run_preflight(fig)
        assert not results['spines_removed']

        plt.close(fig)

    def test_empty_figure(self):
        """Empty figure (no axes) should pass preflight."""
        set_brand_style('treatment_control')
        fig = plt.figure()
        results = run_preflight(fig)
        # Should pass (no axes to check for spines/grid)
        assert results['white_background']
        assert results['spines_removed']  # Vacuously true
        plt.close(fig)


# =============================================================================
# EXTRACT_FIGURE_COLORS TESTS
# =============================================================================

class TestExtractFigureColors:
    """Tests for the extract_figure_colors() function."""

    def test_extracts_line_colors(self):
        """Should extract colors from line plots."""
        fig, ax = plt.subplots()
        ax.plot([1, 2], [1, 2], color='#2DB2E8')
        ax.plot([1, 2], [2, 1], color='#222222')

        colors = extract_figure_colors(fig)
        assert '#2DB2E8' in colors
        assert '#222222' in colors
        plt.close(fig)

    def test_extracts_scatter_colors(self):
        """Should extract colors from scatter plots."""
        fig, ax = plt.subplots()
        ax.scatter([1, 2], [1, 2], c='#E8622D')

        colors = extract_figure_colors(fig)
        assert '#E8622D' in colors
        plt.close(fig)

    def test_extracts_bar_colors(self):
        """Should extract colors from bar plots."""
        fig, ax = plt.subplots()
        ax.bar([1, 2], [3, 4], color='#158BBB')

        colors = extract_figure_colors(fig)
        assert '#158BBB' in colors
        plt.close(fig)

    def test_converts_named_colors_to_hex(self):
        """Should convert named colors to hex."""
        fig, ax = plt.subplots()
        ax.plot([1, 2], [1, 2], color='red')

        colors = extract_figure_colors(fig)
        assert '#FF0000' in colors
        plt.close(fig)

    def test_returns_uppercase_hex(self):
        """All returned colors should be uppercase hex."""
        fig, ax = plt.subplots()
        ax.plot([1, 2], [1, 2], color='#2db2e8')  # lowercase input

        colors = extract_figure_colors(fig)
        for color in colors:
            assert color == color.upper()
            assert color.startswith('#')
        plt.close(fig)

    def test_empty_figure_returns_empty_set(self):
        """Empty figure should return empty set."""
        fig, ax = plt.subplots()
        colors = extract_figure_colors(fig)
        assert len(colors) == 0
        plt.close(fig)


# =============================================================================
# GET_PREFLIGHT_REPORT TESTS
# =============================================================================

class TestGetPreflightReport:
    """Tests for the get_preflight_report() function."""

    def test_report_contains_header(self, brand_styled_figure):
        """Report should contain header."""
        report = get_preflight_report(brand_styled_figure)
        assert "Oligon Brand Preflight Check" in report

    def test_report_shows_pass_for_compliant_figure(self, brand_styled_figure):
        """Report should show PASS for brand-compliant figure."""
        report = get_preflight_report(brand_styled_figure)
        assert "PASS" in report

    def test_report_shows_fail_for_non_compliant_figure(self, default_figure):
        """Report should show FAIL for non-compliant figure."""
        report = get_preflight_report(default_figure)
        assert "FAIL" in report

    def test_report_contains_check_names(self, brand_styled_figure):
        """Report should list all check names."""
        report = get_preflight_report(brand_styled_figure)
        assert "white_background" in report
        assert "spines_removed" in report
        assert "grid_off" in report
        assert "axes_black" in report

    def test_report_uses_checkmark_for_passed(self, brand_styled_figure):
        """Report should use checkmark for passed checks."""
        report = get_preflight_report(brand_styled_figure)
        assert "✓" in report

    def test_report_uses_x_for_failed(self, default_figure):
        """Report should use X for failed checks."""
        report = get_preflight_report(default_figure)
        assert "✗" in report

    def test_report_shows_count(self, brand_styled_figure):
        """Report should show passed/total count."""
        report = get_preflight_report(brand_styled_figure)
        assert "4/4" in report


# =============================================================================
# ALLOWED_COLORS TESTS
# =============================================================================

class TestAllowedColors:
    """Tests for the ALLOWED_COLORS constant."""

    def test_allowed_colors_contains_all_brand_colors(self):
        """ALLOWED_COLORS should contain all brand colors."""
        for color in BRAND_COLORS.values():
            assert color.upper() in ALLOWED_COLORS

    def test_allowed_colors_are_uppercase(self):
        """All allowed colors should be uppercase."""
        for color in ALLOWED_COLORS:
            assert color == color.upper()

    def test_allowed_colors_are_valid_hex(self):
        """All allowed colors should be valid hex codes."""
        for color in ALLOWED_COLORS:
            assert color.startswith('#')
            assert len(color) == 7


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    """Integration tests combining multiple functions."""

    def test_select_and_apply_cycle_workflow(self):
        """Test complete workflow: select cycle -> apply style -> validate."""
        # Select appropriate cycle
        cycle_name, colors = select_cycle(n_series=2, context='comparison')

        # Apply brand style with selected cycle
        set_brand_style(cycle_name)

        # Create figure
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9], label='Control')
        ax.plot([1, 2, 3], [2, 5, 10], label='Treatment')

        # Validate with preflight
        results = run_preflight(fig)
        assert all(results.values())

        plt.close(fig)

    def test_all_cycles_produce_compliant_figures(self):
        """All cycle types should produce preflight-compliant figures."""
        cycle_names = ['treatment_control', 'neutrals_only', 'opposing', 'multi_category']

        for cycle_name in cycle_names:
            set_brand_style(cycle_name)
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 4, 9])

            results = run_preflight(fig)
            assert all(results.values()), f"Cycle {cycle_name} failed preflight"

            plt.close(fig)

    def test_extracted_colors_match_selected_cycle(self):
        """Colors in figure should match the selected cycle."""
        cycle_name, expected_colors = select_cycle(n_series=2, context='comparison')
        set_brand_style(cycle_name)

        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9])  # First color from cycle
        ax.plot([1, 2, 3], [2, 5, 10])  # Second color from cycle

        extracted = extract_figure_colors(fig)

        # At least one color should be from our cycle
        cycle_colors_upper = {c.upper() for c in expected_colors}
        assert extracted & cycle_colors_upper, "No cycle colors found in figure"

        plt.close(fig)


# =============================================================================
# PHASE 2: VALIDATE_PALETTE TESTS
# =============================================================================

class TestValidatePalette:
    """Tests for the validate_palette() function."""

    def test_brand_styled_figure_is_valid(self, brand_styled_figure):
        """Figure using brand colors should be valid."""
        result = validate_palette(brand_styled_figure)
        assert result['valid']
        assert len(result['violations']) == 0

    def test_returns_expected_keys(self, brand_styled_figure):
        """Result should contain expected keys."""
        result = validate_palette(brand_styled_figure)
        assert 'valid' in result
        assert 'used_colors' in result
        assert 'violations' in result
        assert 'allowed_colors' in result

    def test_detects_non_brand_color(self):
        """Should detect non-brand colors as violations."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9], color='red')  # Non-brand color

        result = validate_palette(fig)
        assert not result['valid']
        assert '#FF0000' in result['violations']
        plt.close(fig)

    def test_detects_multiple_violations(self):
        """Should detect multiple non-brand colors."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9], color='red')
        ax.plot([1, 2, 3], [2, 5, 10], color='green')

        result = validate_palette(fig)
        assert not result['valid']
        assert len(result['violations']) >= 2
        plt.close(fig)

    def test_allows_white_and_black(self):
        """White and black should always be allowed (structural colors)."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9], color='black')
        ax.axhline(y=2, color='white')

        result = validate_palette(fig)
        # Should be valid - black and white are structural
        assert result['valid']
        plt.close(fig)

    def test_all_brand_colors_are_valid(self):
        """All brand colors should pass validation."""
        for color_name, hex_color in BRAND_COLORS.items():
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 4, 9], color=hex_color)

            result = validate_palette(fig)
            assert result['valid'], f"Brand color {color_name} ({hex_color}) was rejected"
            plt.close(fig)

    def test_used_colors_populated(self):
        """used_colors should contain colors from the figure."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9], color='#2DB2E8')

        result = validate_palette(fig)
        assert '#2DB2E8' in result['used_colors']
        plt.close(fig)

    def test_allowed_colors_is_copy(self):
        """allowed_colors should be a copy, not the original set."""
        fig, ax = plt.subplots()
        result = validate_palette(fig)

        # Modifying returned set shouldn't affect ALLOWED_COLORS
        original_len = len(ALLOWED_COLORS)
        result['allowed_colors'].add('#XXXXXX')
        assert len(ALLOWED_COLORS) == original_len
        plt.close(fig)

    def test_empty_figure_is_valid(self):
        """Empty figure with no colors should be valid."""
        fig, ax = plt.subplots()
        result = validate_palette(fig)
        assert result['valid']
        assert len(result['violations']) == 0
        plt.close(fig)


# =============================================================================
# PHASE 2: COUNT_BRAND_BLUE TESTS
# =============================================================================

class TestCountBrandBlue:
    """Tests for the count_brand_blue() function."""

    def test_counts_brand_blue_lines(self):
        """Should count Brand Blue lines."""
        set_brand_style('treatment_control')
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9], color='#2DB2E8')

        result = count_brand_blue(fig)
        assert result['total_count'] == 1
        assert result['per_axes'][0] == 1
        plt.close(fig)

    def test_returns_expected_keys(self):
        """Result should contain expected keys."""
        fig, ax = plt.subplots()
        result = count_brand_blue(fig)

        assert 'total_count' in result
        assert 'per_axes' in result
        assert 'compliant' in result
        assert 'violations' in result
        plt.close(fig)

    def test_zero_count_for_no_brand_blue(self):
        """Should return 0 when no Brand Blue is used."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9], color='#222222')  # Dark gray

        result = count_brand_blue(fig)
        assert result['total_count'] == 0
        assert result['compliant']
        plt.close(fig)

    def test_compliant_with_one_element(self):
        """One Brand Blue element should be compliant."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9], color='#2DB2E8')

        result = count_brand_blue(fig)
        assert result['compliant']
        assert len(result['violations']) == 0
        plt.close(fig)

    def test_compliant_with_two_elements(self):
        """Two Brand Blue elements should be compliant."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9], color='#2DB2E8')
        ax.plot([1, 2, 3], [2, 5, 10], color='#2DB2E8')

        result = count_brand_blue(fig)
        assert result['total_count'] == 2
        assert result['compliant']
        plt.close(fig)

    def test_non_compliant_with_three_elements(self):
        """Three Brand Blue elements in one axes should be non-compliant."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9], color='#2DB2E8')
        ax.plot([1, 2, 3], [2, 5, 10], color='#2DB2E8')
        ax.plot([1, 2, 3], [3, 6, 11], color='#2DB2E8')

        result = count_brand_blue(fig)
        assert result['total_count'] == 3
        assert not result['compliant']
        assert 0 in result['violations']
        plt.close(fig)

    def test_counts_scatter_as_single_element(self):
        """Scatter plot with Brand Blue should count as single element."""
        fig, ax = plt.subplots()
        ax.scatter([1, 2, 3], [1, 4, 9], c='#2DB2E8')

        result = count_brand_blue(fig)
        assert result['total_count'] == 1
        plt.close(fig)

    def test_counts_bar_elements(self):
        """Should count Brand Blue bars."""
        fig, ax = plt.subplots()
        ax.bar([1, 2], [3, 4], color='#2DB2E8')

        result = count_brand_blue(fig)
        assert result['total_count'] == 2  # Two bars
        plt.close(fig)

    def test_multi_axes_counts_separately(self):
        """Should count Brand Blue per axes."""
        fig, (ax1, ax2) = plt.subplots(1, 2)
        ax1.plot([1, 2], [1, 2], color='#2DB2E8')
        ax2.plot([1, 2], [1, 2], color='#2DB2E8')
        ax2.plot([1, 2], [2, 3], color='#2DB2E8')

        result = count_brand_blue(fig)
        assert result['per_axes'][0] == 1
        assert result['per_axes'][1] == 2
        assert result['total_count'] == 3
        assert result['compliant']  # Both axes have <= 2
        plt.close(fig)

    def test_violation_in_one_axes_only(self):
        """Violation in one axes should flag only that axes."""
        fig, (ax1, ax2) = plt.subplots(1, 2)
        ax1.plot([1, 2], [1, 2], color='#2DB2E8')
        # ax2 has 3 Brand Blue elements - violation
        ax2.plot([1, 2], [1, 2], color='#2DB2E8')
        ax2.plot([1, 2], [2, 3], color='#2DB2E8')
        ax2.plot([1, 2], [3, 4], color='#2DB2E8')

        result = count_brand_blue(fig)
        assert not result['compliant']
        assert 0 not in result['violations']
        assert 1 in result['violations']
        plt.close(fig)

    def test_case_insensitive_detection(self):
        """Should detect Brand Blue regardless of case."""
        fig, ax = plt.subplots()
        ax.plot([1, 2], [1, 2], color='#2db2e8')  # lowercase

        result = count_brand_blue(fig)
        assert result['total_count'] == 1
        plt.close(fig)

    def test_empty_figure_is_compliant(self):
        """Empty figure should be compliant with zero count."""
        fig, ax = plt.subplots()

        result = count_brand_blue(fig)
        assert result['total_count'] == 0
        assert result['compliant']
        plt.close(fig)


# =============================================================================
# PHASE 2: GET_BRAND_COMPLIANCE_REPORT TESTS
# =============================================================================

class TestGetBrandComplianceReport:
    """Tests for the get_brand_compliance_report() function."""

    def test_report_contains_all_sections(self, brand_styled_figure):
        """Report should contain all validation sections."""
        report = get_brand_compliance_report(brand_styled_figure)

        assert "PREFLIGHT CHECKS:" in report
        assert "PALETTE VALIDATION:" in report
        assert "BRAND BLUE USAGE:" in report
        assert "OVERALL:" in report

    def test_report_contains_header(self, brand_styled_figure):
        """Report should have header."""
        report = get_brand_compliance_report(brand_styled_figure)
        assert "Oligon Brand Compliance Report" in report

    def test_compliant_figure_passes_overall(self, brand_styled_figure):
        """Fully compliant figure should show OVERALL: PASS."""
        report = get_brand_compliance_report(brand_styled_figure)
        assert "OVERALL: PASS" in report

    def test_non_compliant_palette_shows_violations(self):
        """Non-brand colors should be listed in report."""
        fig, ax = plt.subplots()
        set_brand_style('treatment_control')
        ax.plot([1, 2, 3], [1, 4, 9], color='red')

        report = get_brand_compliance_report(fig)
        assert "Non-brand colors detected" in report
        assert "#FF0000" in report
        assert "OVERALL: FAIL" in report
        plt.close(fig)

    def test_excess_brand_blue_shows_in_report(self):
        """Excess Brand Blue should be reported."""
        set_brand_style('treatment_control')
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9], color='#2DB2E8')
        ax.plot([1, 2, 3], [2, 5, 10], color='#2DB2E8')
        ax.plot([1, 2, 3], [3, 6, 11], color='#2DB2E8')

        report = get_brand_compliance_report(fig)
        assert "Exceeds limit" in report
        assert "OVERALL: FAIL" in report
        plt.close(fig)

    def test_preflight_failure_shows_in_report(self, default_figure):
        """Preflight failures should show in report."""
        report = get_brand_compliance_report(default_figure)
        assert "✗" in report
        assert "OVERALL: FAIL" in report

    def test_shows_total_brand_blue_count(self, brand_styled_figure):
        """Report should show total Brand Blue count."""
        report = get_brand_compliance_report(brand_styled_figure)
        assert "Total elements:" in report


# =============================================================================
# PHASE 2: INTEGRATION TESTS
# =============================================================================

class TestPhase2Integration:
    """Integration tests for Phase 2 functions."""

    def test_full_compliance_workflow(self):
        """Test complete compliance validation workflow."""
        # Select cycle
        cycle_name, colors = select_cycle(n_series=2, context='comparison')

        # Apply style
        set_brand_style(cycle_name)

        # Create figure
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9], label='Control')
        ax.plot([1, 2, 3], [2, 5, 10], label='Treatment')

        # Run all validations
        preflight = run_preflight(fig)
        palette = validate_palette(fig)
        brand_blue = count_brand_blue(fig)

        # All should pass
        assert all(preflight.values())
        assert palette['valid']
        assert brand_blue['compliant']

        plt.close(fig)

    def test_compliance_report_matches_individual_checks(self):
        """Compliance report should reflect individual check results."""
        set_brand_style('treatment_control')
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9])

        # Get individual results
        preflight = run_preflight(fig)
        palette = validate_palette(fig)
        brand_blue = count_brand_blue(fig)

        # Get report
        report = get_brand_compliance_report(fig)

        # If all pass individually, report should show PASS
        all_pass = all(preflight.values()) and palette['valid'] and brand_blue['compliant']
        if all_pass:
            assert "OVERALL: PASS" in report
        else:
            assert "OVERALL: FAIL" in report

        plt.close(fig)

    def test_all_cycles_pass_full_compliance(self):
        """All cycle types should pass full compliance check."""
        cycle_names = ['treatment_control', 'neutrals_only', 'opposing', 'multi_category']

        for cycle_name in cycle_names:
            set_brand_style(cycle_name)
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 4, 9])

            preflight = run_preflight(fig)
            palette = validate_palette(fig)
            brand_blue = count_brand_blue(fig)

            assert all(preflight.values()), f"{cycle_name} failed preflight"
            assert palette['valid'], f"{cycle_name} failed palette validation"
            assert brand_blue['compliant'], f"{cycle_name} failed brand blue check"

            plt.close(fig)


# =============================================================================
# SVG OUTPUT CONTRACT TESTS
# =============================================================================

import re
import tempfile
import os


class TestSvgOutputContract:
    """
    Tests for the SVG output contract documented in oligon-brand/SKILL.md
    <svg_output>:

    - svg.fonttype must be 'none' so text stays as <text> elements
      (not glyph paths), enabling grep-based brand verification and
      downstream editability.
    - font-family in emitted SVG must be Arial/Helvetica/sans-serif.
    - font-size must be in the 10/12/14/16 band — no values below 10.
    """

    def _emit_svg(self) -> str:
        """Create a brand-styled figure, save to SVG, return SVG text."""
        set_brand_style('treatment_control')
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.plot([1, 2, 3], [1, 4, 9], label='Control')
        ax.plot([1, 2, 3], [2, 5, 10], label='Treatment')
        ax.set_xlabel('X axis label')
        ax.set_ylabel('Y axis label')
        ax.set_title('Title text')
        ax.legend()

        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.svg', delete=False
        ) as tmp:
            svg_path = tmp.name
        try:
            fig.savefig(svg_path, bbox_inches='tight')
            with open(svg_path, 'r') as fh:
                svg_text = fh.read()
        finally:
            plt.close(fig)
            if os.path.exists(svg_path):
                os.unlink(svg_path)
        return svg_text

    def test_svg_fonttype_is_none(self):
        """set_brand_style() must set svg.fonttype to 'none'."""
        set_brand_style('treatment_control')
        assert plt.rcParams['svg.fonttype'] == 'none'

    def test_svg_contains_text_elements(self):
        """
        With svg.fonttype='none', matplotlib emits <text> elements
        rather than rasterizing glyphs to <path>. If this regresses,
        the brand grep-checks return nothing and the contract fails
        silently.
        """
        svg = self._emit_svg()
        assert '<text' in svg, "SVG has no <text> elements — fonttype likely reverted"

    def test_svg_font_family_is_brand_compliant(self):
        """
        Every font-family declaration must reference Arial/Helvetica
        (or sans-serif fallback). No Times, Calibri, or system defaults.
        """
        svg = self._emit_svg()
        font_families = set(re.findall(r'font-family[^;">]+', svg))
        assert font_families, "No font-family declarations in SVG"

        forbidden = ['Times', 'Calibri']
        for ff in font_families:
            for bad in forbidden:
                assert bad.lower() not in ff.lower(), \
                    f"Forbidden font in {ff!r}"
            # At least one of Arial/Helvetica/sans-serif must appear
            assert any(
                ok.lower() in ff.lower()
                for ok in ['Arial', 'Helvetica', 'sans-serif']
            ), f"font-family {ff!r} has no brand-approved family"

    def test_svg_font_sizes_meet_10pt_floor(self):
        """
        Every font-size in emitted SVG must be >=10 (px or pt).
        Brand contract: 10pt floor, 12pt base, 14pt panel, 16pt title.
        """
        svg = self._emit_svg()
        size_pattern = re.compile(r'font-size:\s*([0-9]+(?:\.[0-9]+)?)(px|pt)')
        sizes = size_pattern.findall(svg)
        assert sizes, "No font-size declarations in SVG"

        for value_str, _unit in sizes:
            value = float(value_str)
            assert value >= 10, \
                f"Found font-size {value_str} below 10pt floor"

    def test_svg_font_sizes_match_ladder(self):
        """
        Sizes should be drawn from the brand ladder {10, 12, 14, 16}.
        Other values in the band suggest the rcParams were overridden
        between style and savefig.
        """
        svg = self._emit_svg()
        size_pattern = re.compile(r'font-size:\s*([0-9]+(?:\.[0-9]+)?)(px|pt)')
        sizes = {float(v) for v, _ in size_pattern.findall(svg)}
        allowed = {10.0, 12.0, 14.0, 16.0}
        unexpected = sizes - allowed
        assert not unexpected, \
            f"Sizes outside brand ladder: {unexpected} (expected subset of {allowed})"
