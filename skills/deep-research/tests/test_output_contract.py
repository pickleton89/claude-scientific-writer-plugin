"""Tests for output_contract.py — contract builder, prompt mapping, and serialization."""

import json
import sys
from datetime import datetime
from pathlib import Path

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from output_contract import (
    OutputContract,
    SectionSpec,
    build_contract,
    contract_to_json,
    format_contract_for_user,
    _extract_user_format_specs,
    _fuzzy_map_section,
    _schema_dicts_to_specs,
    _flatten_specs,
)
from mode_selector import select_mode
from thresholds import ALL_MODES, SECTION_SCHEMAS


# =============================================================================
# Sample prompts used across multiple test classes
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

PROMPT_1 = (
    "What is the role of autophagy in neurodegenerative disease progression?"
)


# =============================================================================
# Schema Loading Tests
# =============================================================================


class TestSchemaLoading:
    def test_build_contract_all_modes(self):
        """Build contracts for all 8 modes; verify sections loaded."""
        for mode in ALL_MODES:
            contract = build_contract(mode=mode, user_prompt="test", topic="test")
            assert contract.mode == mode
            assert isinstance(contract.sections, list)
            # Modes with schemas should have sections loaded
            if SECTION_SCHEMAS.get(mode):
                assert len(contract.sections) > 0, (
                    f"Mode '{mode}' has SECTION_SCHEMAS but contract.sections is empty"
                )

    def test_build_contract_socratic_empty(self):
        """Socratic mode produces empty sections."""
        contract = build_contract(mode="socratic", user_prompt="test", topic="test")
        assert contract.mode == "socratic"
        assert len(contract.sections) == 0


# =============================================================================
# Prompt Mapping Tests
# =============================================================================


class TestPrompt2Mapping:
    """All 5 items from Prompt 2's format spec map correctly."""

    @pytest.fixture(autouse=True)
    def _build(self):
        self.contract = build_contract(
            mode="lit-review", user_prompt=PROMPT_2, topic="CDK4/6 inhibitors"
        )
        self.cmap = self.contract.custom_content_map

    def test_comparative_matrix_maps_to_results_overview(self):
        matches = [v for k, v in self.cmap.items() if "Comparative" in k or "Matrix" in k]
        assert "Results: Overview" in matches

    def test_per_target_evidence_maps_to_thematic_synthesis(self):
        matches = [v for k, v in self.cmap.items() if "Per-target" in k or "evidence summaries" in k.lower()]
        assert "Thematic Synthesis" in matches

    def test_gap_analysis_maps(self):
        matches = [v for k, v in self.cmap.items() if "gap" in k.lower()]
        assert "Gap Analysis" in matches

    def test_recommended_shortlist_maps_to_conclusion(self):
        matches = [v for k, v in self.cmap.items() if "shortlist" in k.lower()]
        assert "Conclusion" in matches

    def test_limitations_maps(self):
        matches = [v for k, v in self.cmap.items() if "limitation" in k.lower()]
        assert "Limitations" in matches


class TestPrompt3Mapping:
    """All 6 items from Prompt 3's format spec map correctly."""

    @pytest.fixture(autouse=True)
    def _build(self):
        self.contract = build_contract(
            mode="full", user_prompt=PROMPT_3, topic="bispecific T-cell engagers"
        )
        self.cmap = self.contract.custom_content_map

    def test_risk_assessment_matrix_maps_to_results_overview(self):
        matches = [v for k, v in self.cmap.items() if "Risk Assessment" in k]
        assert "Results: Overview" in matches

    def test_per_category_evidence_maps_to_thematic_synthesis(self):
        matches = [v for k, v in self.cmap.items() if "Per-category" in k or "evidence synthesis" in k.lower()]
        assert "Thematic Synthesis" in matches

    def test_integrated_risk_profile_maps_to_discussion(self):
        matches = [v for k, v in self.cmap.items() if "Integrated risk" in k]
        assert "Discussion" in matches

    def test_mitigation_strategies_maps_to_discussion(self):
        matches = [v for k, v in self.cmap.items() if "Mitigation" in k]
        assert "Discussion" in matches

    def test_critical_unknowns_maps_to_gap_analysis(self):
        matches = [v for k, v in self.cmap.items() if "Critical unknowns" in k or "unknowns" in k.lower()]
        assert "Gap Analysis" in matches

    def test_limitations_maps(self):
        matches = [v for k, v in self.cmap.items() if "limitation" in k.lower()]
        assert "Limitations" in matches


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    def test_empty_prompt_no_warnings(self):
        """Empty user prompt produces no warnings (no unmapped items)."""
        contract = build_contract(mode="full", user_prompt="", topic="test")
        # Should not have any unmapped-item warnings
        unmapped_warnings = [w for w in contract.warnings if "unmapped" in w.lower()]
        assert len(unmapped_warnings) == 0

    def test_unknown_format_item(self):
        """Completely novel section name lands in unmapped_items."""
        prompt = (
            "Format:\n"
            "- Xenobiotic Metabolomics Dashboard\n"
        )
        contract = build_contract(mode="full", user_prompt=prompt, topic="test")
        assert any("Xenobiotic" in item for item in contract.unmapped_items)

    def test_preamble_phrases_skipped(self):
        """'The final report should include:' is filtered out, not mapped."""
        prompt = (
            "The final report should include:\n"
            "- Gap analysis\n"
        )
        contract = build_contract(mode="full", user_prompt=prompt, topic="test")
        # "The final report should include:" should NOT appear in custom_content_map keys
        # or unmapped_items
        all_items = list(contract.custom_content_map.keys()) + contract.unmapped_items
        assert not any("final report should" in item.lower() for item in all_items)

    def test_contract_frozen_timestamp(self):
        """Contract has a frozen_at ISO timestamp."""
        contract = build_contract(mode="full", user_prompt="test", topic="test")
        assert contract.frozen_at is not None
        # Should parse as valid ISO timestamp
        parsed = datetime.fromisoformat(contract.frozen_at)
        assert parsed.year >= 2026

    def test_invalid_mode_raises(self):
        """Unknown mode raises ValueError."""
        with pytest.raises(ValueError, match="Unknown mode"):
            build_contract(mode="nonexistent", user_prompt="test", topic="test")


# =============================================================================
# Contract Format Tests
# =============================================================================


class TestContractFormat:
    def test_format_contract_for_user(self):
        """Renders as readable markdown with expected structure."""
        contract = build_contract(mode="full", user_prompt="test", topic="EGFR")
        rendered = format_contract_for_user(contract)
        assert isinstance(rendered, str)
        assert "# Output Contract" in rendered
        assert "**Mode:** full" in rendered
        assert "**Topic:** EGFR" in rendered
        assert "## Word Count Targets" in rendered
        assert "## Section Structure" in rendered

    def test_format_contract_with_mappings(self):
        """Rendered contract includes user format mappings table."""
        contract = build_contract(mode="full", user_prompt=PROMPT_3, topic="test")
        rendered = format_contract_for_user(contract)
        if contract.custom_content_map:
            assert "## User Format Mappings" in rendered
            assert "User Item" in rendered
            assert "Mapped To" in rendered

    def test_contract_to_json_roundtrip(self):
        """Serializes to dict with expected keys."""
        contract = build_contract(mode="full", user_prompt=PROMPT_2, topic="CDK4/6")
        json_dict = contract_to_json(contract)
        assert isinstance(json_dict, dict)
        expected_keys = {
            "mode", "topic", "sections", "total_word_range", "file_spec",
            "custom_content_map", "unmapped_items", "frozen_at", "warnings",
        }
        assert set(json_dict.keys()) == expected_keys
        # Verify it's JSON-serializable
        serialized = json.dumps(json_dict)
        deserialized = json.loads(serialized)
        assert deserialized["mode"] == "full"
        assert isinstance(deserialized["sections"], list)
        assert isinstance(deserialized["frozen_at"], str)

    def test_section_spec_serialization(self):
        """Each section in JSON has expected fields."""
        contract = build_contract(mode="full", user_prompt="test", topic="test")
        json_dict = contract_to_json(contract)
        for section in json_dict["sections"]:
            assert "canonical_name" in section
            assert "heading_level" in section
            assert "required" in section
            assert "order_index" in section
            assert "slot_type" in section
            assert "subsection_specs" in section


# =============================================================================
# Mode Selector Integration Tests
# =============================================================================


class TestModeSelector:
    def test_mode_selector_prompt1(self):
        """Prompt 1 text routes to 'full' mode (no keywords match)."""
        result = select_mode(PROMPT_1)
        assert result.selected_mode == "full"
        assert result.confidence == "low"

    def test_mode_selector_prompt2(self):
        """Prompt 2 text routes to 'lit-review' mode ('literature review' keyword)."""
        result = select_mode(PROMPT_2)
        assert result.selected_mode == "lit-review"


# =============================================================================
# Internal Helper Tests
# =============================================================================


class TestInternalHelpers:
    def test_extract_user_format_specs_xml(self):
        """Extracts items from XML output_format blocks."""
        prompt = (
            "<output_format>\n"
            "Gap analysis\n"
            "Risk matrix\n"
            "</output_format>"
        )
        items = _extract_user_format_specs(prompt)
        assert len(items) >= 2
        assert any("Gap analysis" in i for i in items)
        assert any("Risk matrix" in i for i in items)

    def test_extract_user_format_specs_natural(self):
        """Extracts items from natural-language lists."""
        prompt = "The report should include: comparison matrix, gap analysis, and limitations."
        items = _extract_user_format_specs(prompt)
        assert len(items) >= 3

    def test_extract_user_format_specs_empty(self):
        """Empty prompt returns empty list."""
        items = _extract_user_format_specs("")
        assert items == []

    def test_fuzzy_map_section_exact(self):
        """Exact match succeeds with fuzzy mapper."""
        specs = [
            SectionSpec(
                canonical_name="Gap Analysis",
                heading_level=2,
                required=True,
                order_index=0,
                slot_type="fixed",
            )
        ]
        result = _fuzzy_map_section("Gap Analysis", specs)
        assert result is not None
        assert result.canonical_name == "Gap Analysis"

    def test_fuzzy_map_section_no_match(self):
        """Unrelated term returns None."""
        specs = [
            SectionSpec(
                canonical_name="Executive Summary",
                heading_level=2,
                required=True,
                order_index=0,
                slot_type="fixed",
            )
        ]
        result = _fuzzy_map_section("Zebra Phenotyping Dashboard", specs)
        assert result is None

    def test_schema_dicts_to_specs(self):
        """Converts schema dicts to SectionSpec objects correctly."""
        raw = [
            {"name": "Methods", "level": 2, "required": True, "order": 1, "slot_type": "fixed"},
            {"name": "Results", "level": 2, "required": True, "order": 2, "slot_type": "fixed",
             "subsections": ["Overview"]},
        ]
        specs = _schema_dicts_to_specs(raw)
        assert len(specs) == 2
        assert specs[0].canonical_name == "Methods"
        assert specs[1].canonical_name == "Results"
        assert len(specs[1].subsection_specs) == 1

    def test_flatten_specs(self):
        """Flatten includes top-level and nested specs."""
        raw = SECTION_SCHEMAS.get("full", [])
        specs = _schema_dicts_to_specs(raw)
        flat = _flatten_specs(specs)
        assert len(flat) > len(specs)  # subsections add to the count


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
