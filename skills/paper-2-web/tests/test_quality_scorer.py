"""Tests for quality_scorer module."""

import tempfile
from pathlib import Path

import pytest
from lib.quality_scorer import (
    QualityScore,
    QualityReport,
    validate_html,
    check_images_have_alt,
    check_heading_hierarchy,
    check_external_links_noopener,
    check_meta_tags,
    score_website,
    score_poster,
    score_video,
    score_all_components,
    format_quality_report,
)


class TestQualityScore:
    """Tests for QualityScore dataclass."""

    def test_score_creation(self):
        """Test creating QualityScore."""
        score = QualityScore(
            component="website",
            metric="html_valid",
            value=1.0,
            threshold=0.9,
            passed=True,
            severity="critical",
            details="Valid HTML",
        )
        assert score.component == "website"
        assert score.value == 1.0
        assert score.passed is True

    def test_score_to_dict(self):
        """Test score serialization."""
        score = QualityScore(
            component="website",
            metric="test",
            value=0.85,
            threshold=0.8,
            passed=True,
            severity="major",
        )
        d = score.to_dict()
        assert d["value"] == 0.85
        assert d["passed"] is True


class TestQualityReport:
    """Tests for QualityReport dataclass."""

    def test_report_creation(self):
        """Test creating QualityReport."""
        report = QualityReport(component="website")
        assert report.component == "website"
        assert report.passed is True
        assert report.overall_score == 0.0

    def test_add_score_passing(self):
        """Test adding passing score."""
        report = QualityReport(component="website")
        score = QualityScore(
            component="website",
            metric="test",
            value=1.0,
            threshold=0.9,
            passed=True,
            severity="major",
        )
        report.add_score(score)
        assert len(report.scores) == 1
        assert report.passed is True

    def test_add_score_critical_failure(self):
        """Test adding critical failure."""
        report = QualityReport(component="website")
        score = QualityScore(
            component="website",
            metric="test",
            value=0.0,
            threshold=0.9,
            passed=False,
            severity="critical",
            details="Failed check",
        )
        report.add_score(score)
        assert report.passed is False
        assert len(report.critical_failures) == 1

    def test_calculate_overall_weighted(self):
        """Test overall score calculation with weights."""
        report = QualityReport(component="website")
        report.add_score(QualityScore(
            component="website", metric="m1",
            value=1.0, threshold=0.9, passed=True, severity="critical"
        ))
        report.add_score(QualityScore(
            component="website", metric="m2",
            value=0.5, threshold=0.9, passed=False, severity="minor"
        ))
        report.calculate_overall()
        # Critical weighted 3x, minor 1x
        # Expected: (1.0 * 3 + 0.5 * 1) / (3 + 1) = 3.5 / 4 = 0.875
        assert report.overall_score == pytest.approx(0.875, rel=0.01)

    def test_report_to_dict(self):
        """Test report serialization."""
        report = QualityReport(component="website")
        d = report.to_dict()
        assert d["component"] == "website"
        assert "scores" in d

    def test_report_from_dict(self):
        """Test report deserialization."""
        data = {
            "component": "website",
            "overall_score": 0.9,
            "passed": True,
            "scores": [],
            "critical_failures": [],
            "recommendations": [],
        }
        report = QualityReport.from_dict(data)
        assert report.component == "website"
        assert report.overall_score == 0.9


class TestValidateHtml:
    """Tests for validate_html function."""

    def test_valid_html(self):
        """Test validation of valid HTML."""
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Test</title>
</head>
<body>
    <h1>Test</h1>
</body>
</html>"""
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
            f.write(html)
            path = Path(f.name)

        try:
            is_valid, issues = validate_html(path)
            assert is_valid is True
            assert len(issues) == 0
        finally:
            path.unlink()

    def test_missing_doctype(self):
        """Test detection of missing DOCTYPE."""
        html = """<html>
<head><title>Test</title></head>
<body></body>
</html>"""
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
            f.write(html)
            path = Path(f.name)

        try:
            is_valid, issues = validate_html(path)
            assert is_valid is False
            assert any("DOCTYPE" in i for i in issues)
        finally:
            path.unlink()

    def test_missing_title(self):
        """Test detection of missing title."""
        html = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body></body>
</html>"""
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
            f.write(html)
            path = Path(f.name)

        try:
            is_valid, issues = validate_html(path)
            assert any("title" in i.lower() for i in issues)
        finally:
            path.unlink()


class TestCheckImagesHaveAlt:
    """Tests for check_images_have_alt function."""

    def test_all_images_have_alt(self):
        """Test when all images have alt text."""
        html = """<!DOCTYPE html>
<html>
<body>
    <img src="img1.png" alt="Description 1">
    <img src="img2.png" alt="Description 2">
</body>
</html>"""
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
            f.write(html)
            path = Path(f.name)

        try:
            score, missing = check_images_have_alt(path)
            assert score == 1.0
            assert len(missing) == 0
        finally:
            path.unlink()

    def test_some_images_missing_alt(self):
        """Test when some images missing alt text."""
        html = """<!DOCTYPE html>
<html>
<body>
    <img src="img1.png" alt="Description">
    <img src="img2.png">
</body>
</html>"""
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
            f.write(html)
            path = Path(f.name)

        try:
            score, missing = check_images_have_alt(path)
            assert score == 0.5
            assert len(missing) == 1
            assert "img2.png" in missing[0]
        finally:
            path.unlink()


class TestCheckHeadingHierarchy:
    """Tests for check_heading_hierarchy function."""

    def test_proper_hierarchy(self):
        """Test proper heading hierarchy."""
        html = """<!DOCTYPE html>
<html>
<body>
    <h1>Title</h1>
    <h2>Section</h2>
    <h3>Subsection</h3>
</body>
</html>"""
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
            f.write(html)
            path = Path(f.name)

        try:
            score, issues = check_heading_hierarchy(path)
            assert score == 1.0
            assert len(issues) == 0
        finally:
            path.unlink()

    def test_skipped_heading_level(self):
        """Test detection of skipped heading level."""
        html = """<!DOCTYPE html>
<html>
<body>
    <h1>Title</h1>
    <h4>Skipped to h4</h4>
</body>
</html>"""
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
            f.write(html)
            path = Path(f.name)

        try:
            score, issues = check_heading_hierarchy(path)
            assert score < 1.0
            assert any("skipped" in i.lower() for i in issues)
        finally:
            path.unlink()


class TestScoreWebsite:
    """Tests for score_website function."""

    def test_score_valid_website(self):
        """Test scoring valid website."""
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width">
    <meta name="description" content="Test description">
    <title>Test Page</title>
</head>
<body>
    <h1>Test</h1>
    <img src="test.png" alt="Test image">
</body>
</html>"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            website_dir = tmppath / "website"
            website_dir.mkdir()
            (website_dir / "index.html").write_text(html)

            report = score_website(tmppath)
            assert report.component == "website"
            assert report.overall_score > 0.5

    def test_score_missing_website(self):
        """Test scoring when website directory missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report = score_website(Path(tmpdir))
            assert report.passed is False
            assert "not found" in report.critical_failures[0]


class TestScorePoster:
    """Tests for score_poster function."""

    def test_score_missing_poster(self):
        """Test scoring when poster directory missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report = score_poster(Path(tmpdir))
            assert report.passed is False
            assert "not found" in report.critical_failures[0]


class TestScoreVideo:
    """Tests for score_video function."""

    def test_score_missing_video(self):
        """Test scoring when video directory missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report = score_video(Path(tmpdir))
            assert report.passed is False
            assert "not found" in report.critical_failures[0]


class TestScoreAllComponents:
    """Tests for score_all_components function."""

    def test_score_only_existing_components(self):
        """Test that only existing components are scored."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create only website
            website_dir = tmppath / "website"
            website_dir.mkdir()
            (website_dir / "index.html").write_text("<!DOCTYPE html><html><head><title>Test</title></head><body></body></html>")

            reports = score_all_components(tmppath)
            assert "website" in reports
            assert "poster" not in reports
            assert "video" not in reports


class TestFormatQualityReport:
    """Tests for format_quality_report function."""

    def test_format_passing_report(self):
        """Test formatting passing report."""
        report = QualityReport(component="website")
        report.overall_score = 0.95
        report.passed = True
        report.add_score(QualityScore(
            component="website", metric="test",
            value=0.95, threshold=0.9, passed=True, severity="major"
        ))

        formatted = format_quality_report(report)
        assert "website" in formatted
        assert "PASSED" in formatted
        assert "95" in formatted  # 95%

    def test_format_failing_report(self):
        """Test formatting failing report."""
        report = QualityReport(component="website")
        report.passed = False
        report.critical_failures = ["HTML invalid"]

        formatted = format_quality_report(report)
        assert "FAILED" in formatted
        assert "Critical" in formatted


class TestDeterminism:
    """Tests for deterministic behavior."""

    def test_validate_html_deterministic(self):
        """Test that HTML validation is deterministic."""
        html = """<!DOCTYPE html><html><head><title>Test</title></head><body></body></html>"""
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
            f.write(html)
            path = Path(f.name)

        try:
            results = [validate_html(path) for _ in range(3)]
            assert all(r == results[0] for r in results)
        finally:
            path.unlink()

    def test_score_website_deterministic(self):
        """Test that website scoring is deterministic."""
        html = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Test</title></head>
<body><h1>Test</h1></body>
</html>"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            website_dir = tmppath / "website"
            website_dir.mkdir()
            (website_dir / "index.html").write_text(html)

            scores = [score_website(tmppath).overall_score for _ in range(3)]
            assert all(s == scores[0] for s in scores)
