"""PaperBanana Settings factory.

Creates configured PaperBanana Settings instances with Oligon brand
integration and shared API key loading.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

# Skill directory paths (always available, even without paperbanana installed)
SKILL_DIR = Path(__file__).resolve().parent.parent.parent
GUIDELINES_PATH = SKILL_DIR / "data" / "guidelines" / "oligon_style.yaml"
STYLIST_PROMPT_PATH = SKILL_DIR / "prompts" / "diagram" / "stylist.txt"


def create_settings(
    api_key: str,
    iterations: int = 3,
    brand_enabled: bool = True,
    guidelines_path: Optional[Path] = None,
    reference_dir: Optional[Path] = None,
):
    """Create PaperBanana Settings with Oligon brand configuration.

    Args:
        api_key: Google API key for Gemini/Imagen
        iterations: Number of refinement iterations (1-5)
        brand_enabled: Whether to apply Oligon brand styling
        guidelines_path: Custom guidelines YAML path (defaults to Oligon)
        reference_dir: Directory with reference/example images

    Returns:
        Configured PaperBanana Settings instance

    Raises:
        ImportError: If paperbanana is not installed
    """
    from paperbanana import DiagramType
    from paperbanana.core.config import Settings

    kwargs: dict = {
        "vlm_provider": "gemini",
        "image_provider": "google_imagen",
        "diagram_type": DiagramType.METHODOLOGY,
        "refinement_iterations": max(1, min(iterations, 5)),
        "api_key": api_key,
    }

    if brand_enabled:
        gpath = guidelines_path or GUIDELINES_PATH
        if gpath.exists():
            kwargs["guidelines_path"] = str(gpath)

    if reference_dir and Path(reference_dir).is_dir():
        kwargs["reference_dir"] = str(reference_dir)

    return Settings(**kwargs)
