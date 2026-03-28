"""End-to-end integration tests for the output contract → validator pipeline."""

import sys
from pathlib import Path

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from output_contract import build_contract, contract_to_json
from output_validator import validate_against_contract, validate_output
from thresholds import (
    ALL_MODES,
    MANDATORY_SECTIONS_ALL,
    MANDATORY_SECTIONS_BY_MODE,
    WORD_COUNTS,
)


# =============================================================================
# Sample prompts
# =============================================================================

PROMPT_2 = (
    "Conduct a literature review on CDK4/6 inhibitors in HR+ breast cancer.\n"
    "Deliverables:\n"
    "- Comparative Target Evaluation Matrix\n"
    "- Per-target evidence summaries\n"
    "- Gap analysis\n"
    "- Recommended shortlist\n"
    "- Limitations\n"
)

PROMPT_3 = (
    "Assess the safety profile of bispecific T-cell engagers.\n"
    "Format:\n"
    "- Risk Assessment Matrix\n"
    "- Per-category evidence synthesis\n"
    "- Integrated risk profile\n"
    "- Mitigation strategies\n"
    "- Critical unknowns and recommended experiments\n"
    "- Limitations\n"
)


# =============================================================================
# Helper: generate contract-compliant markdown
# =============================================================================


def _make_contract_compliant_markdown(contract_json: dict, word_target: int = 5000) -> str:
    """Generate mock markdown following a contract's section structure.

    Produces a valid document with all required sections, proper citations,
    and AI Disclosure content that passes validation. The word_target controls
    total word count (excluding References), adapting section bulk accordingly.
    """
    from output_validator import count_words

    sections = contract_json.get("sections", [])
    # Count content sections (excluding References and AI Disclosure which have fixed content)
    content_section_count = sum(
        1 for s in sections
        if s["canonical_name"] not in ("References", "AI Disclosure", "Methods")
    )
    content_section_count = max(content_section_count, 1)

    # Distribute words roughly evenly across content sections
    words_per_section = max(word_target // content_section_count, 30)

    lines: list[str] = []

    for spec in sections:
        name = spec["canonical_name"]
        lines.append(f"## {name}\n")

        if name == "AI Disclosure":
            lines.append(
                "Search date: 2026-03-28. Databases queried: PubMed, Consensus, bioRxiv. "
                "Sources verified: 85% spot-checked via full-text retrieval.\n"
            )
        elif name == "Methods":
            lines.append(
                "Database version: PubMed accessed on 2026-03-28, API version 2.0. "
                "We searched PubMed, Consensus, and bioRxiv for relevant studies. "
                "Inclusion criteria required peer-reviewed articles published after 2020. "
                "Exclusion criteria removed case reports and non-English publications.\n"
            )
            for sub in spec.get("subsection_specs", []):
                sub_name = sub.get("canonical_name", "Subsection")
                lines.append(f"### {sub_name}\n")
                lines.append(
                    "Detailed methods for this subsection covering analytical "
                    "procedures and data collection used throughout the study. " * 3 + "\n"
                )
        elif name == "References":
            lines.append("1. Smith et al. (2024). Title. *Journal*, 1-10.\n")
            lines.append("2. Jones et al. (2023). Title. *Journal*, 11-20.\n")
            lines.append("3. Brown et al. (2025). Title. *Journal*, 21-30.\n")
        else:
            # Generate subsection ### headings.
            # The validator counts ALL ### headings in a section and compares
            # against repeating-slot min/max (falling back to parent max_subsections).
            # To stay within bounds, generate exactly the subsection_specs listed
            # in the contract (one ### per entry), no more.
            subsections = spec.get("subsection_specs", [])

            # Main section body with citations
            body_sentence = (
                "The evidence indicates significant effects across multiple studies "
                "[T1: Smith et al. 2024]. Further analysis reveals additional patterns "
                "[T2: Jones 2023]. These results are consistent with prior work "
                "[T3: Brown 2025]. "
            )
            repeats = max(words_per_section // 30, 1)
            lines.append(body_sentence * repeats + "\n")

            # One ### heading per subsection spec entry
            for sub in subsections:
                sub_name = sub.get("canonical_name", "Subsection")
                lines.append(f"### {sub_name}\n")
                lines.append(
                    "Analysis of this subtopic reveals key patterns in the data "
                    "[T1: Adams 2024]. Additional evidence strengthens the conclusion "
                    "[T2: Clark 2023]. " * max(repeats // 2, 1) + "\n"
                )

    # Compute current word count and pad or trim
    current_md = "\n".join(lines)
    current_words = count_words(current_md)

    if current_words < word_target:
        padding_needed = word_target - current_words + 50
        padding_sentence = "The research demonstrates important findings in this domain. "
        repeat_count = (padding_needed // 8) + 1
        # Insert padding BEFORE References section
        ref_marker = "\n## References\n"
        if ref_marker in current_md:
            parts = current_md.split(ref_marker, 1)
            padded = parts[0] + "\n" + padding_sentence * repeat_count + "\n" + ref_marker + parts[1]
            return padded
        lines.append(f"\n{padding_sentence * repeat_count}\n")

    return "\n".join(lines)


def _make_run1_mock_output() -> str:
    """Create a mock of Run 1's problematic output: multi-file, 42K words, HTML.

    Simulates the typical failures from early runs:
      - Way over word limit
      - HTML tags present
      - Multiple file markers
      - Missing required sections
    """
    lines = []

    # Simulate multi-file structure with separators
    lines.append("<!-- FILE: part1.md -->")
    lines.append("# Report Part 1\n")

    # Lots of HTML content (not pure markdown)
    lines.append("<div class='summary'>")
    lines.append("<h2>Executive Summary</h2>")
    lines.append("<p>This is an HTML executive summary.</p>")
    lines.append("</div>\n")

    # Massive content block to simulate 42K words
    filler = "The study demonstrates that this finding is important. " * 200
    lines.append(f"## Results\n{filler}\n")

    lines.append("<!-- FILE: part2.md -->")
    lines.append("# Report Part 2\n")
    lines.append(f"## Discussion\n{filler}\n")

    # Missing: AI Disclosure, Limitations, References, Methods
    # Also missing citations entirely

    return "\n".join(lines)


# =============================================================================
# Full Pipeline Tests
# =============================================================================


class TestFullPipelinePrompt2:
    """Build contract for Prompt 2 (lit-review), generate compliant markdown, validate."""

    def test_full_pipeline_prompt2(self):
        contract = build_contract(
            mode="lit-review", user_prompt=PROMPT_2, topic="CDK4/6 inhibitors"
        )
        contract_json = contract_to_json(contract)

        # Generate compliant markdown with appropriate word count
        limits = WORD_COUNTS["lit-review"]
        md = _make_contract_compliant_markdown(contract_json, word_target=limits["target_min"])

        result = validate_against_contract(markdown=md, contract=contract_json, file_count=1)

        # Should pass — no errors
        assert result.valid is True, (
            f"Pipeline failed for lit-review Prompt 2.\n"
            f"Errors: {result.errors}\n"
            f"Warnings: {result.warnings}"
        )

    def test_prompt2_contract_has_expected_mappings(self):
        """Prompt 2 contract maps all 5 user items."""
        contract = build_contract(
            mode="lit-review", user_prompt=PROMPT_2, topic="CDK4/6 inhibitors"
        )
        # All 5 deliverables should be mapped
        assert len(contract.custom_content_map) == 5
        # No items should be unmapped (all are standard deliverables)
        assert len(contract.unmapped_items) == 0


class TestFullPipelinePrompt3:
    """Build contract for Prompt 3 (full), generate compliant markdown, validate."""

    def test_full_pipeline_prompt3(self):
        contract = build_contract(
            mode="full", user_prompt=PROMPT_3, topic="bispecific T-cell engagers"
        )
        contract_json = contract_to_json(contract)

        limits = WORD_COUNTS["full"]
        md = _make_contract_compliant_markdown(contract_json, word_target=limits["target_min"])

        result = validate_against_contract(markdown=md, contract=contract_json, file_count=1)

        assert result.valid is True, (
            f"Pipeline failed for full Prompt 3.\n"
            f"Errors: {result.errors}\n"
            f"Warnings: {result.warnings}"
        )

    def test_prompt3_contract_has_expected_mappings(self):
        """Prompt 3 contract maps all 6 user items."""
        contract = build_contract(
            mode="full", user_prompt=PROMPT_3, topic="bispecific T-cell engagers"
        )
        assert len(contract.custom_content_map) >= 4
        assert len(contract.unmapped_items) == 0


# =============================================================================
# Validator Catches Bad Output
# =============================================================================


class TestValidatorCatchesBadOutput:
    def test_validator_catches_run1_output(self):
        """Mock of Run 1's output (multi-file, huge, HTML) triggers errors."""
        contract = build_contract(mode="full", user_prompt="EGFR research", topic="EGFR")
        contract_json = contract_to_json(contract)

        md = _make_run1_mock_output()

        result = validate_against_contract(
            markdown=md, contract=contract_json, file_count=2
        )

        # Should fail validation
        assert result.valid is False

        error_text = " ".join(result.errors)
        # Should flag missing mandatory sections (at minimum: AI Disclosure, Limitations, References)
        assert any("Missing" in e for e in result.errors), (
            f"Expected missing-section errors. Got: {result.errors}"
        )
        # Should flag missing citations
        assert any("citation" in e.lower() for e in result.errors), (
            f"Expected citation error. Got: {result.errors}"
        )

    def test_validator_catches_latex(self):
        """Markdown containing LaTeX commands is flagged."""
        contract = build_contract(mode="full", user_prompt="test", topic="test")
        contract_json = contract_to_json(contract)

        # Build otherwise-valid markdown but inject LaTeX
        limits = WORD_COUNTS["full"]
        md = _make_contract_compliant_markdown(contract_json, word_target=limits["target_min"])
        md += r"\begin{document}" + "\n"
        md += r"\section{Introduction}" + "\n"

        result = validate_against_contract(markdown=md, contract=contract_json, file_count=1)

        # LaTeX detection should trigger an error
        assert any("LaTeX" in e or "Non-markdown" in e for e in result.errors), (
            f"Expected LaTeX error. Got errors: {result.errors}"
        )

    def test_validator_catches_excess_files(self):
        """file_count > max_files triggers error."""
        contract = build_contract(mode="full", user_prompt="test", topic="test")
        contract_json = contract_to_json(contract)

        limits = WORD_COUNTS["full"]
        md = _make_contract_compliant_markdown(contract_json, word_target=limits["target_min"])

        # Full mode max_files is 1; pass file_count=3
        result = validate_against_contract(markdown=md, contract=contract_json, file_count=3)

        assert any("File count" in e or "file_count" in e.lower() for e in result.errors), (
            f"Expected file count error. Got errors: {result.errors}"
        )


# =============================================================================
# Cross-Mode Pipeline Tests
# =============================================================================


class TestCrossModePipeline:
    """Verify the contract -> validate pipeline works for all non-socratic modes."""

    @pytest.mark.parametrize("mode", [m for m in ALL_MODES if m != "socratic"])
    def test_compliant_output_passes(self, mode):
        """Contract-compliant markdown passes validation for each mode."""
        contract = build_contract(mode=mode, user_prompt="test", topic="test")
        contract_json = contract_to_json(contract)

        limits = WORD_COUNTS[mode]
        md = _make_contract_compliant_markdown(
            contract_json, word_target=limits["target_min"]
        )

        result = validate_against_contract(
            markdown=md, contract=contract_json, file_count=1
        )

        assert result.valid is True, (
            f"Pipeline failed for mode '{mode}'.\n"
            f"Errors: {result.errors}\n"
            f"Warnings: {result.warnings}\n"
            f"Word count: {result.word_count}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
