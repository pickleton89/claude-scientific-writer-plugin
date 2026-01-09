#!/usr/bin/env python3
"""
Analyze prompts against the 5-component formula.

Validates prompt structure, completeness, and provides improvement suggestions.
Part of the generate-image skill determinism improvement initiative (Phase 1).

Formula: [SUBJECT] + [STYLE] + [MEDIUM] + [TECHNICAL] + [QUALITY]
"""

from dataclasses import dataclass, field
from typing import Literal

# Optimal prompt length bounds (words)
MIN_OPTIMAL_LENGTH = 20
MAX_OPTIMAL_LENGTH = 50
MIN_VIABLE_LENGTH = 10
MAX_VIABLE_LENGTH = 100

# Keywords from references/prompt_templates.md
# Expanded with common variations

STYLE_KEYWORDS = frozenset({
    # Core styles
    "scientific illustration", "scientific illustration style",
    "photorealistic", "modern", "minimalist", "modern minimalist",
    "abstract", "conceptual",
    # Artistic styles
    "3d render", "digital art", "watercolor", "photograph",
    "illustration", "visualization",
    # Scientific specific
    "medical visualization", "molecular visualization",
    "scientific visualization", "scientific imaging",
    # Descriptors that imply style
    "style", "artistic", "realistic",
})

QUALITY_KEYWORDS = frozenset({
    # Detail modifiers
    "detailed", "high detail", "highly detailed", "intricate",
    # Professional quality
    "professional", "publication", "publication-quality",
    "academic publication", "suitable for publication",
    # Resolution indicators
    "4k", "high resolution", "sharp", "sharp focus",
    # General quality
    "quality", "polished",
})

TECHNICAL_KEYWORDS = frozenset({
    # Background
    "background", "white background", "clean background",
    "neutral background", "simple background",
    # Lighting
    "lighting", "well-lit", "professional lighting",
    "light", "lit",
    # Contrast and composition
    "contrast", "high contrast",
    "composition", "centered", "balanced", "centered composition",
    "rule of thirds", "simple composition",
    # Environment
    "clean", "environment",
})

MEDIUM_KEYWORDS = frozenset({
    # Artistic mediums
    "digital art", "3d render", "photograph", "illustration",
    "watercolor", "painting", "render",
    # Scientific visualization types
    "visualization", "diagram", "schematic",
    "microscopic view", "conceptual illustration",
})

# Scientific subject indicators (not exhaustive, but helps detect subject)
SCIENTIFIC_SUBJECT_KEYWORDS = frozenset({
    "dna", "rna", "cell", "cells", "protein", "molecule", "molecular",
    "laboratory", "lab", "microscope", "microscopic",
    "gene", "genome", "crispr", "enzyme", "receptor",
    "bacteria", "virus", "cancer", "tumor", "tissue",
    "structure", "mechanism", "pathway", "process",
    "research", "experiment", "equipment",
})

PromptLength = Literal["too_short", "short", "optimal", "long", "too_long"]


@dataclass
class PromptComponent:
    """Analysis of a single prompt component."""
    present: bool
    keywords_found: list[str] = field(default_factory=list)
    confidence: float = 0.0  # 0-1, how confident we are the component exists


@dataclass
class PromptAnalysis:
    """Result of prompt component analysis."""
    prompt: str
    word_count: int
    subject: PromptComponent
    style: PromptComponent
    medium: PromptComponent
    technical: PromptComponent
    quality: PromptComponent
    length_category: PromptLength
    warnings: list[str]
    suggestions: list[str]

    @property
    def component_count(self) -> int:
        """Count of present components (out of 5)."""
        return sum([
            self.subject.present,
            self.style.present,
            self.medium.present,
            self.technical.present,
            self.quality.present,
        ])

    @property
    def completeness_score(self) -> float:
        """Score from 0-1 based on component coverage and confidence."""
        total_confidence = sum([
            self.subject.confidence,
            self.style.confidence,
            self.medium.confidence,
            self.technical.confidence,
            self.quality.confidence,
        ])
        return total_confidence / 5

    @property
    def is_optimal_length(self) -> bool:
        """Check if prompt is in optimal length range."""
        return self.length_category == "optimal"

    @property
    def is_viable(self) -> bool:
        """Check if prompt is at least viable for generation."""
        return (
            self.length_category not in ("too_short", "too_long")
            and self.component_count >= 2
            and self.subject.present
        )


def _find_keywords(text: str, keywords: frozenset[str]) -> list[str]:
    """Find all matching keywords in text (case-insensitive)."""
    text_lower = text.lower()
    found = []
    for kw in keywords:
        if kw in text_lower:
            found.append(kw)
    return found


def _analyze_component(
    text: str,
    keywords: frozenset[str],
) -> PromptComponent:
    """Analyze a prompt for presence of a component."""
    found = _find_keywords(text, keywords)

    if not found:
        return PromptComponent(present=False, keywords_found=[], confidence=0.0)

    # Confidence based on number and specificity of matches
    # More specific (longer) keywords get higher weight
    confidence = min(1.0, sum(len(kw.split()) * 0.2 for kw in found))

    return PromptComponent(
        present=True,
        keywords_found=found,
        confidence=confidence,
    )


def _categorize_length(word_count: int) -> PromptLength:
    """Categorize prompt length."""
    if word_count < MIN_VIABLE_LENGTH:
        return "too_short"
    elif word_count < MIN_OPTIMAL_LENGTH:
        return "short"
    elif word_count <= MAX_OPTIMAL_LENGTH:
        return "optimal"
    elif word_count <= MAX_VIABLE_LENGTH:
        return "long"
    else:
        return "too_long"


def analyze_prompt(prompt: str) -> PromptAnalysis:
    """
    Analyze prompt against the 5-component formula.

    Formula: [SUBJECT] + [STYLE] + [MEDIUM] + [TECHNICAL] + [QUALITY]

    Args:
        prompt: The image generation prompt

    Returns:
        PromptAnalysis with component coverage and suggestions
    """
    words = prompt.split()
    word_count = len(words)

    # Analyze each component
    style = _analyze_component(prompt, STYLE_KEYWORDS)
    medium = _analyze_component(prompt, MEDIUM_KEYWORDS)
    technical = _analyze_component(prompt, TECHNICAL_KEYWORDS)
    quality = _analyze_component(prompt, QUALITY_KEYWORDS)

    # Subject detection is special - we assume present if prompt has content
    # and boost confidence if scientific keywords found
    scientific_keywords = _find_keywords(prompt, SCIENTIFIC_SUBJECT_KEYWORDS)
    if word_count > 3:
        subject_confidence = 0.5  # Base confidence for having any content
        if scientific_keywords:
            subject_confidence = min(1.0, 0.5 + len(scientific_keywords) * 0.15)
        subject = PromptComponent(
            present=True,
            keywords_found=scientific_keywords,
            confidence=subject_confidence,
        )
    else:
        subject = PromptComponent(present=False, keywords_found=[], confidence=0.0)

    length_category = _categorize_length(word_count)

    # Generate warnings
    warnings = []
    if length_category == "too_short":
        warnings.append(f"Prompt too short ({word_count} words) - likely vague or incomplete")
    elif length_category == "short":
        warnings.append(f"Prompt is short ({word_count} words) - consider adding more detail")
    elif length_category == "too_long":
        warnings.append(f"Prompt very long ({word_count} words) - may confuse model or exceed limits")

    if not style.present:
        warnings.append("Missing STYLE component (e.g., 'scientific illustration style')")
    if not quality.present:
        warnings.append("Missing QUALITY component (e.g., 'high detail', 'professional')")
    if not technical.present:
        warnings.append("Missing TECHNICAL component (e.g., 'clean background', 'well-lit')")
    if not medium.present:
        warnings.append("Consider adding MEDIUM component (e.g., 'digital art', '3D render')")

    # Generate suggestions
    suggestions = []
    if not style.present:
        suggestions.append("Add style: 'scientific illustration style' or 'photorealistic'")
    if not quality.present:
        suggestions.append("Add quality: 'high detail', 'professional', or 'publication-quality'")
    if not technical.present:
        suggestions.append("Add technical: 'clean white background' or 'well-lit'")
    if length_category == "too_short":
        suggestions.append("Expand prompt with more descriptive details about the subject")

    return PromptAnalysis(
        prompt=prompt,
        word_count=word_count,
        subject=subject,
        style=style,
        medium=medium,
        technical=technical,
        quality=quality,
        length_category=length_category,
        warnings=warnings,
        suggestions=suggestions,
    )


def format_analysis(analysis: PromptAnalysis) -> str:
    """Format analysis for display."""
    lines = []

    # Header
    lines.append(f"Prompt Analysis ({analysis.word_count} words)")
    lines.append("=" * 50)

    # Length assessment
    length_emoji = {
        "too_short": "❌",
        "short": "⚠️",
        "optimal": "✅",
        "long": "⚠️",
        "too_long": "❌",
    }
    lines.append(f"Length: {analysis.length_category} {length_emoji[analysis.length_category]}")
    lines.append(f"Completeness: {analysis.completeness_score:.0%}")
    lines.append(f"Components: {analysis.component_count}/5")
    lines.append("")

    # Component details
    lines.append("Component Coverage:")

    def format_component(name: str, comp: PromptComponent) -> str:
        status = "✅" if comp.present else "❌"
        if comp.present and comp.keywords_found:
            keywords = ", ".join(comp.keywords_found[:3])
            if len(comp.keywords_found) > 3:
                keywords += f" (+{len(comp.keywords_found) - 3} more)"
            return f"  {status} {name}: {keywords}"
        return f"  {status} {name}"

    lines.append(format_component("Subject", analysis.subject))
    lines.append(format_component("Style", analysis.style))
    lines.append(format_component("Medium", analysis.medium))
    lines.append(format_component("Technical", analysis.technical))
    lines.append(format_component("Quality", analysis.quality))

    # Warnings
    if analysis.warnings:
        lines.append("")
        lines.append("Warnings:")
        for w in analysis.warnings:
            lines.append(f"  ⚠️ {w}")

    # Suggestions
    if analysis.suggestions:
        lines.append("")
        lines.append("Suggestions:")
        for s in analysis.suggestions:
            lines.append(f"  💡 {s}")

    # Viability
    lines.append("")
    if analysis.is_viable:
        lines.append("Status: ✅ Prompt is viable for generation")
    else:
        lines.append("Status: ❌ Prompt needs improvement before generation")

    return "\n".join(lines)


def suggest_improvements(prompt: str) -> str:
    """
    Analyze prompt and return improved version with suggestions applied.

    Args:
        prompt: Original prompt

    Returns:
        Suggested improved prompt
    """
    analysis = analyze_prompt(prompt)

    additions = []

    if not analysis.style.present:
        additions.append("scientific illustration style")

    if not analysis.quality.present:
        additions.append("high detail, professional")

    if not analysis.technical.present:
        additions.append("clean background")

    if additions:
        return f"{prompt}, {', '.join(additions)}"

    return prompt


def batch_analyze(prompts: list[str]) -> list[PromptAnalysis]:
    """Analyze multiple prompts."""
    return [analyze_prompt(p) for p in prompts]


def summarize_batch(analyses: list[PromptAnalysis]) -> dict:
    """Summarize batch analysis results."""
    total = len(analyses)
    if total == 0:
        return {"total": 0}

    viable = sum(1 for a in analyses if a.is_viable)
    optimal_length = sum(1 for a in analyses if a.is_optimal_length)
    avg_components = sum(a.component_count for a in analyses) / total
    avg_completeness = sum(a.completeness_score for a in analyses) / total

    component_coverage = {
        "subject": sum(1 for a in analyses if a.subject.present),
        "style": sum(1 for a in analyses if a.style.present),
        "medium": sum(1 for a in analyses if a.medium.present),
        "technical": sum(1 for a in analyses if a.technical.present),
        "quality": sum(1 for a in analyses if a.quality.present),
    }

    return {
        "total": total,
        "viable": viable,
        "viable_rate": viable / total,
        "optimal_length": optimal_length,
        "avg_components": round(avg_components, 1),
        "avg_completeness": round(avg_completeness, 2),
        "component_coverage": component_coverage,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python analyze_prompt.py 'your prompt here'")
        print("\nAnalyzes prompts against the 5-component formula:")
        print("  [SUBJECT] + [STYLE] + [MEDIUM] + [TECHNICAL] + [QUALITY]")
        print("\nOptions:")
        print("  --suggest    Show improved version of prompt")
        sys.exit(1)

    # Check for --suggest flag
    suggest_mode = "--suggest" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    prompt = " ".join(args)
    analysis = analyze_prompt(prompt)
    print(format_analysis(analysis))

    if suggest_mode:
        print("")
        print("Suggested Improvement:")
        print("-" * 50)
        improved = suggest_improvements(prompt)
        print(improved)

    sys.exit(0 if analysis.is_viable else 1)
