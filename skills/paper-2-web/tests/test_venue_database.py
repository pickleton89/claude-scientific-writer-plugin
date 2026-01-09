"""Tests for venue_database module."""

import pytest
from lib.venue_database import (
    PosterSpecs,
    VENUE_POSTER_SPECS,
    get_poster_specs,
    list_supported_venues,
    list_venues_by_category,
    get_poster_pixel_dimensions,
    find_similar_venues,
)


class TestPosterSpecs:
    """Tests for PosterSpecs dataclass."""

    def test_poster_specs_creation(self):
        """Test creating PosterSpecs instance."""
        specs = PosterSpecs(48, 36, "landscape", 300, "Test")
        assert specs.width == 48
        assert specs.height == 36
        assert specs.orientation == "landscape"
        assert specs.dpi == 300
        assert specs.notes == "Test"

    def test_poster_specs_frozen(self):
        """Test that PosterSpecs is immutable."""
        specs = PosterSpecs(48, 36, "landscape")
        with pytest.raises(AttributeError):
            specs.width = 60

    def test_aspect_ratio(self):
        """Test aspect ratio calculation."""
        landscape = PosterSpecs(48, 36, "landscape")
        assert landscape.aspect_ratio == pytest.approx(48 / 36)

        portrait = PosterSpecs(36, 48, "portrait")
        assert portrait.aspect_ratio == pytest.approx(36 / 48)

        square = PosterSpecs(45, 45, "square")
        assert square.aspect_ratio == pytest.approx(1.0)

    def test_get_pixel_dimensions_default_dpi(self):
        """Test pixel dimensions with default DPI."""
        specs = PosterSpecs(48, 36, "landscape", 300)
        width_px, height_px = specs.get_pixel_dimensions()
        assert width_px == 48 * 300
        assert height_px == 36 * 300

    def test_get_pixel_dimensions_custom_dpi(self):
        """Test pixel dimensions with custom DPI."""
        specs = PosterSpecs(48, 36, "landscape", 300)
        width_px, height_px = specs.get_pixel_dimensions(150)
        assert width_px == 48 * 150
        assert height_px == 36 * 150


class TestVenueDatabase:
    """Tests for venue database lookups."""

    def test_venue_specs_has_standard(self):
        """Test that standard fallback exists."""
        assert "standard" in VENUE_POSTER_SPECS

    def test_venue_specs_has_major_conferences(self):
        """Test major conferences are included."""
        major_venues = ["neurips", "icml", "cvpr", "acl", "ismb"]
        for venue in major_venues:
            assert venue in VENUE_POSTER_SPECS, f"Missing venue: {venue}"

    def test_get_poster_specs_exact_match(self):
        """Test exact venue name match."""
        specs = get_poster_specs("neurips")
        assert specs.width == 48
        assert specs.height == 36
        assert specs.orientation == "landscape"

    def test_get_poster_specs_case_insensitive(self):
        """Test case-insensitive lookup."""
        specs1 = get_poster_specs("neurips")
        specs2 = get_poster_specs("NeurIPS")
        specs3 = get_poster_specs("NEURIPS")
        assert specs1 == specs2 == specs3

    def test_get_poster_specs_with_spaces(self):
        """Test lookup with spaces in name."""
        specs = get_poster_specs("aps march")
        assert specs.width == 48

    def test_get_poster_specs_with_hyphens(self):
        """Test lookup with hyphens in name."""
        specs = get_poster_specs("a0-portrait")
        assert specs.width == 33.1
        assert specs.orientation == "portrait"

    def test_get_poster_specs_unknown_fallback(self):
        """Test fallback to standard for unknown venues."""
        specs = get_poster_specs("unknown_conference_2024")
        standard = VENUE_POSTER_SPECS["standard"]
        assert specs == standard

    def test_cvpr_larger_format(self):
        """Test CVPR has larger format."""
        specs = get_poster_specs("cvpr")
        assert specs.width == 60
        assert specs.height == 40

    def test_sfn_square_format(self):
        """Test SfN has square format."""
        specs = get_poster_specs("sfn")
        assert specs.width == 45
        assert specs.height == 45
        assert specs.orientation == "square"

    def test_recomb_portrait_format(self):
        """Test RECOMB has portrait format."""
        specs = get_poster_specs("recomb")
        assert specs.width == 36
        assert specs.height == 48
        assert specs.orientation == "portrait"

    def test_iso_paper_sizes(self):
        """Test ISO paper sizes are included."""
        a0_portrait = get_poster_specs("a0_portrait")
        assert a0_portrait.width == 33.1
        assert a0_portrait.height == 46.8

        a0_landscape = get_poster_specs("a0_landscape")
        assert a0_landscape.width == 46.8
        assert a0_landscape.height == 33.1


class TestVenueListFunctions:
    """Tests for venue listing functions."""

    def test_list_supported_venues_not_empty(self):
        """Test that venue list is not empty."""
        venues = list_supported_venues()
        assert len(venues) > 0

    def test_list_supported_venues_sorted(self):
        """Test that venue list is sorted."""
        venues = list_supported_venues()
        assert venues == sorted(venues)

    def test_list_supported_venues_excludes_standard(self):
        """Test that 'standard' is excluded from list."""
        venues = list_supported_venues()
        assert "standard" not in venues

    def test_list_venues_by_category_has_categories(self):
        """Test that category listing has expected categories."""
        categories = list_venues_by_category()
        expected = ["ml_ai", "computer_vision", "nlp", "biology", "neuroscience"]
        for cat in expected:
            assert cat in categories, f"Missing category: {cat}"

    def test_list_venues_by_category_venues_exist(self):
        """Test that all categorized venues exist in database."""
        categories = list_venues_by_category()
        for cat_name, venues in categories.items():
            for venue in venues:
                assert venue in VENUE_POSTER_SPECS, f"Missing venue: {venue}"


class TestPixelDimensions:
    """Tests for get_poster_pixel_dimensions function."""

    def test_pixel_dimensions_neurips(self):
        """Test pixel dimensions for NeurIPS."""
        width, height = get_poster_pixel_dimensions("neurips")
        assert width == 48 * 300
        assert height == 36 * 300

    def test_pixel_dimensions_custom_dpi(self):
        """Test custom DPI."""
        width, height = get_poster_pixel_dimensions("neurips", dpi=150)
        assert width == 48 * 150
        assert height == 36 * 150


class TestSimilarVenues:
    """Tests for find_similar_venues function."""

    def test_find_similar_venues_exact(self):
        """Test finding exact matches."""
        matches = find_similar_venues("neurips")
        assert "neurips" in matches

    def test_find_similar_venues_partial(self):
        """Test finding partial matches."""
        matches = find_similar_venues("aps")
        assert any("aps" in m for m in matches)

    def test_find_similar_venues_limit(self):
        """Test result limiting."""
        matches = find_similar_venues("a", limit=3)
        assert len(matches) <= 3

    def test_find_similar_venues_no_match(self):
        """Test no matches returns empty list."""
        matches = find_similar_venues("xyz123nonexistent")
        assert matches == []


class TestDeterminism:
    """Tests for deterministic behavior."""

    def test_same_input_same_output(self):
        """Test that same input always gives same output."""
        results = [get_poster_specs("neurips") for _ in range(10)]
        assert all(r == results[0] for r in results)

    def test_venue_list_deterministic(self):
        """Test that venue list is deterministic."""
        list1 = list_supported_venues()
        list2 = list_supported_venues()
        assert list1 == list2

    def test_pixel_dimensions_deterministic(self):
        """Test that pixel dimensions are deterministic."""
        dims1 = get_poster_pixel_dimensions("cvpr")
        dims2 = get_poster_pixel_dimensions("cvpr")
        assert dims1 == dims2
