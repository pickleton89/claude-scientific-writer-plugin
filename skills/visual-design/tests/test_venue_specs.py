"""Tests for venue_specs module."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.venue_specs import (
    get_venue_specs,
    normalize_venue_name,
    get_column_width,
    list_supported_venues,
    VENUE_SPECS,
    DEFAULT_SPECS,
)


class TestNormalizeVenueName:
    """Tests for venue name normalization."""

    def test_exact_match(self):
        """Exact venue names should return unchanged."""
        assert normalize_venue_name("nature") == "nature"
        assert normalize_venue_name("science") == "science"
        assert normalize_venue_name("cell") == "cell"

    def test_case_insensitive(self):
        """Venue names should be case-insensitive."""
        assert normalize_venue_name("Nature") == "nature"
        assert normalize_venue_name("SCIENCE") == "science"
        assert normalize_venue_name("Cell") == "cell"

    def test_whitespace_handling(self):
        """Leading/trailing whitespace should be stripped."""
        assert normalize_venue_name("  nature  ") == "nature"
        assert normalize_venue_name("\tscience\n") == "science"

    def test_alias_mapping(self):
        """Common aliases should map to canonical names."""
        assert normalize_venue_name("nature communications") == "nature"
        assert normalize_venue_name("nature medicine") == "nature"
        assert normalize_venue_name("nat commun") == "nature"
        assert normalize_venue_name("science advances") == "science"
        assert normalize_venue_name("cell reports") == "cell"
        assert normalize_venue_name("plos one") == "plos"

    def test_first_word_fallback(self):
        """Unknown multi-word venues should try first word."""
        assert normalize_venue_name("nature unknown journal") == "nature"
        assert normalize_venue_name("science something") == "science"

    def test_unknown_venue_returns_default(self):
        """Completely unknown venues should return 'default'."""
        assert normalize_venue_name("unknown journal") == "default"
        assert normalize_venue_name("random") == "default"
        assert normalize_venue_name("") == "default"


class TestGetVenueSpecs:
    """Tests for venue specification retrieval."""

    def test_known_venues_return_complete_specs(self):
        """Known venues should return complete specification dicts."""
        specs = get_venue_specs("nature")

        # Check required keys
        assert "single_col_mm" in specs
        assert "double_col_mm" in specs
        assert "min_dpi" in specs
        assert "preferred_format" in specs
        assert "panel_label_case" in specs
        assert "venue" in specs
        assert "canonical" in specs

    def test_nature_specs_correct(self):
        """Nature specs should match known values."""
        specs = get_venue_specs("nature")
        assert specs["single_col_mm"] == 89
        assert specs["double_col_mm"] == 183
        assert specs["min_dpi"] == 300
        assert specs["panel_label_case"] == "lower"
        assert "pdf" in specs["preferred_format"]

    def test_science_specs_correct(self):
        """Science specs should match known values."""
        specs = get_venue_specs("science")
        assert specs["single_col_mm"] == 55
        assert specs["double_col_mm"] == 175
        assert specs["panel_label_case"] == "upper"

    def test_unknown_venue_returns_defaults(self):
        """Unknown venues should return default specs."""
        specs = get_venue_specs("unknown journal")
        assert specs["canonical"] == "default"
        assert specs["single_col_mm"] == DEFAULT_SPECS["single_col_mm"]
        assert specs["venue"] == "unknown journal"

    def test_preserves_original_venue_name(self):
        """Original venue name should be preserved in output."""
        specs = get_venue_specs("Nature Medicine")
        assert specs["venue"] == "Nature Medicine"
        assert specs["canonical"] == "nature"


class TestGetColumnWidth:
    """Tests for column width helper."""

    def test_single_column(self):
        """Single column width should match venue specs."""
        result = get_column_width("nature", "single")
        assert result["width_mm"] == 89
        assert result["width_in"] == 3.5
        assert result["column_type"] == "single"

    def test_double_column(self):
        """Double column width should match venue specs."""
        result = get_column_width("nature", "double")
        assert result["width_mm"] == 183
        assert result["width_in"] == 7.2
        assert result["column_type"] == "double"

    def test_default_is_single(self):
        """Default column type should be single."""
        result = get_column_width("nature")
        assert result["column_type"] == "single"


class TestListSupportedVenues:
    """Tests for venue listing."""

    def test_returns_list(self):
        """Should return a list of strings."""
        venues = list_supported_venues()
        assert isinstance(venues, list)
        assert all(isinstance(v, str) for v in venues)

    def test_contains_major_journals(self):
        """Should include major scientific journals."""
        venues = list_supported_venues()
        assert "nature" in venues
        assert "science" in venues
        assert "cell" in venues
        assert "pnas" in venues


class TestVenueSpecsDataIntegrity:
    """Tests for data integrity of venue specifications."""

    def test_all_venues_have_required_fields(self):
        """All venue specs should have required fields."""
        required_fields = [
            "single_col_mm",
            "double_col_mm",
            "min_dpi",
            "preferred_format",
            "panel_label_case",
        ]

        for venue, specs in VENUE_SPECS.items():
            for field in required_fields:
                assert field in specs, f"{venue} missing {field}"

    def test_dimensions_are_positive(self):
        """All dimensions should be positive numbers."""
        for venue, specs in VENUE_SPECS.items():
            assert specs["single_col_mm"] > 0, f"{venue} single_col_mm invalid"
            assert specs["double_col_mm"] > 0, f"{venue} double_col_mm invalid"
            assert specs["min_dpi"] > 0, f"{venue} min_dpi invalid"

    def test_double_column_wider_than_single(self):
        """Double column should always be wider than single."""
        for venue, specs in VENUE_SPECS.items():
            assert specs["double_col_mm"] > specs["single_col_mm"], \
                f"{venue} double column not wider than single"

    def test_preferred_formats_are_lists(self):
        """Preferred formats should be non-empty lists."""
        for venue, specs in VENUE_SPECS.items():
            assert isinstance(specs["preferred_format"], list), \
                f"{venue} preferred_format not a list"
            assert len(specs["preferred_format"]) > 0, \
                f"{venue} has no preferred formats"

    def test_panel_label_case_valid(self):
        """Panel label case should be 'upper' or 'lower'."""
        for venue, specs in VENUE_SPECS.items():
            assert specs["panel_label_case"] in ["upper", "lower"], \
                f"{venue} has invalid panel_label_case"
