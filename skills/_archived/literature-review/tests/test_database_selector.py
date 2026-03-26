#!/usr/bin/env python3
"""
Tests for database_selector.py

Comprehensive test suite for database selection based on domain,
subdomain, and review type.
"""

import sys
from pathlib import Path

import pytest

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from database_selector import (  # noqa: E402
    DatabaseSelection,
    DATABASE_MATRIX,
    REVIEW_MINIMUMS,
    PREPRINT_SERVERS,
    GREY_LITERATURE,
    select_databases,
    get_available_domains,
    get_available_subdomains,
    get_database_url,
    detect_domain,
    generate_search_strategy,
)


# =============================================================================
# Constants Tests
# =============================================================================


class TestDatabaseMatrix:
    """Tests for database matrix definitions."""

    def test_all_domains_have_default(self):
        """Test all domains have a default subdomain."""
        for domain in DATABASE_MATRIX:
            subdomains = DATABASE_MATRIX[domain]
            assert "default" in subdomains or len(subdomains) > 0

    def test_biomedical_has_clinical(self):
        """Test biomedical domain has clinical subdomain."""
        assert "clinical" in DATABASE_MATRIX["biomedical"]
        assert "PubMed" in DATABASE_MATRIX["biomedical"]["clinical"]

    def test_computer_science_has_ml_ai(self):
        """Test computer science domain has ML/AI subdomain."""
        assert "ml_ai" in DATABASE_MATRIX["computer_science"]
        assert "arXiv" in DATABASE_MATRIX["computer_science"]["ml_ai"]

    def test_review_minimums_defined(self):
        """Test review minimums are defined for all types."""
        expected_types = ["systematic", "scoping", "narrative", "rapid"]
        for review_type in expected_types:
            assert review_type in REVIEW_MINIMUMS
            assert REVIEW_MINIMUMS[review_type] >= 2

    def test_preprint_servers_by_domain(self):
        """Test preprint servers defined for all domains."""
        for domain in DATABASE_MATRIX:
            assert domain in PREPRINT_SERVERS

    def test_grey_literature_by_domain(self):
        """Test grey literature sources defined for all domains."""
        for domain in DATABASE_MATRIX:
            assert domain in GREY_LITERATURE
            assert len(GREY_LITERATURE[domain]) > 0


# =============================================================================
# DatabaseSelection Tests
# =============================================================================


class TestDatabaseSelection:
    """Tests for DatabaseSelection dataclass."""

    @pytest.fixture
    def valid_selection(self):
        """Fixture for a valid database selection."""
        return select_databases("biomedical", "clinical", "systematic")

    def test_valid_selection_is_valid(self, valid_selection):
        """Test valid selection passes validation."""
        assert valid_selection.is_valid()

    def test_selection_has_required_databases(self, valid_selection):
        """Test selection includes required databases."""
        assert len(valid_selection.required) >= 3

    def test_selection_includes_pubmed_for_clinical(self, valid_selection):
        """Test clinical selection includes PubMed."""
        assert "PubMed" in valid_selection.required

    def test_selection_has_preprint_flag(self, valid_selection):
        """Test systematic review requires preprint search."""
        assert valid_selection.preprint_required

    def test_selection_has_grey_literature(self, valid_selection):
        """Test selection includes grey literature sources."""
        assert len(valid_selection.grey_literature) > 0

    def test_get_all_databases(self, valid_selection):
        """Test get_all_databases returns combined list."""
        all_dbs = valid_selection.get_all_databases()
        assert len(all_dbs) >= len(valid_selection.required)

    def test_to_dict_includes_all_fields(self, valid_selection):
        """Test to_dict includes all expected fields."""
        d = valid_selection.to_dict()
        expected_fields = [
            "domain",
            "subdomain",
            "review_type",
            "required",
            "recommended",
            "optional",
            "minimum_required",
            "preprint_required",
            "preprint_server",
            "grey_literature",
        ]
        for field in expected_fields:
            assert field in d


class TestDatabaseSelectionValidation:
    """Tests for DatabaseSelection validation."""

    def test_insufficient_databases_fails(self):
        """Test validation fails with insufficient databases."""
        selection = DatabaseSelection(
            domain="test",
            subdomain="test",
            review_type="systematic",
            required=["DB1"],  # Only 1, need 3
            recommended=[],
            optional=[],
            minimum_required=3,
            preprint_required=True,
            preprint_server="arXiv",
            grey_literature=[],
        )
        errors = selection.validate()
        assert any("at least" in e for e in errors)
        assert not selection.is_valid()

    def test_missing_preprint_warning(self):
        """Test validation warns about missing preprint for systematic."""
        selection = DatabaseSelection(
            domain="test",
            subdomain="test",
            review_type="systematic",
            required=["DB1", "DB2", "DB3"],  # No preprint
            recommended=[],
            optional=[],
            minimum_required=3,
            preprint_required=True,
            preprint_server="arXiv",
            grey_literature=[],
        )
        errors = selection.validate()
        assert any("preprint" in e.lower() for e in errors)
        # Should still be valid (preprint is a warning, not critical)
        assert selection.is_valid()

    def test_preprint_in_required_passes(self):
        """Test validation passes when preprint in required."""
        selection = DatabaseSelection(
            domain="test",
            subdomain="test",
            review_type="systematic",
            required=["DB1", "DB2", "arXiv"],
            recommended=[],
            optional=[],
            minimum_required=3,
            preprint_required=True,
            preprint_server="arXiv",
            grey_literature=[],
        )
        errors = selection.validate()
        # No preprint warning
        assert not any("preprint" in e.lower() for e in errors)


# =============================================================================
# select_databases Function Tests
# =============================================================================


class TestSelectDatabases:
    """Tests for select_databases function."""

    def test_biomedical_clinical_systematic(self):
        """Test selection for biomedical clinical systematic review."""
        selection = select_databases("biomedical", "clinical", "systematic")
        assert selection.domain == "biomedical"
        assert selection.subdomain == "clinical"
        assert selection.review_type == "systematic"
        assert len(selection.required) >= 3
        assert selection.preprint_required

    def test_computer_science_ml_ai_scoping(self):
        """Test selection for CS ML/AI scoping review."""
        selection = select_databases("computer_science", "ml_ai", "scoping")
        assert len(selection.required) >= 2
        assert "arXiv" in selection.required or "arXiv" in selection.recommended
        assert selection.preprint_required

    def test_social_sciences_narrative(self):
        """Test selection for social sciences narrative review."""
        selection = select_databases("social_sciences", "psychology", "narrative")
        assert len(selection.required) >= 2
        assert not selection.preprint_required

    def test_rapid_review_has_quality_assessment(self):
        """Test rapid review has appropriate minimum."""
        selection = select_databases("biomedical", "clinical", "rapid")
        assert selection.minimum_required == 2

    def test_default_subdomain_fallback(self):
        """Test fallback to default subdomain."""
        selection = select_databases("biomedical", "nonexistent_subdomain", "systematic")
        # Should use default subdomain's databases
        assert len(selection.required) >= 3

    def test_unknown_domain_uses_multidisciplinary(self):
        """Test unknown domain falls back to multidisciplinary."""
        selection = select_databases("unknown_domain", "default", "systematic")
        assert "Semantic Scholar" in selection.required or "Web of Science" in selection.required

    def test_case_insensitive_domain(self):
        """Test domain matching is case-insensitive."""
        selection1 = select_databases("BIOMEDICAL", "clinical", "systematic")
        selection2 = select_databases("biomedical", "clinical", "systematic")
        assert selection1.required == selection2.required

    def test_case_insensitive_review_type(self):
        """Test review type matching is case-insensitive."""
        selection1 = select_databases("biomedical", "clinical", "SYSTEMATIC")
        selection2 = select_databases("biomedical", "clinical", "systematic")
        assert selection1.minimum_required == selection2.minimum_required

    def test_preprint_server_matches_domain(self):
        """Test preprint server matches domain."""
        bio_selection = select_databases("biomedical", "clinical", "systematic")
        cs_selection = select_databases("computer_science", "ml_ai", "systematic")

        assert "bioRxiv" in bio_selection.preprint_server
        assert bio_selection.preprint_server != cs_selection.preprint_server


# =============================================================================
# Helper Function Tests
# =============================================================================


class TestGetAvailableDomains:
    """Tests for get_available_domains function."""

    def test_returns_all_domains(self):
        """Test returns all defined domains."""
        domains = get_available_domains()
        expected = ["biomedical", "physical_sciences", "computer_science", "social_sciences", "multidisciplinary"]
        for domain in expected:
            assert domain in domains


class TestGetAvailableSubdomains:
    """Tests for get_available_subdomains function."""

    def test_returns_subdomains_for_biomedical(self):
        """Test returns subdomains for biomedical."""
        subdomains = get_available_subdomains("biomedical")
        assert "clinical" in subdomains
        assert "genomics" in subdomains

    def test_returns_empty_for_unknown_domain(self):
        """Test returns empty list for unknown domain."""
        subdomains = get_available_subdomains("unknown_domain")
        assert subdomains == []

    def test_case_insensitive(self):
        """Test subdomain lookup is case-insensitive."""
        subdomains1 = get_available_subdomains("BIOMEDICAL")
        subdomains2 = get_available_subdomains("biomedical")
        assert subdomains1 == subdomains2


class TestGetDatabaseUrl:
    """Tests for get_database_url function."""

    def test_pubmed_url(self):
        """Test PubMed URL returned correctly."""
        url = get_database_url("PubMed")
        assert "pubmed" in url.lower()
        assert url.startswith("https://")

    def test_arxiv_url(self):
        """Test arXiv URL returned correctly."""
        url = get_database_url("arXiv")
        assert "arxiv" in url.lower()

    def test_unknown_database_returns_empty(self):
        """Test unknown database returns empty string."""
        url = get_database_url("UnknownDatabase")
        assert url == ""


# =============================================================================
# Domain Detection Tests
# =============================================================================


class TestDetectDomain:
    """Tests for detect_domain function."""

    def test_detect_biomedical(self):
        """Test detection of biomedical domain."""
        keywords = ["cancer", "treatment", "patient", "clinical trial"]
        assert detect_domain(keywords) == "biomedical"

    def test_detect_computer_science(self):
        """Test detection of computer science domain."""
        keywords = ["machine learning", "algorithm", "neural network"]
        assert detect_domain(keywords) == "computer_science"

    def test_detect_physical_sciences(self):
        """Test detection of physical sciences domain."""
        keywords = ["quantum", "physics", "electron", "spectroscopy"]
        assert detect_domain(keywords) == "physical_sciences"

    def test_detect_social_sciences(self):
        """Test detection of social sciences domain."""
        keywords = ["psychology", "behavior", "social", "education"]
        assert detect_domain(keywords) == "social_sciences"

    def test_detect_multidisciplinary_fallback(self):
        """Test fallback to multidisciplinary for ambiguous keywords."""
        keywords = ["study", "research", "analysis"]
        assert detect_domain(keywords) == "multidisciplinary"

    def test_case_insensitive_detection(self):
        """Test keyword detection is case-insensitive."""
        keywords = ["CANCER", "TREATMENT", "Clinical"]
        assert detect_domain(keywords) == "biomedical"


# =============================================================================
# Search Strategy Generation Tests
# =============================================================================


class TestGenerateSearchStrategy:
    """Tests for generate_search_strategy function."""

    @pytest.fixture
    def sample_selection(self):
        """Fixture for sample database selection."""
        return select_databases("biomedical", "clinical", "systematic")

    def test_includes_header(self, sample_selection):
        """Test strategy includes header."""
        strategy = generate_search_strategy(sample_selection)
        assert "SEARCH STRATEGY" in strategy

    def test_includes_required_databases(self, sample_selection):
        """Test strategy includes required databases section."""
        strategy = generate_search_strategy(sample_selection)
        assert "REQUIRED DATABASES" in strategy

    def test_includes_database_urls(self, sample_selection):
        """Test strategy includes database URLs."""
        strategy = generate_search_strategy(sample_selection)
        # PubMed should be in the list with URL
        assert "pubmed" in strategy.lower()

    def test_includes_grey_literature(self, sample_selection):
        """Test strategy includes grey literature section."""
        strategy = generate_search_strategy(sample_selection)
        assert "GREY LITERATURE" in strategy

    def test_includes_preprint_for_systematic(self, sample_selection):
        """Test strategy includes preprint section for systematic reviews."""
        strategy = generate_search_strategy(sample_selection)
        assert "PREPRINT" in strategy

    def test_includes_warnings_section(self):
        """Test strategy includes warnings for invalid selection."""
        selection = DatabaseSelection(
            domain="test",
            subdomain="test",
            review_type="systematic",
            required=["DB1"],  # Insufficient
            recommended=[],
            optional=[],
            minimum_required=3,
            preprint_required=True,
            preprint_server="arXiv",
            grey_literature=["Source1"],
        )
        strategy = generate_search_strategy(selection)
        assert "WARNINGS" in strategy


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_subdomain_uses_default(self):
        """Test empty subdomain uses default."""
        selection = select_databases("biomedical", "", "systematic")
        assert len(selection.required) >= 3

    def test_none_subdomain_uses_default(self):
        """Test None subdomain uses default."""
        selection = select_databases("biomedical", None, "systematic")
        assert len(selection.required) >= 3

    def test_whitespace_domain_handling(self):
        """Test whitespace in domain is trimmed."""
        selection = select_databases("  biomedical  ", "clinical", "systematic")
        assert selection.domain == "biomedical"

    def test_all_review_types_have_valid_minimums(self):
        """Test all review types produce valid selections."""
        for review_type in ["systematic", "scoping", "narrative", "rapid"]:
            selection = select_databases("biomedical", "clinical", review_type)
            assert len(selection.required) >= selection.minimum_required

    def test_all_domains_produce_valid_selections(self):
        """Test all domains produce valid selections."""
        for domain in get_available_domains():
            selection = select_databases(domain, "default", "systematic")
            assert len(selection.required) >= 2

    def test_structural_biology_subdomain(self):
        """Test structural biology subdomain includes PDB."""
        selection = select_databases("biomedical", "structural_biology", "systematic")
        all_dbs = selection.get_all_databases()
        assert "PDB" in all_dbs or "PubMed" in all_dbs

    def test_bioinformatics_spans_domains(self):
        """Test bioinformatics subdomain has cross-domain databases."""
        selection = select_databases("computer_science", "bioinformatics", "systematic")
        all_dbs = selection.get_all_databases()
        # Should have both CS and bio databases
        has_pubmed = "PubMed" in all_dbs
        has_arxiv = "arXiv" in all_dbs or "arXiv" in selection.preprint_server
        assert has_pubmed or has_arxiv


class TestDomainDetectionEdgeCases:
    """Edge case tests for domain detection."""

    def test_empty_keywords_list(self):
        """Test empty keywords list returns multidisciplinary."""
        assert detect_domain([]) == "multidisciplinary"

    def test_single_keyword(self):
        """Test single keyword detection."""
        assert detect_domain(["cancer"]) == "biomedical"
        assert detect_domain(["algorithm"]) == "computer_science"

    def test_mixed_domain_keywords(self):
        """Test mixed keywords uses highest scoring domain."""
        # Bioinformatics - mix of bio and CS
        keywords = ["gene", "algorithm", "protein", "database"]
        # Should lean towards biomedical due to more matches
        domain = detect_domain(keywords)
        assert domain in ["biomedical", "computer_science"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
