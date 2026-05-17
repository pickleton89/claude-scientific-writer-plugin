"""Tests for output_validator.py — compiler output validation."""

import sys
from pathlib import Path

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from output_validator import (
    ValidationResult,
    count_words,
    count_citations,
    count_uncited_assertions,
    validate_output,
    validate_from_json,
    validate_against_contract,
    _find_section,
    _normalize_section_tokens,
    _extract_headings,
    _strip_code_blocks,
    _strip_references_section,
)
from output_contract import build_contract, contract_to_json
from thresholds import (
    WORD_COUNTS,
    MANDATORY_SECTIONS_ALL,
    MANDATORY_SECTIONS_BY_MODE,
    ALL_MODES,
)


# =============================================================================
# Fixtures
# =============================================================================


def _make_markdown(mode: str, word_target: int = 0, sections: list[str] | None = None,
                   citation_count: int = 5, include_ai_disclosure: bool = True,
                   include_db_versions: bool = True) -> str:
    """Helper to generate test markdown with expected structure."""
    if word_target == 0:
        limits = WORD_COUNTS.get(mode, WORD_COUNTS["full"])
        word_target = limits["target_min"]

    lines = []

    # Mode-specific sections
    if sections is None:
        sections = list(MANDATORY_SECTIONS_ALL) + list(MANDATORY_SECTIONS_BY_MODE.get(mode, ()))

    for section in sections:
        if section == "References":
            continue  # Add at end
        lines.append(f"## {section}\n")
        # Add filler text
        if section == "AI Disclosure" and include_ai_disclosure:
            lines.append("Search date: 2026-03-27. Databases queried: PubMed, Consensus. "
                         "Sources verified: 80% spot-checked via full-text retrieval.\n")
        elif section == "Methods" and include_db_versions:
            lines.append("Database version: PubMed accessed on 2026-03-27, API version 2.0.\n")
        else:
            lines.append("Content for this section. " * 20 + "\n")

    # Add citations scattered through the text
    for i in range(citation_count):
        tier = (i % 4) + 1
        lines.append(f"This finding is supported by evidence [T{tier}: Smith et al. 2024].\n")

    # Pad to approximate target word count
    current_words = len(" ".join(lines).split())
    if current_words < word_target:
        padding_words = word_target - current_words
        filler = " ".join(["word"] * padding_words)
        lines.append(f"\n{filler}\n")

    # References section (excluded from word count)
    lines.append("\n## References\n")
    lines.append("1. Smith et al. (2024). Title. *Journal*, 1-10.\n")
    lines.append("2. Jones et al. (2023). Title. *Journal*, 11-20.\n")

    return "\n".join(lines)


# =============================================================================
# Word Counting Tests
# =============================================================================


class TestWordCount:
    def test_basic_word_count(self):
        """Counts words in plain text."""
        text = "one two three four five"
        assert count_words(text) == 5

    def test_excludes_code_blocks(self):
        """Code blocks not counted."""
        text = "one two three\n```\ncode not counted here please\n```\nfour five"
        assert count_words(text) == 5

    def test_excludes_references_section(self):
        """References section not counted."""
        text = "one two three\n## References\nfour five six seven eight"
        assert count_words(text) == 3

    def test_strips_heading_markers(self):
        """Heading markers (#) not counted as words."""
        text = "# Title\nsome content here"
        wc = count_words(text)
        assert wc == 4  # Title, some, content, here

    def test_empty_text(self):
        """Empty text → 0 words."""
        assert count_words("") == 0


# =============================================================================
# Citation Counting Tests
# =============================================================================


class TestCitationCount:
    def test_counts_standard_citations(self):
        """Counts [T1: source] format citations."""
        text = "Finding one [T1: Smith 2024]. Finding two [T2: Jones 2023]."
        assert count_citations(text) == 2

    def test_counts_all_tiers(self):
        """Counts T1-T4 citations."""
        text = "[T1: a] [T2: b] [T3: c] [T4: d]"
        assert count_citations(text) == 4

    def test_no_citations(self):
        """Text without citations → 0."""
        assert count_citations("No citations here.") == 0

    def test_invalid_tier_not_counted(self):
        """[T5: source] is not a valid citation."""
        assert count_citations("[T5: Invalid]") == 0

    def test_citation_with_complex_source(self):
        """Complex source names counted correctly."""
        text = "[T1: Smith, Jones & Brown (2024) Nature 600:123-145]"
        assert count_citations(text) == 1


# =============================================================================
# Section Detection Tests
# =============================================================================


class TestSectionDetection:
    def test_exact_match(self):
        """Exact section name matches."""
        headings = ["## Executive Summary", "## Methods", "## Results"]
        assert _find_section(headings, "Executive Summary") is True
        assert _find_section(headings, "Methods") is True

    def test_fuzzy_match_gap_analysis(self):
        """'Gaps in the Literature' matches 'Gap Analysis' via token overlap."""
        headings = ["## Gaps in the Literature"]
        # Required: "Gap Analysis" tokens → {"gap", "analysi"}
        # Heading tokens → {"gap", "literatur"}
        # "gap" overlaps — 1/2 = 50% → match
        assert _find_section(headings, "Gap Analysis") is True

    def test_no_match(self):
        """Non-matching section not found."""
        headings = ["## Introduction", "## Methods"]
        assert _find_section(headings, "Conclusion") is False

    def test_empty_headings(self):
        """Empty headings list → not found."""
        assert _find_section([], "Methods") is False

    def test_normalize_strips_hashes(self):
        """Token normalization strips markdown heading markers."""
        tokens = _normalize_section_tokens("## Executive Summary")
        assert "executive" in tokens or "executiv" in tokens
        assert "summary" in tokens or "summar" in tokens

    def test_normalize_strips_punctuation(self):
        """Token normalization strips punctuation."""
        tokens = _normalize_section_tokens("Key Findings:")
        assert all(t.isalpha() for t in tokens)

    def test_extract_headings(self):
        """Extract all headings from markdown."""
        md = "# Title\nText\n## Section\nMore text\n### Subsection\n"
        headings = _extract_headings(md)
        assert len(headings) == 3


# =============================================================================
# Socratic Mode Tests
# =============================================================================


class TestSocraticMode:
    def test_socratic_always_valid(self):
        """Socratic mode returns valid trivially (no compiler output)."""
        result = validate_output({"mode": "socratic", "markdown": ""})
        assert result.valid is True
        assert result.word_count == 0

    def test_socratic_ignores_content(self):
        """Socratic mode ignores any content provided."""
        result = validate_output({
            "mode": "socratic",
            "markdown": "Some unexpected content",
        })
        assert result.valid is True


# =============================================================================
# Full Mode Validation Tests
# =============================================================================


class TestFullModeValidation:
    def test_valid_full_output(self):
        """Well-formed full-mode output passes validation."""
        md = _make_markdown("full")
        result = validate_output({"mode": "full", "markdown": md})
        assert result.valid is True
        assert len(result.errors) == 0

    def test_word_count_below_hard_min(self):
        """Word count below hard min → error."""
        md = "# Short\nToo few words here."
        result = validate_output({"mode": "full", "markdown": md})
        assert result.valid is False
        assert any("below hard minimum" in e for e in result.errors)

    def test_word_count_below_target_min(self):
        """Word count below target but above hard min → warning."""
        limits = WORD_COUNTS["full"]
        # hard_min=2500, target_min=3000 — aim for ~2600 words
        target = limits["hard_min"] + 100
        md = _make_markdown("full", word_target=target)
        result = validate_output({"mode": "full", "markdown": md})
        assert not any("below hard minimum" in e for e in result.errors)
        assert any("below target minimum" in w for w in result.warnings)

    def test_missing_mandatory_section_error(self):
        """Missing mandatory section → error."""
        # Build markdown without References
        md = "## Executive Summary\nContent.\n## Methods\nContent.\n## Results\nContent.\n## Discussion\nContent.\n## AI Disclosure\nSearch date: 2026-03-27. Databases queried: PubMed. Sources verified: 80%.\n## Limitations\nContent.\n"
        md += "word " * 3000
        md += "[T1: Smith 2024] "
        result = validate_output({"mode": "full", "markdown": md})
        # References section is missing as a heading
        assert any("References" in e for e in result.errors)

    def test_no_citations_error(self):
        """No citations → error for non-review modes."""
        md = _make_markdown("full", citation_count=0)
        result = validate_output({"mode": "full", "markdown": md})
        assert any("No [T1-4" in e for e in result.errors)


# =============================================================================
# Review Mode Tests
# =============================================================================


class TestReviewMode:
    def test_review_no_citations_ok(self):
        """Review mode allows zero citations."""
        md = _make_markdown("review", citation_count=0)
        result = validate_output({"mode": "review", "markdown": md})
        assert not any("citation" in e.lower() for e in result.errors)


# =============================================================================
# Quick Mode Tests
# =============================================================================


class TestQuickMode:
    def test_valid_quick_output(self):
        """Valid quick-mode output passes."""
        md = _make_markdown("quick")
        result = validate_output({"mode": "quick", "markdown": md})
        assert result.valid is True

    def test_quick_word_count_limits(self):
        """Quick mode has tighter word limits."""
        limits = WORD_COUNTS["quick"]
        assert limits["hard_min"] == 300
        assert limits["hard_max"] == 2000


# =============================================================================
# AI Disclosure Tests
# =============================================================================


class TestAIDisclosure:
    def test_missing_search_date_warning(self):
        """AI Disclosure without search date → warning."""
        # Build markdown with AI Disclosure that has databases+verified but NO date text
        md = (
            "## Executive Summary\n" + "word " * 500 + "\n"
            "## Methods\nDatabase version: PubMed API v2.0.\n"
            "## Results\n" + "word " * 1000 + "\n"
            "## Discussion\n" + "word " * 500 + "\n"
            "## AI Disclosure\nDatabases queried: PubMed. Sources verified: 80%.\n"
            "## Limitations\nSome limitations apply.\n"
            "## References\n1. Smith (2024). Title. Journal.\n"
            + "[T1: Smith 2024] " * 5
            + "word " * 1000
        )
        result = validate_output({"mode": "full", "markdown": md})
        assert any("search date" in w.lower() for w in result.warnings)

    def test_complete_ai_disclosure_no_warnings(self):
        """Complete AI Disclosure → no AI disclosure warnings."""
        md = _make_markdown("full")
        result = validate_output({"mode": "full", "markdown": md})
        ai_warnings = [w for w in result.warnings if "AI Disclosure" in w]
        assert len(ai_warnings) == 0


# =============================================================================
# Database Versions Tests
# =============================================================================


class TestDatabaseVersions:
    def test_missing_db_versions_warning(self):
        """Missing database versions in Methods → warning for applicable modes."""
        # Build markdown manually without any version/search-date text
        # so _check_database_versions fails
        md = (
            "## Executive Summary\n" + "word " * 500 + "\n"
            "## Methods\nWe queried multiple sources.\n"
            "## Results\n" + "word " * 1000 + "\n"
            "## Discussion\n" + "word " * 500 + "\n"
            "## AI Disclosure\nDatabases queried: PubMed. Sources verified: 80%.\n"
            "## Limitations\nSome limitations apply.\n"
            "## References\n1. Smith (2024). Title. Journal.\n"
            + "[T1: Smith 2024] " * 5
            + "word " * 1000
        )
        result = validate_output({"mode": "full", "markdown": md})
        assert any("database version" in w.lower() for w in result.warnings)

    def test_db_versions_not_required_for_fact_check(self):
        """Fact-check mode doesn't require database versions."""
        md = _make_markdown("fact-check", include_db_versions=False)
        result = validate_output({"mode": "fact-check", "markdown": md})
        assert not any("database version" in w.lower() for w in result.warnings)


# =============================================================================
# Uncited Assertions Tests
# =============================================================================


class TestUncitedAssertions:
    def test_no_uncited_assertions(self):
        """Text with all citations → 0 uncited assertions."""
        md = "## Results\nThis finding is well supported [T1: Smith 2024].\n"
        assert count_uncited_assertions(md) == 0

    def test_detects_uncited_assertions(self):
        """Declarative sentences without citations counted."""
        md = "## Results\nThe protein is expressed at high levels in tumor cells and has been shown to correlate with poor prognosis.\n"
        count = count_uncited_assertions(md)
        assert count >= 1

    def test_many_uncited_does_not_crash(self):
        """Output with many uncited assertions is handled without error."""
        results_text = "## Results\n"
        for i in range(6):
            results_text += f"The data clearly shows that factor {i} is associated with the disease outcome in multiple studies.\n"
        md = _make_markdown("full") + results_text
        result = validate_output({"mode": "full", "markdown": md})
        assert isinstance(result.uncited_assertions, int)
        assert result.uncited_assertions >= 0


# =============================================================================
# JSON Interface Tests
# =============================================================================


class TestJSONInterface:
    def test_validate_from_json(self):
        """JSON wrapper returns correct structure."""
        md = _make_markdown("full")
        result = validate_from_json({"mode": "full", "markdown": md})
        assert "valid" in result
        assert "word_count" in result
        assert "errors" in result
        assert "warnings" in result
        assert "section_report" in result
        assert "citation_count" in result
        assert "uncited_assertions" in result


# =============================================================================
# Mode Coverage Tests
# =============================================================================


class TestModeCoverage:
    def test_all_modes_have_word_counts(self):
        """Every mode in ALL_MODES has a WORD_COUNTS entry."""
        for mode in ALL_MODES:
            assert mode in WORD_COUNTS, f"Mode {mode} missing from WORD_COUNTS"

    def test_all_modes_have_mandatory_sections(self):
        """Every mode in ALL_MODES has a MANDATORY_SECTIONS_BY_MODE entry."""
        for mode in ALL_MODES:
            assert mode in MANDATORY_SECTIONS_BY_MODE, (
                f"Mode {mode} missing from MANDATORY_SECTIONS_BY_MODE"
            )

    def test_all_modes_can_be_validated(self):
        """validate_output doesn't crash for any mode."""
        for mode in ALL_MODES:
            if mode == "socratic":
                result = validate_output({"mode": mode, "markdown": ""})
            else:
                md = _make_markdown(mode)
                result = validate_output({"mode": mode, "markdown": md})
            assert isinstance(result, ValidationResult)


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    def test_empty_markdown(self):
        """Empty markdown for non-socratic mode → errors."""
        result = validate_output({"mode": "full", "markdown": ""})
        assert result.valid is False
        assert len(result.errors) > 0

    def test_unknown_mode_uses_full_defaults(self):
        """Unknown mode falls back to full defaults."""
        md = _make_markdown("full")
        result = validate_output({"mode": "unknown_mode", "markdown": md})
        # Should use full mode word count limits
        assert isinstance(result.word_count, int)

    def test_code_blocks_excluded_from_word_count(self):
        """Large code blocks don't inflate word count."""
        code = "```python\n" + "x = 1\n" * 500 + "```\n"
        text = "One two three four five.\n" + code
        assert count_words(text) < 20

    def test_strip_code_blocks(self):
        """_strip_code_blocks removes fenced blocks."""
        text = "before ```code``` after"
        result = _strip_code_blocks(text)
        assert "code" not in result
        assert "before" in result
        assert "after" in result

    def test_strip_references_section(self):
        """_strip_references_section removes references."""
        text = "Content.\n## References\nRef1\nRef2\n"
        result = _strip_references_section(text)
        assert "Ref1" not in result
        assert "Content" in result

    def test_validation_result_dataclass(self):
        """ValidationResult dataclass works correctly."""
        vr = ValidationResult(mode="full", valid=True, word_count=5000)
        assert vr.errors == []
        assert vr.warnings == []
        assert vr.citation_count == 0


# =============================================================================
# Contract-Based Validation Tests
# =============================================================================


def _make_contract_compliant_md(mode: str = "full", word_target: int = 0) -> tuple[str, dict]:
    """Build a contract and matching compliant markdown.

    Returns (markdown, contract_json).
    """
    contract = build_contract(mode=mode, user_prompt="test", topic="test")
    contract_json = contract_to_json(contract)

    if word_target == 0:
        limits = WORD_COUNTS.get(mode, WORD_COUNTS["full"])
        word_target = limits["target_min"]

    sections = contract_json.get("sections", [])
    content_section_count = sum(
        1 for s in sections
        if s["canonical_name"] not in ("References", "AI Disclosure", "Methods")
    )
    content_section_count = max(content_section_count, 1)
    words_per_section = max(word_target // content_section_count, 30)

    lines: list[str] = []

    for spec in sections:
        name = spec["canonical_name"]
        lines.append(f"## {name}\n")

        if name == "AI Disclosure":
            lines.append(
                "Search date: 2026-03-28. Databases queried: PubMed, Consensus. "
                "Sources verified: 85% spot-checked via full-text retrieval.\n"
            )
        elif name == "Methods":
            lines.append(
                "Database version: PubMed accessed on 2026-03-28, API version 2.0. "
                "We searched PubMed and Consensus for relevant studies.\n"
            )
            for sub in spec.get("subsection_specs", []):
                sub_name = sub.get("canonical_name", "Subsection")
                lines.append(f"### {sub_name}\n")
                lines.append(
                    "Detailed methods for this subsection covering analytical procedures. " * 3 + "\n"
                )
        elif name == "References":
            lines.append("1. Smith et al. (2024). Title. *Journal*, 1-10.\n")
        else:
            subsections = spec.get("subsection_specs", [])

            body_sentence = (
                "This section presents key findings on the research topic "
                "[T1: Smith et al. 2024]. Further evidence supports the conclusion "
                "[T2: Jones 2023]. Additional analysis confirms the overall pattern "
                "and strengthens confidence in the results [T3: Brown 2025]. "
            )
            repeats = max(words_per_section // 30, 1)
            lines.append(body_sentence * repeats + "\n")

            # One ### heading per subsection spec entry (stays within validator bounds)
            for sub in subsections:
                sub_name = sub.get("canonical_name", "Subsection")
                lines.append(f"### {sub_name}\n")
                lines.append(
                    "Analysis of this subtopic reveals key patterns "
                    "[T1: Adams 2024]. " * max(repeats // 2, 1) + "\n"
                )

    # Compute current word count and pad if needed
    current_md = "\n".join(lines)
    current_words = count_words(current_md)

    if current_words < word_target:
        padding_needed = word_target - current_words + 50
        padding_sentence = "The research demonstrates important findings in this domain. "
        repeat_count = (padding_needed // 8) + 1
        # Insert padding before References
        ref_marker = "\n## References\n"
        if ref_marker in current_md:
            parts = current_md.split(ref_marker, 1)
            padded = parts[0] + "\n" + padding_sentence * repeat_count + "\n" + ref_marker + parts[1]
            return padded, contract_json
        lines.append(f"\n{padding_sentence * repeat_count}\n")

    return "\n".join(lines), contract_json


class TestContractValidation:
    def test_contract_validation_valid_output(self):
        """Compliant markdown passes contract validation."""
        md, contract_json = _make_contract_compliant_md("full")
        result = validate_against_contract(markdown=md, contract=contract_json, file_count=1)
        assert result.valid is True, f"Errors: {result.errors}"

    def test_contract_validation_extra_section(self):
        """Extra ## heading triggers warning."""
        md, contract_json = _make_contract_compliant_md("full")
        # Inject an extra section not in the contract
        md += "\n## Bonus Zebra Section\nExtra content here.\n"
        result = validate_against_contract(markdown=md, contract=contract_json, file_count=1)
        assert any("Extra section" in w or "not in contract" in w for w in result.warnings), (
            f"Expected extra-section warning. Got warnings: {result.warnings}"
        )

    def test_contract_validation_missing_section(self):
        """Missing required section triggers error."""
        contract = build_contract(mode="full", user_prompt="test", topic="test")
        contract_json = contract_to_json(contract)

        # Build markdown missing "Executive Summary"
        lines = []
        for spec in contract_json["sections"]:
            name = spec["canonical_name"]
            if name == "Executive Summary":
                continue  # Skip it
            lines.append(f"## {name}\n")
            if name == "AI Disclosure":
                lines.append(
                    "Search date: 2026-03-28. Databases queried: PubMed. "
                    "Sources verified: 80%.\n"
                )
            elif name == "Methods":
                lines.append("Database version: PubMed accessed on 2026-03-28.\n")
            elif name == "References":
                lines.append("1. Smith (2024). Title. *Journal*.\n")
            else:
                lines.append("Content. " * 50 + "[T1: Smith 2024] " * 3 + "\n")
        lines.append("word " * 3000 + "\n")

        md = "\n".join(lines)
        result = validate_against_contract(markdown=md, contract=contract_json, file_count=1)
        assert any("Executive Summary" in e for e in result.errors), (
            f"Expected missing-section error for Executive Summary. Got: {result.errors}"
        )

    def test_contract_validation_latex_detected(self):
        """LaTeX content triggers error."""
        md, contract_json = _make_contract_compliant_md("full")
        md += r"\begin{document}" + "\n"
        result = validate_against_contract(markdown=md, contract=contract_json, file_count=1)
        assert any("LaTeX" in e or "Non-markdown" in e for e in result.errors), (
            f"Expected LaTeX error. Got: {result.errors}"
        )

    def test_contract_validation_file_count_exceeded(self):
        """file_count > max_files triggers error."""
        md, contract_json = _make_contract_compliant_md("full")
        # Full mode max_files is 1
        result = validate_against_contract(markdown=md, contract=contract_json, file_count=5)
        assert any("File count" in e for e in result.errors), (
            f"Expected file-count error. Got: {result.errors}"
        )

    def test_backward_compatibility(self):
        """Existing validate_output still works unchanged."""
        md = _make_markdown("full")
        result = validate_output({"mode": "full", "markdown": md})
        assert isinstance(result, ValidationResult)
        assert result.valid is True
        assert result.word_count > 0
        assert result.citation_count > 0


# ──────────────────────────────────────────────────────────────────────
# Sidecar enforcement (evidence pinning)
# ──────────────────────────────────────────────────────────────────────


def _copy_fixture_sidecars(dest: Path, mode: str, date: str, topic_slug: str) -> None:
    """Materialize fixture sidecars under canonical filenames in dest."""
    import shutil
    from thresholds import SIDECAR_SPECS, sidecar_filename

    fixtures = Path(__file__).parent / "fixtures" / "sidecars"
    kind_to_fixture = {
        "sources": "sources_minimal.json",
        "grading": "grading_minimal.json",
        "synthesis": "synthesis_minimal.json",
        "advocate": "advocate_minimal.json",
    }
    for kind in SIDECAR_SPECS[mode]:
        src = fixtures / kind_to_fixture[kind]
        dst = dest / sidecar_filename(mode, kind, date, topic_slug)
        shutil.copy(src, dst)


class TestSidecarEnforcement:
    """Validate the evidence-pinning gate in validate_against_contract."""

    def test_no_sidecar_params_means_no_check(self, tmp_path):
        """Back-compat: omitting report_dir/date/topic_slug skips sidecar checks."""
        md, contract_json = _make_contract_compliant_md("full")
        result = validate_against_contract(markdown=md, contract=contract_json, file_count=1)
        # No sidecar-related entries
        assert not any("Sidecar" in e for e in result.errors)
        assert not any("Sidecar" in w for w in result.warnings)

    def test_advisory_warns_on_missing_sidecars(self, tmp_path, monkeypatch):
        """Under 'advisory' enforcement → missing sidecars produce warnings, not errors.

        Monkeypatches the module-level constant so the test is independent of
        the default in thresholds.py.
        """
        import output_validator
        monkeypatch.setattr(output_validator, "SIDECAR_ENFORCEMENT", "advisory")
        md, contract_json = _make_contract_compliant_md("full")
        result = validate_against_contract(
            markdown=md,
            contract=contract_json,
            file_count=1,
            report_dir=tmp_path,
            date="2026-05-17",
            topic_slug="test-topic",
        )
        # Errors should not include sidecar-missing entries (advisory mode)
        assert not any("Sidecar missing" in e for e in result.errors)
        # Warnings SHOULD include advisory entries
        assert any("Sidecar advisory" in w for w in result.warnings), result.warnings

    def test_required_errors_on_missing_sidecars(self, tmp_path, monkeypatch):
        """Under 'required' enforcement → missing sidecars produce errors that fail the run."""
        import output_validator
        monkeypatch.setattr(output_validator, "SIDECAR_ENFORCEMENT", "required")
        md, contract_json = _make_contract_compliant_md("full")
        result = validate_against_contract(
            markdown=md,
            contract=contract_json,
            file_count=1,
            report_dir=tmp_path,
            date="2026-05-17",
            topic_slug="test-topic",
        )
        # Errors SHOULD include the missing-sidecar entries
        assert any("Sidecar missing/invalid" in e for e in result.errors), result.errors
        # And valid must be False
        assert result.valid is False

    def test_quick_mode_only_requires_two_sidecars(self, tmp_path):
        md, contract_json = _make_contract_compliant_md("quick")
        _copy_fixture_sidecars(tmp_path, "quick", "2026-05-17", "kras-inhibitors")
        result = validate_against_contract(
            markdown=md,
            contract=contract_json,
            file_count=1,
            report_dir=tmp_path,
            date="2026-05-17",
            topic_slug="kras-inhibitors",
        )
        # All 2 sidecars present → no sidecar warnings/errors
        sidecar_warns = [w for w in result.warnings if "Sidecar" in w and "advisory" in w]
        assert sidecar_warns == [], sidecar_warns

    def test_socratic_skips_sidecar_check(self, tmp_path):
        md, contract_json = _make_contract_compliant_md("socratic")
        # Socratic has empty SIDECAR_SPECS, so nothing should be checked
        result = validate_against_contract(
            markdown=md,
            contract=contract_json,
            file_count=0,
            report_dir=tmp_path,
            date="2026-05-17",
            topic_slug="x",
        )
        assert not any("Sidecar" in e for e in result.errors)

    def test_required_fails_closed_when_validator_unimportable(self, tmp_path, monkeypatch):
        """If validate_sidecar.py can't be imported (broken env), required mode MUST fail closed.

        Simulates the import failure by setting output_validator.SidecarValidator to None.
        Required mode should produce an error (not a warning) so a misconfigured
        environment can never silently bypass the gate.
        """
        import output_validator
        monkeypatch.setattr(output_validator, "SidecarValidator", None)
        monkeypatch.setattr(output_validator, "SIDECAR_ENFORCEMENT", "required")
        md, contract_json = _make_contract_compliant_md("full")
        result = validate_against_contract(
            markdown=md, contract=contract_json, file_count=1,
            report_dir=tmp_path, date="2026-05-17", topic_slug="x",
        )
        assert any("could not run" in e and "validate_sidecar.py" in e for e in result.errors), result.errors
        assert result.valid is False

    def test_advisory_warns_when_validator_unimportable(self, tmp_path, monkeypatch):
        """Same scenario as above but advisory mode: warning, not error."""
        import output_validator
        monkeypatch.setattr(output_validator, "SidecarValidator", None)
        monkeypatch.setattr(output_validator, "SIDECAR_ENFORCEMENT", "advisory")
        md, contract_json = _make_contract_compliant_md("full")
        result = validate_against_contract(
            markdown=md, contract=contract_json, file_count=1,
            report_dir=tmp_path, date="2026-05-17", topic_slug="x",
        )
        assert any("could not run" in w for w in result.warnings), result.warnings
        assert not any("could not run" in e for e in result.errors), result.errors

    def test_open_critical_always_blocks(self, tmp_path):
        """Open CRITICAL advocate finding → assembly blocked even in advisory mode."""
        import json
        from thresholds import sidecar_filename

        md, contract_json = _make_contract_compliant_md("full")
        _copy_fixture_sidecars(tmp_path, "full", "2026-05-17", "kras-inhibitors")

        # Inject an open CRITICAL into the advocate sidecar
        adv_path = tmp_path / sidecar_filename("full", "advocate", "2026-05-17", "kras-inhibitors")
        adv = json.loads(adv_path.read_text())
        adv["findings"].append({
            "id": "A-999",
            "checkpoint": 3,
            "category": "ethics",
            "description": "Dual-use concern unresolved.",
            "severity": "CRITICAL",
            "status": "open",
            "resolution_note": None,
        })
        adv_path.write_text(json.dumps(adv))

        result = validate_against_contract(
            markdown=md,
            contract=contract_json,
            file_count=1,
            report_dir=tmp_path,
            date="2026-05-17",
            topic_slug="kras-inhibitors",
        )
        # Open CRITICAL must surface as ERROR regardless of enforcement mode
        assert any("Open CRITICAL" in e and "A-999" in e for e in result.errors), result.errors
        assert result.valid is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
