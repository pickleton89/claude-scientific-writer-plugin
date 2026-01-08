"""Tests for venue_database module."""

from __future__ import annotations

import sys
from pathlib import Path


# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from venue_database import (  # noqa: E402
    get_database,
    get_venue,
    list_venues,
    list_venues_by_type,
    resolve_venue,
)


class TestVenueDatabase:
    """Tests for VenueDatabase class."""

    def test_load_database(self) -> None:
        """Test that database loads successfully."""
        db = get_database()
        assert db is not None
        assert len(db.list_all()) > 0

    def test_get_venue_by_id(self) -> None:
        """Test getting venue by canonical ID."""
        venue = get_venue("nature")
        assert venue is not None
        assert venue.id == "nature"
        assert venue.full_name == "Nature"
        assert venue.type == "journal"

    def test_get_venue_not_found(self) -> None:
        """Test getting non-existent venue returns None."""
        venue = get_venue("nonexistent_venue")
        assert venue is None

    def test_venue_spec_structure(self) -> None:
        """Test that VenueSpec has all expected fields."""
        venue = get_venue("nature")
        assert venue is not None

        # Check main fields
        assert isinstance(venue.id, str)
        assert isinstance(venue.full_name, str)
        assert isinstance(venue.type, str)
        assert isinstance(venue.aliases, list)

        # Check nested specs
        assert venue.formatting is not None
        assert venue.abstract is not None
        assert venue.style is not None
        assert venue.requirements is not None

    def test_formatting_spec(self) -> None:
        """Test formatting specification structure."""
        venue = get_venue("nature")
        assert venue is not None

        fmt = venue.formatting
        assert fmt.citation_style == "superscript"
        assert fmt.format == "single-column"
        assert fmt.font_size == 12
        assert fmt.word_limit == 3000

    def test_abstract_spec(self) -> None:
        """Test abstract specification structure."""
        venue = get_venue("nature")
        assert venue is not None

        abstract = venue.abstract
        assert abstract.style == "flowing"
        assert abstract.max_words == 200
        assert "significance" in abstract.required_elements

    def test_requirements_spec(self) -> None:
        """Test requirements specification structure."""
        neurips = get_venue("neurips")
        assert neurips is not None

        reqs = neurips.requirements
        assert reqs.anonymization is True
        assert reqs.contribution_list is True
        assert reqs.ablation_studies is True

    def test_list_all_venues(self) -> None:
        """Test listing all venues."""
        venues = list_venues()
        assert len(venues) >= 10  # We have at least 10 venues
        assert "nature" in venues
        assert "neurips" in venues
        assert "nsf" in venues

    def test_list_venues_by_type_journal(self) -> None:
        """Test filtering venues by journal type."""
        journals = list_venues_by_type("journal")
        assert "nature" in journals
        assert "science" in journals
        assert "neurips" not in journals  # conference
        assert "nsf" not in journals  # grant

    def test_list_venues_by_type_conference(self) -> None:
        """Test filtering venues by conference type."""
        conferences = list_venues_by_type("conference")
        assert "neurips" in conferences
        assert "icml" in conferences
        assert "cvpr" in conferences
        assert "nature" not in conferences

    def test_list_venues_by_type_grant(self) -> None:
        """Test filtering venues by grant type."""
        grants = list_venues_by_type("grant")
        assert "nsf" in grants
        assert "nih" in grants
        assert "nature" not in grants

    def test_resolve_venue_exact_match(self) -> None:
        """Test resolving venue by exact ID."""
        result = resolve_venue("nature")
        assert result == "nature"

    def test_resolve_venue_alias(self) -> None:
        """Test resolving venue by alias."""
        result = resolve_venue("nature paper")
        assert result == "nature"

    def test_resolve_venue_case_insensitive(self) -> None:
        """Test venue resolution is case insensitive."""
        result = resolve_venue("NATURE")
        assert result == "nature"

        result = resolve_venue("NeurIPS")
        assert result == "neurips"

    def test_resolve_venue_not_found(self) -> None:
        """Test resolving non-existent venue returns None."""
        result = resolve_venue("xyzzy journal")
        assert result is None


class TestVenueTypes:
    """Tests for different venue types."""

    def test_journal_venues(self) -> None:
        """Test journal venue specifications."""
        nature = get_venue("nature")
        assert nature is not None
        assert nature.type == "journal"
        assert nature.discipline == "multidisciplinary"

        nejm = get_venue("nejm")
        assert nejm is not None
        assert nejm.type == "journal"
        assert nejm.discipline == "medical"

    def test_conference_venues(self) -> None:
        """Test conference venue specifications."""
        neurips = get_venue("neurips")
        assert neurips is not None
        assert neurips.type == "conference"
        assert neurips.requirements.anonymization is True

        cvpr = get_venue("cvpr")
        assert cvpr is not None
        assert cvpr.type == "conference"

    def test_grant_venues(self) -> None:
        """Test grant venue specifications."""
        nsf = get_venue("nsf")
        assert nsf is not None
        assert nsf.type == "grant"
        assert nsf.formatting.page_limit == 15

        nih = get_venue("nih")
        assert nih is not None
        assert nih.type == "grant"
        assert nih.formatting.page_limit == 12


class TestMedicalJournals:
    """Tests for medical journal specifications."""

    def test_structured_abstract(self) -> None:
        """Test medical journals require structured abstracts."""
        nejm = get_venue("nejm")
        assert nejm is not None
        assert nejm.abstract.style == "structured"
        assert nejm.abstract.structured_sections is not None
        assert "Background" in nejm.abstract.structured_sections
        assert "Methods" in nejm.abstract.structured_sections

    def test_lancet_abstract_sections(self) -> None:
        """Test Lancet has specific abstract sections."""
        lancet = get_venue("lancet")
        assert lancet is not None
        assert lancet.abstract.style == "structured"
        sections = lancet.abstract.structured_sections
        assert sections is not None
        assert "Findings" in sections  # Lancet-specific
        assert "Interpretation" in sections

    def test_jama_abstract_sections(self) -> None:
        """Test JAMA has specific abstract sections."""
        jama = get_venue("jama")
        assert jama is not None
        sections = jama.abstract.structured_sections
        assert sections is not None
        assert "Importance" in sections  # JAMA-specific


class TestMLConferences:
    """Tests for ML conference specifications."""

    def test_anonymization_required(self) -> None:
        """Test ML conferences require anonymization."""
        for conf_id in ["neurips", "icml", "cvpr"]:
            conf = get_venue(conf_id)
            assert conf is not None
            assert conf.requirements.anonymization is True

    def test_contribution_list_required(self) -> None:
        """Test ML conferences expect contribution lists."""
        for conf_id in ["neurips", "icml", "cvpr"]:
            conf = get_venue(conf_id)
            assert conf is not None
            assert conf.requirements.contribution_list is True

    def test_page_limits(self) -> None:
        """Test ML conferences have page limits."""
        neurips = get_venue("neurips")
        assert neurips is not None
        assert neurips.formatting.page_limit == 8

        icml = get_venue("icml")
        assert icml is not None
        assert icml.formatting.page_limit == 8


class TestAliases:
    """Tests for venue alias resolution."""

    def test_nature_aliases(self) -> None:
        """Test Nature aliases."""
        db = get_database()
        assert db.resolve("nature paper") == "nature"
        assert db.resolve("nature journal") == "nature"

    def test_neurips_aliases(self) -> None:
        """Test NeurIPS aliases."""
        db = get_database()
        assert db.resolve("neurips") == "neurips"
        assert db.resolve("neurips 2024") == "neurips"
        assert db.resolve("nips") == "neurips"

    def test_nih_aliases(self) -> None:
        """Test NIH aliases."""
        db = get_database()
        assert db.resolve("nih") == "nih"
        assert db.resolve("nih grant") == "nih"
        assert db.resolve("r01") == "nih"
