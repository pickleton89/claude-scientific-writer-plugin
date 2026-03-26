#!/usr/bin/env python3
"""
Unit tests for query_templates.py

Tests deterministic query construction from templates.
"""

import sys
from pathlib import Path
import pytest

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from query_templates import (
    build_query,
    list_templates,
    get_template_info,
    get_templates_for_source,
    validate_template_params,
    format_template_help,
    TemplateError,
    QUERY_TEMPLATES,
)


class TestBuildQuery:
    """Tests for build_query function."""

    def test_simple_topic_search(self):
        """Test basic topic search template."""
        result = build_query("topic_search", topic="CRISPR")
        assert result == "CRISPR"

    def test_review_search(self):
        """Test review search with publication type filter."""
        result = build_query("review_search", topic="CAR-T cell therapy")
        assert result == "CAR-T cell therapy AND Review[Publication Type]"

    def test_recent_advances(self):
        """Test date-bounded search."""
        result = build_query(
            "recent_advances",
            topic="AlphaFold",
            year_start="2022",
            year_end="2024"
        )
        assert result == "AlphaFold AND 2022:2024[Publication Date]"

    def test_author_papers(self):
        """Test author search template."""
        result = build_query("author_papers", author="Doudna JA")
        assert result == "Doudna JA[Author]"

    def test_author_topic(self):
        """Test author + topic combination."""
        result = build_query(
            "author_topic",
            author="Zhang F",
            topic="CRISPR"
        )
        assert result == "Zhang F[Author] AND CRISPR"

    def test_clinical_trials(self):
        """Test clinical trial search."""
        result = build_query("clinical_trials", topic="pembrolizumab melanoma")
        assert result == "pembrolizumab melanoma AND Clinical Trial[Publication Type]"

    def test_gene_function(self):
        """Test gene function search with aliases."""
        result = build_query(
            "gene_function",
            gene="TP53",
            aliases="p53"
        )
        assert "(TP53 OR p53)" in result
        assert "(function OR role OR mechanism)" in result

    def test_gene_function_without_aliases(self):
        """Test gene function uses gene as default alias."""
        result = build_query("gene_function", gene="BRCA1")
        assert "BRCA1" in result
        assert "(function OR role OR mechanism)" in result

    def test_gene_disease(self):
        """Test gene-disease association search."""
        result = build_query(
            "gene_disease",
            gene="BRCA1",
            disease="breast cancer"
        )
        assert "BRCA1" in result
        assert "breast cancer" in result

    def test_drug_target(self):
        """Test drug-target interaction search."""
        result = build_query(
            "drug_target",
            drug="imatinib",
            target="BCR-ABL"
        )
        assert "imatinib" in result
        assert "BCR-ABL" in result
        assert "(mechanism OR pathway OR binding)" in result

    def test_drug_comparison(self):
        """Test comparative drug study search."""
        result = build_query(
            "drug_comparison",
            drug1="nivolumab",
            drug2="pembrolizumab"
        )
        assert "nivolumab" in result
        assert "pembrolizumab" in result
        assert "(comparison OR versus OR efficacy)" in result

    def test_systematic_review(self):
        """Test systematic review search."""
        result = build_query("systematic_review", topic="immunotherapy efficacy")
        assert '"immunotherapy efficacy"' in result
        assert "systematic review[Title]" in result
        assert "meta-analysis[Title]" in result

    def test_method_application(self):
        """Test method application search."""
        result = build_query(
            "method_application",
            method="single-cell RNA-seq",
            application="tumor heterogeneity"
        )
        assert "single-cell RNA-seq" in result
        assert "tumor heterogeneity" in result

    def test_ml_biology(self):
        """Test ML in biology cross-domain search."""
        result = build_query(
            "ml_biology",
            biology_topic="protein structure prediction",
            ml_method="transformer"
        )
        assert "protein structure prediction" in result
        assert "transformer" in result

    def test_ml_biology_default_method(self):
        """Test ML in biology with default method."""
        result = build_query(
            "ml_biology",
            biology_topic="drug discovery"
        )
        assert "drug discovery" in result
        assert "machine learning" in result


class TestTemplateErrors:
    """Tests for error handling in query templates."""

    def test_unknown_template(self):
        """Test error on unknown template name."""
        with pytest.raises(TemplateError) as exc_info:
            build_query("nonexistent_template", topic="test")
        assert "Unknown template" in str(exc_info.value)
        assert "nonexistent_template" in str(exc_info.value)

    def test_missing_required_param(self):
        """Test error on missing required parameter."""
        with pytest.raises(TemplateError) as exc_info:
            build_query("author_topic", author="Smith")  # Missing topic
        assert "Missing required parameters" in str(exc_info.value)
        assert "topic" in str(exc_info.value)

    def test_missing_multiple_params(self):
        """Test error message lists all missing params."""
        with pytest.raises(TemplateError) as exc_info:
            build_query("drug_comparison")  # Missing drug1 and drug2
        assert "drug1" in str(exc_info.value)
        assert "drug2" in str(exc_info.value)


class TestListTemplates:
    """Tests for template listing functions."""

    def test_list_templates_returns_list(self):
        """Test that list_templates returns a list."""
        templates = list_templates()
        assert isinstance(templates, list)
        assert len(templates) > 0

    def test_list_templates_sorted(self):
        """Test that templates are sorted alphabetically."""
        templates = list_templates()
        assert templates == sorted(templates)

    def test_list_templates_includes_core(self):
        """Test that core templates are present."""
        templates = list_templates()
        assert "topic_search" in templates
        assert "review_search" in templates
        assert "author_papers" in templates

    def test_get_template_info(self):
        """Test getting template info."""
        info = get_template_info("review_search")
        assert info is not None
        assert info.name == "review_search"
        assert "topic" in info.required_params
        assert "Review" in info.pattern

    def test_get_template_info_unknown(self):
        """Test None returned for unknown template."""
        info = get_template_info("nonexistent")
        assert info is None


class TestTemplatesForSource:
    """Tests for source-based template filtering."""

    def test_pubmed_templates(self):
        """Test filtering templates for PubMed."""
        templates = get_templates_for_source("pubmed")
        assert len(templates) > 0
        assert "review_search" in templates  # PubMed-specific
        assert "clinical_trials" in templates

    def test_semantic_templates(self):
        """Test filtering templates for Semantic Scholar."""
        templates = get_templates_for_source("semantic")
        assert len(templates) > 0
        assert "landmark_papers" in templates

    def test_biorxiv_templates(self):
        """Test filtering templates for bioRxiv."""
        templates = get_templates_for_source("biorxiv")
        assert len(templates) > 0
        assert "preprint_topic" in templates

    def test_case_insensitive(self):
        """Test case insensitive source matching."""
        lower = get_templates_for_source("pubmed")
        upper = get_templates_for_source("PUBMED")
        assert lower == upper


class TestValidateTemplateParams:
    """Tests for parameter validation."""

    def test_valid_params(self):
        """Test validation with valid parameters."""
        is_valid, errors = validate_template_params(
            "review_search",
            {"topic": "CRISPR"}
        )
        assert is_valid is True
        assert len(errors) == 0

    def test_missing_required(self):
        """Test validation with missing required param."""
        is_valid, errors = validate_template_params(
            "author_topic",
            {"author": "Smith"}  # Missing topic
        )
        assert is_valid is False
        assert any("Missing" in e for e in errors)

    def test_unknown_params(self):
        """Test validation with unknown parameters."""
        is_valid, errors = validate_template_params(
            "topic_search",
            {"topic": "test", "unknown_param": "value"}
        )
        assert is_valid is False
        assert any("Unknown" in e for e in errors)

    def test_unknown_template(self):
        """Test validation with unknown template."""
        is_valid, errors = validate_template_params(
            "nonexistent",
            {"topic": "test"}
        )
        assert is_valid is False
        assert any("Unknown template" in e for e in errors)


class TestFormatHelp:
    """Tests for help text formatting."""

    def test_format_help_returns_string(self):
        """Test that format_help returns a string."""
        help_text = format_template_help()
        assert isinstance(help_text, str)
        assert len(help_text) > 0

    def test_format_help_includes_templates(self):
        """Test that help includes all templates."""
        help_text = format_template_help()
        for template_name in list_templates():
            assert template_name in help_text

    def test_format_help_includes_descriptions(self):
        """Test that help includes descriptions."""
        help_text = format_template_help()
        assert "Pattern:" in help_text
        assert "Required:" in help_text
        assert "Example:" in help_text


class TestDeterminism:
    """Tests to verify deterministic behavior."""

    def test_same_input_same_output(self):
        """Test that same inputs produce same outputs."""
        result1 = build_query("review_search", topic="CRISPR")
        result2 = build_query("review_search", topic="CRISPR")
        assert result1 == result2

    def test_consistent_across_runs(self):
        """Test consistency across multiple invocations."""
        results = [
            build_query("gene_function", gene="TP53", aliases="p53")
            for _ in range(10)
        ]
        assert all(r == results[0] for r in results)

    def test_template_immutability(self):
        """Test that templates cannot be modified."""
        template = get_template_info("review_search")
        # QueryTemplate is frozen dataclass - should raise error on modification
        with pytest.raises(AttributeError):
            template.name = "modified"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
