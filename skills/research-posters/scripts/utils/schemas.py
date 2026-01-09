"""
Data schemas for research poster validation.

Provides structured dataclasses for:
- Poster specification (input)
- Validation results (output)
- Quality report aggregation
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any


class ValidationStatus(Enum):
    """Status levels for validation checks."""

    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


class PosterFormat(Enum):
    """Supported poster output formats."""

    LATEX = "latex"
    PPTX = "pptx"


class LaTeXPackage(Enum):
    """Supported LaTeX poster packages."""

    BEAMERPOSTER = "beamerposter"
    TIKZPOSTER = "tikzposter"
    BAPOSTER = "baposter"


# ============================================================================
# Input Schemas (Poster Specification)
# ============================================================================


@dataclass
class Author:
    """Author information for poster."""

    name: str
    affiliation: int  # Index into affiliations list
    presenting: bool = False
    email: str | None = None
    orcid: str | None = None


@dataclass
class Figure:
    """Figure specification for poster."""

    id: str
    figure_type: str  # "schematic", "chart", "photo", "diagram"
    description: str
    source: str | None = None  # Path or skill name
    min_dpi: int = 300
    position: str | None = None  # Optional placement hint


@dataclass
class SectionContent:
    """Content specification for a poster section."""

    word_budget: int
    key_points: list[str] = field(default_factory=list)
    include_figure: bool = False
    figure_id: str | None = None


@dataclass
class PosterSpec:
    """
    Complete poster specification schema.

    Defines all inputs needed to generate a deterministic poster.
    Can be serialized to/from YAML.
    """

    # Basic info
    title: str
    dimensions: str  # "A0", "36x48", etc.
    orientation: str = "portrait"  # "portrait" or "landscape"
    poster_format: str = "latex"  # "latex" or "pptx"
    latex_package: str = "tikzposter"  # "beamerposter", "tikzposter", "baposter"
    brand: str = "oligon"  # "oligon", "generic", "custom"

    # Authors and affiliations
    authors: list[Author] = field(default_factory=list)
    affiliations: dict[int, str] = field(default_factory=dict)

    # Content sections
    content: dict[str, SectionContent] = field(default_factory=dict)

    # Figures
    figures: list[Figure] = field(default_factory=list)

    # Assets
    logos: list[dict[str, str]] = field(default_factory=list)
    qr_codes: list[dict[str, str]] = field(default_factory=list)

    def validate(self) -> list[str]:
        """
        Validate the specification for completeness.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if not self.title:
            errors.append("Title is required")

        if not self.dimensions:
            errors.append("Dimensions are required")

        if self.orientation not in ("portrait", "landscape"):
            errors.append(f"Invalid orientation: {self.orientation}")

        if self.poster_format not in ("latex", "pptx"):
            errors.append(f"Invalid format: {self.poster_format}")

        if self.poster_format == "latex" and self.latex_package not in (
            "beamerposter",
            "tikzposter",
            "baposter",
        ):
            errors.append(f"Invalid LaTeX package: {self.latex_package}")

        # Validate author affiliations reference valid indices
        for author in self.authors:
            if author.affiliation not in self.affiliations:
                errors.append(
                    f"Author '{author.name}' references undefined affiliation {author.affiliation}"
                )

        # Validate figure references in sections
        figure_ids = {f.id for f in self.figures}
        for section_name, section in self.content.items():
            if section.figure_id and section.figure_id not in figure_ids:
                errors.append(
                    f"Section '{section_name}' references undefined figure '{section.figure_id}'"
                )

        return errors

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PosterSpec":
        """
        Create PosterSpec from dictionary.

        Handles nested object conversion.
        """
        # Convert nested author dicts to Author objects
        authors = [
            Author(**a) if isinstance(a, dict) else a for a in data.get("authors", [])
        ]

        # Convert nested figure dicts to Figure objects
        figures = [
            Figure(**f) if isinstance(f, dict) else f for f in data.get("figures", [])
        ]

        # Convert section content
        content = {}
        for name, section_data in data.get("content", {}).items():
            if isinstance(section_data, dict):
                content[name] = SectionContent(**section_data)
            else:
                content[name] = section_data

        return cls(
            title=data.get("title", ""),
            dimensions=data.get("dimensions", "A0"),
            orientation=data.get("orientation", "portrait"),
            poster_format=data.get("poster_format", data.get("format", "latex")),
            latex_package=data.get("latex_package", "tikzposter"),
            brand=data.get("brand", "oligon"),
            authors=authors,
            affiliations=data.get("affiliations", {}),
            content=content,
            figures=figures,
            logos=data.get("logos", []),
            qr_codes=data.get("qr_codes", []),
        )


# ============================================================================
# Output Schemas (Validation Results)
# ============================================================================


@dataclass
class ValidationResult:
    """Base result for a single validation check."""

    check_name: str
    status: ValidationStatus
    message: str
    value: Any = None
    threshold: Any = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "check_name": self.check_name,
            "status": self.status.value,
            "message": self.message,
            "value": self.value,
            "threshold": self.threshold,
        }


@dataclass
class WordCountResult:
    """Word count validation result."""

    total: int
    by_section: dict[str, int]
    target_min: int
    target_max: int
    status: ValidationStatus

    @property
    def passed(self) -> bool:
        return self.status == ValidationStatus.PASS

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "by_section": self.by_section,
            "target_range": [self.target_min, self.target_max],
            "status": self.status.value,
            "passed": self.passed,
        }


@dataclass
class ContrastCheckResult:
    """Contrast ratio validation result."""

    foreground: str
    background: str
    ratio: float
    wcag_level: str  # "AA", "AAA", "FAIL"
    passes_large_text: bool
    passes_normal_text: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "foreground": self.foreground,
            "background": self.background,
            "ratio": self.ratio,
            "wcag_level": self.wcag_level,
            "passes_large_text": self.passes_large_text,
            "passes_normal_text": self.passes_normal_text,
        }


@dataclass
class ImageCheckResult:
    """Image quality validation result."""

    image_index: int
    page: int
    width_px: int
    height_px: int
    color_space: str
    format: str
    estimated_dpi: float | None = None
    meets_minimum_dpi: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "image_index": self.image_index,
            "page": self.page,
            "dimensions": {"width": self.width_px, "height": self.height_px},
            "color_space": self.color_space,
            "format": self.format,
            "estimated_dpi": self.estimated_dpi,
            "meets_minimum_dpi": self.meets_minimum_dpi,
        }


@dataclass
class FontCheckResult:
    """Font embedding validation result."""

    font_name: str
    font_type: str
    embedded: bool
    subset: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "font_name": self.font_name,
            "font_type": self.font_type,
            "embedded": self.embedded,
            "subset": self.subset,
        }


@dataclass
class QualityReport:
    """
    Complete quality validation report for a poster.

    Aggregates all validation checks into a single structured report.
    """

    # Metadata
    poster_path: str
    source_path: str | None
    validation_timestamp: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )

    # Overall status
    overall_pass: bool = True

    # Individual check results
    word_count: WordCountResult | None = None
    dimensions: dict[str, Any] = field(default_factory=dict)
    fonts: list[FontCheckResult] = field(default_factory=list)
    images: list[ImageCheckResult] = field(default_factory=list)
    contrast_checks: list[ContrastCheckResult] = field(default_factory=list)
    structure: dict[str, Any] = field(default_factory=dict)
    compilation: dict[str, Any] = field(default_factory=dict)

    # Issues and warnings
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        """Add an error and mark report as failed."""
        self.errors.append(message)
        self.overall_pass = False

    def add_warning(self, message: str) -> None:
        """Add a warning (does not affect overall pass status)."""
        self.warnings.append(message)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "poster_path": self.poster_path,
            "source_path": self.source_path,
            "validation_timestamp": self.validation_timestamp,
            "overall_pass": self.overall_pass,
            "checks": {},
            "errors": self.errors,
            "warnings": self.warnings,
        }

        if self.word_count:
            result["checks"]["word_count"] = self.word_count.to_dict()

        if self.dimensions:
            result["checks"]["dimensions"] = self.dimensions

        if self.fonts:
            all_embedded = all(f.embedded for f in self.fonts)
            result["checks"]["fonts"] = {
                "all_embedded": all_embedded,
                "font_count": len(self.fonts),
                "details": [f.to_dict() for f in self.fonts],
                "pass": all_embedded,
            }

        if self.images:
            all_good_dpi = all(img.meets_minimum_dpi for img in self.images)
            result["checks"]["images"] = {
                "count": len(self.images),
                "all_meet_minimum_dpi": all_good_dpi,
                "details": [img.to_dict() for img in self.images],
                "pass": all_good_dpi,
            }

        if self.contrast_checks:
            all_pass = all(c.passes_large_text for c in self.contrast_checks)
            result["checks"]["accessibility"] = {
                "contrast_checks": [c.to_dict() for c in self.contrast_checks],
                "all_pass_large_text": all_pass,
                "pass": all_pass,
            }

        if self.structure:
            result["checks"]["structure"] = self.structure

        if self.compilation:
            result["checks"]["compilation"] = self.compilation

        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "QualityReport":
        """Create QualityReport from dictionary."""
        report = cls(
            poster_path=data.get("poster_path", ""),
            source_path=data.get("source_path"),
            validation_timestamp=data.get(
                "validation_timestamp", datetime.now().isoformat()
            ),
            overall_pass=data.get("overall_pass", True),
            errors=data.get("errors", []),
            warnings=data.get("warnings", []),
        )

        checks = data.get("checks", {})

        if "word_count" in checks:
            wc = checks["word_count"]
            target_range = wc.get("target_range", [300, 800])
            report.word_count = WordCountResult(
                total=wc.get("total", 0),
                by_section=wc.get("by_section", {}),
                target_min=target_range[0] if target_range else 300,
                target_max=target_range[1] if len(target_range) > 1 else 800,
                status=ValidationStatus(wc.get("status", "pass")),
            )

        if "dimensions" in checks:
            report.dimensions = checks["dimensions"]

        if "fonts" in checks:
            font_details = checks["fonts"].get("details", [])
            report.fonts = [
                FontCheckResult(
                    font_name=f.get("font_name", ""),
                    font_type=f.get("font_type", ""),
                    embedded=f.get("embedded", False),
                    subset=f.get("subset", False),
                )
                for f in font_details
            ]

        if "images" in checks:
            image_details = checks["images"].get("details", [])
            report.images = [
                ImageCheckResult(
                    image_index=img.get("image_index", 0),
                    page=img.get("page", 1),
                    width_px=img.get("dimensions", {}).get("width", 0),
                    height_px=img.get("dimensions", {}).get("height", 0),
                    color_space=img.get("color_space", ""),
                    format=img.get("format", ""),
                    estimated_dpi=img.get("estimated_dpi"),
                    meets_minimum_dpi=img.get("meets_minimum_dpi", True),
                )
                for img in image_details
            ]

        if "accessibility" in checks:
            contrast_details = checks["accessibility"].get("contrast_checks", [])
            report.contrast_checks = [
                ContrastCheckResult(
                    foreground=c.get("foreground", ""),
                    background=c.get("background", ""),
                    ratio=c.get("ratio", 0.0),
                    wcag_level=c.get("wcag_level", "FAIL"),
                    passes_large_text=c.get("passes_large_text", False),
                    passes_normal_text=c.get("passes_normal_text", False),
                )
                for c in contrast_details
            ]

        if "structure" in checks:
            report.structure = checks["structure"]

        if "compilation" in checks:
            report.compilation = checks["compilation"]

        return report
