"""Tests for venue_resolver module."""

from __future__ import annotations

import sys
from pathlib import Path


# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from venue_resolver import (  # noqa: E402
    VenueResolver,
    resolve_venue,
    resolve_venue_id,
)


class TestVenueResolver:
    """Tests for VenueResolver class."""

    def test_exact_match(self) -> None:
        """Test exact ID match returns confidence 1.0."""
        result = resolve_venue("nature")
        assert result.venue_id == "nature"
        assert result.confidence == 1.0

    def test_exact_match_case_insensitive(self) -> None:
        """Test exact match is case insensitive."""
        result = resolve_venue("NATURE")
        assert result.venue_id == "nature"
        assert result.confidence == 1.0

        result = resolve_venue("NeurIPS")
        assert result.venue_id == "neurips"

    def test_alias_match(self) -> None:
        """Test alias matching."""
        result = resolve_venue("nature paper")
        assert result.venue_id == "nature"
        assert result.confidence == 1.0

        result = resolve_venue("neurips conference")
        assert result.venue_id == "neurips"

    def test_year_suffix_removal(self) -> None:
        """Test year suffixes are handled."""
        result = resolve_venue("NeurIPS 2024")
        assert result.venue_id == "neurips"

        result = resolve_venue("ICML 2025")
        assert result.venue_id == "icml"

    def test_fuzzy_match_typo(self) -> None:
        """Test fuzzy matching handles typos."""
        result = resolve_venue("natur")  # Missing 'e'
        assert result.venue_id == "nature"
        assert 0.7 <= result.confidence < 1.0

    def test_fuzzy_match_partial(self) -> None:
        """Test fuzzy matching on partial names."""
        result = resolve_venue("neural information")
        assert result.venue_id == "neurips"

    def test_no_match_below_threshold(self) -> None:
        """Test no match when below threshold."""
        result = resolve_venue("xyzzy journal", threshold=0.6)
        assert result.venue_id is None
        assert result.confidence < 0.6

    def test_alternatives_provided(self) -> None:
        """Test alternatives are provided for low confidence matches."""
        result = resolve_venue("xyzzy journal")
        assert result.venue_id is None
        assert len(result.alternatives) > 0

    def test_resolve_venue_id_convenience(self) -> None:
        """Test resolve_venue_id convenience function."""
        venue_id = resolve_venue_id("nature")
        assert venue_id == "nature"

        venue_id = resolve_venue_id("xyzzy journal")
        assert venue_id is None

    def test_common_word_removal(self) -> None:
        """Test common words are removed from query."""
        # "paper", "article", "journal" should be stripped
        result = resolve_venue("nature article")
        assert result.venue_id == "nature"

        result = resolve_venue("neurips paper submission")
        assert result.venue_id == "neurips"


class TestResolverThresholds:
    """Tests for confidence threshold behavior."""

    def test_high_threshold(self) -> None:
        """Test high threshold requires better matches."""
        # With high threshold, fuzzy matches may fail
        result = resolve_venue("natur", threshold=0.95)
        # May or may not match depending on exact similarity
        if result.venue_id is not None:
            assert result.confidence >= 0.95

    def test_low_threshold(self) -> None:
        """Test low threshold accepts worse matches."""
        result = resolve_venue("nat", threshold=0.3)
        # Low threshold may match
        if result.venue_id is not None:
            assert result.confidence >= 0.3

    def test_default_threshold(self) -> None:
        """Test default threshold is reasonable."""
        resolver = VenueResolver()
        result = resolver.resolve("nature")
        assert result.venue_id == "nature"


class TestJournalResolution:
    """Tests for journal venue resolution."""

    def test_nature_variations(self) -> None:
        """Test various Nature references."""
        queries = ["nature", "Nature", "NATURE", "nature journal", "nature paper"]
        for query in queries:
            result = resolve_venue(query)
            assert result.venue_id == "nature", f"Failed for query: {query}"

    def test_science_variations(self) -> None:
        """Test various Science references."""
        queries = ["science", "Science", "science journal"]
        for query in queries:
            result = resolve_venue(query)
            assert result.venue_id == "science", f"Failed for query: {query}"

    def test_plos_one_variations(self) -> None:
        """Test various PLOS ONE references."""
        queries = ["plos one", "plos", "PLOS ONE"]
        for query in queries:
            result = resolve_venue(query)
            assert result.venue_id == "plos_one", f"Failed for query: {query}"


class TestConferenceResolution:
    """Tests for conference venue resolution."""

    def test_neurips_variations(self) -> None:
        """Test various NeurIPS references."""
        queries = ["neurips", "NeurIPS", "nips", "neurips 2024", "neurips conference"]
        for query in queries:
            result = resolve_venue(query)
            assert result.venue_id == "neurips", f"Failed for query: {query}"

    def test_icml_variations(self) -> None:
        """Test various ICML references."""
        queries = ["icml", "ICML", "icml 2024"]
        for query in queries:
            result = resolve_venue(query)
            assert result.venue_id == "icml", f"Failed for query: {query}"

    def test_cvpr_variations(self) -> None:
        """Test various CVPR references."""
        queries = ["cvpr", "CVPR", "cvpr 2024"]
        for query in queries:
            result = resolve_venue(query)
            assert result.venue_id == "cvpr", f"Failed for query: {query}"


class TestMedicalJournalResolution:
    """Tests for medical journal resolution."""

    def test_nejm_variations(self) -> None:
        """Test various NEJM references."""
        queries = ["nejm", "NEJM", "new england journal"]
        for query in queries:
            result = resolve_venue(query)
            assert result.venue_id == "nejm", f"Failed for query: {query}"

    def test_lancet_variations(self) -> None:
        """Test various Lancet references."""
        queries = ["lancet", "the lancet", "Lancet"]
        for query in queries:
            result = resolve_venue(query)
            assert result.venue_id == "lancet", f"Failed for query: {query}"

    def test_jama_variations(self) -> None:
        """Test various JAMA references."""
        queries = ["jama", "JAMA"]
        for query in queries:
            result = resolve_venue(query)
            assert result.venue_id == "jama", f"Failed for query: {query}"


class TestGrantResolution:
    """Tests for grant venue resolution."""

    def test_nsf_variations(self) -> None:
        """Test various NSF references."""
        queries = ["nsf", "NSF", "nsf grant", "nsf proposal"]
        for query in queries:
            result = resolve_venue(query)
            assert result.venue_id == "nsf", f"Failed for query: {query}"

    def test_nih_variations(self) -> None:
        """Test various NIH references."""
        queries = ["nih", "NIH", "nih grant", "r01", "nih r01"]
        for query in queries:
            result = resolve_venue(query)
            assert result.venue_id == "nih", f"Failed for query: {query}"


class TestResolveResult:
    """Tests for ResolveResult dataclass."""

    def test_result_structure(self) -> None:
        """Test ResolveResult has expected fields."""
        result = resolve_venue("nature")
        assert hasattr(result, "venue_id")
        assert hasattr(result, "confidence")
        assert hasattr(result, "matched_alias")
        assert hasattr(result, "alternatives")

    def test_alternatives_structure(self) -> None:
        """Test alternatives are tuples of (venue_id, score)."""
        result = resolve_venue("xyz")
        for alt in result.alternatives:
            assert isinstance(alt, tuple)
            assert len(alt) == 2
            assert isinstance(alt[0], str)
            assert isinstance(alt[1], float)
