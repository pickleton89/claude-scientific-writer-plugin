"""
Tests for Gene Alias Module.

Phase 3 Implementation - Determinism Audit
"""

import json
import tempfile
from pathlib import Path

import pytest

# Import from scripts directory
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from gene_aliases import (
    GeneAliasDatabase,
    GeneInfo,
    detect_genes_in_query,
    expand_gene_terms,
    expand_gene_terms_pubmed,
    get_database,
    get_expansion_explanation,
    get_gene_info,
    list_gene_categories,
    list_supported_genes,
    reload_database,
)


# ============================================================================
# GeneInfo Tests
# ============================================================================


class TestGeneInfo:
    """Tests for GeneInfo dataclass."""

    def test_gene_info_creation(self):
        """Test creating a GeneInfo instance."""
        gene = GeneInfo(
            symbol="TP53",
            name="tumor protein p53",
            aliases=["p53", "tumor protein 53"],
            category="tumor_suppressor",
        )
        assert gene.symbol == "TP53"
        assert gene.name == "tumor protein p53"
        assert len(gene.aliases) == 2
        assert gene.category == "tumor_suppressor"

    def test_gene_info_all_terms(self):
        """Test all_terms method includes symbol and aliases."""
        gene = GeneInfo(
            symbol="BRCA1",
            name="BRCA1 DNA repair",
            aliases=["breast cancer 1", "FANCS"],
        )
        terms = gene.all_terms()
        assert "BRCA1" in terms
        assert "breast cancer 1" in terms
        assert "FANCS" in terms
        assert len(terms) == 3

    def test_gene_info_default_category(self):
        """Test default category is 'unknown'."""
        gene = GeneInfo(symbol="TEST", name="test gene", aliases=[])
        assert gene.category == "unknown"


# ============================================================================
# GeneAliasDatabase Tests
# ============================================================================


class TestGeneAliasDatabase:
    """Tests for GeneAliasDatabase class."""

    @pytest.fixture
    def sample_db(self):
        """Create a sample database for testing."""
        db = GeneAliasDatabase()
        db.add_gene(
            GeneInfo(
                symbol="TP53",
                name="tumor protein p53",
                aliases=["p53", "tumor protein 53"],
                category="tumor_suppressor",
            )
        )
        db.add_gene(
            GeneInfo(
                symbol="BRCA1",
                name="BRCA1 DNA repair",
                aliases=["breast cancer 1"],
                category="tumor_suppressor",
            )
        )
        db.add_gene(
            GeneInfo(
                symbol="EGFR",
                name="epidermal growth factor receptor",
                aliases=["ErbB-1", "HER1"],
                category="receptor_tyrosine_kinase",
            )
        )
        return db

    def test_database_creation(self):
        """Test creating empty database."""
        db = GeneAliasDatabase()
        assert len(db.genes) == 0

    def test_add_gene(self, sample_db):
        """Test adding genes to database."""
        assert len(sample_db.genes) == 3
        assert "TP53" in sample_db.genes

    def test_get_gene_case_insensitive(self, sample_db):
        """Test getting gene is case-insensitive."""
        gene = sample_db.get_gene("tp53")
        assert gene is not None
        assert gene.symbol == "TP53"

        gene2 = sample_db.get_gene("TP53")
        assert gene2 is not None
        assert gene2.symbol == "TP53"

    def test_get_gene_not_found(self, sample_db):
        """Test getting non-existent gene returns None."""
        gene = sample_db.get_gene("NOTREAL")
        assert gene is None

    def test_has_gene(self, sample_db):
        """Test has_gene method."""
        assert sample_db.has_gene("TP53")
        assert sample_db.has_gene("tp53")  # Case insensitive
        assert not sample_db.has_gene("NOTREAL")

    def test_get_aliases(self, sample_db):
        """Test getting aliases for a gene."""
        aliases = sample_db.get_aliases("TP53")
        assert "p53" in aliases
        assert "tumor protein 53" in aliases

    def test_get_aliases_not_found(self, sample_db):
        """Test get_aliases returns empty list for unknown gene."""
        aliases = sample_db.get_aliases("NOTREAL")
        assert aliases == []

    def test_get_all_terms(self, sample_db):
        """Test get_all_terms includes symbol and aliases."""
        terms = sample_db.get_all_terms("EGFR")
        assert "EGFR" in terms
        assert "ErbB-1" in terms
        assert "HER1" in terms

    def test_get_all_terms_unknown(self, sample_db):
        """Test get_all_terms returns symbol for unknown gene."""
        terms = sample_db.get_all_terms("UNKNOWN")
        assert terms == ["UNKNOWN"]

    def test_list_symbols(self, sample_db):
        """Test listing all symbols."""
        symbols = sample_db.list_symbols()
        assert sorted(symbols) == ["BRCA1", "EGFR", "TP53"]

    def test_list_categories(self, sample_db):
        """Test listing all categories."""
        categories = sample_db.list_categories()
        assert "tumor_suppressor" in categories
        assert "receptor_tyrosine_kinase" in categories

    def test_genes_by_category(self, sample_db):
        """Test filtering genes by category."""
        tumor_suppressors = sample_db.genes_by_category("tumor_suppressor")
        assert len(tumor_suppressors) == 2
        symbols = [g.symbol for g in tumor_suppressors]
        assert "TP53" in symbols
        assert "BRCA1" in symbols

    def test_search_by_alias(self, sample_db):
        """Test searching by alias."""
        matches = sample_db.search_by_alias("p53")
        assert len(matches) == 1
        assert matches[0].symbol == "TP53"

    def test_search_by_alias_partial(self, sample_db):
        """Test partial alias matching."""
        matches = sample_db.search_by_alias("cancer")
        assert len(matches) == 1
        assert matches[0].symbol == "BRCA1"


class TestDatabaseLoading:
    """Tests for database loading functionality."""

    def test_load_from_json(self):
        """Test loading database from JSON file."""
        db = GeneAliasDatabase.load_from_json()
        # Should load from default path
        assert len(db.genes) > 0
        assert db.has_gene("TP53")

    def test_load_from_json_custom_path(self):
        """Test loading from custom JSON path."""
        data = {
            "genes": {
                "TEST1": {
                    "name": "Test Gene 1",
                    "aliases": ["alias1", "alias2"],
                    "category": "test",
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = Path(f.name)

        try:
            db = GeneAliasDatabase.load_from_json(temp_path)
            assert db.has_gene("TEST1")
            assert db.get_aliases("TEST1") == ["alias1", "alias2"]
        finally:
            temp_path.unlink()

    def test_load_from_nonexistent_file(self):
        """Test loading from non-existent file returns empty database."""
        db = GeneAliasDatabase.load_from_json(Path("/nonexistent/path.json"))
        assert len(db.genes) == 0

    def test_merge_databases(self):
        """Test merging two databases."""
        db1 = GeneAliasDatabase()
        db1.add_gene(GeneInfo("GENE1", "Gene 1", ["alias1"]))

        db2 = GeneAliasDatabase()
        db2.add_gene(GeneInfo("GENE2", "Gene 2", ["alias2"]))
        db2.add_gene(GeneInfo("GENE1", "Gene 1", ["alias3"]))  # Overlapping

        db1.merge(db2)

        assert db1.has_gene("GENE1")
        assert db1.has_gene("GENE2")
        # Check aliases were combined
        aliases = db1.get_aliases("GENE1")
        assert "alias1" in aliases
        assert "alias3" in aliases


# ============================================================================
# Query Expansion Tests
# ============================================================================


class TestQueryExpansion:
    """Tests for query expansion functionality."""

    @pytest.fixture
    def test_db(self):
        """Create test database and reload global."""
        db = GeneAliasDatabase()
        db.add_gene(
            GeneInfo(
                symbol="TP53",
                name="tumor protein p53",
                aliases=["p53", "tumor protein p53"],
            )
        )
        db.add_gene(
            GeneInfo(
                symbol="BRCA1",
                name="BRCA1 DNA repair",
                aliases=["breast cancer 1"],
            )
        )
        return db

    def test_expand_single_gene(self, test_db):
        """Test expanding a single gene symbol."""
        query = "TP53 mutation"
        result = expand_gene_terms(query, test_db)

        assert "TP53" in result
        assert "p53" in result
        assert "tumor protein p53" in result
        assert "mutation" in result

    def test_expand_preserves_other_terms(self, test_db):
        """Test that non-gene terms are preserved."""
        query = "TP53 AND cancer AND treatment"
        result = expand_gene_terms(query, test_db)

        assert "cancer" in result
        assert "treatment" in result

    def test_expand_multiple_genes(self, test_db):
        """Test expanding multiple genes in one query."""
        query = "TP53 BRCA1 interaction"
        result = expand_gene_terms(query, test_db)

        assert "TP53" in result
        assert "p53" in result
        assert "BRCA1" in result
        assert "breast cancer 1" in result

    def test_expand_case_insensitive(self, test_db):
        """Test expansion works with different cases."""
        query = "tp53 mutation"  # lowercase
        result = expand_gene_terms(query, test_db)

        # Should still expand
        assert "p53" in result or "TP53" in result

    def test_expand_no_genes(self, test_db):
        """Test query without genes is unchanged."""
        query = "cancer treatment therapy"
        result = expand_gene_terms(query, test_db)

        assert result == query

    def test_expand_unknown_gene(self, test_db):
        """Test unknown gene symbols are not expanded."""
        query = "UNKNOWNGENE mutation"
        result = expand_gene_terms(query, test_db)

        assert "UNKNOWNGENE" in result
        # Should not add any OR clauses for unknown genes
        assert result == query

    def test_expand_gene_terms_pubmed(self, test_db):
        """Test PubMed-specific expansion."""
        query = "TP53 mutation"
        result = expand_gene_terms_pubmed(query, test_db)

        assert "p53" in result
        # Should produce valid PubMed syntax with OR
        assert " OR " in result


# ============================================================================
# Detection Tests
# ============================================================================


class TestGeneDetection:
    """Tests for gene detection in queries."""

    @pytest.fixture
    def test_db(self):
        """Create test database."""
        db = GeneAliasDatabase()
        db.add_gene(GeneInfo("TP53", "tumor protein p53", []))
        db.add_gene(GeneInfo("BRCA1", "BRCA1 DNA repair", []))
        db.add_gene(GeneInfo("EGFR", "epidermal growth factor receptor", []))
        return db

    def test_detect_single_gene(self, test_db):
        """Test detecting a single gene."""
        genes = detect_genes_in_query("TP53 mutation", test_db)
        assert genes == ["TP53"]

    def test_detect_multiple_genes(self, test_db):
        """Test detecting multiple genes."""
        genes = detect_genes_in_query("TP53 and BRCA1 interaction", test_db)
        assert "TP53" in genes
        assert "BRCA1" in genes

    def test_detect_no_duplicates(self, test_db):
        """Test no duplicate detections."""
        genes = detect_genes_in_query("TP53 TP53 mutation", test_db)
        assert genes.count("TP53") == 1

    def test_detect_no_genes(self, test_db):
        """Test empty list when no genes found."""
        genes = detect_genes_in_query("cancer treatment", test_db)
        assert genes == []

    def test_get_expansion_explanation(self, test_db):
        """Test expansion explanation."""
        # Need to add aliases for this test
        test_db.genes["TP53"].aliases = ["p53"]

        explanation = get_expansion_explanation("TP53 mutation", test_db)
        assert "TP53" in explanation
        assert "p53" in explanation["TP53"]


# ============================================================================
# Global Database Tests
# ============================================================================


class TestGlobalDatabase:
    """Tests for global database functions."""

    def test_get_database(self):
        """Test getting global database."""
        db = get_database()
        assert db is not None
        assert isinstance(db, GeneAliasDatabase)

    def test_get_database_singleton(self):
        """Test database is singleton (same instance)."""
        db1 = get_database()
        db2 = get_database()
        assert db1 is db2

    def test_reload_database(self):
        """Test reloading database."""
        db = reload_database()
        assert db is not None
        # Should have loaded from default file
        assert len(db.genes) > 0

    def test_list_supported_genes(self):
        """Test listing supported genes."""
        genes = list_supported_genes()
        assert isinstance(genes, list)
        assert len(genes) > 0
        assert "TP53" in genes

    def test_list_gene_categories(self):
        """Test listing gene categories."""
        categories = list_gene_categories()
        assert isinstance(categories, list)
        assert len(categories) > 0

    def test_get_gene_info(self):
        """Test getting gene info by symbol."""
        info = get_gene_info("TP53")
        assert info is not None
        assert info.symbol == "TP53"
        assert len(info.aliases) > 0


# ============================================================================
# Determinism Tests
# ============================================================================


class TestDeterminism:
    """Tests verifying deterministic behavior."""

    def test_expansion_determinism(self):
        """Test that expansion produces identical output for identical input."""
        db = GeneAliasDatabase()
        db.add_gene(GeneInfo("TP53", "tumor protein p53", ["p53", "tumor protein 53"]))

        query = "TP53 mutation in cancer"

        result1 = expand_gene_terms(query, db)
        result2 = expand_gene_terms(query, db)
        result3 = expand_gene_terms(query, db)

        assert result1 == result2 == result3

    def test_detection_determinism(self):
        """Test that detection produces identical output for identical input."""
        db = GeneAliasDatabase()
        db.add_gene(GeneInfo("TP53", "tumor protein p53", []))
        db.add_gene(GeneInfo("BRCA1", "BRCA1 DNA repair", []))

        query = "TP53 BRCA1 study"

        genes1 = detect_genes_in_query(query, db)
        genes2 = detect_genes_in_query(query, db)
        genes3 = detect_genes_in_query(query, db)

        assert genes1 == genes2 == genes3

    def test_list_symbols_determinism(self):
        """Test that list_symbols returns consistent order."""
        db = GeneAliasDatabase()
        db.add_gene(GeneInfo("ZEBRA", "zebra gene", []))
        db.add_gene(GeneInfo("ALPHA", "alpha gene", []))
        db.add_gene(GeneInfo("BETA", "beta gene", []))

        list1 = db.list_symbols()
        list2 = db.list_symbols()

        assert list1 == list2
        assert list1 == ["ALPHA", "BETA", "ZEBRA"]  # Sorted

    def test_all_terms_determinism(self):
        """Test that all_terms returns consistent order."""
        gene = GeneInfo("TEST", "test", ["alias1", "alias2", "alias3"])

        terms1 = gene.all_terms()
        terms2 = gene.all_terms()

        assert terms1 == terms2


# ============================================================================
# Edge Cases
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_query(self):
        """Test handling empty query."""
        db = GeneAliasDatabase()
        result = expand_gene_terms("", db)
        assert result == ""

    def test_query_with_special_characters(self):
        """Test query with special characters."""
        db = GeneAliasDatabase()
        db.add_gene(GeneInfo("TP53", "tumor protein p53", ["p53"]))

        query = "TP53 (mutation OR deletion)"
        result = expand_gene_terms(query, db)
        assert "mutation OR deletion" in result

    def test_gene_at_word_boundary(self):
        """Test gene detection respects word boundaries."""
        db = GeneAliasDatabase()
        db.add_gene(GeneInfo("TP53", "tumor protein p53", []))

        # Should not match "ATP53" or "TP53A"
        genes = detect_genes_in_query("ATP53 and TP53A", db)
        assert "TP53" not in genes

        # Should match standalone TP53
        genes = detect_genes_in_query("TP53 mutation", db)
        assert "TP53" in genes

    def test_numeric_gene_symbol(self):
        """Test gene symbols with numbers."""
        db = GeneAliasDatabase()
        db.add_gene(GeneInfo("IL6", "interleukin 6", ["interleukin-6"]))

        genes = detect_genes_in_query("IL6 levels", db)
        assert "IL6" in genes

    def test_short_gene_symbol(self):
        """Test short gene symbols (2 chars)."""
        db = GeneAliasDatabase()
        # Very short symbols might cause issues
        db.add_gene(GeneInfo("AR", "androgen receptor", []))

        genes = detect_genes_in_query("AR signaling", db)
        # AR should be detected (meets 2-char minimum)
        assert "AR" in genes

    def test_gene_with_no_aliases(self):
        """Test gene with empty aliases list."""
        db = GeneAliasDatabase()
        db.add_gene(GeneInfo("SOLO", "solo gene", []))

        result = expand_gene_terms("SOLO mutation", db)
        # Should not expand if no aliases (len <= 1)
        assert result == "SOLO mutation"
