"""Tests for complexity analyzer and tier selection logic.

Tests cover:
- Diagram type detection from prompts
- Complexity analysis (node/edge estimation)
- Tier recommendation (Mermaid vs AI)
- Mermaid compatibility checking
- Quality threshold handling
- Forced tier overrides
"""

from __future__ import annotations

from utils.complexity_analyzer import (
    MERMAID_MAX_EDGES,
    MERMAID_MAX_NODES,
    GenerationTier,
    analyze_complexity,
    detect_diagram_type,
    estimate_edges_from_prompt,
    get_quality_requirement,
    get_tier_summary,
    is_mermaid_compatible,
    should_use_mermaid,
)


# =====================================================================
# GenerationTier Enum Tests
# =====================================================================


class TestGenerationTier:
    """Tests for GenerationTier enum."""

    def test_tier_values(self) -> None:
        """Test tier enum values."""
        assert GenerationTier.MERMAID.value == "mermaid"
        assert GenerationTier.AI.value == "ai"
        assert GenerationTier.MERMAID_PLUS_POLISH.value == "mermaid+ai"

    def test_tier_from_string(self) -> None:
        """Test creating tier from string."""
        assert GenerationTier("mermaid") == GenerationTier.MERMAID
        assert GenerationTier("ai") == GenerationTier.AI
        assert GenerationTier("mermaid+ai") == GenerationTier.MERMAID_PLUS_POLISH


# =====================================================================
# Diagram Type Detection Tests
# =====================================================================


class TestDetectDiagramType:
    """Tests for diagram type detection from prompts."""

    def test_detect_consort(self) -> None:
        """Test CONSORT diagram detection."""
        assert detect_diagram_type("CONSORT participant flow diagram") == "consort"
        assert detect_diagram_type("RCT flow showing randomization") == "consort"

    def test_detect_prisma(self) -> None:
        """Test PRISMA diagram detection."""
        assert detect_diagram_type("PRISMA flow for systematic review") == "prisma"
        assert detect_diagram_type("Literature search flowchart") == "prisma"

    def test_detect_transformer(self) -> None:
        """Test transformer architecture detection."""
        assert detect_diagram_type("Transformer encoder-decoder") == "transformer"
        assert detect_diagram_type("Self-attention mechanism diagram") == "transformer"
        assert detect_diagram_type("BERT architecture") == "transformer"

    def test_detect_cnn(self) -> None:
        """Test CNN detection."""
        assert detect_diagram_type("CNN architecture for image classification") == "cnn"
        assert detect_diagram_type("Convolutional neural network") == "cnn"

    def test_detect_rnn_lstm(self) -> None:
        """Test RNN/LSTM detection."""
        assert detect_diagram_type("LSTM network for sequence") == "rnn_lstm"
        assert detect_diagram_type("Recurrent neural network") == "rnn_lstm"

    def test_detect_pathway(self) -> None:
        """Test biological pathway detection."""
        assert detect_diagram_type("MAPK signaling pathway") == "pathway"
        assert detect_diagram_type("Metabolic pathway diagram") == "pathway"

    def test_detect_sequence_diagram(self) -> None:
        """Test sequence diagram detection."""
        assert detect_diagram_type("Sequence diagram for API") == "sequence"
        assert detect_diagram_type("Message flow between services") == "sequence"

    def test_detect_state_diagram(self) -> None:
        """Test state diagram detection."""
        assert detect_diagram_type("State machine for order processing") == "state"
        assert detect_diagram_type("FSM diagram") == "state"

    def test_detect_class_diagram(self) -> None:
        """Test class diagram detection."""
        assert detect_diagram_type("UML class diagram") == "class"
        assert detect_diagram_type("Class diagram showing inheritance") == "class"

    def test_detect_er_diagram(self) -> None:
        """Test ER diagram detection."""
        assert detect_diagram_type("Entity relationship diagram") == "er"
        assert detect_diagram_type("ERD for database") == "er"

    def test_detect_gantt(self) -> None:
        """Test Gantt chart detection."""
        assert detect_diagram_type("Gantt chart for project") == "gantt"
        assert detect_diagram_type("Project schedule timeline") == "gantt"

    def test_detect_pie_chart(self) -> None:
        """Test pie chart detection."""
        assert detect_diagram_type("Pie chart showing distribution") == "pie"

    def test_detect_mindmap(self) -> None:
        """Test mindmap detection."""
        assert detect_diagram_type("Mind map of concepts") == "mindmap"
        assert detect_diagram_type("Concept map diagram") == "mindmap"

    def test_detect_flowchart_default(self) -> None:
        """Test flowchart as default for generic descriptions."""
        assert detect_diagram_type("A simple process diagram") == "flowchart"
        assert detect_diagram_type("Workflow showing steps") == "flowchart"

    def test_detect_generic_defaults_to_flowchart(self) -> None:
        """Test generic prompts default to flowchart."""
        assert detect_diagram_type("A picture of something") == "flowchart"
        assert detect_diagram_type("Some boxes connected") == "flowchart"


# =====================================================================
# Mermaid Compatibility Tests
# =====================================================================


class TestMermaidCompatibility:
    """Tests for Mermaid compatibility checking."""

    def test_flowchart_compatible(self) -> None:
        """Test flowchart is Mermaid compatible."""
        assert is_mermaid_compatible("flowchart")
        assert is_mermaid_compatible("FLOWCHART")

    def test_sequence_compatible(self) -> None:
        """Test sequence diagram is Mermaid compatible."""
        assert is_mermaid_compatible("sequence")

    def test_state_compatible(self) -> None:
        """Test state diagram is Mermaid compatible."""
        assert is_mermaid_compatible("state")

    def test_class_compatible(self) -> None:
        """Test class diagram is Mermaid compatible."""
        assert is_mermaid_compatible("class")

    def test_er_compatible(self) -> None:
        """Test ER diagram is Mermaid compatible."""
        assert is_mermaid_compatible("er")

    def test_consort_compatible(self) -> None:
        """Test CONSORT is Mermaid compatible."""
        assert is_mermaid_compatible("consort")

    def test_prisma_compatible(self) -> None:
        """Test PRISMA is Mermaid compatible."""
        assert is_mermaid_compatible("prisma")

    def test_transformer_not_compatible(self) -> None:
        """Test transformer is NOT Mermaid compatible."""
        assert not is_mermaid_compatible("transformer")

    def test_cnn_not_compatible(self) -> None:
        """Test CNN is NOT Mermaid compatible."""
        assert not is_mermaid_compatible("cnn")

    def test_pathway_not_compatible(self) -> None:
        """Test biological pathway is NOT Mermaid compatible."""
        assert not is_mermaid_compatible("pathway")

    def test_neural_network_not_compatible(self) -> None:
        """Test neural network types are NOT Mermaid compatible."""
        assert not is_mermaid_compatible("neural_network")
        assert not is_mermaid_compatible("lstm")
        assert not is_mermaid_compatible("rnn")

    def test_simple_flowchart_variant_compatible(self) -> None:
        """Test flowchart variants are Mermaid compatible."""
        assert is_mermaid_compatible("simple_flowchart")

    def test_unknown_type_not_compatible(self) -> None:
        """Test unknown types are NOT Mermaid compatible."""
        assert not is_mermaid_compatible("unknown_type_xyz")


# =====================================================================
# Quality Threshold Tests
# =====================================================================


class TestQualityThresholds:
    """Tests for quality threshold by document type."""

    def test_journal_high_quality(self) -> None:
        """Test journal requires high quality."""
        assert get_quality_requirement("journal") == 8.5
        assert get_quality_requirement("publication") == 8.5

    def test_conference_quality(self) -> None:
        """Test conference quality threshold."""
        assert get_quality_requirement("conference") == 8.0
        assert get_quality_requirement("thesis") == 8.0

    def test_preprint_quality(self) -> None:
        """Test preprint quality threshold."""
        assert get_quality_requirement("preprint") == 7.5
        assert get_quality_requirement("report") == 7.5

    def test_presentation_lower_quality(self) -> None:
        """Test presentation accepts lower quality."""
        assert get_quality_requirement("presentation") == 6.5
        assert get_quality_requirement("slides") == 6.5

    def test_draft_low_quality(self) -> None:
        """Test draft accepts low quality."""
        assert get_quality_requirement("draft") == 5.0

    def test_default_quality(self) -> None:
        """Test default quality threshold."""
        assert get_quality_requirement("default") == 7.5
        assert get_quality_requirement("unknown") == 7.5

    def test_case_insensitive(self) -> None:
        """Test quality requirement is case-insensitive."""
        assert get_quality_requirement("JOURNAL") == 8.5
        assert get_quality_requirement("Journal") == 8.5


# =====================================================================
# Edge Estimation Tests
# =====================================================================


class TestEdgeEstimation:
    """Tests for edge count estimation."""

    def test_arrow_count(self) -> None:
        """Test counting explicit arrows."""
        assert estimate_edges_from_prompt("A → B → C → D", 4) == 3
        assert estimate_edges_from_prompt("A -> B -> C", 3) == 2

    def test_connection_keywords(self) -> None:
        """Test counting connection keywords."""
        prompt = "Step 1 connects to Step 2, which leads to Step 3"
        # Should count "connects to" and "leads to"
        assert estimate_edges_from_prompt(prompt, 3) >= 2

    def test_branching_heuristic(self) -> None:
        """Test branching increases edge estimate."""
        prompt = "Decision tree with branching paths"
        edges = estimate_edges_from_prompt(prompt, 5)
        assert edges >= 5  # Should be nodes * 1.3

    def test_network_heuristic(self) -> None:
        """Test network increases edge estimate."""
        prompt = "Network mesh topology"
        edges = estimate_edges_from_prompt(prompt, 5)
        assert edges >= 6  # Should be nodes * 1.5

    def test_linear_default(self) -> None:
        """Test linear flow default."""
        # No special keywords - should be nodes - 1
        edges = estimate_edges_from_prompt("Simple process flow", 5)
        assert edges == 4  # nodes - 1


# =====================================================================
# Complexity Analysis Tests
# =====================================================================


class TestAnalyzeComplexity:
    """Tests for full complexity analysis."""

    def test_simple_flowchart_routes_to_mermaid(self) -> None:
        """Test simple flowchart routes to Mermaid tier."""
        analysis = analyze_complexity("Simple 5-step process flow")
        assert analysis.recommended_tier == GenerationTier.MERMAID
        assert analysis.mermaid_compatible
        assert analysis.estimated_nodes <= MERMAID_MAX_NODES

    def test_complex_pathway_routes_to_ai(self) -> None:
        """Test complex pathway routes to AI tier."""
        analysis = analyze_complexity("MAPK signaling pathway with 15 proteins")
        assert analysis.recommended_tier == GenerationTier.AI
        assert not analysis.mermaid_compatible

    def test_neural_network_always_ai(self) -> None:
        """Test neural network always routes to AI."""
        analysis = analyze_complexity("Transformer architecture diagram")
        assert analysis.recommended_tier == GenerationTier.AI
        assert analysis.diagram_type == "transformer"

    def test_publication_quality_forces_ai(self) -> None:
        """Test publication quality requirement forces AI."""
        analysis = analyze_complexity("Simple flowchart", doc_type="journal")
        assert analysis.recommended_tier == GenerationTier.AI
        assert "journal" in analysis.reasoning.lower() or "quality" in analysis.reasoning.lower()

    def test_draft_allows_mermaid(self) -> None:
        """Test draft quality allows Mermaid."""
        analysis = analyze_complexity("Simple flowchart", doc_type="draft")
        assert analysis.recommended_tier == GenerationTier.MERMAID

    def test_force_mermaid_override(self) -> None:
        """Test force_tier overrides recommendation."""
        # This would normally route to AI
        analysis = analyze_complexity(
            "Complex transformer architecture",
            force_tier=GenerationTier.MERMAID,
        )
        assert analysis.recommended_tier == GenerationTier.MERMAID
        assert "forced" in analysis.reasoning.lower()
        assert analysis.confidence == 1.0

    def test_force_ai_override(self) -> None:
        """Test force AI tier override."""
        # This would normally route to Mermaid
        analysis = analyze_complexity(
            "Simple flowchart",
            force_tier=GenerationTier.AI,
        )
        assert analysis.recommended_tier == GenerationTier.AI

    def test_high_node_count_routes_to_ai(self) -> None:
        """Test high node count routes to AI."""
        prompt = "Flowchart with 15 different steps and processes"
        analysis = analyze_complexity(prompt)
        # If estimated nodes > MERMAID_MAX_NODES, should route to AI
        if analysis.estimated_nodes > MERMAID_MAX_NODES:
            assert analysis.recommended_tier == GenerationTier.AI

    def test_explicit_diagram_type(self) -> None:
        """Test explicit diagram type is used."""
        analysis = analyze_complexity(
            "Some generic text",
            diagram_type="sequence",
        )
        assert analysis.diagram_type == "sequence"

    def test_confidence_for_incompatible_type(self) -> None:
        """Test high confidence when type is incompatible with Mermaid."""
        analysis = analyze_complexity("CNN architecture diagram")
        assert analysis.recommended_tier == GenerationTier.AI
        assert analysis.confidence >= 0.9

    def test_reasoning_contains_explanation(self) -> None:
        """Test reasoning contains explanation."""
        analysis = analyze_complexity("Transformer encoder-decoder")
        assert len(analysis.reasoning) > 0
        assert "not supported" in analysis.reasoning.lower() or "transformer" in analysis.reasoning.lower()

    def test_analysis_dataclass_fields(self) -> None:
        """Test ComplexityAnalysis has all required fields."""
        analysis = analyze_complexity("Simple flowchart")
        assert isinstance(analysis.estimated_nodes, int)
        assert isinstance(analysis.estimated_edges, int)
        assert isinstance(analysis.diagram_type, str)
        assert isinstance(analysis.mermaid_compatible, bool)
        assert isinstance(analysis.recommended_tier, GenerationTier)
        assert isinstance(analysis.confidence, float)
        assert isinstance(analysis.reasoning, str)


# =====================================================================
# Convenience Function Tests
# =====================================================================


class TestShouldUseMermaid:
    """Tests for should_use_mermaid convenience function."""

    def test_simple_flowchart_true(self) -> None:
        """Test simple flowchart returns True."""
        assert should_use_mermaid("Simple flowchart: A → B → C")

    def test_transformer_false(self) -> None:
        """Test transformer returns False."""
        assert not should_use_mermaid("Transformer architecture")

    def test_journal_quality_false(self) -> None:
        """Test journal quality returns False even for simple diagram."""
        assert not should_use_mermaid("Simple flowchart", doc_type="journal")


# =====================================================================
# Tier Summary Tests
# =====================================================================


class TestTierSummary:
    """Tests for tier summary information."""

    def test_mermaid_tier_summary(self) -> None:
        """Test Mermaid tier summary."""
        info = get_tier_summary(GenerationTier.MERMAID)
        assert info["cost"] == "$0.00"
        assert "instant" in info["speed"].lower() or "100ms" in info["speed"]
        assert info["deterministic"] is True

    def test_ai_tier_summary(self) -> None:
        """Test AI tier summary."""
        info = get_tier_summary(GenerationTier.AI)
        assert "$0.0" in info["cost"]  # Contains cost info
        assert info["deterministic"] is False
        assert "publication" in info["quality"].lower()

    def test_mermaid_plus_polish_summary(self) -> None:
        """Test Mermaid+AI polish tier summary."""
        info = get_tier_summary(GenerationTier.MERMAID_PLUS_POLISH)
        assert "polish" in info["description"].lower() or "enhance" in info["description"].lower()


# =====================================================================
# AI-Suggesting Keywords Tests
# =====================================================================


class TestKeywordAnalysis:
    """Tests for keyword-based tier suggestion."""

    def test_ai_keywords_detected(self) -> None:
        """Test AI-suggesting keywords push toward AI tier."""
        analysis = analyze_complexity(
            "Deep learning neural network with attention layers"
        )
        # Multiple AI keywords should increase AI confidence
        assert analysis.recommended_tier == GenerationTier.AI

    def test_mermaid_keywords_detected(self) -> None:
        """Test Mermaid-suggesting keywords push toward Mermaid tier."""
        analysis = analyze_complexity(
            "Simple basic flowchart with quick draft"
        )
        assert analysis.recommended_tier == GenerationTier.MERMAID
        assert "mermaid" in analysis.reasoning.lower() or "simple" in analysis.reasoning.lower()

    def test_mixed_keywords(self) -> None:
        """Test mixed keywords result in balanced analysis."""
        analysis = analyze_complexity(
            "Simple flowchart showing neural network training process"
        )
        # Has both Mermaid ("simple", "flowchart") and AI ("neural network") keywords
        # Result depends on the balance
        assert analysis.diagram_type in ("flowchart", "neural_network")


# =====================================================================
# Edge Cases Tests
# =====================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_prompt(self) -> None:
        """Test handling of empty prompt."""
        analysis = analyze_complexity("")
        # Should not crash, should have some default
        assert analysis.diagram_type == "flowchart"

    def test_very_long_prompt(self) -> None:
        """Test handling of very long prompt."""
        long_prompt = "process step " * 100
        analysis = analyze_complexity(long_prompt)
        # Should handle without crashing
        assert analysis is not None

    def test_special_characters_in_prompt(self) -> None:
        """Test handling of special characters."""
        analysis = analyze_complexity("Flow: A → B → C → D → E")
        assert analysis.diagram_type == "flowchart"

    def test_node_threshold_boundary(self) -> None:
        """Test behavior at node count boundary."""
        # Exactly at threshold
        analysis = analyze_complexity("10-node flowchart")
        # Should still allow Mermaid at boundary if type is compatible
        if analysis.estimated_nodes <= MERMAID_MAX_NODES:
            assert analysis.mermaid_compatible

    def test_edge_threshold_boundary(self) -> None:
        """Test behavior at edge count boundary."""
        # Many edges should trigger AI
        prompt = "Fully connected network with 20 edges"
        analysis = analyze_complexity(prompt)
        if analysis.estimated_edges > MERMAID_MAX_EDGES:
            assert analysis.recommended_tier == GenerationTier.AI
