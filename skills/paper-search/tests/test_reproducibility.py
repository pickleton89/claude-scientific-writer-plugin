"""
Tests for Reproducibility Module.

Phase 3 Implementation - Determinism Audit
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Import from scripts directory
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from reproducibility import (
    ReproducibilityLog,
    ReproducibilityRecord,
    ResultHash,
    SearchHash,
    SearchSpecification,
    compute_search_hash,
    create_reproducibility_record,
    format_reproducibility_note,
    generate_citation_key,
    hash_query,
    verify_reproduction,
)


# ============================================================================
# SearchSpecification Tests
# ============================================================================


class TestSearchSpecification:
    """Tests for SearchSpecification dataclass."""

    def test_basic_creation(self):
        """Test creating a basic specification."""
        spec = SearchSpecification(
            query="cancer mutation",
            sources=["pubmed"],
        )
        assert spec.query == "cancer mutation"
        assert spec.sources == ["pubmed"]
        assert spec.max_results == 20  # Default

    def test_full_specification(self):
        """Test creating a full specification."""
        spec = SearchSpecification(
            query="BRCA1 mutation",
            sources=["pubmed", "semantic"],
            max_results=50,
            date_start="2020",
            date_end="2024",
            publication_types=["Review"],
            fields_of_study=["Biology"],
            min_citations=10,
            open_access_only=True,
            author_filter="Smith",
            journal_filter="Nature",
            exclude_terms=["mouse"],
        )
        assert spec.max_results == 50
        assert spec.date_start == "2020"
        assert spec.min_citations == 10
        assert spec.open_access_only is True

    def test_to_dict(self):
        """Test converting to dictionary."""
        spec = SearchSpecification(
            query="test",
            sources=["pubmed"],
            max_results=10,
        )
        d = spec.to_dict()

        assert d["query"] == "test"
        assert d["sources"] == ["pubmed"]
        assert d["max_results"] == 10

    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "query": "cancer",
            "sources": ["pubmed", "semantic"],
            "max_results": 30,
            "date_start": "2020",
        }
        spec = SearchSpecification.from_dict(data)

        assert spec.query == "cancer"
        assert spec.sources == ["pubmed", "semantic"]
        assert spec.max_results == 30
        assert spec.date_start == "2020"

    def test_from_dict_ignores_extra_keys(self):
        """Test that from_dict ignores unknown keys."""
        data = {
            "query": "test",
            "sources": ["pubmed"],
            "unknown_key": "value",
        }
        spec = SearchSpecification.from_dict(data)
        assert spec.query == "test"

    def test_to_canonical_string(self):
        """Test canonical string generation."""
        spec = SearchSpecification(
            query="test",
            sources=["semantic", "pubmed"],  # Unsorted
        )
        canonical = spec.to_canonical_string()

        # Should be valid JSON
        parsed = json.loads(canonical)
        # Sources should be sorted
        assert parsed["sources"] == ["pubmed", "semantic"]

    def test_canonical_string_determinism(self):
        """Test that canonical string is deterministic."""
        spec = SearchSpecification(
            query="cancer mutation",
            sources=["semantic", "pubmed", "biorxiv"],
            publication_types=["Review", "Article"],
        )

        canonical1 = spec.to_canonical_string()
        canonical2 = spec.to_canonical_string()
        canonical3 = spec.to_canonical_string()

        assert canonical1 == canonical2 == canonical3


# ============================================================================
# SearchHash Tests
# ============================================================================


class TestSearchHash:
    """Tests for SearchHash class."""

    def test_compute_hash(self):
        """Test computing hash from specification."""
        spec = SearchSpecification(query="test", sources=["pubmed"])
        hash_obj = SearchHash.compute(spec)

        assert len(hash_obj.hash_value) == 12  # Default truncation
        assert hash_obj.algorithm == "sha256"
        assert hash_obj.truncated is True

    def test_compute_full_hash(self):
        """Test computing full (non-truncated) hash."""
        spec = SearchSpecification(query="test", sources=["pubmed"])
        hash_obj = SearchHash.compute(spec, truncate=False)

        assert len(hash_obj.hash_value) == 64  # Full SHA256
        assert hash_obj.truncated is False

    def test_custom_truncation_length(self):
        """Test custom truncation length."""
        spec = SearchSpecification(query="test", sources=["pubmed"])
        hash_obj = SearchHash.compute(spec, truncate=True, length=8)

        assert len(hash_obj.hash_value) == 8
        assert hash_obj.truncation_length == 8

    def test_hash_determinism(self):
        """Test that hashing is deterministic."""
        spec = SearchSpecification(query="cancer mutation", sources=["pubmed"])

        hash1 = SearchHash.compute(spec)
        hash2 = SearchHash.compute(spec)
        hash3 = SearchHash.compute(spec)

        assert hash1.hash_value == hash2.hash_value == hash3.hash_value

    def test_different_specs_different_hashes(self):
        """Test that different specs produce different hashes."""
        spec1 = SearchSpecification(query="cancer", sources=["pubmed"])
        spec2 = SearchSpecification(query="diabetes", sources=["pubmed"])

        hash1 = SearchHash.compute(spec1)
        hash2 = SearchHash.compute(spec2)

        assert hash1.hash_value != hash2.hash_value

    def test_source_order_independence(self):
        """Test that source order doesn't affect hash."""
        spec1 = SearchSpecification(
            query="test", sources=["pubmed", "semantic", "biorxiv"]
        )
        spec2 = SearchSpecification(
            query="test", sources=["biorxiv", "pubmed", "semantic"]
        )

        hash1 = SearchHash.compute(spec1)
        hash2 = SearchHash.compute(spec2)

        assert hash1.hash_value == hash2.hash_value

    def test_str_representation(self):
        """Test string representation of hash."""
        spec = SearchSpecification(query="test", sources=["pubmed"])
        hash_obj = SearchHash.compute(spec)

        assert str(hash_obj) == hash_obj.hash_value


# ============================================================================
# compute_search_hash Function Tests
# ============================================================================


class TestComputeSearchHash:
    """Tests for compute_search_hash convenience function."""

    def test_basic_usage(self):
        """Test basic hash computation."""
        hash_value = compute_search_hash("cancer", ["pubmed"])

        assert len(hash_value) == 12
        assert isinstance(hash_value, str)

    def test_with_parameters(self):
        """Test hash computation with additional parameters."""
        hash_value = compute_search_hash(
            "cancer",
            ["pubmed"],
            max_results=50,
            date_start="2020",
            publication_types=["Review"],
        )

        assert len(hash_value) == 12

    def test_parameter_name_aliases(self):
        """Test that 'max' and 'max_results' produce same hash."""
        hash1 = compute_search_hash("test", ["pubmed"], max=30)
        hash2 = compute_search_hash("test", ["pubmed"], max_results=30)

        assert hash1 == hash2

    def test_determinism(self):
        """Test deterministic output."""
        query = "BRCA1"
        sources = ["pubmed", "semantic"]

        hash1 = compute_search_hash(query, sources, max_results=20)
        hash2 = compute_search_hash(query, sources, max_results=20)

        assert hash1 == hash2


# ============================================================================
# ResultHash Tests
# ============================================================================


class TestResultHash:
    """Tests for ResultHash class."""

    def test_compute_result_hash(self):
        """Test computing hash of results."""
        results = [
            {"doi": "10.1000/test1"},
            {"doi": "10.1000/test2"},
        ]
        hash_obj = ResultHash.compute(results)

        assert len(hash_obj.hash_value) == 12
        assert hash_obj.result_count == 2

    def test_hash_uses_doi(self):
        """Test that DOI is used for hashing."""
        results1 = [{"doi": "10.1000/test", "title": "Title A"}]
        results2 = [{"doi": "10.1000/test", "title": "Title B"}]

        hash1 = ResultHash.compute(results1)
        hash2 = ResultHash.compute(results2)

        # Same DOI should produce same hash despite different titles
        assert hash1.hash_value == hash2.hash_value

    def test_hash_fallback_to_pmid(self):
        """Test fallback to PMID when no DOI."""
        results = [{"pmid": "12345678"}]
        hash_obj = ResultHash.compute(results)

        assert hash_obj.result_count == 1
        assert len(hash_obj.hash_value) == 12

    def test_hash_fallback_to_title(self):
        """Test fallback to title when no ID."""
        results = [{"title": "A Very Long Paper Title Here"}]
        hash_obj = ResultHash.compute(results)

        assert hash_obj.result_count == 1

    def test_empty_results(self):
        """Test hashing empty results."""
        hash_obj = ResultHash.compute([])
        assert hash_obj.result_count == 0

    def test_order_independence(self):
        """Test that result order doesn't affect hash."""
        results1 = [
            {"doi": "10.1000/a"},
            {"doi": "10.1000/b"},
            {"doi": "10.1000/c"},
        ]
        results2 = [
            {"doi": "10.1000/c"},
            {"doi": "10.1000/a"},
            {"doi": "10.1000/b"},
        ]

        hash1 = ResultHash.compute(results1)
        hash2 = ResultHash.compute(results2)

        assert hash1.hash_value == hash2.hash_value


# ============================================================================
# ReproducibilityRecord Tests
# ============================================================================


class TestReproducibilityRecord:
    """Tests for ReproducibilityRecord class."""

    @pytest.fixture
    def sample_record(self):
        """Create a sample record for testing."""
        spec = SearchSpecification(query="test", sources=["pubmed"])
        return ReproducibilityRecord(
            search_spec=spec,
            search_hash="abc123def456",
            result_hash="xyz789ghi012",
            result_count=10,
            timestamp="2026-01-09T10:00:00Z",
            duration_ms=150.5,
        )

    def test_record_creation(self, sample_record):
        """Test creating a reproducibility record."""
        assert sample_record.search_hash == "abc123def456"
        assert sample_record.result_count == 10
        assert sample_record.duration_ms == 150.5

    def test_to_dict(self, sample_record):
        """Test converting record to dictionary."""
        d = sample_record.to_dict()

        assert d["search_hash"] == "abc123def456"
        assert d["result_count"] == 10
        assert "search_spec" in d
        assert d["search_spec"]["query"] == "test"

    def test_from_dict(self, sample_record):
        """Test creating record from dictionary."""
        d = sample_record.to_dict()
        recreated = ReproducibilityRecord.from_dict(d)

        assert recreated.search_hash == sample_record.search_hash
        assert recreated.result_count == sample_record.result_count
        assert recreated.search_spec.query == sample_record.search_spec.query

    def test_to_json(self, sample_record):
        """Test JSON serialization."""
        json_str = sample_record.to_json()
        parsed = json.loads(json_str)

        assert parsed["search_hash"] == "abc123def456"


# ============================================================================
# create_reproducibility_record Tests
# ============================================================================


class TestCreateReproducibilityRecord:
    """Tests for create_reproducibility_record function."""

    def test_basic_creation(self):
        """Test creating a record from search results."""
        results = [{"doi": "10.1000/test"}]
        record = create_reproducibility_record(
            query="cancer",
            sources=["pubmed"],
            results=results,
        )

        assert record.search_spec.query == "cancer"
        assert record.result_count == 1
        assert len(record.search_hash) == 12
        assert len(record.result_hash) == 12

    def test_with_duration(self):
        """Test including duration."""
        record = create_reproducibility_record(
            query="test",
            sources=["pubmed"],
            results=[],
            duration_ms=250.5,
        )

        assert record.duration_ms == 250.5

    def test_timestamp_format(self):
        """Test that timestamp is ISO format."""
        record = create_reproducibility_record(
            query="test",
            sources=["pubmed"],
            results=[],
        )

        # Should be valid ISO format
        assert "T" in record.timestamp
        assert record.timestamp.endswith("Z") or "+" in record.timestamp

    def test_with_parameters(self):
        """Test with additional search parameters."""
        record = create_reproducibility_record(
            query="cancer",
            sources=["pubmed"],
            results=[{"doi": "10.1000/test"}],
            max_results=50,
            date_start="2020",
            publication_types=["Review"],
        )

        assert record.search_spec.max_results == 50
        assert record.search_spec.date_start == "2020"
        assert record.search_spec.publication_types == ["Review"]


# ============================================================================
# Verification Tests
# ============================================================================


class TestVerifyReproduction:
    """Tests for verify_reproduction function."""

    def test_matching_results(self):
        """Test verification with matching results."""
        results = [{"doi": "10.1000/a"}, {"doi": "10.1000/b"}]

        record = create_reproducibility_record(
            query="test", sources=["pubmed"], results=results
        )

        matches, differences = verify_reproduction(record, results)

        assert matches is True
        assert len(differences) == 0

    def test_different_count(self):
        """Test verification with different result count."""
        original_results = [{"doi": "10.1000/a"}, {"doi": "10.1000/b"}]
        record = create_reproducibility_record(
            query="test", sources=["pubmed"], results=original_results
        )

        new_results = [{"doi": "10.1000/a"}]  # One fewer
        matches, differences = verify_reproduction(record, new_results)

        assert matches is False
        assert any("count" in d.lower() for d in differences)

    def test_different_results(self):
        """Test verification with different result set."""
        original_results = [{"doi": "10.1000/a"}]
        record = create_reproducibility_record(
            query="test", sources=["pubmed"], results=original_results
        )

        new_results = [{"doi": "10.1000/b"}]  # Different DOI
        matches, differences = verify_reproduction(record, new_results)

        assert matches is False
        assert any("hash" in d.lower() for d in differences)


# ============================================================================
# ReproducibilityLog Tests
# ============================================================================


class TestReproducibilityLog:
    """Tests for ReproducibilityLog class."""

    def test_create_log(self):
        """Test creating a log without file."""
        log = ReproducibilityLog()
        assert len(log._records) == 0

    def test_add_record(self):
        """Test adding records to log."""
        log = ReproducibilityLog()
        record = create_reproducibility_record(
            query="test", sources=["pubmed"], results=[]
        )

        log.add(record)
        assert len(log._records) == 1

    def test_find_by_hash(self):
        """Test finding records by search hash."""
        log = ReproducibilityLog()

        record1 = create_reproducibility_record(
            query="cancer", sources=["pubmed"], results=[]
        )
        record2 = create_reproducibility_record(
            query="diabetes", sources=["pubmed"], results=[]
        )

        log.add(record1)
        log.add(record2)

        found = log.find_by_hash(record1.search_hash)
        assert len(found) == 1
        assert found[0].search_spec.query == "cancer"

    def test_get_recent(self):
        """Test getting recent records."""
        log = ReproducibilityLog()

        for i in range(15):
            record = create_reproducibility_record(
                query=f"query{i}", sources=["pubmed"], results=[]
            )
            log.add(record)

        recent = log.get_recent(limit=5)
        assert len(recent) == 5

    def test_persistence(self):
        """Test log persistence to file."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            log_path = Path(f.name)

        try:
            # Create and save
            log1 = ReproducibilityLog(log_path)
            record = create_reproducibility_record(
                query="test", sources=["pubmed"], results=[]
            )
            log1.add(record)

            # Load in new instance
            log2 = ReproducibilityLog(log_path)
            assert len(log2._records) == 1
            assert log2._records[0].search_spec.query == "test"
        finally:
            log_path.unlink()

    def test_clear(self):
        """Test clearing log."""
        log = ReproducibilityLog()
        log.add(
            create_reproducibility_record(query="test", sources=["pubmed"], results=[])
        )

        assert len(log._records) == 1
        log.clear()
        assert len(log._records) == 0


# ============================================================================
# Convenience Function Tests
# ============================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_hash_query(self):
        """Test simple query hashing."""
        hash_value = hash_query("cancer", ["pubmed"])

        assert len(hash_value) == 12
        assert isinstance(hash_value, str)

    def test_hash_query_determinism(self):
        """Test hash_query is deterministic."""
        hash1 = hash_query("test", ["pubmed", "semantic"])
        hash2 = hash_query("test", ["pubmed", "semantic"])

        assert hash1 == hash2

    def test_hash_query_source_order(self):
        """Test source order independence for hash_query."""
        hash1 = hash_query("test", ["pubmed", "semantic"])
        hash2 = hash_query("test", ["semantic", "pubmed"])

        assert hash1 == hash2

    def test_generate_citation_key(self):
        """Test citation key generation."""
        record = create_reproducibility_record(
            query="test", sources=["pubmed"], results=[]
        )
        key = generate_citation_key(record)

        assert key.startswith("search_")
        assert record.search_hash in key

    def test_format_reproducibility_note(self):
        """Test formatting reproducibility note."""
        record = create_reproducibility_record(
            query="cancer mutation",
            sources=["pubmed", "semantic"],
            results=[{"doi": "10.1000/test"}],
            duration_ms=150.0,
        )

        note = format_reproducibility_note(record)

        assert "cancer mutation" in note
        assert record.search_hash in note
        assert "pubmed" in note
        assert "150" in note


# ============================================================================
# Determinism Tests
# ============================================================================


class TestDeterminism:
    """Tests specifically for deterministic behavior."""

    def test_search_hash_determinism_full(self):
        """Test complete search hash determinism."""
        spec = SearchSpecification(
            query="BRCA1 AND cancer",
            sources=["pubmed", "semantic", "biorxiv"],
            max_results=50,
            date_start="2020",
            date_end="2024",
            publication_types=["Review", "Article"],
            fields_of_study=["Biology", "Medicine"],
            min_citations=10,
            open_access_only=True,
        )

        hashes = [SearchHash.compute(spec).hash_value for _ in range(10)]

        # All hashes should be identical
        assert len(set(hashes)) == 1

    def test_result_hash_determinism(self):
        """Test result hash determinism."""
        results = [
            {"doi": "10.1000/a", "title": "Paper A"},
            {"doi": "10.1000/b", "title": "Paper B"},
            {"pmid": "12345", "title": "Paper C"},
        ]

        hashes = [ResultHash.compute(results).hash_value for _ in range(10)]
        assert len(set(hashes)) == 1

    def test_record_creation_determinism(self):
        """Test record creation produces consistent hashes."""
        params = {
            "query": "test query",
            "sources": ["pubmed"],
            "results": [{"doi": "10.1000/test"}],
        }

        records = [create_reproducibility_record(**params) for _ in range(5)]

        search_hashes = [r.search_hash for r in records]
        result_hashes = [r.result_hash for r in records]

        assert len(set(search_hashes)) == 1
        assert len(set(result_hashes)) == 1


# ============================================================================
# Edge Cases
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_query(self):
        """Test handling empty query."""
        spec = SearchSpecification(query="", sources=["pubmed"])
        hash_obj = SearchHash.compute(spec)

        assert len(hash_obj.hash_value) == 12

    def test_special_characters_in_query(self):
        """Test query with special characters."""
        spec = SearchSpecification(
            query='cancer AND "breast cancer" OR (tumor)',
            sources=["pubmed"],
        )
        hash_obj = SearchHash.compute(spec)

        assert len(hash_obj.hash_value) == 12

    def test_unicode_in_query(self):
        """Test query with unicode characters."""
        spec = SearchSpecification(query="Müller syndrome", sources=["pubmed"])
        hash_obj = SearchHash.compute(spec)

        assert len(hash_obj.hash_value) == 12

    def test_very_long_query(self):
        """Test very long query."""
        long_query = "cancer " * 1000
        spec = SearchSpecification(query=long_query, sources=["pubmed"])
        hash_obj = SearchHash.compute(spec)

        assert len(hash_obj.hash_value) == 12

    def test_empty_sources(self):
        """Test with empty sources list."""
        spec = SearchSpecification(query="test", sources=[])
        hash_obj = SearchHash.compute(spec)

        assert len(hash_obj.hash_value) == 12

    def test_many_sources(self):
        """Test with many sources."""
        spec = SearchSpecification(
            query="test",
            sources=["pubmed", "semantic", "biorxiv", "arxiv", "google"],
        )
        hash_obj = SearchHash.compute(spec)

        assert len(hash_obj.hash_value) == 12

    def test_none_values_in_spec(self):
        """Test specification with None values."""
        spec = SearchSpecification(
            query="test",
            sources=["pubmed"],
            date_start=None,
            date_end=None,
            min_citations=None,
        )

        canonical = spec.to_canonical_string()
        parsed = json.loads(canonical)

        # None values should be converted to defaults
        assert parsed["date_start"] == ""
        assert parsed["min_citations"] == 0
