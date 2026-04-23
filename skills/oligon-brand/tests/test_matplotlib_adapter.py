"""
Tests for oligon-brand matplotlib adapter (v5.0 — Style Guide v2.3).

Covers:
- select_cycle(): deterministic Rule 1 cycle selection
- run_preflight(): automated brand compliance validation
- extract_figure_colors(): color extraction from figures
- get_preflight_report(): human-readable preflight report
- validate_palette(): v2.3 ramp palette validation
- count_brand_blue(): brand.blue usage counting (<=2 per panel)
- get_brand_compliance_report(): combined compliance report
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "adapters"))

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
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
    BRAND_BLUE,
    BLUE_200, BLUE_300, BLUE_400, BLUE_500,
    BLUE_600, BLUE_700, BLUE_800, BLUE_900,
    ORANGE_500, ORANGE_600, ORANGE_700,
    NEUTRAL_300, NEUTRAL_700, NEUTRAL_900,
    CYCLE_TREATMENT_CONTROL,
    CYCLE_PEER_3, CYCLE_PEER_4,
    CYCLE_FOCUS,
    CYCLE_OPPOSING,
    CYCLE_MULTI_CATEGORY,
    CYCLE_NEUTRALS_ONLY,  # deprecated alias -> CYCLE_PEER_3
    VOLCANO_COLORS,
    ALLOWED_COLORS,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def brand_styled_figure():
    """Figure with default brand style applied."""
    set_brand_style('treatment_control')
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])
    yield fig
    plt.close(fig)


@pytest.fixture
def default_figure():
    """Figure with matplotlib defaults (non-compliant)."""
    plt.rcdefaults()
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])
    yield fig
    plt.close(fig)


@pytest.fixture(autouse=True)
def cleanup_plots():
    yield
    plt.close('all')


# =============================================================================
# SELECT_CYCLE TESTS
# =============================================================================

class TestSelectCycle:
    """Tests for the select_cycle() function (Rule 1)."""

    # --- Single series ---

    def test_single_series_returns_brand_blue(self):
        cycle_name, colors = select_cycle(n_series=1)
        assert cycle_name == 'single'
        assert colors == [BRAND_BLUE]
        assert colors == ['#2DB2E8']

    def test_single_series_ignores_context(self):
        for context in ['comparison', 'equal_weight', 'bidirectional']:
            cycle_name, colors = select_cycle(n_series=1, context=context)
            assert cycle_name == 'single'
            assert colors == [BRAND_BLUE]

    # --- Two series ---

    def test_two_series_comparison_returns_treatment_control(self):
        """v2.3 Cycle 1 is same-hue: brand.blue + blue.300."""
        cycle_name, colors = select_cycle(n_series=2, context='comparison')
        assert cycle_name == 'treatment_control'
        assert colors == CYCLE_TREATMENT_CONTROL
        assert colors == [BRAND_BLUE, BLUE_300]
        assert colors == ['#2DB2E8', '#76CAF3']

    def test_two_series_default_is_comparison(self):
        cycle_name, colors = select_cycle(n_series=2)
        assert cycle_name == 'treatment_control'
        assert colors == [BRAND_BLUE, BLUE_300]

    def test_two_series_bidirectional_returns_opposing(self):
        """v2.3 Cycle 3 opposing: blue.600 + orange.600."""
        cycle_name, colors = select_cycle(n_series=2, context='bidirectional')
        assert cycle_name == 'opposing'
        assert colors == CYCLE_OPPOSING[:2]
        assert colors == [BLUE_600, ORANGE_600]
        assert colors == ['#006EA6', '#A0421D']

    def test_two_series_equal_weight_returns_treatment_control(self):
        cycle_name, colors = select_cycle(n_series=2, context='equal_weight')
        assert cycle_name == 'treatment_control'
        assert colors == [BRAND_BLUE, BLUE_300]

    # --- Three series ---

    def test_three_series_comparison_returns_focus(self):
        """v2.3: no 3-arm treatment/control cycle exists; comparison falls to focus."""
        cycle_name, colors = select_cycle(n_series=3, context='comparison')
        assert cycle_name == 'focus'
        assert len(colors) == 3

    def test_three_series_equal_weight_returns_peer_3(self):
        """v2.3 Cycle 2 Peer 3-arm: blue.700/500/300."""
        cycle_name, colors = select_cycle(n_series=3, context='equal_weight')
        assert cycle_name == 'peer_3'
        assert colors == CYCLE_PEER_3
        assert colors == [BLUE_700, BLUE_500, BLUE_300]
        assert colors == ['#00507E', '#008ECB', '#76CAF3']

    def test_three_series_no_highlight_returns_peer_3(self):
        cycle_name, colors = select_cycle(n_series=3, has_highlight=False)
        assert cycle_name == 'peer_3'
        assert colors == CYCLE_PEER_3

    def test_three_series_bidirectional_returns_opposing(self):
        cycle_name, colors = select_cycle(n_series=3, context='bidirectional')
        assert cycle_name == 'opposing'
        assert colors == CYCLE_OPPOSING
        assert len(colors) == 3

    def test_three_series_focus_returns_focus(self):
        """v2.3 Cycle 2 Focus with 2 receding arms + 1 focus arm (orange.500)."""
        cycle_name, colors = select_cycle(n_series=3, context='focus')
        assert cycle_name == 'focus'
        assert len(colors) == 3
        # 2 receding (blue.500, blue.300) + 1 focus (orange.500)
        assert colors == [BLUE_500, BLUE_300, ORANGE_500]

    def test_two_series_focus_returns_focus(self):
        """Minimal focus case: 1 receding + 1 focus arm."""
        cycle_name, colors = select_cycle(n_series=2, context='focus')
        assert cycle_name == 'focus'
        assert colors == [BLUE_500, ORANGE_500]

    def test_four_series_focus_returns_full_focus_cycle(self):
        """v2.3 canonical Cycle 2 Focus: 3 receding + 1 focus arm."""
        cycle_name, colors = select_cycle(n_series=4, context='focus')
        assert cycle_name == 'focus'
        assert len(colors) == 4
        # blue.500 / blue.300 / blue.200 + orange.500
        assert colors == [BLUE_500, BLUE_300, BLUE_200, ORANGE_500]

    # --- Four series ---

    def test_four_series_default_returns_multi_category(self):
        cycle_name, colors = select_cycle(n_series=4)
        assert cycle_name == 'multi_category'
        assert colors == CYCLE_MULTI_CATEGORY
        assert colors == [BLUE_800, BLUE_500, BLUE_300, ORANGE_500]
        assert len(colors) == 4

    def test_four_series_equal_weight_returns_peer_4(self):
        """v2.3 Cycle 2 Peer 4-arm: blue.800/600/400/200."""
        cycle_name, colors = select_cycle(n_series=4, context='equal_weight')
        assert cycle_name == 'peer_4'
        assert colors == CYCLE_PEER_4
        assert colors == [BLUE_800, BLUE_600, BLUE_400, BLUE_200]

    def test_four_series_comparison_returns_multi_category(self):
        cycle_name, colors = select_cycle(n_series=4, context='comparison')
        assert cycle_name == 'multi_category'

    # --- Edge cases ---

    def test_zero_series_raises_error(self):
        with pytest.raises(ValueError, match="n_series must be >= 1"):
            select_cycle(n_series=0)

    def test_negative_series_raises_error(self):
        with pytest.raises(ValueError, match="n_series must be >= 1"):
            select_cycle(n_series=-1)

    def test_five_series_raises_error(self):
        with pytest.raises(ValueError, match="Too many series"):
            select_cycle(n_series=5)

    def test_five_series_error_suggests_faceting(self):
        with pytest.raises(ValueError, match="faceting"):
            select_cycle(n_series=5)

    def test_large_series_raises_error(self):
        with pytest.raises(ValueError, match="Too many series"):
            select_cycle(n_series=10)

    # --- Determinism ---

    def test_determinism_same_inputs_same_outputs(self):
        for _ in range(10):
            result1 = select_cycle(n_series=2, context='comparison')
            result2 = select_cycle(n_series=2, context='comparison')
            assert result1 == result2

    def test_all_returned_colors_are_valid_hex(self):
        test_cases = [
            (1, 'comparison'),
            (2, 'comparison'), (2, 'bidirectional'), (2, 'focus'),
            (3, 'comparison'), (3, 'equal_weight'), (3, 'bidirectional'),
            (3, 'focus'),
            (4, 'comparison'), (4, 'equal_weight'), (4, 'focus'),
        ]
        for n_series, context in test_cases:
            _, colors = select_cycle(n_series=n_series, context=context)
            for color in colors:
                assert color.startswith('#')
                assert len(color) == 7


# =============================================================================
# CYCLE STRUCTURE TESTS
# =============================================================================

class TestCycleStructure:
    """Tests that verify v2.3 cycle composition."""

    def test_treatment_control_is_same_hue(self):
        """Cycle 1 is a same-hue lightness hierarchy (all blue family)."""
        assert CYCLE_TREATMENT_CONTROL == [BRAND_BLUE, BLUE_300]

    def test_peer_4_is_blue_ramp(self):
        assert CYCLE_PEER_4 == [BLUE_800, BLUE_600, BLUE_400, BLUE_200]

    def test_peer_3_is_blue_ramp(self):
        assert CYCLE_PEER_3 == [BLUE_700, BLUE_500, BLUE_300]

    def test_opposing_uses_ramp_steps(self):
        """Cycle 3 uses blue.600 + orange.600, not brand.blue + vermilion."""
        assert CYCLE_OPPOSING == [BLUE_600, ORANGE_600, NEUTRAL_300]
        assert '#2DB2E8' not in CYCLE_OPPOSING
        assert '#E8622D' not in CYCLE_OPPOSING

    def test_multi_category_uses_ramp_steps(self):
        """Cycle 4 uses blue.800/500/300 + orange.500 outlier."""
        assert CYCLE_MULTI_CATEGORY == [BLUE_800, BLUE_500, BLUE_300, ORANGE_500]

    def test_focus_receding_is_light_blue(self):
        """Focus receding subset uses blue.500/300/200; default focus is orange.500."""
        assert CYCLE_FOCUS == [BLUE_500, BLUE_300, BLUE_200, ORANGE_500]

    def test_neutrals_only_aliases_peer_3(self):
        """Legacy name routes to Peer 3."""
        assert CYCLE_NEUTRALS_ONLY == CYCLE_PEER_3

    def test_volcano_uses_v23_colors(self):
        assert VOLCANO_COLORS['down'] == BLUE_600
        assert VOLCANO_COLORS['up'] == ORANGE_600
        assert VOLCANO_COLORS['nonsig'] == NEUTRAL_300


# =============================================================================
# RUN_PREFLIGHT TESTS
# =============================================================================

class TestRunPreflight:
    """Tests for the run_preflight() function."""

    def test_brand_styled_figure_passes_all_checks(self, brand_styled_figure):
        results = run_preflight(brand_styled_figure)
        assert all(results.values()), f"Failed: {[k for k, v in results.items() if not v]}"

    def test_returns_dict_with_expected_keys(self, brand_styled_figure):
        results = run_preflight(brand_styled_figure)
        expected_keys = {'white_background', 'spines_removed', 'grid_off', 'axes_black'}
        assert set(results.keys()) == expected_keys

    def test_all_values_are_boolean(self, brand_styled_figure):
        results = run_preflight(brand_styled_figure)
        for key, value in results.items():
            assert isinstance(value, bool)

    def test_default_figure_fails_spines_check(self, default_figure):
        results = run_preflight(default_figure)
        assert not results['spines_removed']

    def test_white_background_check(self):
        set_brand_style('treatment_control')
        fig1, ax1 = plt.subplots()
        fig1.set_facecolor('white')
        assert run_preflight(fig1)['white_background']
        plt.close(fig1)

        fig2, ax2 = plt.subplots()
        fig2.set_facecolor('lightgray')
        assert not run_preflight(fig2)['white_background']
        plt.close(fig2)

    def test_spines_removed_check(self):
        set_brand_style('treatment_control')
        fig1, ax1 = plt.subplots()
        assert run_preflight(fig1)['spines_removed']
        plt.close(fig1)

        plt.rcdefaults()
        fig2, ax2 = plt.subplots()
        assert not run_preflight(fig2)['spines_removed']
        plt.close(fig2)


# =============================================================================
# EXTRACT_FIGURE_COLORS TESTS
# =============================================================================

class TestExtractFigureColors:

    def test_extracts_line_colors(self):
        fig, ax = plt.subplots()
        ax.plot([1, 2], [1, 2], color=BRAND_BLUE)
        ax.plot([1, 2], [2, 1], color=NEUTRAL_900)

        colors = extract_figure_colors(fig)
        assert BRAND_BLUE in colors
        assert NEUTRAL_900 in colors
        plt.close(fig)

    def test_extracts_scatter_colors(self):
        fig, ax = plt.subplots()
        ax.scatter([1, 2], [1, 2], c=ORANGE_600)

        colors = extract_figure_colors(fig)
        assert ORANGE_600 in colors
        plt.close(fig)

    def test_extracts_bar_colors(self):
        fig, ax = plt.subplots()
        ax.bar([1, 2], [3, 4], color=BLUE_500)

        colors = extract_figure_colors(fig)
        assert BLUE_500 in colors
        plt.close(fig)

    def test_converts_named_colors_to_hex(self):
        fig, ax = plt.subplots()
        ax.plot([1, 2], [1, 2], color='red')

        colors = extract_figure_colors(fig)
        assert '#FF0000' in colors
        plt.close(fig)

    def test_returns_uppercase_hex(self):
        fig, ax = plt.subplots()
        ax.plot([1, 2], [1, 2], color='#2db2e8')

        colors = extract_figure_colors(fig)
        for color in colors:
            assert color == color.upper()
            assert color.startswith('#')
        plt.close(fig)

    def test_empty_figure_returns_empty_set(self):
        fig, ax = plt.subplots()
        colors = extract_figure_colors(fig)
        assert len(colors) == 0
        plt.close(fig)


# =============================================================================
# GET_PREFLIGHT_REPORT TESTS
# =============================================================================

class TestGetPreflightReport:

    def test_report_contains_header(self, brand_styled_figure):
        report = get_preflight_report(brand_styled_figure)
        assert "Oligon Brand Preflight Check" in report

    def test_report_shows_pass_for_compliant_figure(self, brand_styled_figure):
        assert "PASS" in get_preflight_report(brand_styled_figure)

    def test_report_shows_fail_for_non_compliant_figure(self, default_figure):
        assert "FAIL" in get_preflight_report(default_figure)

    def test_report_contains_check_names(self, brand_styled_figure):
        report = get_preflight_report(brand_styled_figure)
        for name in ('white_background', 'spines_removed', 'grid_off', 'axes_black'):
            assert name in report

    def test_report_uses_checkmark_for_passed(self, brand_styled_figure):
        assert "✓" in get_preflight_report(brand_styled_figure)

    def test_report_uses_x_for_failed(self, default_figure):
        assert "✗" in get_preflight_report(default_figure)

    def test_report_shows_count(self, brand_styled_figure):
        assert "4/4" in get_preflight_report(brand_styled_figure)


# =============================================================================
# ALLOWED_COLORS TESTS
# =============================================================================

class TestAllowedColors:

    def test_allowed_colors_contains_all_brand_colors(self):
        for color in BRAND_COLORS.values():
            assert color.upper() in ALLOWED_COLORS

    def test_allowed_colors_are_uppercase(self):
        for color in ALLOWED_COLORS:
            assert color == color.upper()

    def test_allowed_colors_are_valid_hex(self):
        for color in ALLOWED_COLORS:
            assert color.startswith('#')
            assert len(color) == 7

    def test_allowed_colors_contains_v23_ramp_steps(self):
        for ramp_color in (BLUE_300, BLUE_600, BLUE_700, ORANGE_500, ORANGE_600,
                           ORANGE_700, NEUTRAL_300, NEUTRAL_700, NEUTRAL_900):
            assert ramp_color in ALLOWED_COLORS

    def test_retired_v4_hexes_are_not_allowed(self):
        """#E8622D, #7D250F, #0F5D7D, #158BBB, #222222 are retired in v2.3."""
        for retired in ('#E8622D', '#7D250F', '#0F5D7D', '#158BBB',
                        '#222222', '#666666', '#999999', '#BDBDBD'):
            assert retired not in ALLOWED_COLORS


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration:

    def test_select_and_apply_cycle_workflow(self):
        cycle_name, colors = select_cycle(n_series=2, context='comparison')
        set_brand_style(cycle_name)

        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9], label='Treatment')
        ax.plot([1, 2, 3], [2, 5, 10], label='Control')

        results = run_preflight(fig)
        assert all(results.values())
        plt.close(fig)

    def test_all_cycles_produce_compliant_figures(self):
        cycle_names = ['treatment_control', 'peer', 'peer_3', 'peer_4',
                       'focus', 'opposing', 'multi_category']
        for cycle_name in cycle_names:
            set_brand_style(cycle_name)
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 4, 9])
            results = run_preflight(fig)
            assert all(results.values()), f"Cycle {cycle_name} failed preflight"
            plt.close(fig)

    def test_extracted_colors_match_selected_cycle(self):
        cycle_name, expected_colors = select_cycle(n_series=2, context='comparison')
        set_brand_style(cycle_name)

        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9])
        ax.plot([1, 2, 3], [2, 5, 10])

        extracted = extract_figure_colors(fig)
        cycle_upper = {c.upper() for c in expected_colors}
        assert extracted & cycle_upper, "No cycle colors found in figure"
        plt.close(fig)


# =============================================================================
# VALIDATE_PALETTE TESTS
# =============================================================================

class TestValidatePalette:

    def test_brand_styled_figure_is_valid(self, brand_styled_figure):
        result = validate_palette(brand_styled_figure)
        assert result['valid']
        assert len(result['violations']) == 0

    def test_returns_expected_keys(self, brand_styled_figure):
        result = validate_palette(brand_styled_figure)
        assert set(result.keys()) >= {'valid', 'used_colors', 'violations', 'allowed_colors'}

    def test_detects_non_brand_color(self):
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9], color='red')

        result = validate_palette(fig)
        assert not result['valid']
        assert '#FF0000' in result['violations']
        plt.close(fig)

    def test_detects_retired_v4_color_as_violation(self):
        """Retired #E8622D vermilion should now fail validation."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9], color='#E8622D')

        result = validate_palette(fig)
        assert not result['valid']
        assert '#E8622D' in result['violations']
        plt.close(fig)

    def test_detects_multiple_violations(self):
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9], color='red')
        ax.plot([1, 2, 3], [2, 5, 10], color='green')

        result = validate_palette(fig)
        assert not result['valid']
        assert len(result['violations']) >= 2
        plt.close(fig)

    def test_allows_white_and_black(self):
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9], color='black')
        ax.axhline(y=2, color='white')

        result = validate_palette(fig)
        assert result['valid']
        plt.close(fig)

    def test_all_brand_colors_are_valid(self):
        for color_name, hex_color in BRAND_COLORS.items():
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 4, 9], color=hex_color)
            result = validate_palette(fig)
            assert result['valid'], f"Brand color {color_name} ({hex_color}) was rejected"
            plt.close(fig)

    def test_used_colors_populated(self):
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9], color=BRAND_BLUE)

        result = validate_palette(fig)
        assert BRAND_BLUE in result['used_colors']
        plt.close(fig)

    def test_allowed_colors_is_copy(self):
        fig, ax = plt.subplots()
        result = validate_palette(fig)
        original_len = len(ALLOWED_COLORS)
        result['allowed_colors'].add('#XXXXXX')
        assert len(ALLOWED_COLORS) == original_len
        plt.close(fig)

    def test_empty_figure_is_valid(self):
        fig, ax = plt.subplots()
        result = validate_palette(fig)
        assert result['valid']
        assert len(result['violations']) == 0
        plt.close(fig)


# =============================================================================
# COUNT_BRAND_BLUE TESTS
# =============================================================================

class TestCountBrandBlue:

    def test_counts_brand_blue_lines(self):
        set_brand_style('treatment_control')
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9], color=BRAND_BLUE)

        result = count_brand_blue(fig)
        assert result['total_count'] == 1
        assert result['per_axes'][0] == 1
        plt.close(fig)

    def test_returns_expected_keys(self):
        fig, ax = plt.subplots()
        result = count_brand_blue(fig)
        assert set(result.keys()) >= {'total_count', 'per_axes', 'compliant', 'violations'}
        plt.close(fig)

    def test_zero_count_for_no_brand_blue(self):
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9], color=NEUTRAL_900)

        result = count_brand_blue(fig)
        assert result['total_count'] == 0
        assert result['compliant']
        plt.close(fig)

    def test_compliant_with_one_element(self):
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9], color=BRAND_BLUE)
        assert count_brand_blue(fig)['compliant']
        plt.close(fig)

    def test_compliant_with_two_elements(self):
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9], color=BRAND_BLUE)
        ax.plot([1, 2, 3], [2, 5, 10], color=BRAND_BLUE)

        result = count_brand_blue(fig)
        assert result['total_count'] == 2
        assert result['compliant']
        plt.close(fig)

    def test_non_compliant_with_three_elements(self):
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9], color=BRAND_BLUE)
        ax.plot([1, 2, 3], [2, 5, 10], color=BRAND_BLUE)
        ax.plot([1, 2, 3], [3, 6, 11], color=BRAND_BLUE)

        result = count_brand_blue(fig)
        assert result['total_count'] == 3
        assert not result['compliant']
        assert 0 in result['violations']
        plt.close(fig)

    def test_counts_scatter_as_single_element(self):
        fig, ax = plt.subplots()
        ax.scatter([1, 2, 3], [1, 4, 9], c=BRAND_BLUE)
        assert count_brand_blue(fig)['total_count'] == 1
        plt.close(fig)

    def test_counts_bar_elements(self):
        fig, ax = plt.subplots()
        ax.bar([1, 2], [3, 4], color=BRAND_BLUE)
        assert count_brand_blue(fig)['total_count'] == 2
        plt.close(fig)

    def test_multi_axes_counts_separately(self):
        fig, (ax1, ax2) = plt.subplots(1, 2)
        ax1.plot([1, 2], [1, 2], color=BRAND_BLUE)
        ax2.plot([1, 2], [1, 2], color=BRAND_BLUE)
        ax2.plot([1, 2], [2, 3], color=BRAND_BLUE)

        result = count_brand_blue(fig)
        assert result['per_axes'][0] == 1
        assert result['per_axes'][1] == 2
        assert result['total_count'] == 3
        assert result['compliant']
        plt.close(fig)

    def test_violation_in_one_axes_only(self):
        fig, (ax1, ax2) = plt.subplots(1, 2)
        ax1.plot([1, 2], [1, 2], color=BRAND_BLUE)
        ax2.plot([1, 2], [1, 2], color=BRAND_BLUE)
        ax2.plot([1, 2], [2, 3], color=BRAND_BLUE)
        ax2.plot([1, 2], [3, 4], color=BRAND_BLUE)

        result = count_brand_blue(fig)
        assert not result['compliant']
        assert 0 not in result['violations']
        assert 1 in result['violations']
        plt.close(fig)

    def test_case_insensitive_detection(self):
        fig, ax = plt.subplots()
        ax.plot([1, 2], [1, 2], color='#2db2e8')
        assert count_brand_blue(fig)['total_count'] == 1
        plt.close(fig)

    def test_empty_figure_is_compliant(self):
        fig, ax = plt.subplots()
        result = count_brand_blue(fig)
        assert result['total_count'] == 0
        assert result['compliant']
        plt.close(fig)


# =============================================================================
# GET_BRAND_COMPLIANCE_REPORT TESTS
# =============================================================================

class TestGetBrandComplianceReport:

    def test_report_contains_all_sections(self, brand_styled_figure):
        report = get_brand_compliance_report(brand_styled_figure)
        for section in ('PREFLIGHT CHECKS:', 'PALETTE VALIDATION:',
                        'BRAND BLUE USAGE:', 'OVERALL:'):
            assert section in report

    def test_report_contains_header(self, brand_styled_figure):
        assert "Oligon Brand Compliance Report" in get_brand_compliance_report(brand_styled_figure)

    def test_compliant_figure_passes_overall(self, brand_styled_figure):
        assert "OVERALL: PASS" in get_brand_compliance_report(brand_styled_figure)

    def test_non_compliant_palette_shows_violations(self):
        set_brand_style('treatment_control')
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9], color='red')

        report = get_brand_compliance_report(fig)
        assert "Non-brand colors detected" in report
        assert "#FF0000" in report
        assert "OVERALL: FAIL" in report
        plt.close(fig)

    def test_excess_brand_blue_shows_in_report(self):
        set_brand_style('treatment_control')
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9], color=BRAND_BLUE)
        ax.plot([1, 2, 3], [2, 5, 10], color=BRAND_BLUE)
        ax.plot([1, 2, 3], [3, 6, 11], color=BRAND_BLUE)

        report = get_brand_compliance_report(fig)
        assert "Exceeds limit" in report
        assert "OVERALL: FAIL" in report
        plt.close(fig)

    def test_preflight_failure_shows_in_report(self, default_figure):
        report = get_brand_compliance_report(default_figure)
        assert "✗" in report
        assert "OVERALL: FAIL" in report

    def test_shows_total_brand_blue_count(self, brand_styled_figure):
        assert "Total elements:" in get_brand_compliance_report(brand_styled_figure)


# =============================================================================
# FULL COMPLIANCE INTEGRATION
# =============================================================================

class TestFullCompliance:

    def test_full_compliance_workflow(self):
        cycle_name, _ = select_cycle(n_series=2, context='comparison')
        set_brand_style(cycle_name)

        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9], label='Treatment')
        ax.plot([1, 2, 3], [2, 5, 10], label='Control')

        preflight = run_preflight(fig)
        palette = validate_palette(fig)
        brand_blue = count_brand_blue(fig)

        assert all(preflight.values())
        assert palette['valid']
        assert brand_blue['compliant']
        plt.close(fig)

    def test_compliance_report_matches_individual_checks(self):
        set_brand_style('treatment_control')
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9])

        preflight = run_preflight(fig)
        palette = validate_palette(fig)
        brand_blue = count_brand_blue(fig)

        report = get_brand_compliance_report(fig)
        all_pass = all(preflight.values()) and palette['valid'] and brand_blue['compliant']
        assert ("OVERALL: PASS" in report) == all_pass

        plt.close(fig)

    def test_all_cycles_pass_full_compliance(self):
        cycle_names = ['treatment_control', 'peer', 'peer_3', 'peer_4',
                       'focus', 'opposing', 'multi_category']
        for cycle_name in cycle_names:
            set_brand_style(cycle_name)
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 4, 9])

            preflight = run_preflight(fig)
            palette = validate_palette(fig)
            brand_blue = count_brand_blue(fig)

            assert all(preflight.values()), f"{cycle_name} failed preflight"
            assert palette['valid'], f"{cycle_name} failed palette"
            assert brand_blue['compliant'], f"{cycle_name} failed brand blue"
            plt.close(fig)
