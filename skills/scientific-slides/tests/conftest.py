"""Pytest configuration and shared fixtures for scientific-slides tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

# Add scripts directory to path for imports
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))


@pytest.fixture
def valid_slide_plan() -> dict[str, Any]:
    """A valid slide plan for a 15-minute conference talk."""
    return {
        "talk_type": "conference",
        "duration_minutes": 15,
        "title": "Novel Approaches to Protein Structure Prediction",
        "speaker": "Dr. Jane Smith",
        "affiliation": "Institute for Structural Biology",
        "formatting": {
            "background_color": "#FFFFFF",
            "text_color": "#222222",
            "accent_color": "#2DB2E8",
            "highlight_color": "#E8622D",
            "font_family": "Arial",
            "style": "minimal",
        },
        "slides": [
            {"slide_type": "title", "title": "Novel Approaches to Protein Structure"},
            {"slide_type": "section", "title": "Introduction"},
            {
                "slide_type": "content",
                "title": "Background",
                "key_points": [
                    "Protein structure determines function",
                    "Traditional methods are expensive",
                    "New ML approaches show promise",
                ],
                "citations": ["(AlphaFold, 2021)"],
            },
            {
                "slide_type": "content",
                "title": "Problem Statement",
                "key_points": [
                    "Current methods are slow",
                    "Accuracy varies by protein family",
                ],
            },
            {"slide_type": "section", "title": "Methods"},
            {
                "slide_type": "content",
                "title": "Our Approach",
                "key_points": [
                    "Novel architecture combining CNN and Transformer",
                    "Training on expanded dataset",
                    "Multi-scale feature extraction",
                ],
            },
            {
                "slide_type": "figure",
                "title": "Model Architecture",
                "visual_description": "Neural network diagram showing data flow",
            },
            {"slide_type": "section", "title": "Results"},
            {
                "slide_type": "content",
                "title": "Performance Comparison",
                "key_points": [
                    "20% improvement in accuracy",
                    "5x faster inference",
                    "Generalizes across protein families",
                ],
            },
            {
                "slide_type": "figure",
                "title": "Benchmark Results",
                "visual_description": "Bar chart comparing methods",
            },
            {
                "slide_type": "conclusion",
                "title": "Key Takeaways",
                "key_points": [
                    "New method achieves SOTA results",
                    "Open source implementation available",
                    "Future work on larger proteins",
                ],
            },
            {
                "slide_type": "acknowledgments",
                "title": "Acknowledgments",
                "key_points": ["NIH funding", "Compute resources from AWS"],
            },
        ],
    }


@pytest.fixture
def minimal_slide_plan() -> dict[str, Any]:
    """Minimal valid slide plan with only required fields."""
    return {
        "talk_type": "lightning",
        "duration_minutes": 5,
        "title": "Quick Update",
        "slides": [
            {"slide_type": "title", "title": "Quick Update"},
            {"slide_type": "content", "title": "Key Point"},
        ],
    }


@pytest.fixture
def invalid_slide_plan() -> dict[str, Any]:
    """Invalid slide plan with schema violations."""
    return {
        "talk_type": "unknown_type",  # Invalid enum value
        "duration_minutes": 1000,  # Exceeds maximum
        "title": "Test",
        "slides": [],  # Empty slides array
    }


@pytest.fixture
def plan_too_many_slides() -> dict[str, Any]:
    """Slide plan with too many slides for the duration."""
    return {
        "talk_type": "lightning",
        "duration_minutes": 5,
        "title": "Overloaded Talk",
        "slides": [{"slide_type": "content", "title": f"Slide {i}"} for i in range(20)],
    }


@pytest.fixture
def plan_too_few_slides() -> dict[str, Any]:
    """Slide plan with too few slides for the duration."""
    return {
        "talk_type": "conference",
        "duration_minutes": 45,
        "title": "Sparse Talk",
        "slides": [
            {"slide_type": "title", "title": "Title"},
            {"slide_type": "content", "title": "Content"},
            {"slide_type": "conclusion", "title": "End"},
        ],
    }


@pytest.fixture
def slide_with_many_points() -> dict[str, Any]:
    """A slide with too many bullet points."""
    return {
        "slide_type": "content",
        "title": "Overcrowded Slide",
        "key_points": [
            "Point one about the topic",
            "Point two with more detail",
            "Point three explaining further",
            "Point four adding context",
            "Point five with examples",
            "Point six summarizing",
            "Point seven concluding",
            "Point eight for good measure",
        ],
    }


@pytest.fixture
def sample_formatting() -> dict[str, str]:
    """Sample formatting configuration."""
    return {
        "background_color": "#FFFFFF",
        "text_color": "#222222",
        "accent_color": "#2DB2E8",
        "highlight_color": "#E8622D",
        "font_family": "Arial",
        "style": "minimal",
    }


@pytest.fixture
def brand_colors() -> list[str]:
    """Sample brand colors for compliance checking."""
    return ["#2DB2E8", "#E8622D", "#FFFFFF", "#222222"]


@pytest.fixture
def create_test_image(tmp_path):
    """Factory fixture to create test images with specific properties."""
    from PIL import Image, ImageDraw

    def _create_image(
        width: int = 1920,
        height: int = 1080,
        color: tuple[int, int, int] = (255, 255, 255),
        filename: str = "test_slide.png",
        add_content: bool = False,
    ) -> Path:
        img = Image.new("RGB", (width, height), color=color)

        if add_content:
            # Add some content to create contrast and reduce white space
            draw = ImageDraw.Draw(img)
            # Title area (dark header)
            draw.rectangle([0, 0, width, 150], fill=(50, 50, 50))
            # Some text-like content blocks
            draw.rectangle([100, 200, 800, 250], fill=(30, 30, 30))
            draw.rectangle([100, 280, 600, 320], fill=(60, 60, 60))
            draw.rectangle([100, 350, 700, 390], fill=(40, 40, 40))
            # Footer area
            draw.rectangle([0, height - 80, width, height], fill=(100, 100, 100))

        img_path = tmp_path / filename
        img.save(img_path, "PNG", compress_level=6)
        return img_path

    return _create_image


@pytest.fixture
def valid_slide_image(create_test_image) -> Path:
    """Create a valid 1920x1080 slide image with content."""
    return create_test_image(1920, 1080, (255, 255, 255), add_content=True)


@pytest.fixture
def small_slide_image(create_test_image) -> Path:
    """Create an undersized slide image."""
    return create_test_image(640, 480, (255, 255, 255), "small_slide.png")


@pytest.fixture
def square_slide_image(create_test_image) -> Path:
    """Create a square (wrong aspect ratio) slide image."""
    return create_test_image(1024, 1024, (255, 255, 255), "square_slide.png")


@pytest.fixture
def low_contrast_image(create_test_image) -> Path:
    """Create a low contrast image."""
    return create_test_image(1920, 1080, (200, 200, 200), "low_contrast.png")


@pytest.fixture
def high_contrast_image(tmp_path) -> Path:
    """Create a high contrast image with black and white regions."""
    from PIL import Image

    img = Image.new("RGB", (1920, 1080), color=(255, 255, 255))
    # Add a black rectangle
    for x in range(0, 960):
        for y in range(0, 540):
            img.putpixel((x, y), (0, 0, 0))
    img_path = tmp_path / "high_contrast.png"
    img.save(img_path)
    return img_path


@pytest.fixture
def schemas_dir() -> Path:
    """Path to schemas directory."""
    return Path(__file__).parent.parent / "schemas"


@pytest.fixture
def slide_plan_schema(schemas_dir) -> dict[str, Any]:
    """Load the slide plan schema."""
    schema_path = schemas_dir / "slide_plan_schema.json"
    with open(schema_path) as f:
        return json.load(f)
