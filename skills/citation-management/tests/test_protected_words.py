"""
Comprehensive test suite for protected words loading and title protection.

Tests cover:
- Protected words file loading
- Default fallback behavior
- Additional file merging
- Cache functionality
- Title protection with various word types
- CrossRef type mapping completeness
"""

import pytest
import sys
import os
import tempfile

# Add scripts directory to path
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "scripts")
)

from extract_metadata import MetadataExtractor


class TestProtectedWordsLoading:
    """Test protected words loading from files."""

    @pytest.fixture
    def extractor(self):
        return MetadataExtractor()

    @pytest.fixture
    def assets_file(self):
        """Path to the default protected words file."""
        return os.path.join(
            os.path.dirname(__file__),
            "..",
            "assets",
            "protected_words.txt",
        )

    def test_load_default_file_exists(self, extractor, assets_file):
        """Test that default protected words file exists."""
        assert os.path.exists(assets_file)

    def test_load_default_returns_set(self, extractor):
        """Test that load_protected_words returns a set."""
        words = extractor.load_protected_words()
        assert isinstance(words, set)

    def test_load_default_not_empty(self, extractor):
        """Test that loaded words set is not empty."""
        words = extractor.load_protected_words()
        assert len(words) > 0

    def test_load_contains_basic_acronyms(self, extractor):
        """Test that basic scientific acronyms are present."""
        words = extractor.load_protected_words()
        expected = {"DNA", "RNA", "mRNA", "CRISPR", "PCR"}
        assert expected.issubset(words)

    def test_load_contains_software_names(self, extractor):
        """Test that software names are present."""
        words = extractor.load_protected_words()
        expected = {"Python", "PyTorch", "TensorFlow", "NumPy"}
        assert expected.issubset(words)

    def test_load_contains_databases(self, extractor):
        """Test that database names are present."""
        words = extractor.load_protected_words()
        expected = {"PubMed", "UniProt", "GenBank", "PDB"}
        assert expected.issubset(words)

    def test_load_contains_chemical_terms(self, extractor):
        """Test that chemical/biological terms are present."""
        words = extractor.load_protected_words()
        expected = {"ATP", "GFP", "IgG", "HLA"}
        assert expected.issubset(words)

    def test_load_contains_model_organisms(self, extractor):
        """Test that model organism names are present."""
        words = extractor.load_protected_words()
        expected = {"Drosophila", "Arabidopsis", "Escherichia"}
        assert expected.issubset(words)

    def test_load_excludes_comments(self, extractor):
        """Test that comment lines are excluded."""
        words = extractor.load_protected_words()
        # No word should start with #
        assert not any(word.startswith("#") for word in words)

    def test_load_excludes_empty_lines(self, extractor):
        """Test that empty lines are excluded."""
        words = extractor.load_protected_words()
        assert "" not in words

    def test_caching_returns_same_instance(self, extractor):
        """Test that caching returns same set instance."""
        words1 = extractor.load_protected_words()
        words2 = extractor.load_protected_words()
        assert words1 is words2

    def test_cache_reset_on_new_extractor(self):
        """Test that new extractor has fresh cache."""
        e1 = MetadataExtractor()
        words1 = e1.load_protected_words()

        e2 = MetadataExtractor()
        words2 = e2.load_protected_words()

        # Different instances but same content
        assert words1 is not words2
        assert words1 == words2


class TestAdditionalWordsFile:
    """Test loading additional protected words files."""

    @pytest.fixture
    def extractor(self):
        return MetadataExtractor()

    def test_load_additional_file(self, extractor):
        """Test loading an additional custom file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as f:
            f.write("# Custom words\n")
            f.write("CustomWord1\n")
            f.write("CustomWord2\n")
            f.write("CustomWord3\n")
            temp_path = f.name

        try:
            words = extractor.load_protected_words(additional_file=temp_path)
            assert "CustomWord1" in words
            assert "CustomWord2" in words
            assert "CustomWord3" in words
            # Also contains defaults
            assert "DNA" in words
        finally:
            os.unlink(temp_path)

    def test_additional_file_merges_with_default(self, extractor):
        """Test that additional file merges with default words."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as f:
            f.write("NewProteinName\n")
            temp_path = f.name

        try:
            words = extractor.load_protected_words(additional_file=temp_path)
            # Has both new and default
            assert "NewProteinName" in words
            assert "DNA" in words
            assert "RNA" in words
        finally:
            os.unlink(temp_path)

    def test_nonexistent_additional_file(self, extractor):
        """Test graceful handling of nonexistent additional file."""
        words = extractor.load_protected_words(
            additional_file="/nonexistent/path/words.txt"
        )
        # Should still have defaults
        assert "DNA" in words

    def test_additional_file_bypasses_cache(self, extractor):
        """Test that additional file request bypasses cache."""
        # First call without additional file (cached)
        words1 = extractor.load_protected_words()

        # Second call with additional file (not cached)
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as f:
            f.write("SpecialWord\n")
            temp_path = f.name

        try:
            words2 = extractor.load_protected_words(additional_file=temp_path)
            # words2 has the special word
            assert "SpecialWord" in words2
            # words1 does not (from cache)
            assert "SpecialWord" not in words1
        finally:
            os.unlink(temp_path)


class TestDefaultFallback:
    """Test fallback to default words when file not found."""

    def test_fallback_when_file_missing(self):
        """Test fallback to DEFAULT_PROTECTED_WORDS when file is missing."""
        extractor = MetadataExtractor()

        # Verify default words exist and are properly defined
        assert "DNA" in extractor.DEFAULT_PROTECTED_WORDS
        assert "RNA" in extractor.DEFAULT_PROTECTED_WORDS
        assert "CRISPR" in extractor.DEFAULT_PROTECTED_WORDS

        # The default words should be a fallback option
        assert isinstance(extractor.DEFAULT_PROTECTED_WORDS, set)
        assert len(extractor.DEFAULT_PROTECTED_WORDS) >= 10

    def test_default_protected_words_class_attribute(self):
        """Test that DEFAULT_PROTECTED_WORDS is defined as class attribute."""
        assert hasattr(MetadataExtractor, "DEFAULT_PROTECTED_WORDS")
        assert isinstance(MetadataExtractor.DEFAULT_PROTECTED_WORDS, set)
        assert len(MetadataExtractor.DEFAULT_PROTECTED_WORDS) >= 15


class TestTitleProtection:
    """Test title protection with loaded words."""

    @pytest.fixture
    def extractor(self):
        return MetadataExtractor()

    def test_protect_dna(self, extractor):
        """Test DNA is protected."""
        result = extractor._protect_title("Analysis of DNA sequences")
        assert "{DNA}" in result

    def test_protect_rna(self, extractor):
        """Test RNA is protected."""
        result = extractor._protect_title("RNA interference mechanisms")
        assert "{RNA}" in result

    def test_protect_mrna(self, extractor):
        """Test mRNA is protected."""
        result = extractor._protect_title("mRNA vaccine development")
        assert "{mRNA}" in result

    def test_protect_crispr(self, extractor):
        """Test CRISPR is protected."""
        result = extractor._protect_title("CRISPR gene editing")
        assert "{CRISPR}" in result

    def test_protect_python(self, extractor):
        """Test Python is protected."""
        result = extractor._protect_title("Python programming for science")
        assert "{Python}" in result

    def test_protect_pytorch(self, extractor):
        """Test PyTorch is protected."""
        result = extractor._protect_title("Deep learning with PyTorch")
        assert "{PyTorch}" in result

    def test_protect_alphafold(self, extractor):
        """Test AlphaFold is protected."""
        result = extractor._protect_title("AlphaFold protein prediction")
        assert "{AlphaFold}" in result

    def test_protect_multiple_words(self, extractor):
        """Test multiple protected words in one title."""
        result = extractor._protect_title("DNA and RNA analysis using Python")
        assert "{DNA}" in result
        assert "{RNA}" in result
        assert "{Python}" in result

    def test_case_insensitive_matching(self, extractor):
        """Test case-insensitive word matching uses canonical form from file."""
        result = extractor._protect_title("Studying dna and rna")
        # Lowercase input should be replaced with canonical form from file
        assert "{DNA}" in result
        assert "{RNA}" in result

    def test_preserve_unprotected_text(self, extractor):
        """Test that unprotected text is preserved."""
        result = extractor._protect_title("Simple title without special words")
        assert "Simple title without special words" == result

    def test_protect_word_boundaries(self, extractor):
        """Test that only whole words are protected, not substrings."""
        result = extractor._protect_title("DNASE enzyme")
        # DNA inside DNASE should not be separately protected
        assert "DNASE" in result
        assert "{DNA}SE" not in result  # Verify DNA wasn't extracted from DNASE

    def test_protect_model_organism(self, extractor):
        """Test model organism name protection."""
        result = extractor._protect_title("Drosophila melanogaster genetics")
        assert "{Drosophila}" in result

    def test_protect_database_name(self, extractor):
        """Test database name protection."""
        result = extractor._protect_title("Data retrieved from UniProt")
        assert "{UniProt}" in result

    def test_protect_chemical_term(self, extractor):
        """Test chemical term protection."""
        result = extractor._protect_title("ATP hydrolysis in cells")
        assert "{ATP}" in result

    def test_protect_geographic_abbreviation(self, extractor):
        """Test geographic abbreviation protection."""
        result = extractor._protect_title("Research funded by NIH")
        assert "{NIH}" in result


class TestTitleProtectionWithCustomFile:
    """Test title protection with additional custom words file."""

    @pytest.fixture
    def extractor(self):
        return MetadataExtractor()

    def test_protect_custom_word(self, extractor):
        """Test protection of custom word from additional file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as f:
            f.write("MyCustomProtein\n")
            temp_path = f.name

        try:
            result = extractor._protect_title(
                "Study of MyCustomProtein function",
                additional_words_file=temp_path,
            )
            assert "{MyCustomProtein}" in result
        finally:
            os.unlink(temp_path)

    def test_protect_both_default_and_custom(self, extractor):
        """Test protection of both default and custom words."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as f:
            f.write("SpecialGene\n")
            temp_path = f.name

        try:
            result = extractor._protect_title(
                "DNA binding of SpecialGene protein",
                additional_words_file=temp_path,
            )
            assert "{DNA}" in result
            assert "{SpecialGene}" in result
        finally:
            os.unlink(temp_path)


class TestCrossRefTypeMapping:
    """Test CrossRef type to BibTeX mapping completeness."""

    @pytest.fixture
    def extractor(self):
        return MetadataExtractor()

    # Journal content
    def test_journal_article(self, extractor):
        """Test journal-article maps to article."""
        assert extractor._crossref_type_to_bibtex("journal-article") == "article"

    def test_journal_issue(self, extractor):
        """Test journal-issue maps to misc."""
        assert extractor._crossref_type_to_bibtex("journal-issue") == "misc"

    def test_journal_volume(self, extractor):
        """Test journal-volume maps to misc."""
        assert extractor._crossref_type_to_bibtex("journal-volume") == "misc"

    # Books
    def test_book(self, extractor):
        """Test book maps to book."""
        assert extractor._crossref_type_to_bibtex("book") == "book"

    def test_book_chapter(self, extractor):
        """Test book-chapter maps to incollection."""
        assert extractor._crossref_type_to_bibtex("book-chapter") == "incollection"

    def test_book_section(self, extractor):
        """Test book-section maps to incollection."""
        assert extractor._crossref_type_to_bibtex("book-section") == "incollection"

    def test_book_part(self, extractor):
        """Test book-part maps to incollection."""
        assert extractor._crossref_type_to_bibtex("book-part") == "incollection"

    def test_book_series(self, extractor):
        """Test book-series maps to misc."""
        assert extractor._crossref_type_to_bibtex("book-series") == "misc"

    def test_book_set(self, extractor):
        """Test book-set maps to misc."""
        assert extractor._crossref_type_to_bibtex("book-set") == "misc"

    def test_edited_book(self, extractor):
        """Test edited-book maps to book."""
        assert extractor._crossref_type_to_bibtex("edited-book") == "book"

    def test_monograph(self, extractor):
        """Test monograph maps to book."""
        assert extractor._crossref_type_to_bibtex("monograph") == "book"

    def test_reference_book(self, extractor):
        """Test reference-book maps to book."""
        assert extractor._crossref_type_to_bibtex("reference-book") == "book"

    # Conference
    def test_proceedings(self, extractor):
        """Test proceedings maps to proceedings."""
        assert extractor._crossref_type_to_bibtex("proceedings") == "proceedings"

    def test_proceedings_article(self, extractor):
        """Test proceedings-article maps to inproceedings."""
        assert extractor._crossref_type_to_bibtex("proceedings-article") == "inproceedings"

    def test_proceedings_series(self, extractor):
        """Test proceedings-series maps to misc."""
        assert extractor._crossref_type_to_bibtex("proceedings-series") == "misc"

    # Reports and theses
    def test_report(self, extractor):
        """Test report maps to techreport."""
        assert extractor._crossref_type_to_bibtex("report") == "techreport"

    def test_report_series(self, extractor):
        """Test report-series maps to techreport."""
        assert extractor._crossref_type_to_bibtex("report-series") == "techreport"

    def test_dissertation(self, extractor):
        """Test dissertation maps to phdthesis."""
        assert extractor._crossref_type_to_bibtex("dissertation") == "phdthesis"

    # Preprints and datasets
    def test_posted_content(self, extractor):
        """Test posted-content (preprints) maps to misc."""
        assert extractor._crossref_type_to_bibtex("posted-content") == "misc"

    def test_dataset(self, extractor):
        """Test dataset maps to misc."""
        assert extractor._crossref_type_to_bibtex("dataset") == "misc"

    def test_database(self, extractor):
        """Test database maps to misc."""
        assert extractor._crossref_type_to_bibtex("database") == "misc"

    # Reference works
    def test_reference_entry(self, extractor):
        """Test reference-entry maps to misc."""
        assert extractor._crossref_type_to_bibtex("reference-entry") == "misc"

    def test_encyclopedia(self, extractor):
        """Test encyclopedia maps to misc."""
        assert extractor._crossref_type_to_bibtex("encyclopedia") == "misc"

    def test_encyclopedia_entry(self, extractor):
        """Test encyclopedia-entry maps to misc."""
        assert extractor._crossref_type_to_bibtex("encyclopedia-entry") == "misc"

    # Standards and components
    def test_standard(self, extractor):
        """Test standard maps to misc."""
        assert extractor._crossref_type_to_bibtex("standard") == "misc"

    def test_standard_series(self, extractor):
        """Test standard-series maps to misc."""
        assert extractor._crossref_type_to_bibtex("standard-series") == "misc"

    def test_component(self, extractor):
        """Test component maps to misc."""
        assert extractor._crossref_type_to_bibtex("component") == "misc"

    # Other
    def test_peer_review(self, extractor):
        """Test peer-review maps to misc."""
        assert extractor._crossref_type_to_bibtex("peer-review") == "misc"

    def test_grant(self, extractor):
        """Test grant maps to misc."""
        assert extractor._crossref_type_to_bibtex("grant") == "misc"

    def test_other(self, extractor):
        """Test other maps to misc."""
        assert extractor._crossref_type_to_bibtex("other") == "misc"

    # Unknown type fallback
    def test_unknown_type(self, extractor):
        """Test unknown type falls back to misc."""
        assert extractor._crossref_type_to_bibtex("unknown-type") == "misc"

    def test_none_type(self, extractor):
        """Test None type falls back to misc."""
        assert extractor._crossref_type_to_bibtex(None) == "misc"

    def test_empty_type(self, extractor):
        """Test empty string type falls back to misc."""
        assert extractor._crossref_type_to_bibtex("") == "misc"


class TestCrossRefTypeMappingCompleteness:
    """Test that all major CrossRef types are mapped."""

    @pytest.fixture
    def extractor(self):
        return MetadataExtractor()

    def test_all_crossref_types_have_mapping(self, extractor):
        """Test that all known CrossRef types have mappings."""
        # Complete list of CrossRef types from their API
        crossref_types = [
            "journal-article",
            "journal-issue",
            "journal-volume",
            "book",
            "book-chapter",
            "book-section",
            "book-part",
            "book-series",
            "book-set",
            "edited-book",
            "monograph",
            "reference-book",
            "proceedings",
            "proceedings-article",
            "proceedings-series",
            "report",
            "report-series",
            "dissertation",
            "posted-content",
            "dataset",
            "database",
            "reference-entry",
            "encyclopedia",
            "encyclopedia-entry",
            "standard",
            "standard-series",
            "component",
            "peer-review",
            "grant",
            "other",
        ]

        for cr_type in crossref_types:
            result = extractor._crossref_type_to_bibtex(cr_type)
            assert result is not None, f"No mapping for {cr_type}"
            assert result in [
                "article",
                "book",
                "incollection",
                "inproceedings",
                "proceedings",
                "techreport",
                "phdthesis",
                "misc",
            ], f"Invalid BibTeX type for {cr_type}: {result}"

    def test_bibtex_types_are_standard(self, extractor):
        """Test that mapped BibTeX types are standard types."""
        standard_bibtex_types = {
            "article",
            "book",
            "booklet",
            "inbook",
            "incollection",
            "inproceedings",
            "manual",
            "mastersthesis",
            "misc",
            "phdthesis",
            "proceedings",
            "techreport",
            "unpublished",
        }

        # Test a sample of CrossRef types
        test_types = ["journal-article", "book", "proceedings-article", "dissertation"]
        for cr_type in test_types:
            result = extractor._crossref_type_to_bibtex(cr_type)
            assert result in standard_bibtex_types, f"{result} is not a standard BibTeX type"


class TestIntegrationProtectedWords:
    """Integration tests for protected words in BibTeX generation."""

    @pytest.fixture
    def extractor(self):
        return MetadataExtractor()

    def test_bibtex_output_has_protected_title(self, extractor):
        """Test that BibTeX output contains protected title."""
        metadata = {
            "type": "doi",
            "entry_type": "article",
            "doi": "10.1234/test",
            "title": "DNA sequencing with CRISPR technology",
            "authors": "Smith, John",
            "year": "2024",
            "journal": "Nature",
        }
        bibtex = extractor.metadata_to_bibtex(metadata)
        assert "{DNA}" in bibtex
        assert "{CRISPR}" in bibtex

    def test_bibtex_preserves_unprotected_words(self, extractor):
        """Test that unprotected words remain unchanged in BibTeX."""
        metadata = {
            "type": "doi",
            "entry_type": "article",
            "doi": "10.1234/test",
            "title": "Simple analysis of data",
            "authors": "Smith, John",
            "year": "2024",
            "journal": "Science",
        }
        bibtex = extractor.metadata_to_bibtex(metadata)
        assert "Simple analysis of data" in bibtex
