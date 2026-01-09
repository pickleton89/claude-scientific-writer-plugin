#!/usr/bin/env python3
"""
Unit tests for query_schema.py

Tests structured query specification and conversion.
"""

import sys
from pathlib import Path
import json
import pytest
import tempfile

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from query_schema import (
    StructuredQuery,
    load_query_from_json,
    load_query_from_string,
    validate_query_schema,
    get_example_schema,
    list_example_schemas,
    EXAMPLE_SCHEMAS,
)


class TestStructuredQueryBasic:
    """Tests for basic StructuredQuery functionality."""

    def test_minimal_query(self):
        """Test query with only required fields."""
        q = StructuredQuery(concepts=["CRISPR"])
        assert q.concepts == ["CRISPR"]
        assert q.operator == "AND"

    def test_multiple_concepts(self):
        """Test query with multiple concepts."""
        q = StructuredQuery(concepts=["CRISPR", "gene therapy", "cancer"])
        assert len(q.concepts) == 3

    def test_operator_or(self):
        """Test OR operator."""
        q = StructuredQuery(concepts=["term1", "term2"], operator="OR")
        assert q.operator == "OR"

    def test_operator_case_insensitive(self):
        """Test operator normalization to uppercase."""
        q = StructuredQuery(concepts=["term1"], operator="and")
        assert q.operator == "AND"

    def test_invalid_operator(self):
        """Test error on invalid operator."""
        with pytest.raises(ValueError) as exc_info:
            StructuredQuery(concepts=["term1"], operator="XOR")
        assert "Invalid operator" in str(exc_info.value)

    def test_empty_concepts_error(self):
        """Test error on empty concepts list."""
        with pytest.raises(ValueError):
            StructuredQuery(concepts=[])


class TestPubMedQueryGeneration:
    """Tests for PubMed query generation."""

    def test_simple_query(self):
        """Test simple PubMed query."""
        q = StructuredQuery(concepts=["CRISPR", "therapy"])
        result = q.to_pubmed_query()
        assert "CRISPR" in result
        assert "therapy" in result
        assert "AND" in result

    def test_or_operator(self):
        """Test OR operator in PubMed query."""
        q = StructuredQuery(concepts=["CRISPR", "TALEN"], operator="OR")
        result = q.to_pubmed_query()
        assert " OR " in result

    def test_synonyms_expansion(self):
        """Test synonym expansion in query."""
        q = StructuredQuery(
            concepts=["TP53"],
            synonyms={"TP53": ["p53", "tumor protein p53"]}
        )
        result = q.to_pubmed_query()
        assert "TP53" in result
        assert "p53" in result
        assert "tumor protein p53" in result
        assert "OR" in result

    def test_field_constraints_author(self):
        """Test author field constraint."""
        q = StructuredQuery(
            concepts=["CRISPR"],
            field_constraints={"author": "Doudna JA"}
        )
        result = q.to_pubmed_query()
        assert "Doudna JA[Author]" in result

    def test_field_constraints_title(self):
        """Test title field constraint."""
        q = StructuredQuery(
            concepts=["therapy"],
            field_constraints={"title": "gene"}
        )
        result = q.to_pubmed_query()
        assert "gene[Title]" in result

    def test_date_range(self):
        """Test date range filter."""
        q = StructuredQuery(
            concepts=["CRISPR"],
            date_range={"start": "2020", "end": "2024"}
        )
        result = q.to_pubmed_query()
        assert "2020:2024[Publication Date]" in result

    def test_publication_types(self):
        """Test publication type filter."""
        q = StructuredQuery(
            concepts=["cancer"],
            publication_types=["Review", "Meta-Analysis"]
        )
        result = q.to_pubmed_query()
        assert "Review[Publication Type]" in result
        assert "Meta-Analysis[Publication Type]" in result

    def test_exclude_terms(self):
        """Test exclusion terms."""
        q = StructuredQuery(
            concepts=["cancer"],
            exclude_terms=["review", "survey"]
        )
        result = q.to_pubmed_query()
        assert "NOT review" in result
        assert "NOT survey" in result

    def test_complex_query(self):
        """Test complex query with multiple features."""
        q = StructuredQuery(
            concepts=["CRISPR", "gene editing"],
            operator="AND",
            synonyms={"CRISPR": ["CRISPR-Cas9"]},
            field_constraints={"author": "Zhang F"},
            date_range={"start": "2022", "end": "2024"},
            publication_types=["Review"],
            exclude_terms=["protocol"]
        )
        result = q.to_pubmed_query()
        assert "CRISPR" in result
        assert "CRISPR-Cas9" in result
        assert "Zhang F[Author]" in result
        assert "2022:2024[Publication Date]" in result
        assert "Review[Publication Type]" in result
        assert "NOT protocol" in result


class TestSemanticQueryGeneration:
    """Tests for Semantic Scholar query generation."""

    def test_simple_query(self):
        """Test simple Semantic Scholar query."""
        q = StructuredQuery(concepts=["machine learning", "biology"])
        result = q.to_semantic_query()
        assert "machine learning" in result
        assert "biology" in result

    def test_synonyms_expansion(self):
        """Test synonym expansion."""
        q = StructuredQuery(
            concepts=["ML"],
            synonyms={"ML": ["machine learning", "deep learning"]}
        )
        result = q.to_semantic_query()
        assert "ML" in result
        assert "machine learning" in result

    def test_exclude_terms(self):
        """Test exclusion with minus prefix."""
        q = StructuredQuery(
            concepts=["neural network"],
            exclude_terms=["survey"]
        )
        result = q.to_semantic_query()
        assert "-survey" in result


class TestBioRxivQueryGeneration:
    """Tests for bioRxiv query generation."""

    def test_simple_query(self):
        """Test simple bioRxiv query."""
        q = StructuredQuery(concepts=["protein folding"])
        result = q.to_biorxiv_query()
        assert "protein folding" in result

    def test_exclude_terms(self):
        """Test exclusion terms."""
        q = StructuredQuery(
            concepts=["CRISPR"],
            exclude_terms=["review"]
        )
        result = q.to_biorxiv_query()
        assert "-review" in result


class TestAPIParams:
    """Tests for API parameter extraction."""

    def test_semantic_params(self):
        """Test Semantic Scholar API params."""
        q = StructuredQuery(
            concepts=["test"],
            fields_of_study=["Biology", "Medicine"],
            min_citations=100,
            open_access=True,
            date_range={"start": "2020", "end": "2024"}
        )
        params = q.get_api_params("semantic")
        assert params["fields_of_study"] == ["Biology", "Medicine"]
        assert params["min_citations"] == 100
        assert params["open_access"] is True
        assert params["year_start"] == 2020
        assert params["year_end"] == 2024

    def test_pubmed_params(self):
        """Test PubMed API params."""
        q = StructuredQuery(
            concepts=["test"],
            publication_types=["Review"],
            date_range={"start": "2020", "end": "2024"}
        )
        params = q.get_api_params("pubmed")
        assert params["publication_types"] == ["Review"]
        assert params["date_start"] == "2020"
        assert params["date_end"] == "2024"

    def test_biorxiv_params(self):
        """Test bioRxiv API params."""
        q = StructuredQuery(
            concepts=["test"],
            date_range={"start": "2020", "end": "2024"}
        )
        params = q.get_api_params("biorxiv")
        assert params["date_start"] == "2020-01-01"
        assert params["date_end"] == "2024-12-31"


class TestSerialization:
    """Tests for serialization/deserialization."""

    def test_to_dict(self):
        """Test conversion to dictionary."""
        q = StructuredQuery(
            concepts=["CRISPR", "therapy"],
            operator="AND",
            synonyms={"CRISPR": ["CRISPR-Cas9"]}
        )
        d = q.to_dict()
        assert d["concepts"] == ["CRISPR", "therapy"]
        assert d["operator"] == "AND"
        assert d["synonyms"] == {"CRISPR": ["CRISPR-Cas9"]}

    def test_from_dict(self):
        """Test creation from dictionary."""
        d = {
            "concepts": ["CRISPR", "therapy"],
            "operator": "AND",
            "synonyms": {"CRISPR": ["CRISPR-Cas9"]}
        }
        q = StructuredQuery.from_dict(d)
        assert q.concepts == ["CRISPR", "therapy"]
        assert q.operator == "AND"
        assert q.synonyms == {"CRISPR": ["CRISPR-Cas9"]}

    def test_round_trip(self):
        """Test serialization round-trip."""
        original = StructuredQuery(
            concepts=["cancer", "therapy"],
            synonyms={"cancer": ["tumor", "malignancy"]},
            date_range={"start": "2020", "end": "2024"},
            publication_types=["Review"],
            min_citations=50
        )
        d = original.to_dict()
        restored = StructuredQuery.from_dict(d)

        assert restored.concepts == original.concepts
        assert restored.synonyms == original.synonyms
        assert restored.date_range == original.date_range
        assert restored.publication_types == original.publication_types
        assert restored.min_citations == original.min_citations


class TestLoadFromJSON:
    """Tests for JSON file loading."""

    def test_load_from_file(self):
        """Test loading query from JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"concepts": ["CRISPR", "therapy"]}, f)
            f.flush()

            q = load_query_from_json(f.name)
            assert q.concepts == ["CRISPR", "therapy"]

    def test_load_from_string(self):
        """Test loading query from JSON string."""
        json_str = '{"concepts": ["CRISPR"], "operator": "AND"}'
        q = load_query_from_string(json_str)
        assert q.concepts == ["CRISPR"]
        assert q.operator == "AND"

    def test_file_not_found(self):
        """Test error on missing file."""
        with pytest.raises(FileNotFoundError):
            load_query_from_json("/nonexistent/path.json")

    def test_invalid_json_string(self):
        """Test error on invalid JSON."""
        with pytest.raises(json.JSONDecodeError):
            load_query_from_string("not valid json")


class TestValidateSchema:
    """Tests for schema validation."""

    def test_valid_minimal(self):
        """Test validation of minimal valid schema."""
        is_valid, errors = validate_query_schema({"concepts": ["test"]})
        assert is_valid is True
        assert len(errors) == 0

    def test_missing_concepts(self):
        """Test validation with missing concepts."""
        is_valid, errors = validate_query_schema({})
        assert is_valid is False
        assert any("concepts" in e.lower() for e in errors)

    def test_empty_concepts(self):
        """Test validation with empty concepts."""
        is_valid, errors = validate_query_schema({"concepts": []})
        assert is_valid is False

    def test_invalid_operator(self):
        """Test validation with invalid operator."""
        is_valid, errors = validate_query_schema({
            "concepts": ["test"],
            "operator": "NAND"
        })
        assert is_valid is False
        assert any("operator" in e.lower() for e in errors)

    def test_invalid_synonyms_type(self):
        """Test validation with wrong synonyms type."""
        is_valid, errors = validate_query_schema({
            "concepts": ["test"],
            "synonyms": ["list", "instead", "of", "dict"]
        })
        assert is_valid is False

    def test_invalid_date_range(self):
        """Test validation with wrong date_range type."""
        is_valid, errors = validate_query_schema({
            "concepts": ["test"],
            "date_range": "2020-2024"  # Should be dict
        })
        assert is_valid is False


class TestExampleSchemas:
    """Tests for example schemas."""

    def test_list_examples(self):
        """Test listing example schemas."""
        examples = list_example_schemas()
        assert len(examples) > 0
        assert "basic" in examples

    def test_get_basic_example(self):
        """Test getting basic example."""
        schema = get_example_schema("basic")
        assert schema is not None
        assert "concepts" in schema

    def test_get_unknown_example(self):
        """Test getting unknown example returns None."""
        schema = get_example_schema("nonexistent")
        assert schema is None

    def test_all_examples_valid(self):
        """Test that all examples pass validation."""
        for name in list_example_schemas():
            schema = get_example_schema(name)
            is_valid, errors = validate_query_schema(schema)
            assert is_valid, f"Example '{name}' failed validation: {errors}"

    def test_all_examples_construct(self):
        """Test that all examples can construct queries."""
        for name in list_example_schemas():
            schema = get_example_schema(name)
            q = StructuredQuery.from_dict(schema)
            # Should not raise
            pubmed = q.to_pubmed_query()
            semantic = q.to_semantic_query()
            assert len(pubmed) > 0
            assert len(semantic) > 0


class TestDeterminism:
    """Tests for deterministic behavior."""

    def test_same_input_same_output(self):
        """Test that same inputs produce same outputs."""
        q1 = StructuredQuery(
            concepts=["CRISPR", "therapy"],
            synonyms={"CRISPR": ["CRISPR-Cas9"]}
        )
        q2 = StructuredQuery(
            concepts=["CRISPR", "therapy"],
            synonyms={"CRISPR": ["CRISPR-Cas9"]}
        )
        assert q1.to_pubmed_query() == q2.to_pubmed_query()
        assert q1.to_semantic_query() == q2.to_semantic_query()

    def test_consistent_across_runs(self):
        """Test consistency across multiple invocations."""
        q = StructuredQuery(
            concepts=["cancer", "immunotherapy"],
            date_range={"start": "2020", "end": "2024"}
        )
        results = [q.to_pubmed_query() for _ in range(10)]
        assert all(r == results[0] for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
