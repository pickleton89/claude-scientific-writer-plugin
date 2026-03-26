#!/usr/bin/env python3
"""
Unit tests for database_router.py

Tests deterministic database selection based on query content.
"""

import sys
from pathlib import Path
import pytest

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from database_router import (
    select_databases,
    get_routing_result,
    get_routing_explanation,
    get_matched_terms,
    RoutingResult,
    BIOMEDICAL_TERMS,
    CS_AI_TERMS,
    PREPRINT_INDICATORS,
)


class TestSelectDatabases:
    """Tests for select_databases function."""

    # Biomedical queries
    def test_biomedical_single_term(self):
        """Test biomedical query with single domain term."""
        databases = select_databases("cancer treatment")
        assert "pubmed" in databases

    def test_biomedical_multiple_terms(self):
        """Test biomedical query with multiple domain terms."""
        databases = select_databases("BRCA1 gene mutation breast cancer therapy")
        assert databases == ["pubmed"]

    def test_biomedical_clinical(self):
        """Test clinical research query."""
        databases = select_databases("patient treatment clinical trial drug efficacy")
        assert databases[0] == "pubmed"

    # CS/AI queries
    def test_cs_single_term(self):
        """Test CS query with single domain term."""
        databases = select_databases("neural network architecture")
        assert "semantic" in databases

    def test_cs_multiple_terms(self):
        """Test CS query with multiple domain terms."""
        databases = select_databases("transformer deep learning attention mechanism")
        assert databases == ["semantic"]

    def test_ml_benchmark(self):
        """Test ML benchmark query."""
        databases = select_databases("dataset benchmark classification accuracy")
        assert "semantic" in databases

    # Cross-domain queries
    def test_cross_domain_ml_biology(self):
        """Test ML + biology cross-domain query."""
        databases = select_databases("deep learning protein structure prediction")
        assert "semantic" in databases
        assert "pubmed" in databases

    def test_cross_domain_drug_discovery(self):
        """Test drug discovery + AI query."""
        databases = select_databases("machine learning drug discovery molecular")
        assert len(databases) >= 2

    def test_cross_domain_bioinformatics(self):
        """Test bioinformatics query."""
        databases = select_databases("neural network gene expression prediction")
        assert len(databases) >= 2

    # Preprint handling
    def test_preprint_indicator(self):
        """Test preprint indicator triggers bioRxiv."""
        databases = select_databases("recent protein folding advances preprint")
        assert "biorxiv" in databases

    def test_latest_triggers_preprint(self):
        """Test 'latest' keyword triggers preprints with biomedical context."""
        # Need enough biomedical terms to route to PubMed first
        databases = select_databases("latest gene therapy cancer treatment")
        assert "biorxiv" in databases
        assert "pubmed" in databases

    def test_novel_triggers_preprint(self):
        """Test 'novel' keyword triggers preprints with biomedical context."""
        databases = select_databases("novel gene therapy treatment method")
        assert "biorxiv" in databases

    # No domain signals
    def test_general_query(self):
        """Test query with no domain-specific terms."""
        databases = select_databases("climate change effects")
        # Should default to Semantic Scholar for broad coverage
        assert "semantic" in databases

    def test_ambiguous_query(self):
        """Test ambiguous query defaults to semantic."""
        databases = select_databases("recent developments innovations")
        assert "semantic" in databases


class TestUserHints:
    """Tests for user hint handling."""

    def test_hint_biomedical(self):
        """Test biomedical hint."""
        databases = select_databases("test query", user_hint="biomedical")
        assert databases == ["pubmed"]

    def test_hint_medical(self):
        """Test medical hint (alias for biomedical)."""
        databases = select_databases("test query", user_hint="medical")
        assert databases == ["pubmed"]

    def test_hint_cs(self):
        """Test CS hint."""
        databases = select_databases("test query", user_hint="cs")
        assert databases == ["semantic"]

    def test_hint_ai(self):
        """Test AI hint (alias for CS)."""
        databases = select_databases("test query", user_hint="ai")
        assert databases == ["semantic"]

    def test_hint_comprehensive(self):
        """Test comprehensive hint."""
        databases = select_databases("test query", user_hint="comprehensive")
        assert "pubmed" in databases
        assert "semantic" in databases

    def test_hint_preprint(self):
        """Test preprint hint."""
        databases = select_databases("test query", user_hint="preprint")
        assert "biorxiv" in databases
        assert "medrxiv" in databases

    def test_hint_overrides_content(self):
        """Test that hint overrides content-based routing."""
        # This query has biomedical terms but hint says CS
        databases = select_databases("cancer gene therapy", user_hint="cs")
        assert databases == ["semantic"]

    def test_hint_with_preprint_indicator(self):
        """Test hint + preprint indicator combination."""
        databases = select_databases("latest gene therapy", user_hint="biomedical")
        assert "pubmed" in databases
        assert "biorxiv" in databases


class TestIncludePreprints:
    """Tests for explicit preprint inclusion."""

    def test_force_preprints_true(self):
        """Test forcing preprint inclusion."""
        databases = select_databases("cancer therapy", include_preprints=True)
        assert "biorxiv" in databases

    def test_force_preprints_false(self):
        """Test forcing no preprints even with indicator."""
        databases = select_databases(
            "latest cancer research",
            include_preprints=False
        )
        assert "biorxiv" not in databases


class TestRoutingResult:
    """Tests for detailed routing results."""

    def test_result_contains_confidence(self):
        """Test that result includes confidence score."""
        result = get_routing_result("CRISPR gene therapy")
        assert 0.0 <= result.confidence <= 1.0

    def test_result_contains_explanation(self):
        """Test that result includes explanation."""
        result = get_routing_result("transformer attention")
        assert len(result.explanation) > 0

    def test_result_contains_domain(self):
        """Test that result includes domain classification."""
        result = get_routing_result("cancer treatment")
        assert result.domain in ("biomedical", "cs_ai", "cross_domain", "general",
                                   "comprehensive", "preprint")

    def test_result_contains_scores(self):
        """Test that result includes domain scores."""
        result = get_routing_result("deep learning protein")
        assert result.biomedical_score >= 0
        assert result.cs_score >= 0

    def test_result_immutable(self):
        """Test that RoutingResult is immutable."""
        result = get_routing_result("test query")
        with pytest.raises(AttributeError):
            result.confidence = 0.5

    def test_user_hint_full_confidence(self):
        """Test that user hints give 100% confidence."""
        result = get_routing_result("test query", user_hint="biomedical")
        assert result.confidence == 1.0


class TestRoutingExplanation:
    """Tests for human-readable explanations."""

    def test_explanation_includes_databases(self):
        """Test explanation includes selected databases."""
        explanation = get_routing_explanation("CRISPR therapy")
        assert "pubmed" in explanation.lower() or "Selected" in explanation

    def test_explanation_includes_confidence(self):
        """Test explanation includes confidence."""
        explanation = get_routing_explanation("neural network")
        assert "%" in explanation or "Confidence" in explanation

    def test_explanation_for_cross_domain(self):
        """Test explanation for cross-domain query."""
        explanation = get_routing_explanation("deep learning drug discovery")
        # Should mention both domains
        assert "biomedical" in explanation.lower() or "cross" in explanation.lower()


class TestMatchedTerms:
    """Tests for term matching diagnostics."""

    def test_matched_biomedical_terms(self):
        """Test that biomedical terms are identified."""
        matched = get_matched_terms("cancer gene therapy treatment")
        assert "cancer" in matched["biomedical"]
        assert "gene" in matched["biomedical"]
        assert "therapy" in matched["biomedical"]
        assert "treatment" in matched["biomedical"]

    def test_matched_cs_terms(self):
        """Test that CS/AI terms are identified."""
        matched = get_matched_terms("neural network deep learning")
        assert "neural" in matched["cs_ai"]
        assert "deep" in matched["cs_ai"]
        assert "learning" in matched["cs_ai"]

    def test_matched_preprint_indicators(self):
        """Test that preprint indicators are identified."""
        matched = get_matched_terms("latest cutting-edge research preprint")
        assert "latest" in matched["preprint_indicators"]
        assert "preprint" in matched["preprint_indicators"]

    def test_no_false_positives(self):
        """Test that unrelated terms aren't matched."""
        matched = get_matched_terms("astronomy telescope observation")
        assert len(matched["biomedical"]) == 0
        assert len(matched["cs_ai"]) == 0


class TestDeterminism:
    """Tests to verify deterministic behavior."""

    def test_same_query_same_result(self):
        """Test that same query produces same result."""
        result1 = select_databases("CRISPR gene therapy")
        result2 = select_databases("CRISPR gene therapy")
        assert result1 == result2

    def test_consistent_across_runs(self):
        """Test consistency across multiple invocations."""
        results = [
            select_databases("deep learning protein prediction")
            for _ in range(10)
        ]
        assert all(r == results[0] for r in results)

    def test_consistent_confidence(self):
        """Test confidence is consistent."""
        results = [
            get_routing_result("cancer treatment therapy")
            for _ in range(10)
        ]
        confidences = [r.confidence for r in results]
        assert all(c == confidences[0] for c in confidences)

    def test_order_independent_databases(self):
        """Test that returned database list order is deterministic."""
        # Run multiple times and verify order is consistent
        results = [
            select_databases("machine learning drug discovery")
            for _ in range(10)
        ]
        assert all(r == results[0] for r in results)


class TestKeywordCoverage:
    """Tests to verify keyword sets have good coverage."""

    def test_biomedical_has_core_terms(self):
        """Test biomedical set has essential terms."""
        core_terms = {"gene", "protein", "cell", "drug", "disease", "cancer"}
        assert core_terms.issubset(BIOMEDICAL_TERMS)

    def test_cs_has_core_terms(self):
        """Test CS/AI set has essential terms."""
        core_terms = {"neural", "learning", "algorithm", "network", "training"}
        assert core_terms.issubset(CS_AI_TERMS)

    def test_preprint_has_core_indicators(self):
        """Test preprint set has essential indicators."""
        core_indicators = {"preprint", "recent", "latest", "new"}
        assert core_indicators.issubset(PREPRINT_INDICATORS)


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_query(self):
        """Test handling of empty query."""
        databases = select_databases("")
        # Should still return a valid default
        assert isinstance(databases, list)
        assert len(databases) > 0

    def test_single_word_query(self):
        """Test single word query handling."""
        databases = select_databases("cancer")
        assert "pubmed" in databases

    def test_very_long_query(self):
        """Test very long query handling."""
        long_query = " ".join(["gene"] * 100 + ["neural"] * 100)
        databases = select_databases(long_query)
        assert isinstance(databases, list)

    def test_special_characters(self):
        """Test query with special characters."""
        databases = select_databases("BRCA1/2 gene p53 (tumor suppressor)")
        assert isinstance(databases, list)

    def test_case_insensitive(self):
        """Test case insensitivity."""
        lower = select_databases("cancer gene therapy")
        upper = select_databases("CANCER GENE THERAPY")
        mixed = select_databases("Cancer Gene Therapy")
        assert lower == upper == mixed

    def test_multiword_terms(self):
        """Test multiword term detection."""
        # "deep learning" and "machine learning" should be detected
        matched = get_matched_terms("deep learning for biology")
        assert "deep" in matched["cs_ai"]
        assert "learning" in matched["cs_ai"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
