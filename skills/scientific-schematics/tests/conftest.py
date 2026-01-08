"""Pytest fixtures for scientific-schematics skill tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add scripts directory to path for imports
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


# ---------------------------------------------------------------------
# Sample Prompts
# ---------------------------------------------------------------------


@pytest.fixture
def valid_consort_prompt() -> str:
    """Valid CONSORT flowchart prompt with all recommended elements."""
    return """CONSORT participant flow diagram for randomized controlled trial.
    Layout: top-to-bottom

    Enrollment: n=500 assessed for eligibility
    - 150 excluded (100 not meeting criteria, 50 declined)
    Randomization: n=350 randomized
    - Intervention: n=175 allocated
    - Control: n=175 allocated
    Follow-up: 90% retention
    Analysis: intention-to-treat

    Use colorblind-safe colors with clear labels."""


@pytest.fixture
def valid_transformer_prompt() -> str:
    """Valid transformer architecture prompt."""
    return """Transformer encoder-decoder architecture diagram.
    Layout: left-to-right

    6 encoder layers with multi-head attention
    6 decoder layers with masked attention
    512 dimension model with 8 attention heads

    Show positional encoding and feed-forward networks."""


@pytest.fixture
def valid_pathway_prompt() -> str:
    """Valid biological pathway prompt."""
    return """MAPK signaling pathway diagram.
    Layout: top-to-bottom

    Components: RTK receptor, RAS, RAF, MEK, ERK
    Show phosphorylation cascade with arrows
    Include feedback inhibition loop

    Use Okabe-Ito colorblind-safe palette."""


@pytest.fixture
def minimal_prompt() -> str:
    """Minimal prompt that should generate warnings."""
    return "A simple diagram"


@pytest.fixture
def vague_prompt() -> str:
    """Vague prompt with unclear elements."""
    return "Make something with boxes and stuff, whatever looks good, etc."


@pytest.fixture
def overcrowded_prompt() -> str:
    """Prompt requesting too many elements."""
    return """CONSORT flowchart with 30 boxes showing every possible outcome.
    Include 25 exclusion criteria, 15 randomization branches,
    and 20 different analysis paths."""


# ---------------------------------------------------------------------
# Sample Images
# ---------------------------------------------------------------------


@pytest.fixture
def valid_image_path(tmp_path: Path) -> Path:
    """Create a valid test image."""
    try:
        from PIL import Image
    except ImportError:
        pytest.skip("PIL not available")

    # Create a realistic scientific diagram-like image
    img = Image.new("RGB", (1024, 768), color=(255, 255, 255))

    # Add some dark elements to simulate diagram content
    from PIL import ImageDraw

    draw = ImageDraw.Draw(img)

    # Draw some boxes
    draw.rectangle([100, 100, 300, 200], outline=(0, 0, 0), width=2)
    draw.rectangle([400, 100, 600, 200], outline=(0, 0, 0), width=2)
    draw.rectangle([250, 350, 450, 450], outline=(0, 0, 0), width=2)

    # Draw connecting lines
    draw.line([200, 200, 200, 350], fill=(0, 0, 0), width=2)
    draw.line([200, 350, 350, 350], fill=(0, 0, 0), width=2)
    draw.line([500, 200, 500, 350], fill=(0, 0, 0), width=2)
    draw.line([500, 350, 350, 350], fill=(0, 0, 0), width=2)

    # Add some text simulation (rectangles)
    draw.rectangle([110, 140, 290, 160], fill=(50, 50, 50))
    draw.rectangle([410, 140, 590, 160], fill=(50, 50, 50))

    img_path = tmp_path / "valid_diagram.png"
    img.save(img_path, "PNG")
    return img_path


@pytest.fixture
def small_image_path(tmp_path: Path) -> Path:
    """Create an image that's too small."""
    try:
        from PIL import Image
    except ImportError:
        pytest.skip("PIL not available")

    img = Image.new("RGB", (100, 100), color=(255, 255, 255))
    img_path = tmp_path / "small_image.png"
    img.save(img_path, "PNG")
    return img_path


@pytest.fixture
def low_contrast_image_path(tmp_path: Path) -> Path:
    """Create a low contrast image."""
    try:
        from PIL import Image
    except ImportError:
        pytest.skip("PIL not available")

    # Light gray on slightly lighter gray - poor contrast
    # This creates an image where all pixels are very similar luminance
    img = Image.new("RGB", (800, 600), color=(245, 245, 245))
    from PIL import ImageDraw

    draw = ImageDraw.Draw(img)
    # Fill with light gray elements
    draw.rectangle([100, 100, 300, 200], fill=(235, 235, 235), outline=(240, 240, 240), width=2)
    draw.rectangle([400, 100, 600, 200], fill=(238, 238, 238), outline=(242, 242, 242), width=2)

    img_path = tmp_path / "low_contrast.png"
    img.save(img_path, "PNG")
    return img_path


@pytest.fixture
def nonexistent_image_path(tmp_path: Path) -> Path:
    """Return path to nonexistent image."""
    return tmp_path / "does_not_exist.png"


# ---------------------------------------------------------------------
# Schema Test Data
# ---------------------------------------------------------------------


@pytest.fixture
def valid_iteration_result() -> dict:
    """Valid iteration result data."""
    return {
        "iteration": 1,
        "image_path": "/path/to/image_v1.png",
        "prompt": "Create a CONSORT flowchart",
        "critique": "Good clarity, labels are clear",
        "score": 8.5,
        "needs_improvement": False,
        "success": True,
    }


@pytest.fixture
def valid_generation_results() -> dict:
    """Valid generation results data."""
    return {
        "user_prompt": "CONSORT flowchart for clinical trial",
        "doc_type": "journal",
        "quality_threshold": 8.5,
        "iterations": [
            {
                "iteration": 1,
                "image_path": "/path/to/image_v1.png",
                "prompt": "Create a CONSORT flowchart",
                "critique": "Meets quality threshold",
                "score": 8.7,
                "needs_improvement": False,
                "success": True,
            }
        ],
        "final_image": "/path/to/image_v1.png",
        "final_score": 8.7,
        "success": True,
        "early_stop": True,
        "early_stop_reason": "Quality score 8.7 meets threshold 8.5",
    }


# ---------------------------------------------------------------------
# Color Palette Fixtures
# ---------------------------------------------------------------------


@pytest.fixture
def oligon_colors() -> dict:
    """Oligon brand colors for testing."""
    return {
        "primary": "#2DB2E8",
        "contrast": "#E8622D",
        "text": "#222222",
        "secondary": "#666666",
        "background": "#FFFFFF",
    }


@pytest.fixture
def okabe_ito_colors() -> dict:
    """Okabe-Ito colorblind-safe colors."""
    return {
        "blue": "#0072B2",
        "vermillion": "#D55E00",
        "yellow": "#F0E442",
        "bluish_green": "#009E73",
        "sky_blue": "#56B4E9",
        "orange": "#E69F00",
        "reddish_purple": "#CC79A7",
        "black": "#000000",
    }
