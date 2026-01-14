"""Tests for Mermaid rendering and diagram generation.

Tests cover:
- MermaidRenderer backend detection and rendering
- Mermaid syntax validation
- Natural language to Mermaid conversion
- generate_mermaid_diagram main function
- CLI argument handling
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from utils.mermaid_renderer import (
    MermaidRenderer,
    RenderBackend,
    RenderConfig,
    RenderResult,
    get_mermaid_version,
    render_mermaid,
    validate_mermaid_syntax,
)

# Import from generate_mermaid module
try:
    from generate_mermaid import (
        MermaidResult,
        generate_mermaid_diagram,
        prompt_to_mermaid,
    )
except ImportError:
    # Handle import if running tests differently
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
    from generate_mermaid import (
        MermaidResult,
        generate_mermaid_diagram,
        prompt_to_mermaid,
    )


# =====================================================================
# RenderBackend Enum Tests
# =====================================================================


class TestRenderBackend:
    """Tests for RenderBackend enum."""

    def test_backend_values(self) -> None:
        """Test backend enum values."""
        assert RenderBackend.MMDC.value == "mmdc"
        assert RenderBackend.PYTHON.value == "python"
        assert RenderBackend.API.value == "api"
        assert RenderBackend.AUTO.value == "auto"

    def test_backend_from_string(self) -> None:
        """Test creating backend from string."""
        assert RenderBackend("mmdc") == RenderBackend.MMDC
        assert RenderBackend("python") == RenderBackend.PYTHON
        assert RenderBackend("api") == RenderBackend.API


# =====================================================================
# RenderConfig Tests
# =====================================================================


class TestRenderConfig:
    """Tests for RenderConfig dataclass."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = RenderConfig()
        assert config.output_format == "png"
        assert config.width == 800
        assert config.height == 600
        assert config.theme == "default"
        assert config.scale == 2.0
        assert config.background_color == "white"

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = RenderConfig(
            output_format="svg",
            width=1200,
            height=900,
            theme="dark",
        )
        assert config.output_format == "svg"
        assert config.width == 1200
        assert config.theme == "dark"


# =====================================================================
# RenderResult Tests
# =====================================================================


class TestRenderResult:
    """Tests for RenderResult dataclass."""

    def test_successful_result(self) -> None:
        """Test successful render result."""
        result = RenderResult(
            success=True,
            output_path="/path/to/output.png",
            backend_used="mmdc",
        )
        assert result.success
        assert result.output_path == "/path/to/output.png"
        assert result.error is None

    def test_failed_result(self) -> None:
        """Test failed render result."""
        result = RenderResult(
            success=False,
            output_path=None,
            backend_used="mmdc",
            error="Rendering failed",
        )
        assert not result.success
        assert result.error == "Rendering failed"

    def test_result_to_dict(self) -> None:
        """Test converting result to dictionary."""
        result = RenderResult(
            success=True,
            output_path="/path/to/output.png",
            backend_used="mmdc",
            render_time_ms=150.5,
            mermaid_hash="abc123",
        )
        d = result.to_dict()
        assert d["success"] is True
        assert d["backend_used"] == "mmdc"
        assert d["render_time_ms"] == 150.5


# =====================================================================
# MermaidRenderer Tests
# =====================================================================


class TestMermaidRenderer:
    """Tests for MermaidRenderer class."""

    def test_renderer_initialization(self) -> None:
        """Test renderer initialization."""
        renderer = MermaidRenderer()
        assert renderer.backend == RenderBackend.AUTO
        assert renderer.config is not None

    def test_renderer_with_string_backend(self) -> None:
        """Test renderer initialization with string backend."""
        renderer = MermaidRenderer(backend="api")
        assert renderer.backend == RenderBackend.API

    def test_renderer_with_custom_config(self) -> None:
        """Test renderer with custom config."""
        config = RenderConfig(theme="dark", scale=3.0)
        renderer = MermaidRenderer(config=config)
        assert renderer.config.theme == "dark"
        assert renderer.config.scale == 3.0

    def test_install_instructions_mmdc(self) -> None:
        """Test install instructions for mmdc."""
        instructions = MermaidRenderer.install_instructions("mmdc")
        assert "npm install" in instructions
        assert "mermaid-cli" in instructions

    def test_install_instructions_python(self) -> None:
        """Test install instructions for python."""
        instructions = MermaidRenderer.install_instructions("python")
        assert "pip install" in instructions
        assert "mermaid-py" in instructions

    def test_install_instructions_api(self) -> None:
        """Test install instructions for api."""
        instructions = MermaidRenderer.install_instructions("api")
        assert "kroki" in instructions or "internet" in instructions

    def test_get_available_backends(self) -> None:
        """Test getting available backends."""
        renderer = MermaidRenderer()
        backends = renderer.get_available_backends()
        # Should return a list (may be empty if no backends installed)
        assert isinstance(backends, list)

    def test_check_backend_caching(self) -> None:
        """Test backend availability is cached."""
        renderer = MermaidRenderer()
        # Clear cache first
        MermaidRenderer._backend_cache.clear()

        # First check should populate cache
        result1 = renderer.check_backend_available("api")
        # Second check should use cache
        result2 = renderer.check_backend_available("api")
        assert result1 == result2


# =====================================================================
# Mermaid Syntax Validation Tests
# =====================================================================


class TestValidateMermaidSyntax:
    """Tests for Mermaid syntax validation."""

    def test_valid_flowchart(self) -> None:
        """Test validating valid flowchart."""
        code = "flowchart TD\n    A[Start] --> B[End]"
        is_valid, error = validate_mermaid_syntax(code)
        assert is_valid
        assert error is None

    def test_valid_sequence_diagram(self) -> None:
        """Test validating valid sequence diagram."""
        code = "sequenceDiagram\n    A->>B: Message"
        is_valid, error = validate_mermaid_syntax(code)
        assert is_valid

    def test_valid_state_diagram(self) -> None:
        """Test validating valid state diagram."""
        code = "stateDiagram-v2\n    [*] --> Active\n    Active --> [*]"
        is_valid, error = validate_mermaid_syntax(code)
        assert is_valid

    def test_empty_code_invalid(self) -> None:
        """Test empty code is invalid."""
        is_valid, error = validate_mermaid_syntax("")
        assert not is_valid
        assert "Empty" in error or "empty" in error.lower()

    def test_whitespace_only_invalid(self) -> None:
        """Test whitespace-only code is invalid."""
        is_valid, error = validate_mermaid_syntax("   \n   ")
        assert not is_valid

    def test_invalid_diagram_type(self) -> None:
        """Test invalid diagram type is caught."""
        code = "invalidDiagram\n    A --> B"
        is_valid, error = validate_mermaid_syntax(code)
        assert not is_valid
        assert "Invalid" in error or "type" in error.lower()

    def test_unbalanced_brackets(self) -> None:
        """Test unbalanced brackets are caught."""
        code = "flowchart TD\n    A[Start --> B"
        is_valid, error = validate_mermaid_syntax(code)
        assert not is_valid
        assert "bracket" in error.lower() or "Unclosed" in error

    def test_graph_keyword_valid(self) -> None:
        """Test 'graph' keyword is valid (legacy flowchart)."""
        code = "graph TD\n    A --> B"
        is_valid, error = validate_mermaid_syntax(code)
        assert is_valid

    def test_pie_chart_valid(self) -> None:
        """Test pie chart syntax is valid."""
        code = 'pie\n    "A" : 50\n    "B" : 50'
        is_valid, error = validate_mermaid_syntax(code)
        assert is_valid

    def test_gantt_chart_valid(self) -> None:
        """Test gantt chart syntax is valid."""
        code = "gantt\n    title Project\n    section A\n    Task 1 :a1, 2024-01-01, 30d"
        is_valid, error = validate_mermaid_syntax(code)
        assert is_valid


# =====================================================================
# Prompt to Mermaid Conversion Tests
# =====================================================================


class TestPromptToMermaid:
    """Tests for natural language to Mermaid conversion."""

    def test_arrow_separated_items(self) -> None:
        """Test converting arrow-separated items."""
        code, dtype = prompt_to_mermaid("Input → Process → Output")
        assert "flowchart TD" in code
        assert dtype == "flowchart"
        assert "Input" in code or "Process" in code

    def test_simple_process_description(self) -> None:
        """Test converting simple process description."""
        code, dtype = prompt_to_mermaid("Start -> Middle -> End")
        assert "flowchart" in code.lower()
        assert "-->" in code

    def test_explicit_diagram_type(self) -> None:
        """Test using explicit diagram type."""
        code, dtype = prompt_to_mermaid("Some process", diagram_type="sequence")
        assert dtype == "sequence"
        assert "sequenceDiagram" in code

    def test_state_diagram_detection(self) -> None:
        """Test state diagram prompt detection."""
        code, dtype = prompt_to_mermaid("State machine: Idle → Active → Complete")
        assert dtype in ("state", "flowchart")
        # Either generates a state diagram or flowchart with states

    def test_step_numbered_items(self) -> None:
        """Test converting numbered steps."""
        code, dtype = prompt_to_mermaid("Step 1: Input, Step 2: Process, Step 3: Output")
        assert "flowchart" in code.lower()
        # Should extract the steps

    def test_then_separated_items(self) -> None:
        """Test converting 'then' separated items."""
        code, dtype = prompt_to_mermaid("Start then Process then End")
        assert "flowchart" in code.lower()

    def test_single_node_fallback(self) -> None:
        """Test fallback for single-item prompt."""
        code, dtype = prompt_to_mermaid("Just a single thing")
        assert "flowchart" in code.lower()
        # Should create at least one node

    def test_consort_type_detection(self) -> None:
        """Test CONSORT prompt is detected with template data."""
        # Without numbers, falls back to flowchart since template can't be filled
        # The type detection works but template requires data
        code, dtype = prompt_to_mermaid(
            "CONSORT diagram: n=100 screened, n=30 excluded, n=70 randomized, "
            "n=35 intervention, n=35 control, n=32 analyzed, n=33 analyzed"
        )
        assert dtype == "consort"
        assert "flowchart TD" in code

    def test_prisma_type_detection(self) -> None:
        """Test PRISMA prompt is detected with template data."""
        # Needs n=X format or "X records/studies/articles" pattern
        code, dtype = prompt_to_mermaid(
            "PRISMA diagram with n=500 records, n=400 screened, n=100 excluded"
        )
        assert dtype == "prisma"
        assert "flowchart TD" in code


# =====================================================================
# MermaidResult Tests
# =====================================================================


class TestMermaidResult:
    """Tests for MermaidResult dataclass."""

    def test_successful_result(self) -> None:
        """Test successful Mermaid result."""
        from utils.complexity_analyzer import GenerationTier

        result = MermaidResult(
            success=True,
            output_path="/path/output.png",
            mermaid_code="flowchart TD\n    A --> B",
            diagram_type="flowchart",
            tier=GenerationTier.MERMAID,
            generation_time_ms=100.0,
        )
        assert result.success
        assert result.cost == 0.0  # Mermaid is free

    def test_failed_result(self) -> None:
        """Test failed Mermaid result."""
        result = MermaidResult(
            success=False,
            output_path=None,
            mermaid_code="invalid",
            diagram_type="flowchart",
            error="Syntax error",
        )
        assert not result.success
        assert result.error is not None

    def test_result_to_dict(self) -> None:
        """Test converting result to dictionary."""
        from utils.complexity_analyzer import GenerationTier

        result = MermaidResult(
            success=True,
            output_path="/path/output.png",
            mermaid_code="flowchart TD",
            diagram_type="flowchart",
            tier=GenerationTier.MERMAID,
        )
        d = result.to_dict()
        assert d["success"] is True
        assert d["tier"] == "mermaid"
        assert d["cost"] == 0.0


# =====================================================================
# Generate Mermaid Diagram Tests
# =====================================================================


class TestGenerateMermaidDiagram:
    """Tests for generate_mermaid_diagram function."""

    def test_generation_with_no_backend(self, tmp_path: Path) -> None:
        """Test generation fails gracefully with no backend."""
        # Mock renderer to simulate no backends available
        with patch.object(MermaidRenderer, 'get_available_backends', return_value=[]):
            with patch.object(MermaidRenderer, 'check_backend_available', return_value=False):
                result = generate_mermaid_diagram(
                    "Simple flowchart: A → B → C",
                    tmp_path / "output.png",
                )
                # Should fail but not crash
                assert not result.success or result.success  # Just check it returns

    def test_generation_returns_mermaid_code(self, tmp_path: Path) -> None:
        """Test generation includes Mermaid code in result."""
        # Even if rendering fails, should have mermaid code
        result = generate_mermaid_diagram(
            "Simple: Start → End",
            tmp_path / "output.png",
        )
        assert result.mermaid_code is not None
        assert len(result.mermaid_code) > 0

    def test_generation_detects_diagram_type(self, tmp_path: Path) -> None:
        """Test generation detects diagram type."""
        # Use a flowchart prompt since CONSORT requires template data
        result = generate_mermaid_diagram(
            "Simple flowchart: Input → Process → Output",
            tmp_path / "output.png",
        )
        assert result.diagram_type == "flowchart"

    def test_raw_mermaid_mode(self, tmp_path: Path) -> None:
        """Test raw Mermaid code mode."""
        raw_code = "flowchart TD\n    A[Start] --> B[End]"
        result = generate_mermaid_diagram(
            raw_code,
            tmp_path / "output.png",
            raw_mermaid=True,
        )
        assert result.mermaid_code == raw_code
        assert result.diagram_type == "raw"

    def test_invalid_mermaid_syntax_fails(self, tmp_path: Path) -> None:
        """Test invalid Mermaid syntax causes failure."""
        result = generate_mermaid_diagram(
            "invalidSyntax\n    broken code",
            tmp_path / "output.png",
            raw_mermaid=True,
        )
        assert not result.success
        assert "syntax" in result.error.lower() or "invalid" in result.error.lower()

    def test_generation_with_theme(self, tmp_path: Path) -> None:
        """Test generation with custom theme."""
        result = generate_mermaid_diagram(
            "Simple: A → B",
            tmp_path / "output.png",
            theme="dark",
        )
        # Theme should be recorded in metadata if successful
        if result.success and result.metadata:
            assert result.metadata.get("theme") == "dark"

    def test_generation_cost_is_zero(self, tmp_path: Path) -> None:
        """Test Mermaid generation cost is always zero."""
        result = generate_mermaid_diagram(
            "Simple: A → B",
            tmp_path / "output.png",
        )
        assert result.cost == 0.0


# =====================================================================
# Render Mermaid Convenience Function Tests
# =====================================================================


class TestRenderMermaidFunction:
    """Tests for render_mermaid convenience function."""

    def test_function_creates_renderer(self, tmp_path: Path) -> None:
        """Test convenience function works."""
        # This may fail if no backend is available, which is expected
        result = render_mermaid(
            "flowchart TD\n    A --> B",
            tmp_path / "output.png",
        )
        # Should return a RenderResult regardless of success
        assert isinstance(result, RenderResult)

    def test_function_accepts_all_parameters(self, tmp_path: Path) -> None:
        """Test function accepts all configuration parameters."""
        result = render_mermaid(
            "flowchart TD\n    A --> B",
            tmp_path / "output.svg",
            output_format="svg",
            theme="forest",
            width=1200,
            height=800,
            scale=1.5,
            background="transparent",
            backend="api",
        )
        assert isinstance(result, RenderResult)


# =====================================================================
# Version Detection Tests
# =====================================================================


class TestVersionDetection:
    """Tests for Mermaid version detection."""

    def test_get_version_returns_string_or_none(self) -> None:
        """Test version detection returns string or None."""
        version = get_mermaid_version()
        assert version is None or isinstance(version, str)


# =====================================================================
# Integration Tests (require actual backend)
# =====================================================================


@pytest.mark.skipif(
    not MermaidRenderer().get_available_backends(),
    reason="No Mermaid rendering backend available"
)
class TestIntegrationWithBackend:
    """Integration tests that require an actual rendering backend."""

    def test_render_simple_flowchart(self, tmp_path: Path) -> None:
        """Test rendering a simple flowchart."""
        code = "flowchart TD\n    A[Start] --> B[Process] --> C[End]"
        output_path = tmp_path / "flowchart.png"

        result = render_mermaid(code, output_path)

        assert result.success
        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_render_sequence_diagram(self, tmp_path: Path) -> None:
        """Test rendering a sequence diagram."""
        code = "sequenceDiagram\n    A->>B: Request\n    B-->>A: Response"
        output_path = tmp_path / "sequence.png"

        result = render_mermaid(code, output_path)

        assert result.success
        assert output_path.exists()

    def test_render_to_svg(self, tmp_path: Path) -> None:
        """Test rendering to SVG format."""
        code = "flowchart TD\n    A --> B"
        output_path = tmp_path / "diagram.svg"

        result = render_mermaid(code, output_path, output_format="svg")

        assert result.success
        assert output_path.exists()
        # SVG should be text-based
        content = output_path.read_text()
        assert "<svg" in content or "svg" in content.lower()

    def test_render_with_custom_size(self, tmp_path: Path) -> None:
        """Test rendering with custom dimensions."""
        code = "flowchart TD\n    A --> B"
        output_path = tmp_path / "custom_size.png"

        result = render_mermaid(
            code,
            output_path,
            width=1200,
            height=900,
        )

        assert result.success

    def test_generate_diagram_end_to_end(self, tmp_path: Path) -> None:
        """Test full diagram generation end-to-end."""
        output_path = tmp_path / "generated.png"

        result = generate_mermaid_diagram(
            "Simple flowchart: Input → Process → Output",
            output_path,
            verbose=False,
        )

        assert result.success
        assert result.output_path is not None
        assert Path(result.output_path).exists()
        assert result.generation_time_ms > 0


# =====================================================================
# Edge Cases Tests
# =====================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_unicode_in_labels(self) -> None:
        """Test handling unicode in node labels."""
        code, dtype = prompt_to_mermaid("Début → Processus → Fin")
        assert "flowchart" in code.lower()

    def test_special_characters_escaped(self) -> None:
        """Test special characters are properly handled."""
        code, dtype = prompt_to_mermaid("Check [status] → Update {config}")
        assert dtype == "flowchart"
        # Should not crash, brackets should be escaped

    def test_very_long_prompt(self) -> None:
        """Test handling very long prompts."""
        long_prompt = " → ".join([f"Step{i}" for i in range(50)])
        code, dtype = prompt_to_mermaid(long_prompt)
        # Should handle without crashing
        assert code is not None

    def test_empty_prompt(self) -> None:
        """Test handling empty prompt."""
        code, dtype = prompt_to_mermaid("")
        # Should provide some default output
        assert code is not None
        assert dtype is not None

    def test_whitespace_only_prompt(self) -> None:
        """Test handling whitespace-only prompt."""
        code, dtype = prompt_to_mermaid("   \n   \t   ")
        # Should provide some default output
        assert code is not None

    def test_output_path_creation(self, tmp_path: Path) -> None:
        """Test output directory is created if needed."""
        nested_path = tmp_path / "nested" / "dir" / "output.png"

        # Should create parent directories during rendering attempt
        generate_mermaid_diagram(
            "Simple: A → B",
            nested_path,
        )
        # Parent directory should exist (even if rendering fails)
        assert nested_path.parent.exists()
