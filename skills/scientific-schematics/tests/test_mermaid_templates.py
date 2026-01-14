"""Tests for Mermaid diagram templates.

Tests cover:
- Template filling with placeholders
- Template retrieval by diagram type
- Template metadata and required fields
- Node and connection string building
- Flowchart construction helpers
- Template validation
"""

from __future__ import annotations

import pytest

from utils.mermaid_templates import (
    DIAGRAM_TYPE_TO_TEMPLATES,
    TEMPLATES,
    build_connections_string,
    build_flowchart,
    build_nodes_string,
    fill_template,
    get_required_fields,
    get_template,
    get_template_for_type,
    get_template_metadata,
    list_diagram_types,
    list_templates,
    validate_template_data,
)


# =====================================================================
# Template Listing Tests
# =====================================================================


class TestTemplateListing:
    """Tests for template listing functions."""

    def test_list_templates_returns_sorted(self) -> None:
        """Test list_templates returns sorted list."""
        templates = list_templates()
        assert templates == sorted(templates)
        assert len(templates) > 0

    def test_list_diagram_types_returns_sorted(self) -> None:
        """Test list_diagram_types returns sorted list."""
        types = list_diagram_types()
        assert types == sorted(types)
        assert len(types) > 0

    def test_expected_diagram_types_present(self) -> None:
        """Test expected diagram types are present."""
        types = list_diagram_types()
        expected = ["flowchart", "sequence", "state", "consort", "prisma"]
        for dtype in expected:
            assert dtype in types, f"Expected diagram type '{dtype}' not found"

    def test_expected_templates_present(self) -> None:
        """Test expected templates are present."""
        templates = list_templates()
        expected = ["consort_basic", "prisma_basic", "simple_flowchart_td"]
        for template in expected:
            assert template in templates, f"Expected template '{template}' not found"


# =====================================================================
# Template Retrieval Tests
# =====================================================================


class TestTemplateRetrieval:
    """Tests for template retrieval functions."""

    def test_get_template_existing(self) -> None:
        """Test getting existing template."""
        template = get_template("consort_basic")
        assert template is not None
        assert "flowchart TD" in template

    def test_get_template_nonexistent(self) -> None:
        """Test getting nonexistent template returns None."""
        template = get_template("nonexistent_template")
        assert template is None

    def test_get_template_for_type_basic(self) -> None:
        """Test getting basic template for diagram type."""
        template_name = get_template_for_type("consort", "basic")
        assert template_name == "consort_basic"

    def test_get_template_for_type_detailed(self) -> None:
        """Test getting detailed template for diagram type."""
        template_name = get_template_for_type("consort", "detailed")
        # Should return second template if available
        assert template_name in ["consort_basic", "consort_with_followup"]

    def test_get_template_for_type_exact_name(self) -> None:
        """Test getting template by exact name."""
        template_name = get_template_for_type("simple_flowchart_td")
        assert template_name == "simple_flowchart_td"

    def test_get_template_for_type_unknown(self) -> None:
        """Test getting template for unknown type returns None."""
        template_name = get_template_for_type("unknown_type")
        assert template_name is None


# =====================================================================
# Template Filling Tests
# =====================================================================


class TestFillTemplate:
    """Tests for template filling."""

    def test_fill_consort_basic(self) -> None:
        """Test filling CONSORT basic template."""
        result = fill_template(
            "consort_basic",
            screened=100,
            excluded=30,
            randomized=70,
            intervention=35,
            control=35,
            analyzed_intervention=32,
            analyzed_control=33,
        )
        assert "n=100" in result
        assert "n=30" in result
        assert "n=70" in result
        assert "flowchart TD" in result

    def test_fill_prisma_basic(self) -> None:
        """Test filling PRISMA basic template."""
        result = fill_template(
            "prisma_basic",
            identified=500,
            screened=400,
            excluded_screening=200,
            full_text=200,
            excluded_full_text=150,
            included=50,
        )
        assert "n=500" in result
        assert "n=50" in result

    def test_fill_simple_flowchart(self) -> None:
        """Test filling simple flowchart template."""
        nodes = "    A[Start]\n    B[Process]"
        connections = "    A --> B"
        result = fill_template(
            "simple_flowchart_td",
            nodes=nodes,
            connections=connections,
        )
        assert "flowchart TD" in result
        assert "A[Start]" in result
        assert "A --> B" in result

    def test_fill_template_missing_placeholder(self) -> None:
        """Test filling template with missing placeholder raises error."""
        with pytest.raises(ValueError, match="Missing"):
            fill_template(
                "consort_basic",
                screened=100,
                # Missing other required fields
            )

    def test_fill_template_nonexistent(self) -> None:
        """Test filling nonexistent template raises error."""
        with pytest.raises(KeyError, match="not found"):
            fill_template("nonexistent_template", foo="bar")

    def test_fill_pie_chart(self) -> None:
        """Test filling pie chart template."""
        result = fill_template(
            "pie_chart",
            title="Distribution",
            segments='    "A" : 50\n    "B" : 30\n    "C" : 20',
        )
        assert "pie showData" in result
        assert "Distribution" in result

    def test_fill_decision_tree(self) -> None:
        """Test filling decision tree template."""
        result = fill_template(
            "decision_tree",
            start_label="Question",
            decision1="Is it valid?",
            yes_label="Yes",
            no_label="No",
            outcome1="Accept",
            decision2="Can fix?",
            outcome2="Fix it",
            outcome3="Reject",
        )
        assert "flowchart TD" in result
        assert "Question" in result
        assert "Is it valid?" in result


# =====================================================================
# Required Fields Tests
# =====================================================================


class TestRequiredFields:
    """Tests for required fields extraction."""

    def test_get_required_fields_consort(self) -> None:
        """Test getting required fields for CONSORT."""
        fields = get_required_fields("consort_basic")
        assert "screened" in fields
        assert "excluded" in fields
        assert "randomized" in fields
        assert "intervention" in fields
        assert "control" in fields

    def test_get_required_fields_prisma(self) -> None:
        """Test getting required fields for PRISMA."""
        fields = get_required_fields("prisma_basic")
        assert "identified" in fields
        assert "screened" in fields
        assert "included" in fields

    def test_get_required_fields_flowchart(self) -> None:
        """Test getting required fields for flowchart."""
        fields = get_required_fields("simple_flowchart_td")
        assert "nodes" in fields
        assert "connections" in fields

    def test_get_required_fields_nonexistent(self) -> None:
        """Test getting fields for nonexistent template returns empty."""
        fields = get_required_fields("nonexistent")
        assert fields == []


# =====================================================================
# Template Validation Tests
# =====================================================================


class TestValidateTemplateData:
    """Tests for template data validation."""

    def test_validate_complete_data(self) -> None:
        """Test validating complete data."""
        data = {
            "screened": 100,
            "excluded": 30,
            "randomized": 70,
            "intervention": 35,
            "control": 35,
            "analyzed_intervention": 32,
            "analyzed_control": 33,
        }
        valid, missing = validate_template_data("consort_basic", data)
        assert valid
        assert len(missing) == 0

    def test_validate_incomplete_data(self) -> None:
        """Test validating incomplete data."""
        data = {"screened": 100}
        valid, missing = validate_template_data("consort_basic", data)
        assert not valid
        assert "excluded" in missing
        assert "randomized" in missing

    def test_validate_extra_data_ok(self) -> None:
        """Test validation allows extra data."""
        data = {
            "screened": 100,
            "excluded": 30,
            "randomized": 70,
            "intervention": 35,
            "control": 35,
            "analyzed_intervention": 32,
            "analyzed_control": 33,
            "extra_field": "ignored",
        }
        valid, missing = validate_template_data("consort_basic", data)
        assert valid


# =====================================================================
# Template Metadata Tests
# =====================================================================


class TestTemplateMetadata:
    """Tests for template metadata."""

    def test_get_metadata_existing(self) -> None:
        """Test getting metadata for existing template."""
        metadata = get_template_metadata("consort_basic")
        assert metadata is not None
        assert metadata.name == "CONSORT Basic"
        assert metadata.diagram_type == "consort"
        assert "screened" in metadata.required_fields

    def test_get_metadata_nonexistent(self) -> None:
        """Test getting metadata for nonexistent template."""
        metadata = get_template_metadata("nonexistent")
        assert metadata is None

    def test_metadata_has_required_fields(self) -> None:
        """Test metadata includes required fields list."""
        for template_name in list_templates():
            metadata = get_template_metadata(template_name)
            if metadata:
                assert isinstance(metadata.required_fields, list)
                assert isinstance(metadata.optional_fields, list)

    def test_metadata_matches_template(self) -> None:
        """Test metadata required fields match actual template placeholders."""
        for template_name in list_templates():
            metadata = get_template_metadata(template_name)
            if metadata:
                actual_fields = get_required_fields(template_name)
                # All metadata required fields should be in actual fields
                for field in metadata.required_fields:
                    assert field in actual_fields, (
                        f"Metadata field '{field}' not found in template '{template_name}'"
                    )


# =====================================================================
# Node String Building Tests
# =====================================================================


class TestBuildNodesString:
    """Tests for node string building."""

    def test_build_rect_nodes(self) -> None:
        """Test building rectangular nodes."""
        nodes = [
            {"id": "A", "label": "Start"},
            {"id": "B", "label": "Process"},
        ]
        result = build_nodes_string(nodes)
        assert "A[Start]" in result
        assert "B[Process]" in result

    def test_build_rounded_nodes(self) -> None:
        """Test building rounded nodes."""
        nodes = [{"id": "A", "label": "Start", "shape": "rounded"}]
        result = build_nodes_string(nodes)
        assert "A(Start)" in result

    def test_build_diamond_nodes(self) -> None:
        """Test building diamond nodes."""
        nodes = [{"id": "A", "label": "Decision", "shape": "diamond"}]
        result = build_nodes_string(nodes)
        # Mermaid uses double braces {{}} for diamond shape
        assert "A{{Decision}}" in result

    def test_build_circle_nodes(self) -> None:
        """Test building circle nodes."""
        nodes = [{"id": "A", "label": "State", "shape": "circle"}]
        result = build_nodes_string(nodes)
        assert "A((State))" in result

    def test_build_stadium_nodes(self) -> None:
        """Test building stadium nodes."""
        nodes = [{"id": "A", "label": "Start", "shape": "stadium"}]
        result = build_nodes_string(nodes)
        assert "A([Start])" in result

    def test_custom_indent(self) -> None:
        """Test custom indentation."""
        nodes = [{"id": "A", "label": "Node"}]
        result = build_nodes_string(nodes, indent="  ")
        assert result.startswith("  A[Node]")


# =====================================================================
# Connection String Building Tests
# =====================================================================


class TestBuildConnectionsString:
    """Tests for connection string building."""

    def test_build_simple_connections(self) -> None:
        """Test building simple connections."""
        connections = [
            {"from": "A", "to": "B"},
            {"from": "B", "to": "C"},
        ]
        result = build_connections_string(connections)
        assert "A --> B" in result
        assert "B --> C" in result

    def test_build_labeled_connections(self) -> None:
        """Test building labeled connections."""
        connections = [
            {"from": "A", "to": "B", "label": "yes"},
            {"from": "A", "to": "C", "label": "no"},
        ]
        result = build_connections_string(connections)
        assert "A -->|yes| B" in result
        assert "A -->|no| C" in result

    def test_custom_indent(self) -> None:
        """Test custom indentation."""
        connections = [{"from": "A", "to": "B"}]
        result = build_connections_string(connections, indent="  ")
        assert result.startswith("  A --> B")


# =====================================================================
# Flowchart Building Tests
# =====================================================================


class TestBuildFlowchart:
    """Tests for complete flowchart building."""

    def test_build_simple_flowchart(self) -> None:
        """Test building simple flowchart."""
        nodes = [
            {"id": "A", "label": "Start"},
            {"id": "B", "label": "Process"},
            {"id": "C", "label": "End"},
        ]
        connections = [
            {"from": "A", "to": "B"},
            {"from": "B", "to": "C"},
        ]
        result = build_flowchart(nodes, connections)
        assert "flowchart TD" in result
        assert "A[Start]" in result
        assert "A --> B" in result

    def test_build_left_right_flowchart(self) -> None:
        """Test building left-to-right flowchart."""
        nodes = [{"id": "A", "label": "Start"}, {"id": "B", "label": "End"}]
        connections = [{"from": "A", "to": "B"}]
        result = build_flowchart(nodes, connections, direction="LR")
        assert "flowchart LR" in result

    def test_build_bottom_top_flowchart(self) -> None:
        """Test building bottom-to-top flowchart."""
        nodes = [{"id": "A", "label": "Start"}, {"id": "B", "label": "End"}]
        connections = [{"from": "A", "to": "B"}]
        result = build_flowchart(nodes, connections, direction="BT")
        assert "flowchart BT" in result

    def test_build_right_left_flowchart(self) -> None:
        """Test building right-to-left flowchart."""
        nodes = [{"id": "A", "label": "Start"}, {"id": "B", "label": "End"}]
        connections = [{"from": "A", "to": "B"}]
        result = build_flowchart(nodes, connections, direction="RL")
        assert "flowchart RL" in result


# =====================================================================
# Template Content Tests
# =====================================================================


class TestTemplateContent:
    """Tests for specific template content."""

    def test_consort_has_standard_sections(self) -> None:
        """Test CONSORT template has standard sections."""
        template = TEMPLATES["consort_basic"]
        assert "Assessed for eligibility" in template
        assert "Excluded" in template
        assert "Randomized" in template
        assert "Allocated to intervention" in template
        assert "Allocated to control" in template
        assert "Analyzed" in template

    def test_prisma_has_standard_sections(self) -> None:
        """Test PRISMA template has standard sections."""
        template = TEMPLATES["prisma_basic"]
        assert "Records identified" in template
        assert "Records screened" in template
        assert "Full-text assessed" in template
        assert "Studies included" in template

    def test_sequence_template_format(self) -> None:
        """Test sequence diagram template format."""
        template = TEMPLATES["sequence_basic"]
        assert "sequenceDiagram" in template
        assert "participant" in template

    def test_state_template_format(self) -> None:
        """Test state diagram template format."""
        template = TEMPLATES["state_machine_basic"]
        assert "stateDiagram-v2" in template
        assert "[*]" in template  # Initial/final state markers


# =====================================================================
# Diagram Type Mapping Tests
# =====================================================================


class TestDiagramTypeMapping:
    """Tests for diagram type to template mapping."""

    def test_consort_mapping(self) -> None:
        """Test CONSORT type has templates."""
        templates = DIAGRAM_TYPE_TO_TEMPLATES.get("consort", [])
        assert len(templates) >= 1
        assert "consort_basic" in templates

    def test_prisma_mapping(self) -> None:
        """Test PRISMA type has templates."""
        templates = DIAGRAM_TYPE_TO_TEMPLATES.get("prisma", [])
        assert len(templates) >= 1
        assert "prisma_basic" in templates

    def test_flowchart_mapping(self) -> None:
        """Test flowchart type has templates."""
        templates = DIAGRAM_TYPE_TO_TEMPLATES.get("flowchart", [])
        assert len(templates) >= 1
        assert any("flowchart" in t for t in templates)

    def test_all_mapped_templates_exist(self) -> None:
        """Test all mapped templates actually exist."""
        for dtype, template_list in DIAGRAM_TYPE_TO_TEMPLATES.items():
            for template_name in template_list:
                assert template_name in TEMPLATES, (
                    f"Template '{template_name}' for type '{dtype}' not found"
                )
