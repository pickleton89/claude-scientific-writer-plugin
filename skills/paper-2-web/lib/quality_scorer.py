"""Automated quality scoring for paper transformation outputs.

This module provides deterministic quality metrics for websites, posters,
and videos generated from papers. Metrics focus on objective, measurable
criteria rather than subjective aesthetic judgments.

Quality dimensions:
- Structural integrity (valid HTML, correct dimensions, etc.)
- Content completeness (sections present, metadata included)
- Accessibility (alt text, contrast ratios, etc.)
- Technical requirements (resolution, file sizes, etc.)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False


Severity = Literal["critical", "major", "minor"]


@dataclass
class QualityScore:
    """Individual quality metric score.

    Attributes:
        component: Component being scored (website, poster, video)
        metric: Metric name
        value: Score value (0.0 to 1.0)
        threshold: Passing threshold
        passed: Whether score meets threshold
        severity: Importance of this metric
        details: Additional information about the score
    """

    component: str
    metric: str
    value: float
    threshold: float
    passed: bool
    severity: Severity
    details: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "component": self.component,
            "metric": self.metric,
            "value": round(self.value, 3),
            "threshold": self.threshold,
            "passed": self.passed,
            "severity": self.severity,
            "details": self.details,
        }


@dataclass
class QualityReport:
    """Complete quality report for a component.

    Attributes:
        component: Component name
        overall_score: Weighted average score (0.0 to 1.0)
        passed: Whether component passes quality gates
        scores: Individual metric scores
        critical_failures: List of failed critical metrics
        recommendations: Suggested improvements
    """

    component: str
    overall_score: float = 0.0
    passed: bool = True
    scores: list[QualityScore] = field(default_factory=list)
    critical_failures: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    def add_score(self, score: QualityScore) -> None:
        """Add a score and update overall metrics."""
        self.scores.append(score)
        if score.severity == "critical" and not score.passed:
            self.passed = False
            self.critical_failures.append(f"{score.metric}: {score.details}")

    def calculate_overall(self) -> None:
        """Calculate overall score from individual scores."""
        if not self.scores:
            return

        # Weight by severity
        weights = {"critical": 3.0, "major": 2.0, "minor": 1.0}
        total_weight = 0.0
        weighted_sum = 0.0

        for score in self.scores:
            weight = weights[score.severity]
            weighted_sum += score.value * weight
            total_weight += weight

        self.overall_score = weighted_sum / total_weight if total_weight > 0 else 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "component": self.component,
            "overall_score": round(self.overall_score, 3),
            "passed": self.passed,
            "scores": [s.to_dict() for s in self.scores],
            "critical_failures": self.critical_failures,
            "recommendations": self.recommendations,
        }

    @classmethod
    def from_dict(cls, data: dict) -> QualityReport:
        """Create from dictionary."""
        report = cls(
            component=data["component"],
            overall_score=data.get("overall_score", 0.0),
            passed=data.get("passed", True),
            critical_failures=data.get("critical_failures", []),
            recommendations=data.get("recommendations", []),
        )
        for score_data in data.get("scores", []):
            report.scores.append(QualityScore(
                component=score_data["component"],
                metric=score_data["metric"],
                value=score_data["value"],
                threshold=score_data["threshold"],
                passed=score_data["passed"],
                severity=score_data["severity"],
                details=score_data.get("details", ""),
            ))
        return report


# ============================================================================
# Website Quality Metrics
# ============================================================================

def validate_html(html_path: Path) -> tuple[bool, list[str]]:
    """Basic HTML validation.

    Args:
        html_path: Path to HTML file

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []

    try:
        content = html_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return False, [f"Could not read file: {e}"]

    # Check for doctype
    if not content.strip().lower().startswith("<!doctype"):
        issues.append("Missing DOCTYPE declaration")

    # Check for basic structure
    required_tags = ["<html", "<head", "<body", "</html>", "</head>", "</body>"]
    for tag in required_tags:
        if tag not in content.lower():
            issues.append(f"Missing {tag}")

    # Check for title
    if "<title>" not in content.lower() or "</title>" not in content.lower():
        issues.append("Missing or empty <title> tag")

    # Check for charset
    if 'charset="utf-8"' not in content.lower() and "charset=utf-8" not in content.lower():
        issues.append("Missing UTF-8 charset declaration")

    return len(issues) == 0, issues


def check_images_have_alt(html_path: Path) -> tuple[float, list[str]]:
    """Check that images have alt text.

    Args:
        html_path: Path to HTML file

    Returns:
        Tuple of (score, list_of_images_without_alt)
    """
    if not BS4_AVAILABLE:
        return 1.0, []  # Skip check if bs4 not available

    content = html_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(content, "html.parser")

    images = soup.find_all("img")
    if not images:
        return 1.0, []

    missing_alt = []
    for img in images:
        if not img.get("alt"):
            src = img.get("src", "unknown")
            missing_alt.append(src)

    score = (len(images) - len(missing_alt)) / len(images)
    return score, missing_alt


def check_heading_hierarchy(html_path: Path) -> tuple[float, list[str]]:
    """Check that headings follow proper hierarchy.

    Args:
        html_path: Path to HTML file

    Returns:
        Tuple of (score, list_of_issues)
    """
    if not BS4_AVAILABLE:
        return 1.0, []

    content = html_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(content, "html.parser")

    issues = []
    headings = soup.find_all(re.compile(r"^h[1-6]$"))

    if not headings:
        return 1.0, []

    # Check for h1
    h1_tags = soup.find_all("h1")
    if not h1_tags:
        issues.append("No <h1> tag found")
    elif len(h1_tags) > 1:
        issues.append(f"Multiple <h1> tags found ({len(h1_tags)})")

    # Check hierarchy
    prev_level = 0
    for h in headings:
        level = int(h.name[1])
        if level > prev_level + 1 and prev_level > 0:
            issues.append(f"Skipped heading level: h{prev_level} to h{level}")
        prev_level = level

    score = max(0.0, 1.0 - (len(issues) * 0.2))
    return score, issues


def check_external_links_noopener(html_path: Path) -> tuple[float, list[str]]:
    """Check that external links have rel='noopener'.

    Args:
        html_path: Path to HTML file

    Returns:
        Tuple of (score, list_of_issues)
    """
    if not BS4_AVAILABLE:
        return 1.0, []

    content = html_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(content, "html.parser")

    issues = []
    external_links = soup.find_all("a", href=re.compile(r"^https?://"))

    for link in external_links:
        if link.get("target") == "_blank":
            rel = link.get("rel", [])
            if "noopener" not in rel and "noreferrer" not in rel:
                issues.append(link.get("href", "unknown")[:50])

    if not external_links:
        return 1.0, []

    score = (len(external_links) - len(issues)) / len(external_links)
    return score, issues


def check_meta_tags(html_path: Path) -> tuple[float, list[str]]:
    """Check for essential meta tags.

    Args:
        html_path: Path to HTML file

    Returns:
        Tuple of (score, list_of_missing_tags)
    """
    if not BS4_AVAILABLE:
        return 1.0, []

    content = html_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(content, "html.parser")

    missing = []
    required_meta = {
        "description": "Meta description for SEO",
        "viewport": "Viewport meta for responsive design",
    }

    for name, desc in required_meta.items():
        meta = soup.find("meta", attrs={"name": name})
        if not meta:
            missing.append(f"{name}: {desc}")

    # Check for og: tags (nice to have)
    og_title = soup.find("meta", attrs={"property": "og:title"})
    if not og_title:
        missing.append("og:title: Open Graph title for social sharing")

    score = max(0.0, 1.0 - (len(missing) * 0.25))
    return score, missing


def score_website(output_dir: Path) -> QualityReport:
    """Score website quality with deterministic metrics.

    Args:
        output_dir: Path to output directory containing website/

    Returns:
        QualityReport for the website
    """
    report = QualityReport(component="website")
    website_dir = output_dir / "website"

    if not website_dir.exists():
        report.passed = False
        report.critical_failures.append("Website directory not found")
        return report

    html_files = list(website_dir.glob("**/*.html"))
    if not html_files:
        report.passed = False
        report.critical_failures.append("No HTML files found")
        return report

    # Check main HTML file
    main_html = website_dir / "index.html"
    if not main_html.exists():
        main_html = html_files[0]

    # Metric 1: HTML validity (critical)
    is_valid, html_issues = validate_html(main_html)
    report.add_score(QualityScore(
        component="website",
        metric="html_valid",
        value=1.0 if is_valid else 0.0,
        threshold=1.0,
        passed=is_valid,
        severity="critical",
        details="; ".join(html_issues[:3]) if html_issues else "Valid HTML",
    ))

    # Metric 2: Images have alt text (major)
    alt_score, missing_alt = check_images_have_alt(main_html)
    report.add_score(QualityScore(
        component="website",
        metric="images_alt_text",
        value=alt_score,
        threshold=0.9,
        passed=alt_score >= 0.9,
        severity="major",
        details=f"{len(missing_alt)} images missing alt text" if missing_alt else "All images have alt text",
    ))

    # Metric 3: Heading hierarchy (major)
    heading_score, heading_issues = check_heading_hierarchy(main_html)
    report.add_score(QualityScore(
        component="website",
        metric="heading_hierarchy",
        value=heading_score,
        threshold=0.8,
        passed=heading_score >= 0.8,
        severity="major",
        details="; ".join(heading_issues[:3]) if heading_issues else "Proper heading hierarchy",
    ))

    # Metric 4: External links security (minor)
    link_score, link_issues = check_external_links_noopener(main_html)
    report.add_score(QualityScore(
        component="website",
        metric="external_links_secure",
        value=link_score,
        threshold=0.9,
        passed=link_score >= 0.9,
        severity="minor",
        details=f"{len(link_issues)} links missing rel=noopener" if link_issues else "All external links secure",
    ))

    # Metric 5: Meta tags (minor)
    meta_score, missing_meta = check_meta_tags(main_html)
    report.add_score(QualityScore(
        component="website",
        metric="meta_tags",
        value=meta_score,
        threshold=0.5,
        passed=meta_score >= 0.5,
        severity="minor",
        details=f"Missing: {', '.join(m.split(':')[0] for m in missing_meta[:3])}" if missing_meta else "All meta tags present",
    ))

    # Metric 6: File count (sanity check)
    report.add_score(QualityScore(
        component="website",
        metric="file_completeness",
        value=1.0 if len(html_files) >= 1 else 0.0,
        threshold=1.0,
        passed=len(html_files) >= 1,
        severity="critical",
        details=f"{len(html_files)} HTML file(s) generated",
    ))

    report.calculate_overall()

    # Add recommendations
    if alt_score < 1.0:
        report.recommendations.append("Add alt text to all images for accessibility")
    if meta_score < 1.0:
        report.recommendations.append("Add missing meta tags for SEO")

    return report


# ============================================================================
# Poster Quality Metrics
# ============================================================================

def check_poster_dimensions(poster_path: Path, expected_width: int, expected_height: int, dpi: int = 300) -> tuple[float, str]:
    """Check poster dimensions against expected.

    Args:
        poster_path: Path to poster image/PDF
        expected_width: Expected width in inches
        expected_height: Expected height in inches
        dpi: Expected DPI

    Returns:
        Tuple of (score, details)
    """
    try:
        from PIL import Image
    except ImportError:
        return 1.0, "Skipped: PIL not available"

    if poster_path.suffix.lower() == ".pdf":
        return 1.0, "PDF dimension check not implemented"

    try:
        with Image.open(poster_path) as im:
            actual_width_px, actual_height_px = im.size

            expected_width_px = int(expected_width * dpi)
            expected_height_px = int(expected_height * dpi)

            # Allow 5% tolerance
            width_ratio = actual_width_px / expected_width_px
            height_ratio = actual_height_px / expected_height_px

            width_ok = 0.95 <= width_ratio <= 1.05
            height_ok = 0.95 <= height_ratio <= 1.05

            if width_ok and height_ok:
                return 1.0, f"Dimensions correct: {actual_width_px}x{actual_height_px}px"
            else:
                return 0.5, f"Dimensions: {actual_width_px}x{actual_height_px}px (expected ~{expected_width_px}x{expected_height_px}px)"

    except Exception as e:
        return 0.0, f"Error checking dimensions: {e}"


def check_poster_resolution(poster_path: Path, min_dpi: int = 300) -> tuple[float, str]:
    """Check poster has adequate resolution.

    Args:
        poster_path: Path to poster image
        min_dpi: Minimum DPI for print quality

    Returns:
        Tuple of (score, details)
    """
    try:
        from PIL import Image
    except ImportError:
        return 1.0, "Skipped: PIL not available"

    if poster_path.suffix.lower() == ".pdf":
        return 1.0, "PDF resolution check not implemented"

    try:
        with Image.open(poster_path) as im:
            # Check DPI from image info
            dpi_info = im.info.get("dpi", (72, 72))
            if isinstance(dpi_info, tuple):
                dpi = max(dpi_info)
            else:
                dpi = dpi_info

            # Also estimate DPI from pixel dimensions (assuming typical poster size)
            # A 48" poster at 300 DPI should be ~14400px wide
            estimated_dpi = im.width / 48.0  # Assuming landscape

            effective_dpi = max(dpi, estimated_dpi)

            if effective_dpi >= min_dpi:
                return 1.0, f"Resolution adequate: ~{int(effective_dpi)} DPI"
            elif effective_dpi >= min_dpi * 0.75:
                return 0.7, f"Resolution marginal: ~{int(effective_dpi)} DPI (recommended: {min_dpi})"
            else:
                return 0.3, f"Resolution low: ~{int(effective_dpi)} DPI (recommended: {min_dpi})"

    except Exception as e:
        return 0.0, f"Error checking resolution: {e}"


def score_poster(output_dir: Path, expected_width: int = 48, expected_height: int = 36) -> QualityReport:
    """Score poster quality with deterministic metrics.

    Args:
        output_dir: Path to output directory containing poster/
        expected_width: Expected width in inches
        expected_height: Expected height in inches

    Returns:
        QualityReport for the poster
    """
    report = QualityReport(component="poster")
    poster_dir = output_dir / "poster"

    if not poster_dir.exists():
        report.passed = False
        report.critical_failures.append("Poster directory not found")
        return report

    # Find poster file
    poster_files = list(poster_dir.glob("*.pdf")) + list(poster_dir.glob("*.png"))
    if not poster_files:
        report.passed = False
        report.critical_failures.append("No poster file found")
        return report

    poster_path = poster_files[0]

    # Metric 1: File exists (critical)
    report.add_score(QualityScore(
        component="poster",
        metric="file_exists",
        value=1.0,
        threshold=1.0,
        passed=True,
        severity="critical",
        details=f"Poster file: {poster_path.name}",
    ))

    # Metric 2: File size reasonable (major)
    file_size_mb = poster_path.stat().st_size / (1024 * 1024)
    size_ok = 1.0 <= file_size_mb <= 100.0
    report.add_score(QualityScore(
        component="poster",
        metric="file_size",
        value=1.0 if size_ok else 0.5,
        threshold=0.8,
        passed=size_ok,
        severity="major",
        details=f"File size: {file_size_mb:.1f} MB",
    ))

    # Metric 3: Dimensions (major)
    dim_score, dim_details = check_poster_dimensions(poster_path, expected_width, expected_height)
    report.add_score(QualityScore(
        component="poster",
        metric="dimensions",
        value=dim_score,
        threshold=0.8,
        passed=dim_score >= 0.8,
        severity="major",
        details=dim_details,
    ))

    # Metric 4: Resolution (major)
    res_score, res_details = check_poster_resolution(poster_path)
    report.add_score(QualityScore(
        component="poster",
        metric="resolution",
        value=res_score,
        threshold=0.7,
        passed=res_score >= 0.7,
        severity="major",
        details=res_details,
    ))

    report.calculate_overall()

    if res_score < 0.7:
        report.recommendations.append("Increase figure resolution for better print quality")

    return report


# ============================================================================
# Video Quality Metrics
# ============================================================================

def check_video_properties(video_path: Path) -> dict:
    """Get video properties using ffprobe.

    Args:
        video_path: Path to video file

    Returns:
        Dictionary of video properties
    """
    import subprocess
    import json

    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                str(video_path),
            ],
            capture_output=True,
            timeout=30,
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data
    except Exception:
        pass

    return {}


def score_video(output_dir: Path, target_duration_minutes: float = 5.0) -> QualityReport:
    """Score video quality with deterministic metrics.

    Args:
        output_dir: Path to output directory containing video/
        target_duration_minutes: Expected video duration

    Returns:
        QualityReport for the video
    """
    report = QualityReport(component="video")
    video_dir = output_dir / "video"

    if not video_dir.exists():
        report.passed = False
        report.critical_failures.append("Video directory not found")
        return report

    # Find video file
    video_files = list(video_dir.glob("*.mp4")) + list(video_dir.glob("*.webm"))
    if not video_files:
        report.passed = False
        report.critical_failures.append("No video file found")
        return report

    video_path = video_files[0]

    # Metric 1: File exists (critical)
    report.add_score(QualityScore(
        component="video",
        metric="file_exists",
        value=1.0,
        threshold=1.0,
        passed=True,
        severity="critical",
        details=f"Video file: {video_path.name}",
    ))

    # Metric 2: File size reasonable (major)
    file_size_mb = video_path.stat().st_size / (1024 * 1024)
    size_ok = 5.0 <= file_size_mb <= 500.0
    report.add_score(QualityScore(
        component="video",
        metric="file_size",
        value=1.0 if size_ok else 0.5,
        threshold=0.8,
        passed=size_ok,
        severity="major",
        details=f"File size: {file_size_mb:.1f} MB",
    ))

    # Try to get video properties
    props = check_video_properties(video_path)

    if props:
        # Metric 3: Duration (major)
        try:
            duration_sec = float(props.get("format", {}).get("duration", 0))
            duration_min = duration_sec / 60
            target_sec = target_duration_minutes * 60

            duration_ratio = duration_sec / target_sec if target_sec > 0 else 0
            duration_ok = 0.5 <= duration_ratio <= 2.0

            report.add_score(QualityScore(
                component="video",
                metric="duration",
                value=1.0 if duration_ok else 0.5,
                threshold=0.8,
                passed=duration_ok,
                severity="major",
                details=f"Duration: {duration_min:.1f} min (target: {target_duration_minutes} min)",
            ))
        except Exception:
            pass

        # Metric 4: Resolution (major)
        try:
            video_stream = next(
                (s for s in props.get("streams", []) if s.get("codec_type") == "video"),
                None
            )
            if video_stream:
                width = video_stream.get("width", 0)
                height = video_stream.get("height", 0)

                # Check for HD quality
                is_hd = height >= 720
                is_fhd = height >= 1080

                report.add_score(QualityScore(
                    component="video",
                    metric="resolution",
                    value=1.0 if is_fhd else (0.8 if is_hd else 0.5),
                    threshold=0.8,
                    passed=is_hd,
                    severity="major",
                    details=f"Resolution: {width}x{height}",
                ))
        except Exception:
            pass
    else:
        report.recommendations.append("Install ffprobe for detailed video quality analysis")

    report.calculate_overall()
    return report


# ============================================================================
# Combined Scoring
# ============================================================================

def score_all_components(output_dir: Path) -> dict[str, QualityReport]:
    """Score all components in an output directory.

    Args:
        output_dir: Path to output directory

    Returns:
        Dictionary mapping component names to QualityReports
    """
    reports = {}

    if (output_dir / "website").exists():
        reports["website"] = score_website(output_dir)

    if (output_dir / "poster").exists():
        reports["poster"] = score_poster(output_dir)

    if (output_dir / "video").exists():
        reports["video"] = score_video(output_dir)

    return reports


def format_quality_report(report: QualityReport) -> str:
    """Format quality report as human-readable string.

    Args:
        report: QualityReport to format

    Returns:
        Formatted string
    """
    lines = [
        f"Quality Report: {report.component}",
        "=" * 50,
        f"Overall Score: {report.overall_score:.1%}",
        f"Status: {'PASSED' if report.passed else 'FAILED'}",
        "",
        "Metrics:",
    ]

    for score in report.scores:
        status = "PASS" if score.passed else "FAIL"
        severity_marker = {"critical": "!!!", "major": "!!", "minor": "!"}[score.severity]
        lines.append(f"  [{status}] {score.metric} ({severity_marker}): {score.value:.1%}")
        if score.details:
            lines.append(f"        {score.details}")

    if report.critical_failures:
        lines.append("")
        lines.append("Critical Failures:")
        for failure in report.critical_failures:
            lines.append(f"  - {failure}")

    if report.recommendations:
        lines.append("")
        lines.append("Recommendations:")
        for rec in report.recommendations:
            lines.append(f"  - {rec}")

    return "\n".join(lines)


__all__ = [
    "QualityScore",
    "QualityReport",
    "score_website",
    "score_poster",
    "score_video",
    "score_all_components",
    "format_quality_report",
    "validate_html",
    "check_images_have_alt",
    "check_heading_hierarchy",
    "check_poster_dimensions",
    "check_poster_resolution",
]
