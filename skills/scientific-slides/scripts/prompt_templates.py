#!/usr/bin/env python3
"""
Template-based prompt generation for consistent slide creation.

Reduces variance by using structured templates with variable substitution.
Templates ensure consistent formatting while allowing customization.

Usage:
    from prompt_templates import PromptTemplateEngine

    engine = PromptTemplateEngine()
    prompt = engine.generate_slide_prompt(slide_data)
    prompts = engine.generate_batch_prompts(plan)
"""

from __future__ import annotations

from string import Template
from typing import Any


# Base template for full slides
FULL_SLIDE_TEMPLATE = Template(
    """Create a professional presentation slide with these specifications:

SLIDE TYPE: $slide_type
TITLE: $title
$subtitle_line

CONTENT:
$content_section

VISUAL REQUIREMENTS:
$visual_description

FORMATTING:
- Background: $background_color
- Text color: $text_color
- Accent color: $accent_color
- Font: $font_family
- Style: $style

LAYOUT:
- 16:9 aspect ratio
- Clear visual hierarchy
- Minimum 5% margins on all sides
- $white_space_guidance

$citations_section

Generate a high-quality slide image following all specifications above."""
)


# Template for visual-only generation
VISUAL_ONLY_TEMPLATE = Template(
    """Create a presentation visual/figure:

DESCRIPTION: $visual_description

REQUIREMENTS:
- Clean, professional appearance
- High resolution and sharp details
- High contrast for projection readability
- Transparent or white background preferred
- $style style
- Color palette: $accent_color (primary), $background_color (background)

Generate the visual without any slide frame or title text."""
)


# Template for title slides
TITLE_SLIDE_TEMPLATE = Template(
    """Create a professional title slide:

TITLE: $title
$speaker_line
$affiliation_line

DESIGN:
- Large, prominent title centered
- Clean, minimal layout
- $style style
- Background: $background_color
- Title text: $text_color
- Accent elements: $accent_color

LAYOUT:
- 16:9 aspect ratio
- Title uses 60-70% of vertical space
- Speaker info below title
- Generous margins (15%+ on sides)

Generate an impactful title slide that sets professional tone."""
)


# Template for section divider slides
SECTION_SLIDE_TEMPLATE = Template(
    """Create a section divider slide:

SECTION TITLE: $title
$subtitle_line

DESIGN:
- Prominent section heading
- Subtle, elegant background
- $style style
- Background: $background_color with subtle accent of $accent_color
- Text: $text_color

LAYOUT:
- 16:9 aspect ratio
- Centered heading
- Minimal additional elements
- Clear visual break from content slides

Generate a clean section transition slide."""
)


class PromptTemplateEngine:
    """Generate consistent prompts from structured slide plans."""

    SLIDE_TYPE_GUIDANCE: dict[str, str] = {
        "title": "Large centered title, speaker name below, minimal design",
        "section": "Section heading prominently displayed, subtle background",
        "content": "Title at top, key points below, supporting visual on right",
        "figure": "Large figure/chart as dominant element, brief caption",
        "comparison": "Side-by-side layout comparing two items",
        "timeline": "Horizontal or vertical timeline visualization",
        "conclusion": "Key takeaways prominently listed, memorable closing visual",
        "acknowledgments": "Funding logos, collaborator names, contact info",
        "backup": "Detailed supporting information for Q&A",
    }

    DEFAULT_FORMATTING: dict[str, str] = {
        "background_color": "#FFFFFF",
        "text_color": "#222222",
        "accent_color": "#2DB2E8",
        "highlight_color": "#E8622D",
        "font_family": "Arial",
        "style": "minimal",
    }

    def __init__(self, formatting: dict[str, str] | None = None):
        """
        Initialize with default or custom formatting.

        Args:
            formatting: Dict with color/font settings
        """
        self.formatting = self.DEFAULT_FORMATTING.copy()
        if formatting:
            self.formatting.update(formatting)

    def generate_slide_prompt(self, slide: dict[str, Any]) -> str:
        """
        Generate prompt for a single slide.

        Args:
            slide: Slide definition from plan

        Returns:
            Formatted prompt string
        """
        slide_type = slide.get("slide_type", "content")

        # Use specialized templates for certain slide types
        if slide_type == "title":
            return self._generate_title_prompt(slide)
        elif slide_type == "section":
            return self._generate_section_prompt(slide)

        # Build content section
        content_lines = []
        if slide.get("key_points"):
            content_lines.append("Key Points:")
            for point in slide["key_points"]:
                content_lines.append(f"- {point}")

        content_section = "\n".join(content_lines) if content_lines else "No bullet points"

        # Build subtitle line
        subtitle = slide.get("subtitle", "")
        subtitle_line = f"SUBTITLE: {subtitle}" if subtitle else ""

        # Build citations section
        citations = slide.get("citations", [])
        if citations:
            citations_section = "CITATIONS (display at bottom):\n" + "\n".join(
                f"- {c}" for c in citations
            )
        else:
            citations_section = ""

        # Get visual description or default
        visual_description = slide.get(
            "visual_description",
            self.SLIDE_TYPE_GUIDANCE.get(slide_type, "Professional supporting visual"),
        )

        # White space guidance based on content density
        point_count = len(slide.get("key_points", []))
        white_space_guidance = self._get_white_space_guidance(point_count)

        return FULL_SLIDE_TEMPLATE.substitute(
            slide_type=slide_type.upper(),
            title=slide.get("title", "Untitled"),
            subtitle_line=subtitle_line,
            content_section=content_section,
            visual_description=visual_description,
            background_color=self.formatting["background_color"],
            text_color=self.formatting["text_color"],
            accent_color=self.formatting["accent_color"],
            font_family=self.formatting["font_family"],
            style=self.formatting["style"],
            white_space_guidance=white_space_guidance,
            citations_section=citations_section,
        )

    def _generate_title_prompt(self, slide: dict[str, Any]) -> str:
        """Generate prompt for title slide."""
        speaker = slide.get("speaker", "")
        affiliation = slide.get("affiliation", "")

        speaker_line = f"SPEAKER: {speaker}" if speaker else ""
        affiliation_line = f"AFFILIATION: {affiliation}" if affiliation else ""

        subtitle = slide.get("subtitle", "")
        subtitle_line = f"SUBTITLE: {subtitle}" if subtitle else ""

        return TITLE_SLIDE_TEMPLATE.substitute(
            title=slide.get("title", "Untitled"),
            speaker_line=speaker_line,
            affiliation_line=affiliation_line,
            subtitle_line=subtitle_line,
            style=self.formatting["style"],
            background_color=self.formatting["background_color"],
            text_color=self.formatting["text_color"],
            accent_color=self.formatting["accent_color"],
        )

    def _generate_section_prompt(self, slide: dict[str, Any]) -> str:
        """Generate prompt for section divider slide."""
        subtitle = slide.get("subtitle", "")
        subtitle_line = f"SUBTITLE: {subtitle}" if subtitle else ""

        return SECTION_SLIDE_TEMPLATE.substitute(
            title=slide.get("title", "Section"),
            subtitle_line=subtitle_line,
            style=self.formatting["style"],
            background_color=self.formatting["background_color"],
            text_color=self.formatting["text_color"],
            accent_color=self.formatting["accent_color"],
        )

    def _get_white_space_guidance(self, point_count: int) -> str:
        """Get white space guidance based on content density."""
        if point_count <= 2:
            return "High white space (50%+) - minimal content"
        elif point_count <= 4:
            return "Moderate white space (40-50%)"
        else:
            return "Balanced layout with adequate breathing room"

    def generate_visual_prompt(self, description: str) -> str:
        """Generate prompt for visual-only generation."""
        return VISUAL_ONLY_TEMPLATE.substitute(
            visual_description=description,
            style=self.formatting["style"],
            accent_color=self.formatting["accent_color"],
            background_color=self.formatting["background_color"],
        )

    def generate_batch_prompts(
        self, plan: dict[str, Any]
    ) -> list[tuple[int, str, dict[str, Any]]]:
        """
        Generate prompts for all slides in a plan.

        Args:
            plan: Complete slide plan dictionary

        Returns:
            List of (slide_index, prompt, slide_data) tuples
        """
        # Update formatting from plan if provided
        if plan.get("formatting"):
            self.formatting.update(plan["formatting"])

        # Add speaker/affiliation to title slides from plan metadata
        speaker = plan.get("speaker", "")
        affiliation = plan.get("affiliation", "")

        prompts = []
        for i, slide in enumerate(plan.get("slides", [])):
            # Inject speaker info for title slides
            if slide.get("slide_type") == "title":
                slide = slide.copy()
                if not slide.get("speaker") and speaker:
                    slide["speaker"] = speaker
                if not slide.get("affiliation") and affiliation:
                    slide["affiliation"] = affiliation

            prompt = self.generate_slide_prompt(slide)
            prompts.append((i + 1, prompt, slide))

        return prompts

    def get_slide_type_options(self) -> list[str]:
        """Return available slide types."""
        return list(self.SLIDE_TYPE_GUIDANCE.keys())

    def get_style_options(self) -> list[str]:
        """Return available style options."""
        return ["minimal", "modern", "academic", "corporate"]


def main() -> None:
    """Demo the prompt template engine."""

    # Example slide plan
    example_plan = {
        "talk_type": "conference",
        "duration_minutes": 15,
        "title": "Novel Approaches to Protein Structure Prediction",
        "speaker": "Dr. Jane Smith",
        "affiliation": "Institute for Structural Biology",
        "formatting": {
            "background_color": "#FFFFFF",
            "accent_color": "#2DB2E8",
            "style": "minimal",
        },
        "slides": [
            {"slide_type": "title", "title": "Novel Approaches to Protein Structure Prediction"},
            {"slide_type": "section", "title": "Introduction"},
            {
                "slide_type": "content",
                "title": "Background",
                "key_points": [
                    "Protein structure determines function",
                    "Traditional methods are computationally expensive",
                    "New ML approaches show promise",
                ],
                "citations": ["(AlphaFold, 2021)", "(RoseTTAFold, 2021)"],
            },
            {
                "slide_type": "figure",
                "title": "Method Overview",
                "visual_description": "Flowchart showing the three-stage prediction pipeline",
            },
            {"slide_type": "conclusion", "title": "Key Takeaways", "key_points": ["20x faster", "Higher accuracy", "Open source"]},
        ],
    }

    engine = PromptTemplateEngine()
    prompts = engine.generate_batch_prompts(example_plan)

    print("Generated Prompts:")
    print("=" * 60)
    for slide_num, prompt, slide_data in prompts:
        print(f"\n--- Slide {slide_num}: {slide_data.get('title', 'Untitled')} ---\n")
        print(prompt)
        print()


if __name__ == "__main__":
    main()
