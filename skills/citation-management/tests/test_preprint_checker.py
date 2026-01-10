"""
Comprehensive test suite for preprint status checking.

Tests cover:
- Preprint source identification (arXiv, bioRxiv, medRxiv)
- BibTeX parsing for preprint entries
- Report generation and structure
- Edge cases and error handling

Note: Tests that would require actual API calls use mocking to avoid
network dependencies and rate limiting issues.
"""

import pytest
import sys
import os
import tempfile
import json
from unittest.mock import Mock, patch

# Add scripts directory to path
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "scripts")
)

from check_preprint_status import (
    PreprintChecker,
    PreprintSource,
    PreprintInfo,
    CheckReport,
)


class TestPreprintSourceIdentification:
    """Test identification of preprint sources from BibTeX entries."""

    @pytest.fixture
    def checker(self):
        return PreprintChecker(verbose=False)

    # arXiv identification tests

    def test_identify_arxiv_from_eprint(self, checker):
        """Test arXiv identification from eprint field."""
        entry = {
            'fields': {
                'eprint': '2103.14030',
            }
        }
        source, identifier = checker.identify_preprint_source(entry)
        assert source == PreprintSource.ARXIV
        assert identifier == '2103.14030'

    def test_identify_arxiv_with_version(self, checker):
        """Test arXiv identification with version number."""
        entry = {
            'fields': {
                'eprint': '2103.14030v2',
            }
        }
        source, identifier = checker.identify_preprint_source(entry)
        assert source == PreprintSource.ARXIV
        assert identifier == '2103.14030v2'

    def test_identify_arxiv_from_archiveprefix(self, checker):
        """Test arXiv identification from archiveprefix field."""
        entry = {
            'fields': {
                'archiveprefix': 'arXiv',
                'eprint': '1906.08237',
            }
        }
        source, identifier = checker.identify_preprint_source(entry)
        assert source == PreprintSource.ARXIV
        assert identifier == '1906.08237'

    def test_identify_arxiv_from_howpublished(self, checker):
        """Test arXiv identification from howpublished field."""
        entry = {
            'fields': {
                'howpublished': 'arXiv',
                'url': 'https://arxiv.org/abs/2103.14030',
            }
        }
        source, identifier = checker.identify_preprint_source(entry)
        assert source == PreprintSource.ARXIV
        assert '2103.14030' in identifier

    def test_identify_arxiv_from_url(self, checker):
        """Test arXiv identification from URL field."""
        entry = {
            'fields': {
                'url': 'https://arxiv.org/abs/2201.12345v1',
            }
        }
        source, identifier = checker.identify_preprint_source(entry)
        assert source == PreprintSource.ARXIV
        assert '2201.12345' in identifier

    def test_arxiv_id_validation_rejects_invalid(self, checker):
        """Test that invalid arXiv IDs are not matched."""
        entry = {
            'fields': {
                'eprint': 'not-an-arxiv-id',
            }
        }
        source, identifier = checker.identify_preprint_source(entry)
        assert source == PreprintSource.UNKNOWN

    def test_arxiv_old_format_not_matched(self, checker):
        """Test that old arXiv format (pre-2007) requires URL extraction."""
        # Old format like hep-th/9901001 is not directly supported
        entry = {
            'fields': {
                'eprint': 'hep-th/9901001',
            }
        }
        source, identifier = checker.identify_preprint_source(entry)
        assert source == PreprintSource.UNKNOWN

    # bioRxiv identification tests

    def test_identify_biorxiv_from_doi(self, checker):
        """Test bioRxiv identification from DOI field."""
        entry = {
            'fields': {
                'doi': '10.1101/2021.07.09.451778',
                'howpublished': 'bioRxiv',
            }
        }
        source, identifier = checker.identify_preprint_source(entry)
        assert source == PreprintSource.BIORXIV
        assert identifier == '10.1101/2021.07.09.451778'

    def test_identify_biorxiv_from_url(self, checker):
        """Test bioRxiv identification from URL field."""
        entry = {
            'fields': {
                'url': 'https://www.biorxiv.org/content/10.1101/2021.07.09.451778',
                'doi': '10.1101/2021.07.09.451778',
            }
        }
        source, identifier = checker.identify_preprint_source(entry)
        assert source == PreprintSource.BIORXIV

    # medRxiv identification tests

    def test_identify_medrxiv_from_howpublished(self, checker):
        """Test medRxiv identification from howpublished field."""
        entry = {
            'fields': {
                'doi': '10.1101/2021.05.01.21256466',
                'howpublished': 'medRxiv',
            }
        }
        source, identifier = checker.identify_preprint_source(entry)
        assert source == PreprintSource.MEDRXIV
        assert identifier == '10.1101/2021.05.01.21256466'

    def test_identify_medrxiv_from_url(self, checker):
        """Test medRxiv identification from URL field."""
        entry = {
            'fields': {
                'url': 'https://www.medrxiv.org/content/10.1101/2021.05.01.21256466',
                'doi': '10.1101/2021.05.01.21256466',
            }
        }
        source, identifier = checker.identify_preprint_source(entry)
        assert source == PreprintSource.MEDRXIV

    # Non-preprint tests

    def test_regular_article_not_identified(self, checker):
        """Test that regular articles are not identified as preprints."""
        entry = {
            'fields': {
                'author': 'Smith, John',
                'title': 'A Regular Paper',
                'journal': 'Nature',
                'year': '2024',
                'doi': '10.1038/s41586-024-12345-6',
            }
        }
        source, identifier = checker.identify_preprint_source(entry)
        assert source == PreprintSource.UNKNOWN

    def test_book_not_identified(self, checker):
        """Test that books are not identified as preprints."""
        entry = {
            'fields': {
                'author': 'Jones, Mary',
                'title': 'A Book Title',
                'publisher': 'Academic Press',
                'year': '2023',
            }
        }
        source, identifier = checker.identify_preprint_source(entry)
        assert source == PreprintSource.UNKNOWN

    def test_empty_entry_not_identified(self, checker):
        """Test that empty entries return UNKNOWN."""
        entry = {'fields': {}}
        source, identifier = checker.identify_preprint_source(entry)
        assert source == PreprintSource.UNKNOWN
        assert identifier == ""


class TestBibTeXParsing:
    """Test BibTeX file parsing for preprint detection."""

    @pytest.fixture
    def checker(self):
        return PreprintChecker(verbose=False)

    def test_parse_arxiv_entry(self, checker):
        """Test parsing a BibTeX file with arXiv entry."""
        content = """@misc{Smith2024arxiv,
    author = {Smith, John},
    title = {A Preprint Paper},
    year = {2024},
    eprint = {2401.12345},
    archiveprefix = {arXiv},
    primaryclass = {cs.LG}
}
"""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.bib', delete=False, encoding='utf-8'
        ) as f:
            f.write(content)
            filepath = f.name

        try:
            entries = checker.parse_bibtex_file(filepath)
            assert len(entries) == 1
            assert entries[0]['key'] == 'Smith2024arxiv'
            assert entries[0]['fields'].get('eprint') == '2401.12345'
        finally:
            os.unlink(filepath)

    def test_parse_biorxiv_entry(self, checker):
        """Test parsing a BibTeX file with bioRxiv entry."""
        content = """@article{Jones2023biorxiv,
    author = {Jones, Mary},
    title = {A Biology Preprint},
    year = {2023},
    doi = {10.1101/2023.01.15.524000},
    howpublished = {bioRxiv}
}
"""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.bib', delete=False, encoding='utf-8'
        ) as f:
            f.write(content)
            filepath = f.name

        try:
            entries = checker.parse_bibtex_file(filepath)
            assert len(entries) == 1
            source, identifier = checker.identify_preprint_source(entries[0])
            assert source == PreprintSource.BIORXIV
        finally:
            os.unlink(filepath)

    def test_parse_mixed_file(self, checker):
        """Test parsing a file with preprints and regular articles."""
        content = """@misc{Preprint2024,
    author = {Author, First},
    title = {Preprint Paper},
    year = {2024},
    eprint = {2401.00001}
}

@article{Regular2024,
    author = {Author, Second},
    title = {Regular Paper},
    journal = {Nature},
    year = {2024},
    doi = {10.1038/s41586-024-00001-1}
}

@misc{AnotherPreprint2024,
    author = {Author, Third},
    title = {Another Preprint},
    year = {2024},
    doi = {10.1101/2024.01.01.123456},
    howpublished = {bioRxiv}
}
"""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.bib', delete=False, encoding='utf-8'
        ) as f:
            f.write(content)
            filepath = f.name

        try:
            entries = checker.parse_bibtex_file(filepath)
            assert len(entries) == 3

            # Count preprints
            preprint_count = 0
            for entry in entries:
                source, _ = checker.identify_preprint_source(entry)
                if source != PreprintSource.UNKNOWN:
                    preprint_count += 1

            assert preprint_count == 2
        finally:
            os.unlink(filepath)

    def test_parse_empty_file(self, checker):
        """Test parsing an empty BibTeX file."""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.bib', delete=False, encoding='utf-8'
        ) as f:
            f.write("")
            filepath = f.name

        try:
            entries = checker.parse_bibtex_file(filepath)
            assert len(entries) == 0
        finally:
            os.unlink(filepath)

    def test_parse_file_not_found(self, checker):
        """Test handling of non-existent file."""
        entries = checker.parse_bibtex_file('/nonexistent/path/file.bib')
        assert len(entries) == 0


class TestReportGeneration:
    """Test report generation and structure."""

    def test_check_report_structure(self):
        """Test CheckReport dataclass structure."""
        report = CheckReport(
            filepath="test.bib",
            check_date="2024-01-10T12:00:00Z",
            total_entries=10,
            total_preprints=3,
        )
        assert report.filepath == "test.bib"
        assert report.total_entries == 10
        assert report.total_preprints == 3
        assert len(report.now_published) == 0
        assert len(report.still_preprint) == 0
        assert len(report.errors) == 0

    def test_check_report_to_dict(self):
        """Test CheckReport serialization to dictionary."""
        report = CheckReport(
            filepath="test.bib",
            check_date="2024-01-10T12:00:00Z",
            total_entries=10,
            total_preprints=3,
        )
        report.now_published.append(PreprintInfo(
            citation_key="Test2024",
            source=PreprintSource.ARXIV,
            identifier="2401.12345",
            is_published=True,
            published_doi="10.1234/test",
        ))

        d = report.to_dict()
        assert d['filepath'] == "test.bib"
        assert d['now_published_count'] == 1
        assert d['still_preprint_count'] == 0
        assert len(d['now_published']) == 1
        assert d['now_published'][0]['citation_key'] == "Test2024"

    def test_check_report_json_serializable(self):
        """Test that CheckReport can be serialized to JSON."""
        report = CheckReport(
            filepath="test.bib",
            check_date="2024-01-10T12:00:00Z",
            total_entries=5,
            total_preprints=2,
        )
        report.still_preprint.append(PreprintInfo(
            citation_key="Preprint2024",
            source=PreprintSource.BIORXIV,
            identifier="10.1101/2024.01.01.123456",
        ))

        # Should not raise
        json_str = json.dumps(report.to_dict(), default=str)
        assert json_str is not None

        # Should be parseable back
        parsed = json.loads(json_str)
        assert parsed['total_preprints'] == 2

    def test_preprint_info_structure(self):
        """Test PreprintInfo dataclass structure."""
        info = PreprintInfo(
            citation_key="Test2024",
            source=PreprintSource.ARXIV,
            identifier="2401.12345",
            title="Test Paper",
            is_published=True,
            published_doi="10.1234/test",
            published_venue="Nature",
        )
        assert info.citation_key == "Test2024"
        assert info.source == PreprintSource.ARXIV
        assert info.is_published is True
        assert info.published_doi == "10.1234/test"


class TestAPIChecking:
    """Test API checking with mocked responses."""

    @pytest.fixture
    def checker(self):
        return PreprintChecker(verbose=False)

    @patch('check_preprint_status.PreprintChecker.check_arxiv_published')
    @patch('check_preprint_status.PreprintChecker.check_biorxiv_published')
    def test_check_file_with_mocked_apis(
        self, mock_biorxiv, mock_arxiv, checker
    ):
        """Test check_file with mocked API responses."""
        # Setup mocks
        mock_arxiv.return_value = (True, "10.1234/published", "Nature")
        mock_biorxiv.return_value = (False, None, None)

        content = """@misc{Arxiv2024,
    author = {Smith, John},
    title = {arXiv Paper},
    year = {2024},
    eprint = {2401.12345}
}

@misc{Biorxiv2024,
    author = {Jones, Mary},
    title = {bioRxiv Paper},
    year = {2024},
    doi = {10.1101/2024.01.01.123456},
    howpublished = {bioRxiv}
}
"""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.bib', delete=False, encoding='utf-8'
        ) as f:
            f.write(content)
            filepath = f.name

        try:
            report = checker.check_file(filepath)

            assert report.total_entries == 2
            assert report.total_preprints == 2
            assert len(report.now_published) == 1
            assert len(report.still_preprint) == 1
            assert report.now_published[0].citation_key == "Arxiv2024"
            assert report.still_preprint[0].citation_key == "Biorxiv2024"
        finally:
            os.unlink(filepath)

    @patch('check_preprint_status.PreprintChecker.check_arxiv_published')
    def test_check_file_handles_api_errors(self, mock_arxiv, checker):
        """Test that API errors are captured in report."""
        # Setup mock to raise exception
        mock_arxiv.side_effect = Exception("API error")

        content = """@misc{Arxiv2024,
    author = {Smith, John},
    title = {arXiv Paper},
    year = {2024},
    eprint = {2401.12345}
}
"""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.bib', delete=False, encoding='utf-8'
        ) as f:
            f.write(content)
            filepath = f.name

        try:
            report = checker.check_file(filepath)

            assert report.total_preprints == 1
            assert len(report.errors) == 1
            assert "API error" in report.errors[0].error
        finally:
            os.unlink(filepath)


class TestArxivAPIResponse:
    """Test arXiv API response parsing."""

    @pytest.fixture
    def checker(self):
        return PreprintChecker(verbose=False)

    def test_arxiv_with_doi_field(self, checker):
        """Test parsing arXiv response with DOI field."""
        # The code uses regex: r'<arxiv:doi>([^<]+)</arxiv:doi>'
        # So the XML must have arxiv:doi tags without namespace declarations inside
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <arxiv:doi>10.1038/s41586-024-00001-1</arxiv:doi>
  </entry>
</feed>
"""
        mock_response.raise_for_status = Mock()

        with patch.object(checker.session, 'get', return_value=mock_response):
            with patch.object(checker, '_get_venue_from_doi', return_value="Nature"):
                is_published, doi, venue = checker.check_arxiv_published("2401.12345")

        assert is_published is True
        assert doi == "10.1038/s41586-024-00001-1"
        assert venue == "Nature"

    def test_arxiv_without_doi_field(self, checker):
        """Test parsing arXiv response without DOI field."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """<?xml version="1.0" encoding="UTF-8"?>
<feed>
  <entry>
    <title>A Preprint Paper</title>
  </entry>
</feed>
"""
        mock_response.raise_for_status = Mock()

        with patch.object(checker.session, 'get', return_value=mock_response):
            is_published, doi, venue = checker.check_arxiv_published("2401.12345")

        assert is_published is False
        assert doi is None

    def test_arxiv_with_journal_ref(self, checker):
        """Test parsing arXiv response with journal_ref field."""
        # The code uses regex: r'<arxiv:journal_ref>([^<]+)</arxiv:journal_ref>'
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <arxiv:journal_ref>Nature 612, 123-456 (2024)</arxiv:journal_ref>
  </entry>
</feed>
"""
        mock_response.raise_for_status = Mock()

        with patch.object(checker.session, 'get', return_value=mock_response):
            is_published, doi, venue = checker.check_arxiv_published("2401.12345")

        assert is_published is True
        assert venue == "Nature 612, 123-456 (2024)"


class TestBiorxivAPIResponse:
    """Test bioRxiv/CrossRef API response parsing."""

    @pytest.fixture
    def checker(self):
        return PreprintChecker(verbose=False)

    @patch.object(PreprintChecker, '_get_venue_from_doi')
    def test_biorxiv_with_published_relation(self, mock_venue, checker):
        """Test bioRxiv with is-preprint-of relation."""
        mock_venue.return_value = "Cell"

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'message': {
                'relation': {
                    'is-preprint-of': [
                        {'id': '10.1016/j.cell.2024.00001'}
                    ]
                }
            }
        }

        with patch.object(checker.session, 'get', return_value=mock_response):
            is_published, doi, venue = checker.check_biorxiv_published(
                "10.1101/2024.01.01.123456"
            )

        assert is_published is True
        assert doi == "10.1016/j.cell.2024.00001"
        assert venue == "Cell"

    def test_biorxiv_without_published_relation(self, checker):
        """Test bioRxiv without is-preprint-of relation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'message': {
                'relation': {}
            }
        }

        with patch.object(checker.session, 'get', return_value=mock_response):
            is_published, doi, venue = checker.check_biorxiv_published(
                "10.1101/2024.01.01.123456"
            )

        assert is_published is False
        assert doi is None

    def test_biorxiv_invalid_doi_prefix(self, checker):
        """Test that non-10.1101 DOIs return False."""
        is_published, doi, venue = checker.check_biorxiv_published(
            "10.1038/s41586-024-00001-1"  # Not a bioRxiv DOI
        )

        assert is_published is False
        assert doi is None


class TestPreprintSourceEnum:
    """Test PreprintSource enum."""

    def test_source_values(self):
        """Test that source enum has expected values."""
        assert PreprintSource.ARXIV.value == "arxiv"
        assert PreprintSource.BIORXIV.value == "biorxiv"
        assert PreprintSource.MEDRXIV.value == "medrxiv"
        assert PreprintSource.UNKNOWN.value == "unknown"

    def test_source_comparison(self):
        """Test source enum comparison."""
        assert PreprintSource.ARXIV != PreprintSource.BIORXIV
        assert PreprintSource.ARXIV == PreprintSource.ARXIV
