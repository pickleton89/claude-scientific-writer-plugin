#!/usr/bin/env python3
"""
Mermaid diagram generation engine for scientific schematics.

This module provides Tier 1 generation using Mermaid - free, instant,
and deterministic diagram rendering for simple use cases.

Features:
    - Natural language to Mermaid syntax conversion
    - Template-based generation for common diagram types (CONSORT, PRISMA, etc.)
    - Direct raw Mermaid code rendering
    - Multiple output formats (PNG, SVG, PDF)
    - Mermaid theme support

Usage:
    # Generate from natural language description
    python generate_mermaid.py "Simple flowchart: Start → Process → End" -o output.png

    # Generate from raw Mermaid code
    python generate_mermaid.py --raw "flowchart TD; A-->B" -o output.png

    # Use specific diagram type/template
    python generate_mermaid.py "Show enrollment flow" -o consort.png --type consort

    # Custom theme
    python generate_mermaid.py "State machine" -o states.svg --theme forest
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

# Import from utils package
try:
    from utils.mermaid_renderer import (
        MermaidRenderer,
        RenderResult,
        render_mermaid,
        validate_mermaid_syntax,
    )
    from utils.mermaid_templates import (
        DIAGRAM_TYPE_TO_TEMPLATES,
        build_flowchart,
        fill_template,
        get_required_fields,
        get_template_for_type,
        list_diagram_types,
        list_templates,
    )
    from utils.complexity_analyzer import (
        GenerationTier,
        analyze_complexity,
        detect_diagram_type,
        get_tier_summary,
    )
except ImportError:
    # Handle running from different directory
    import os

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from utils.mermaid_renderer import (
        MermaidRenderer,
        RenderResult,
        render_mermaid,
        validate_mermaid_syntax,
    )
    from utils.mermaid_templates import (
        DIAGRAM_TYPE_TO_TEMPLATES,
        build_flowchart,
        fill_template,
        get_required_fields,
        get_template_for_type,
        list_diagram_types,
        list_templates,
    )
    from utils.complexity_analyzer import (
        GenerationTier,
        analyze_complexity,
        detect_diagram_type,
        get_tier_summary,
    )


@dataclass
class MermaidResult:
    """Result of a Mermaid diagram generation operation.

    Attributes:
        success: Whether generation succeeded
        output_path: Path to generated image file
        mermaid_code: The Mermaid source code used
        diagram_type: Detected or specified diagram type
        tier: Generation tier used (always MERMAID for this module)
        render_result: Underlying render result from renderer
        generation_time_ms: Total time for generation
        cost: Cost estimate (always $0 for Mermaid)
        error: Error message if failed
    """

    success: bool
    output_path: str | None
    mermaid_code: str
    diagram_type: str
    tier: GenerationTier = GenerationTier.MERMAID
    render_result: RenderResult | None = None
    generation_time_ms: float = 0.0
    cost: float = 0.0  # Mermaid is free!
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "success": self.success,
            "output_path": self.output_path,
            "mermaid_code": self.mermaid_code,
            "diagram_type": self.diagram_type,
            "tier": self.tier.value,
            "generation_time_ms": self.generation_time_ms,
            "cost": self.cost,
            "error": self.error,
            "metadata": self.metadata,
            "render_result": self.render_result.to_dict() if self.render_result else None,
        }


def prompt_to_mermaid(
    prompt: str,
    diagram_type: str | None = None,
) -> tuple[str, str]:
    """Convert natural language prompt to Mermaid syntax.

    Uses pattern matching and templates to convert common natural language
    descriptions to Mermaid diagram code. Node shapes are automatically
    determined based on keywords (e.g., "start" gets stadium shape).

    Args:
        prompt: Natural language description of the diagram
        diagram_type: Optional diagram type hint

    Returns:
        Tuple of (mermaid_code, detected_type)

    Example:
        >>> code, dtype = prompt_to_mermaid("Input → Process → Output")
        >>> dtype
        'flowchart'
        >>> "flowchart TD" in code
        True
        >>> "Process" in code
        True
    """
    # Detect diagram type if not provided
    if diagram_type is None:
        diagram_type = detect_diagram_type(prompt)

    # Try template-based generation for known types
    if diagram_type in DIAGRAM_TYPE_TO_TEMPLATES:
        template_code = _try_template_generation(prompt, diagram_type)
        if template_code:
            return template_code, diagram_type

    # Parse flowchart-style prompts
    if diagram_type in ("flowchart", "process", "workflow"):
        mermaid_code = _parse_flowchart_prompt(prompt)
        return mermaid_code, "flowchart"

    # Parse sequence diagram prompts
    if diagram_type == "sequence":
        mermaid_code = _parse_sequence_prompt(prompt)
        return mermaid_code, "sequence"

    # Parse state diagram prompts
    if diagram_type == "state":
        mermaid_code = _parse_state_prompt(prompt)
        return mermaid_code, "state"

    # Default: try to create a simple flowchart
    mermaid_code = _parse_flowchart_prompt(prompt)
    return mermaid_code, "flowchart"


def _escape_mermaid_label(text: str) -> str:
    """Escape special Mermaid characters in node labels.

    Mermaid uses brackets for node shapes, so raw brackets in labels
    can cause syntax errors. This function escapes them using HTML entities.

    Args:
        text: Raw label text

    Returns:
        Escaped label safe for use in Mermaid nodes

    Example:
        >>> _escape_mermaid_label("Check [status]")
        'Check #91;status#93;'
    """
    # Escape brackets that could interfere with Mermaid node syntax
    # Using HTML decimal entities that Mermaid renders correctly
    text = text.replace("[", "#91;")
    text = text.replace("]", "#93;")
    text = text.replace("{", "#123;")
    text = text.replace("}", "#125;")
    text = text.replace("(", "#40;")
    text = text.replace(")", "#41;")
    # Also escape quotes and pipes which can cause issues
    text = text.replace('"', "#34;")
    text = text.replace("|", "#124;")
    return text


def _try_template_generation(prompt: str, diagram_type: str) -> str | None:
    """Try to fill a template based on numbers/data in the prompt.

    Args:
        prompt: User's prompt
        diagram_type: Detected diagram type

    Returns:
        Filled template code or None if not enough data
    """
    prompt_lower = prompt.lower()

    # CONSORT template - look for participant numbers
    if diagram_type == "consort":
        numbers = re.findall(r"n\s*=\s*(\d+)|(\d+)\s*(?:participants?|patients?|subjects?)", prompt_lower)
        if len(numbers) >= 4:
            # Extract numbers, flatten the tuples
            nums = [int(n) for group in numbers for n in group if n]
            if len(nums) >= 4:
                try:
                    template_name = get_template_for_type("consort", "basic")
                    if template_name:
                        # Estimate values from available numbers
                        return fill_template(
                            template_name,
                            screened=nums[0] if len(nums) > 0 else 100,
                            excluded=nums[1] if len(nums) > 1 else 30,
                            randomized=nums[2] if len(nums) > 2 else 70,
                            intervention=nums[3] if len(nums) > 3 else 35,
                            control=nums[4] if len(nums) > 4 else 35,
                            analyzed_intervention=nums[5] if len(nums) > 5 else 32,
                            analyzed_control=nums[6] if len(nums) > 6 else 33,
                        )
                except (KeyError, ValueError):
                    pass

    # PRISMA template - look for literature search numbers
    if diagram_type == "prisma":
        numbers = re.findall(r"n\s*=\s*(\d+)|(\d+)\s*(?:records?|studies?|articles?)", prompt_lower)
        if len(numbers) >= 3:
            nums = [int(n) for group in numbers for n in group if n]
            if len(nums) >= 3:
                try:
                    template_name = get_template_for_type("prisma", "basic")
                    if template_name:
                        return fill_template(
                            template_name,
                            identified=nums[0] if len(nums) > 0 else 500,
                            screened=nums[1] if len(nums) > 1 else 400,
                            excluded_screening=nums[2] if len(nums) > 2 else 200,
                            full_text=nums[3] if len(nums) > 3 else 200,
                            excluded_full_text=nums[4] if len(nums) > 4 else 150,
                            included=nums[5] if len(nums) > 5 else 50,
                        )
                except (KeyError, ValueError):
                    pass

    return None


def _parse_flowchart_prompt(prompt: str) -> str:
    """Parse a flowchart-style prompt into Mermaid code.

    Handles patterns like:
    - "A → B → C"
    - "Start, then Process, then End"
    - "Step 1: Input, Step 2: Process, Step 3: Output"

    Args:
        prompt: Natural language flowchart description

    Returns:
        Mermaid flowchart code
    """
    # Extract arrow-separated items
    if "→" in prompt or "->" in prompt or "-->" in prompt:
        # Normalize arrows
        normalized = prompt.replace("-->", "→").replace("->", "→")
        parts = [p.strip() for p in normalized.split("→") if p.strip()]
        if len(parts) >= 2:
            return _build_linear_flowchart(parts)

    # Extract comma or "then" separated items
    if "then" in prompt.lower():
        parts = re.split(r",?\s+then\s+", prompt, flags=re.IGNORECASE)
        parts = [p.strip() for p in parts if p.strip()]
        if len(parts) >= 2:
            return _build_linear_flowchart(parts)

    # Extract numbered steps
    step_pattern = r"(?:step\s*)?(\d+)[:\.\)]\s*([^,;\n]+)"
    steps = re.findall(step_pattern, prompt, re.IGNORECASE)
    if len(steps) >= 2:
        parts = [step[1].strip() for step in sorted(steps, key=lambda x: int(x[0]))]
        return _build_linear_flowchart(parts)

    # Extract colon-separated items
    if ":" in prompt:
        # Check if it's a labeled list
        parts = re.split(r"[,;]\s*", prompt)
        items = []
        for part in parts:
            if ":" in part:
                label = part.split(":", 1)[1].strip()
                if label:
                    items.append(label)
            else:
                items.append(part.strip())
        if len(items) >= 2:
            return _build_linear_flowchart(items)

    # Fallback: try comma-separated
    parts = [p.strip() for p in prompt.split(",") if p.strip()]
    if len(parts) >= 2:
        return _build_linear_flowchart(parts)

    # Last resort: create a simple single-node diagram
    escaped_label = _escape_mermaid_label(prompt[:50])
    return f"flowchart TD\n    A[{escaped_label}]"


def _build_linear_flowchart(
    items: list[str],
    direction: Literal["TD", "LR", "BT", "RL"] = "TD",
) -> str:
    """Build a linear flowchart from a list of items.

    Args:
        items: List of node labels
        direction: Flow direction

    Returns:
        Mermaid flowchart code
    """
    # Generate node IDs
    nodes = []
    connections = []

    for i, item in enumerate(items):
        # Clean up the item label
        label = item.strip()
        # Remove common prefixes
        label = re.sub(r"^(start|end|begin|finish|step\s*\d*)[:\.\)]\s*", "", label, flags=re.IGNORECASE)
        if not label:
            label = item.strip()

        # Generate node ID
        node_id = chr(ord("A") + i) if i < 26 else f"N{i}"

        # Determine node shape based on content (check before escaping)
        label_lower = label.lower()
        # Escape special characters for Mermaid syntax safety
        escaped_label = _escape_mermaid_label(label)

        if any(kw in label_lower for kw in ["start", "begin", "init"]):
            nodes.append({"id": node_id, "label": escaped_label, "shape": "stadium"})
        elif any(kw in label_lower for kw in ["end", "finish", "done", "complete"]):
            nodes.append({"id": node_id, "label": escaped_label, "shape": "stadium"})
        elif "?" in label or any(kw in label_lower for kw in ["decision", "check", "if "]):
            nodes.append({"id": node_id, "label": escaped_label, "shape": "diamond"})
        else:
            nodes.append({"id": node_id, "label": escaped_label, "shape": "rect"})

        # Add connection to previous node
        if i > 0:
            prev_id = chr(ord("A") + i - 1) if i - 1 < 26 else f"N{i-1}"
            connections.append({"from": prev_id, "to": node_id})

    return build_flowchart(nodes, connections, direction)


def _parse_sequence_prompt(prompt: str) -> str:
    """Parse a sequence diagram prompt into Mermaid code.

    Args:
        prompt: Natural language sequence description

    Returns:
        Mermaid sequence diagram code
    """
    # Look for participant mentions
    participants = []
    participant_pattern = r"(?:between|from|to|with)\s+(\w+)(?:\s+and\s+(\w+))?"
    matches = re.findall(participant_pattern, prompt, re.IGNORECASE)
    for match in matches:
        for p in match:
            if p and p.lower() not in ["the", "a", "an"]:
                if p not in participants:
                    participants.append(p)

    # Default participants if none found
    if len(participants) < 2:
        participants = ["Client", "Server"]

    # Build sequence diagram
    lines = ["sequenceDiagram"]
    for p in participants[:4]:  # Max 4 participants
        lines.append(f"    participant {p}")

    # Add a simple interaction
    if len(participants) >= 2:
        lines.append(f"    {participants[0]}->>{participants[1]}: Request")
        lines.append(f"    {participants[1]}-->>{participants[0]}: Response")

    return "\n".join(lines)


def _parse_state_prompt(prompt: str) -> str:
    """Parse a state diagram prompt into Mermaid code.

    Args:
        prompt: Natural language state description

    Returns:
        Mermaid state diagram code
    """
    # Look for state mentions
    state_pattern = r"(?:state|status|phase)[:\s]+(\w+)"
    states = re.findall(state_pattern, prompt, re.IGNORECASE)

    if not states:
        # Look for arrow-separated states (handle all arrow types consistently)
        if "→" in prompt or "->" in prompt or "-->" in prompt:
            normalized = prompt.replace("-->", "→").replace("->", "→")
            states = [s.strip() for s in normalized.split("→") if s.strip()]

    if not states or len(states) < 2:
        states = ["Idle", "Active", "Complete"]

    # Build state diagram
    lines = ["stateDiagram-v2", f"    [*] --> {states[0]}"]

    for i in range(len(states) - 1):
        lines.append(f"    {states[i]} --> {states[i+1]}")

    lines.append(f"    {states[-1]} --> [*]")

    return "\n".join(lines)


def generate_mermaid_diagram(
    prompt: str,
    output_path: str | Path,
    diagram_type: str | None = None,
    output_format: Literal["png", "svg", "pdf"] = "png",
    theme: Literal["default", "dark", "forest", "neutral", "base"] = "default",
    width: int = 800,
    height: int = 600,
    scale: float = 2.0,
    background: str = "white",
    raw_mermaid: bool = False,
    backend: str = "auto",
    verbose: bool = False,
) -> MermaidResult:
    """Generate a diagram from natural language using Mermaid.

    This is the main entry point for Mermaid-based diagram generation.

    Args:
        prompt: Natural language description or raw Mermaid code
        output_path: Path for output file
        diagram_type: Optional diagram type hint (consort, prisma, flowchart, etc.)
        output_format: Output format (png, svg, pdf)
        theme: Mermaid theme
        width: Output width in pixels
        height: Output height in pixels
        scale: Scale factor for high-DPI
        background: Background color
        raw_mermaid: If True, treat prompt as raw Mermaid code
        backend: Rendering backend (auto, mmdc, python, api)
        verbose: Print detailed progress

    Returns:
        MermaidResult with generation status and metadata

    Example:
        >>> result = generate_mermaid_diagram(
        ...     "Simple flowchart: Start → Process → End",
        ...     "output.png"
        ... )
        >>> print(result.success, result.output_path)
    """
    start_time = time.time()
    output_path = Path(output_path)

    def log(msg: str) -> None:
        if verbose:
            print(f"[Mermaid] {msg}")

    log(f"Starting generation for: {prompt[:50]}...")

    # Step 1: Get Mermaid code
    if raw_mermaid:
        mermaid_code = prompt
        detected_type = "raw"
        log("Using raw Mermaid code")
    else:
        log("Converting prompt to Mermaid syntax...")
        mermaid_code, detected_type = prompt_to_mermaid(prompt, diagram_type)
        log(f"Detected diagram type: {detected_type}")

    # Step 2: Validate syntax
    log("Validating Mermaid syntax...")
    is_valid, error_msg = validate_mermaid_syntax(mermaid_code)
    if not is_valid:
        return MermaidResult(
            success=False,
            output_path=None,
            mermaid_code=mermaid_code,
            diagram_type=detected_type,
            generation_time_ms=(time.time() - start_time) * 1000,
            error=f"Invalid Mermaid syntax: {error_msg}",
        )
    log("Syntax validation passed")

    # Step 3: Render to image
    log(f"Rendering to {output_format.upper()}...")
    render_result = render_mermaid(
        mermaid_code=mermaid_code,
        output_path=output_path,
        output_format=output_format,
        theme=theme,
        width=width,
        height=height,
        scale=scale,
        background=background,
        backend=backend,
    )

    generation_time = (time.time() - start_time) * 1000

    if render_result.success:
        log(f"Generation complete: {render_result.output_path}")
        log(f"Backend used: {render_result.backend_used}")
        log(f"Time: {generation_time:.1f}ms")

        return MermaidResult(
            success=True,
            output_path=render_result.output_path,
            mermaid_code=mermaid_code,
            diagram_type=detected_type,
            render_result=render_result,
            generation_time_ms=generation_time,
            metadata={
                "backend": render_result.backend_used,
                "theme": theme,
                "mermaid_hash": render_result.mermaid_hash,
            },
        )
    else:
        log(f"Rendering failed: {render_result.error}")
        return MermaidResult(
            success=False,
            output_path=None,
            mermaid_code=mermaid_code,
            diagram_type=detected_type,
            render_result=render_result,
            generation_time_ms=generation_time,
            error=render_result.error,
        )


def main() -> int:
    """Command-line interface for Mermaid diagram generation."""
    parser = argparse.ArgumentParser(
        description="Generate diagrams using Mermaid (Tier 1 - free, instant)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate from natural language description
  python generate_mermaid.py "Simple flow: Start → Process → End" -o flow.png

  # Generate from raw Mermaid code
  python generate_mermaid.py --raw "flowchart TD; A-->B-->C" -o diagram.png

  # Specify diagram type
  python generate_mermaid.py "Patient enrollment flow" -o consort.png --type consort

  # Custom theme and format
  python generate_mermaid.py "State machine" -o states.svg --theme forest --format svg

  # List available templates
  python generate_mermaid.py --list-templates

Supported Diagram Types:
  flowchart, sequence, state, class, er, gantt, pie, mindmap, timeline,
  consort, prisma, decision, block

Themes:
  default, dark, forest, neutral, base

Tier 1 Benefits:
  - Cost: $0.00 (local rendering)
  - Speed: ~100ms
  - Deterministic: Same input = same output
  - Git-friendly: Text source can be version controlled
        """,
    )

    parser.add_argument(
        "prompt",
        nargs="?",
        help="Description of the diagram or raw Mermaid code (with --raw)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output file path (required unless using --list-*)",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Treat prompt as raw Mermaid code",
    )
    parser.add_argument(
        "--type",
        dest="diagram_type",
        choices=list_diagram_types() + ["raw"],
        help="Diagram type hint for better template selection",
    )
    parser.add_argument(
        "--format",
        dest="output_format",
        choices=["png", "svg", "pdf"],
        default="png",
        help="Output format (default: png)",
    )
    parser.add_argument(
        "--theme",
        choices=["default", "dark", "forest", "neutral", "base"],
        default="default",
        help="Mermaid theme (default: default)",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=800,
        help="Output width in pixels (default: 800)",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=600,
        help="Output height in pixels (default: 600)",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=2.0,
        help="Scale factor for high-DPI (default: 2.0)",
    )
    parser.add_argument(
        "--background",
        default="white",
        help="Background color (default: white)",
    )
    parser.add_argument(
        "--backend",
        choices=["auto", "mmdc", "python", "api"],
        default="auto",
        help="Rendering backend (default: auto)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output",
    )
    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="List available Mermaid templates",
    )
    parser.add_argument(
        "--list-types",
        action="store_true",
        help="List supported diagram types",
    )
    parser.add_argument(
        "--check-backends",
        action="store_true",
        help="Check available rendering backends",
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Analyze prompt complexity without generating",
    )

    args = parser.parse_args()

    # Handle info commands
    if args.list_templates:
        print("Available Mermaid Templates:")
        print("-" * 40)
        for template_name in list_templates():
            fields = get_required_fields(template_name)
            print(f"  {template_name}")
            print(f"    Required fields: {', '.join(fields)}")
            print()
        return 0

    if args.list_types:
        print("Supported Diagram Types:")
        print("-" * 40)
        for dtype in list_diagram_types():
            templates = DIAGRAM_TYPE_TO_TEMPLATES.get(dtype, [])
            print(f"  {dtype}: {', '.join(templates)}")
        return 0

    if args.check_backends:
        print("Checking Rendering Backends:")
        print("-" * 40)
        renderer = MermaidRenderer()
        available = renderer.get_available_backends()
        for backend in ["mmdc", "python", "api"]:
            status = "available" if backend in available else "not available"
            print(f"  {backend}: {status}")
            if backend not in available:
                print(f"    Install: {MermaidRenderer.install_instructions(backend)[:80]}...")
        return 0

    # Validate required args for generation
    if not args.prompt:
        parser.error("prompt is required for generation")

    if args.analyze:
        # Just analyze complexity without generating
        analysis = analyze_complexity(args.prompt)
        print("Complexity Analysis:")
        print("-" * 40)
        print(f"  Diagram type: {analysis.diagram_type}")
        print(f"  Estimated nodes: {analysis.estimated_nodes}")
        print(f"  Estimated edges: {analysis.estimated_edges}")
        print(f"  Mermaid compatible: {analysis.mermaid_compatible}")
        print(f"  Recommended tier: {analysis.recommended_tier.value}")
        print(f"  Confidence: {analysis.confidence:.0%}")
        print(f"  Reasoning: {analysis.reasoning}")

        tier_info = get_tier_summary(analysis.recommended_tier)
        print()
        print(f"Tier Info ({tier_info['name']}):")
        print(f"  Cost: {tier_info['cost']}")
        print(f"  Speed: {tier_info['speed']}")
        print(f"  Quality: {tier_info['quality']}")
        return 0

    if not args.output:
        parser.error("-o/--output is required for generation")

    # Generate diagram
    print()
    print("=" * 60)
    print("Mermaid Diagram Generation (Tier 1)")
    print("=" * 60)
    print(f"Input: {args.prompt[:60]}{'...' if len(args.prompt) > 60 else ''}")
    print(f"Output: {args.output}")
    print(f"Format: {args.output_format}")
    print(f"Theme: {args.theme}")
    if args.raw:
        print("Mode: Raw Mermaid code")
    print("=" * 60)
    print()

    result = generate_mermaid_diagram(
        prompt=args.prompt,
        output_path=args.output,
        diagram_type=args.diagram_type,
        output_format=args.output_format,
        theme=args.theme,
        width=args.width,
        height=args.height,
        scale=args.scale,
        background=args.background,
        raw_mermaid=args.raw,
        backend=args.backend,
        verbose=args.verbose,
    )

    if result.success:
        print(f"Generated: {result.output_path}")
        print(f"Diagram type: {result.diagram_type}")
        print(f"Time: {result.generation_time_ms:.1f}ms")
        print(f"Cost: ${result.cost:.2f}")
        if result.render_result:
            print(f"Backend: {result.render_result.backend_used}")

        # Also save the Mermaid source for version control
        mermaid_source_path = Path(args.output).with_suffix(".mmd")
        with open(mermaid_source_path, "w") as f:
            f.write(result.mermaid_code)
        print(f"Source: {mermaid_source_path}")

        print()
        print("Mermaid Source Code:")
        print("-" * 40)
        print(result.mermaid_code)
        print("-" * 40)
        return 0
    else:
        print(f"Generation failed: {result.error}")
        if args.verbose and result.mermaid_code:
            print()
            print("Generated Mermaid code (may contain errors):")
            print("-" * 40)
            print(result.mermaid_code)
            print("-" * 40)
        return 1


if __name__ == "__main__":
    sys.exit(main())
