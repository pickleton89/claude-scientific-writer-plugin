"""
Comprehensive test suite for citation key generation and collision detection.

Tests cover:
- Basic citation key generation from metadata
- Author name parsing (various formats)
- Year extraction and fallbacks
- Title keyword extraction
- Collision detection with suffix generation
- Edge cases and error handling
"""

import pytest
import sys
import os

# Add scripts directory to path
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "scripts")
)

from extract_metadata import MetadataExtractor


class TestBasicCitationKeyGeneration:
    """Test basic citation key generation without collision detection."""

    @pytest.fixture
    def extractor(self):
        return MetadataExtractor()

    # Author parsing tests
    def test_simple_author_lastname_first(self, extractor):
        """Test author in 'Lastname, Firstname' format."""
        metadata = {
            "authors": "Smith, John",
            "year": "2024",
            "title": "Machine learning approaches",
        }
        key = extractor._generate_citation_key(metadata)
        assert key == "Smith2024machine"

    def test_simple_author_firstname_last(self, extractor):
        """Test author in 'Firstname Lastname' format."""
        metadata = {
            "authors": "John Smith",
            "year": "2024",
            "title": "Machine learning approaches",
        }
        key = extractor._generate_citation_key(metadata)
        assert key == "Smith2024machine"

    def test_multiple_authors(self, extractor):
        """Test multiple authors - should use first author."""
        metadata = {
            "authors": "Smith, John and Doe, Jane and Brown, Robert",
            "year": "2024",
            "title": "Collaborative research paper",
        }
        key = extractor._generate_citation_key(metadata)
        assert key == "Smith2024collaborative"

    def test_author_with_middle_name(self, extractor):
        """Test author with middle name."""
        metadata = {
            "authors": "Smith, John Robert",
            "year": "2024",
            "title": "Research findings",
        }
        key = extractor._generate_citation_key(metadata)
        assert key == "Smith2024research"

    def test_author_with_hyphenated_lastname(self, extractor):
        """Test author with hyphenated last name."""
        metadata = {
            "authors": "Garcia-Lopez, Maria",
            "year": "2024",
            "title": "Study results",
        }
        key = extractor._generate_citation_key(metadata)
        # Hyphens removed by cleaning
        assert key == "GarciaLopez2024study"

    def test_author_with_special_characters(self, extractor):
        """Test author with accented characters."""
        metadata = {
            "authors": "Müller, Hans",
            "year": "2024",
            "title": "German research",
        }
        key = extractor._generate_citation_key(metadata)
        # Non-ASCII removed by cleaning
        assert key == "Mller2024german"

    def test_author_with_apostrophe(self, extractor):
        """Test author with apostrophe in name."""
        metadata = {
            "authors": "O'Brien, Patrick",
            "year": "2024",
            "title": "Irish studies",
        }
        key = extractor._generate_citation_key(metadata)
        assert key == "OBrien2024irish"

    def test_empty_author(self, extractor):
        """Test fallback when no author provided."""
        metadata = {"authors": "", "year": "2024", "title": "Anonymous work"}
        key = extractor._generate_citation_key(metadata)
        assert key == "Unknown2024anonymous"

    def test_missing_author_key(self, extractor):
        """Test fallback when author key missing."""
        metadata = {"year": "2024", "title": "Authorless paper"}
        key = extractor._generate_citation_key(metadata)
        assert key == "Unknown2024authorless"

    def test_single_name_author(self, extractor):
        """Test author with single name (like 'Plato')."""
        metadata = {
            "authors": "Aristotle",
            "year": "350",
            "title": "Philosophical treatise",
        }
        key = extractor._generate_citation_key(metadata)
        assert key == "Aristotle350philosophical"

    # Year extraction tests
    def test_standard_year(self, extractor):
        """Test standard 4-digit year."""
        metadata = {
            "authors": "Smith, John",
            "year": "2024",
            "title": "Recent work",
        }
        key = extractor._generate_citation_key(metadata)
        assert "2024" in key

    def test_year_with_whitespace(self, extractor):
        """Test year with surrounding whitespace."""
        metadata = {
            "authors": "Smith, John",
            "year": "  2024  ",
            "title": "Research paper",
        }
        key = extractor._generate_citation_key(metadata)
        assert key == "Smith2024research"

    def test_empty_year(self, extractor):
        """Test fallback when year is empty."""
        metadata = {
            "authors": "Smith, John",
            "year": "",
            "title": "Undated work",
        }
        key = extractor._generate_citation_key(metadata)
        assert key == "SmithXXXXundated"

    def test_missing_year_key(self, extractor):
        """Test fallback when year key missing."""
        metadata = {"authors": "Smith, John", "title": "No year given"}
        key = extractor._generate_citation_key(metadata)
        assert "XXXX" in key

    def test_whitespace_only_year(self, extractor):
        """Test year that is only whitespace."""
        metadata = {
            "authors": "Smith, John",
            "year": "   ",
            "title": "Testing",
        }
        key = extractor._generate_citation_key(metadata)
        assert "XXXX" in key

    # Title keyword extraction tests
    def test_title_first_long_word(self, extractor):
        """Test extraction of first 4+ letter word from title."""
        metadata = {
            "authors": "Smith, John",
            "year": "2024",
            "title": "A new approach to machine learning",
        }
        key = extractor._generate_citation_key(metadata)
        assert key == "Smith2024approach"

    def test_title_with_short_words_first(self, extractor):
        """Test skipping short words at start of title."""
        metadata = {
            "authors": "Smith, John",
            "year": "2024",
            "title": "On the use of deep learning",
        }
        key = extractor._generate_citation_key(metadata)
        assert key == "Smith2024deep"

    def test_title_all_short_words(self, extractor):
        """Test fallback when all title words are short."""
        metadata = {
            "authors": "Smith, John",
            "year": "2024",
            "title": "A is not B",
        }
        key = extractor._generate_citation_key(metadata)
        assert key == "Smith2024paper"

    def test_empty_title(self, extractor):
        """Test fallback when title is empty."""
        metadata = {"authors": "Smith, John", "year": "2024", "title": ""}
        key = extractor._generate_citation_key(metadata)
        assert key == "Smith2024paper"

    def test_missing_title_key(self, extractor):
        """Test fallback when title key missing."""
        metadata = {"authors": "Smith, John", "year": "2024"}
        key = extractor._generate_citation_key(metadata)
        assert key == "Smith2024paper"

    def test_title_keyword_lowercase(self, extractor):
        """Test that keyword is lowercased."""
        metadata = {
            "authors": "Smith, John",
            "year": "2024",
            "title": "MACHINE Learning Study",
        }
        key = extractor._generate_citation_key(metadata)
        assert key == "Smith2024machine"

    def test_title_with_numbers(self, extractor):
        """Test title containing numbers."""
        metadata = {
            "authors": "Smith, John",
            "year": "2024",
            "title": "GPT-4 and LLM research",
        }
        key = extractor._generate_citation_key(metadata)
        assert key == "Smith2024research"

    def test_title_with_special_characters(self, extractor):
        """Test title with special characters."""
        metadata = {
            "authors": "Smith, John",
            "year": "2024",
            "title": "DNA-binding proteins: a review",
        }
        key = extractor._generate_citation_key(metadata)
        assert key == "Smith2024binding"


class TestSuffixGeneration:
    """Test alphabetic suffix generation for collision resolution."""

    @pytest.fixture
    def extractor(self):
        return MetadataExtractor()

    def test_suffix_index_0(self, extractor):
        """Test suffix for index 0 is 'a'."""
        assert extractor._generate_suffix(0) == "a"

    def test_suffix_index_1(self, extractor):
        """Test suffix for index 1 is 'b'."""
        assert extractor._generate_suffix(1) == "b"

    def test_suffix_index_25(self, extractor):
        """Test suffix for index 25 is 'z'."""
        assert extractor._generate_suffix(25) == "z"

    def test_suffix_index_26(self, extractor):
        """Test suffix for index 26 is 'aa'."""
        assert extractor._generate_suffix(26) == "aa"

    def test_suffix_index_27(self, extractor):
        """Test suffix for index 27 is 'ab'."""
        assert extractor._generate_suffix(27) == "ab"

    def test_suffix_index_51(self, extractor):
        """Test suffix for index 51 is 'az'."""
        assert extractor._generate_suffix(51) == "az"

    def test_suffix_index_52(self, extractor):
        """Test suffix for index 52 is 'ba'."""
        assert extractor._generate_suffix(52) == "ba"

    def test_suffix_sequence_first_26(self, extractor):
        """Test full sequence of first 26 suffixes."""
        expected = list("abcdefghijklmnopqrstuvwxyz")
        actual = [extractor._generate_suffix(i) for i in range(26)]
        assert actual == expected

    def test_suffix_two_letter_start(self, extractor):
        """Test two-letter suffixes start correctly."""
        assert extractor._generate_suffix(26) == "aa"
        assert extractor._generate_suffix(27) == "ab"
        assert extractor._generate_suffix(28) == "ac"

    def test_suffix_two_letter_end(self, extractor):
        """Test last two-letter suffix is 'zz' at index 701."""
        assert extractor._generate_suffix(701) == "zz"

    def test_suffix_three_letter_start(self, extractor):
        """Test three-letter suffixes start at index 702."""
        assert extractor._generate_suffix(702) == "aaa"
        assert extractor._generate_suffix(703) == "aab"
        assert extractor._generate_suffix(704) == "aac"

    def test_suffix_three_letter_progression(self, extractor):
        """Test three-letter suffix progression."""
        # aaz should be at 702 + 25 = 727
        assert extractor._generate_suffix(727) == "aaz"
        # aba should be at 702 + 26 = 728
        assert extractor._generate_suffix(728) == "aba"
        # baa should be at 702 + 676 = 1378
        assert extractor._generate_suffix(1378) == "baa"


class TestCollisionDetection:
    """Test citation key collision detection and resolution."""

    @pytest.fixture
    def extractor(self):
        return MetadataExtractor()

    def test_no_collision_empty_set(self, extractor):
        """Test no collision when existing_keys is empty set."""
        metadata = {
            "authors": "Smith, John",
            "year": "2024",
            "title": "Machine learning",
        }
        key = extractor._generate_citation_key(metadata, existing_keys=set())
        assert key == "Smith2024machine"

    def test_no_collision_none(self, extractor):
        """Test no collision check when existing_keys is None."""
        metadata = {
            "authors": "Smith, John",
            "year": "2024",
            "title": "Machine learning",
        }
        key = extractor._generate_citation_key(metadata, existing_keys=None)
        assert key == "Smith2024machine"

    def test_single_collision(self, extractor):
        """Test single collision adds 'a' suffix."""
        metadata = {
            "authors": "Smith, John",
            "year": "2024",
            "title": "Machine learning",
        }
        existing = {"Smith2024machine"}
        key = extractor._generate_citation_key(metadata, existing_keys=existing)
        assert key == "Smith2024machinea"

    def test_double_collision(self, extractor):
        """Test double collision adds 'b' suffix."""
        metadata = {
            "authors": "Smith, John",
            "year": "2024",
            "title": "Machine learning",
        }
        existing = {"Smith2024machine", "Smith2024machinea"}
        key = extractor._generate_citation_key(metadata, existing_keys=existing)
        assert key == "Smith2024machineb"

    def test_triple_collision(self, extractor):
        """Test triple collision adds 'c' suffix."""
        metadata = {
            "authors": "Smith, John",
            "year": "2024",
            "title": "Machine learning",
        }
        existing = {
            "Smith2024machine",
            "Smith2024machinea",
            "Smith2024machineb",
        }
        key = extractor._generate_citation_key(metadata, existing_keys=existing)
        assert key == "Smith2024machinec"

    def test_many_collisions(self, extractor):
        """Test many collisions cycle through alphabet."""
        metadata = {
            "authors": "Smith, John",
            "year": "2024",
            "title": "Machine learning",
        }
        # Create 26 existing keys
        existing = {"Smith2024machine"} | {
            f"Smith2024machine{chr(ord('a') + i)}" for i in range(26)
        }
        key = extractor._generate_citation_key(metadata, existing_keys=existing)
        assert key == "Smith2024machineaa"

    def test_collision_with_unrelated_keys(self, extractor):
        """Test no collision when existing keys are unrelated."""
        metadata = {
            "authors": "Smith, John",
            "year": "2024",
            "title": "Machine learning",
        }
        existing = {"Jones2023deep", "Brown2022neural", "Lee2024protein"}
        key = extractor._generate_citation_key(metadata, existing_keys=existing)
        assert key == "Smith2024machine"

    def test_collision_accumulation(self, extractor):
        """Test building a set of keys incrementally."""
        keys = set()
        for i in range(5):
            metadata = {
                "authors": "Smith, John",
                "year": "2024",
                "title": "Protein folding studies",
            }
            key = extractor._generate_citation_key(metadata, existing_keys=keys)
            keys.add(key)

        expected = {
            "Smith2024protein",
            "Smith2024proteina",
            "Smith2024proteinb",
            "Smith2024proteinc",
            "Smith2024proteind",
        }
        assert keys == expected

    def test_collision_with_different_metadata(self, extractor):
        """Test collision detection with different metadata yielding same base key."""
        keys = set()

        # First paper
        m1 = {
            "authors": "Smith, Alice",
            "year": "2024",
            "title": "Protein structure prediction",
        }
        k1 = extractor._generate_citation_key(m1, existing_keys=keys)
        keys.add(k1)

        # Second paper - different author but same last name/year/keyword
        m2 = {
            "authors": "Smith, Bob",
            "year": "2024",
            "title": "Protein folding dynamics",
        }
        k2 = extractor._generate_citation_key(m2, existing_keys=keys)
        keys.add(k2)

        assert k1 == "Smith2024protein"
        assert k2 == "Smith2024proteina"


class TestEdgeCases:
    """Test edge cases and unusual inputs."""

    @pytest.fixture
    def extractor(self):
        return MetadataExtractor()

    def test_empty_metadata(self, extractor):
        """Test completely empty metadata dict."""
        key = extractor._generate_citation_key({})
        assert key == "UnknownXXXXpaper"

    def test_none_values(self, extractor):
        """Test metadata with None values."""
        metadata = {"authors": None, "year": None, "title": None}
        key = extractor._generate_citation_key(metadata)
        # None becomes empty string via .get() default
        assert key == "UnknownXXXXpaper"

    def test_very_long_author_name(self, extractor):
        """Test very long author name."""
        long_name = "Superlongauthorlastname" + "x" * 100
        metadata = {
            "authors": f"{long_name}, John",
            "year": "2024",
            "title": "Testing",
        }
        key = extractor._generate_citation_key(metadata)
        assert long_name in key

    def test_very_long_title(self, extractor):
        """Test very long title."""
        long_title = "A " + "comprehensive " * 50 + "study"
        metadata = {
            "authors": "Smith, John",
            "year": "2024",
            "title": long_title,
        }
        key = extractor._generate_citation_key(metadata)
        assert key == "Smith2024comprehensive"

    def test_unicode_title(self, extractor):
        """Test title with unicode characters."""
        metadata = {
            "authors": "Smith, John",
            "year": "2024",
            "title": "Étude sur les protéines",
        }
        key = extractor._generate_citation_key(metadata)
        # Should extract 'tude' as first 4+ letter word (after É is stripped)
        assert "Smith2024" in key

    def test_numeric_author(self, extractor):
        """Test author that is numeric (edge case)."""
        metadata = {
            "authors": "12345",
            "year": "2024",
            "title": "Strange author name",
        }
        key = extractor._generate_citation_key(metadata)
        # Numeric chars stripped from last name
        assert key == "2024strange"

    def test_whitespace_everywhere(self, extractor):
        """Test metadata with excessive whitespace."""
        metadata = {
            "authors": "  Smith  ,  John  ",
            "year": "  2024  ",
            "title": "  Machine   learning  ",
        }
        key = extractor._generate_citation_key(metadata)
        assert key == "Smith2024machine"

    def test_author_only_firstname(self, extractor):
        """Test author with only first name no comma."""
        metadata = {
            "authors": "Prince",
            "year": "2020",
            "title": "Musical genius",
        }
        key = extractor._generate_citation_key(metadata)
        assert key == "Prince2020musical"

    def test_empty_string_author(self, extractor):
        """Test empty string author."""
        metadata = {
            "authors": "",
            "year": "2024",
            "title": "Unknown authorship",
        }
        key = extractor._generate_citation_key(metadata)
        assert key == "Unknown2024unknown"


class TestIntegration:
    """Integration tests for citation key generation."""

    @pytest.fixture
    def extractor(self):
        return MetadataExtractor()

    def test_real_world_doi_metadata(self, extractor):
        """Test with realistic DOI metadata structure."""
        metadata = {
            "type": "doi",
            "entry_type": "article",
            "doi": "10.1038/s41586-021-03819-2",
            "title": "Highly accurate protein structure prediction with AlphaFold",
            "authors": "Jumper, John and Evans, Richard and Pritzel, Alexander",
            "year": "2021",
            "journal": "Nature",
            "volume": "596",
            "pages": "583-589",
        }
        key = extractor._generate_citation_key(metadata)
        assert key == "Jumper2021highly"

    def test_real_world_pubmed_metadata(self, extractor):
        """Test with realistic PubMed metadata structure."""
        metadata = {
            "type": "pmid",
            "entry_type": "article",
            "pmid": "34265844",
            "title": "Accurate prediction of protein structures and interactions",
            "authors": "Baek, Minkyung and DiMaio, Frank",
            "year": "2021",
            "journal": "Science",
        }
        key = extractor._generate_citation_key(metadata)
        assert key == "Baek2021accurate"

    def test_real_world_arxiv_metadata(self, extractor):
        """Test with realistic arXiv metadata structure."""
        metadata = {
            "type": "arxiv",
            "entry_type": "misc",
            "arxiv_id": "2103.14030",
            "title": "Learning Transferable Visual Models From Natural Language",
            "authors": "Radford, Alec and Kim, Jong Wook and Hallacy, Chris",
            "year": "2021",
        }
        key = extractor._generate_citation_key(metadata)
        assert key == "Radford2021learning"

    def test_bibliography_building(self, extractor):
        """Test building a complete bibliography with collision handling."""
        papers = [
            {"authors": "Smith, John", "year": "2024", "title": "Deep learning for proteins"},
            {"authors": "Smith, Alice", "year": "2024", "title": "Deep neural networks"},
            {"authors": "Smith, Bob", "year": "2024", "title": "Deep reinforcement learning"},
            {"authors": "Jones, Mary", "year": "2024", "title": "Protein folding"},
            {"authors": "Smith, Carol", "year": "2024", "title": "Deep architectures"},
        ]

        keys = set()
        generated = []
        for paper in papers:
            key = extractor._generate_citation_key(paper, existing_keys=keys)
            keys.add(key)
            generated.append(key)

        # All keys should be unique
        assert len(generated) == len(set(generated))

        # First three Smiths with 'deep' keyword should have suffixes
        assert "Smith2024deep" in generated
        assert "Smith2024deepa" in generated
        assert "Smith2024deepb" in generated
        assert "Smith2024deepc" in generated
        assert "Jones2024protein" in generated
