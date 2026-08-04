"""Mermaid diagram templates for scientific schematic generation.

Provides reusable Mermaid templates for common diagram types used in
scientific publications. Templates use string formatting placeholders
that can be filled with actual data.

Usage:
    >>> from utils.mermaid_templates import fill_template, get_template_for_type
    >>> template = get_template_for_type("consort")
    >>> mermaid_code = fill_template(
    ...     "consort_basic",
    ...     screened=100, excluded=30, randomized=70,
    ...     intervention=35, control=35,
    ...     analyzed_intervention=32, analyzed_control=33
    ... )
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


@dataclass
class TemplateInfo:
    """Metadata about a Mermaid template."""

    name: str
    description: str
    diagram_type: str
    required_fields: list[str]
    optional_fields: list[str]
    example_output: str


# Mermaid diagram templates for common scientific diagram types
# Use {placeholder} syntax for string.format() compatibility

TEMPLATES: dict[str, str] = {
    # =========================================================================
    # STUDY DESIGN TEMPLATES
    # =========================================================================
    "consort_basic": """\
flowchart TD
    A[Assessed for eligibility<br/>n={screened}] --> B{{Excluded n={excluded}}}
    A --> C[Randomized<br/>n={randomized}]
    C --> D[Allocated to intervention<br/>n={intervention}]
    C --> E[Allocated to control<br/>n={control}]
    D --> F[Analyzed<br/>n={analyzed_intervention}]
    E --> G[Analyzed<br/>n={analyzed_control}]
""",
    "consort_with_followup": """\
flowchart TD
    A[Assessed for eligibility<br/>n={screened}] --> B{{Excluded n={excluded}}}
    A --> C[Randomized<br/>n={randomized}]
    C --> D[Allocated to intervention<br/>n={intervention}]
    C --> E[Allocated to control<br/>n={control}]
    D --> F[Lost to follow-up<br/>n={lost_intervention}]
    E --> G[Lost to follow-up<br/>n={lost_control}]
    D --> H[Analyzed<br/>n={analyzed_intervention}]
    E --> I[Analyzed<br/>n={analyzed_control}]
""",
    "prisma_basic": """\
flowchart TD
    A[Records identified<br/>n={identified}] --> B[Records screened<br/>n={screened}]
    B --> C{{Records excluded<br/>n={excluded_screening}}}
    B --> D[Full-text assessed<br/>n={full_text}]
    D --> E{{Excluded n={excluded_full_text}}}
    D --> F[Studies included<br/>n={included}]
""",
    "prisma_with_duplicates": """\
flowchart TD
    A[Records from databases<br/>n={database_records}] --> B[Records after duplicates removed<br/>n={after_duplicates}]
    C[Additional records<br/>n={additional_records}] --> B
    B --> D[Records screened<br/>n={screened}]
    D --> E{{Records excluded<br/>n={excluded_screening}}}
    D --> F[Full-text assessed<br/>n={full_text}]
    F --> G{{Excluded n={excluded_full_text}}}
    F --> H[Studies included<br/>n={included}]
""",
    # =========================================================================
    # PROCESS FLOW TEMPLATES
    # =========================================================================
    "simple_flowchart_td": """\
flowchart TD
{nodes}
{connections}
""",
    "simple_flowchart_lr": """\
flowchart LR
{nodes}
{connections}
""",
    "simple_flowchart_bt": """\
flowchart BT
{nodes}
{connections}
""",
    "simple_flowchart_rl": """\
flowchart RL
{nodes}
{connections}
""",
    "methods_pipeline": """\
flowchart LR
    subgraph Input
        A[{input_label}]
    end
    subgraph Processing
        B[{step1_label}]
        C[{step2_label}]
        D[{step3_label}]
    end
    subgraph Output
        E[{output_label}]
    end
    A --> B --> C --> D --> E
""",
    "data_processing_pipeline": """\
flowchart LR
    subgraph Collection["Data Collection"]
        A[{source}]
    end
    subgraph Preprocessing["Preprocessing"]
        B[{preprocess}]
    end
    subgraph Analysis["Analysis"]
        C[{analysis}]
    end
    subgraph Results["Results"]
        D[{results}]
    end
    A --> B --> C --> D
""",
    # =========================================================================
    # SEQUENCE DIAGRAM TEMPLATES
    # =========================================================================
    "sequence_basic": """\
sequenceDiagram
    participant {participant1}
    participant {participant2}
{interactions}
""",
    "sequence_three_party": """\
sequenceDiagram
    participant {participant1}
    participant {participant2}
    participant {participant3}
{interactions}
""",
    "api_sequence": """\
sequenceDiagram
    participant Client
    participant API
    participant Database
    Client->>API: {request_label}
    API->>Database: Query
    Database-->>API: Results
    API-->>Client: {response_label}
""",
    # =========================================================================
    # STATE DIAGRAM TEMPLATES
    # =========================================================================
    "state_machine_basic": """\
stateDiagram-v2
    [*] --> {initial_state}
{transitions}
    {final_state} --> [*]
""",
    "state_machine_with_notes": """\
stateDiagram-v2
    [*] --> {initial_state}
{transitions}
    {final_state} --> [*]
    note right of {initial_state}: {initial_note}
    note left of {final_state}: {final_note}
""",
    # =========================================================================
    # CLASS/ER DIAGRAM TEMPLATES
    # =========================================================================
    "class_diagram_basic": """\
classDiagram
{class_definitions}
{relationships}
""",
    "er_diagram_basic": """\
erDiagram
{entities}
{relationships}
""",
    # =========================================================================
    # TIMELINE TEMPLATES
    # =========================================================================
    "timeline_basic": """\
timeline
    title {title}
{events}
""",
    "study_timeline": """\
timeline
    title {study_name}
    section Enrollment
        {enrollment_start} : {enrollment_desc}
    section Treatment
        {treatment_start} : {treatment_desc}
    section Follow-up
        {followup_start} : {followup_desc}
    section Analysis
        {analysis_start} : {analysis_desc}
""",
    # =========================================================================
    # DECISION/BRANCHING TEMPLATES
    # =========================================================================
    "decision_tree": """\
flowchart TD
    A[{start_label}] --> B{{{decision1}}}
    B -->|{yes_label}| C[{outcome1}]
    B -->|{no_label}| D{{{decision2}}}
    D -->|{yes_label}| E[{outcome2}]
    D -->|{no_label}| F[{outcome3}]
""",
    "algorithm_flowchart": """\
flowchart TD
    START([Start]) --> INPUT[/{input_label}/]
    INPUT --> PROCESS[{process_label}]
    PROCESS --> DECISION{{{decision_label}}}
    DECISION -->|Yes| OUTPUT1[{output_yes}]
    DECISION -->|No| OUTPUT2[{output_no}]
    OUTPUT1 --> END([End])
    OUTPUT2 --> END
""",
    # =========================================================================
    # PIE/CHART TEMPLATES
    # =========================================================================
    "pie_chart": """\
pie showData
    title {title}
{segments}
""",
    # =========================================================================
    # MINDMAP TEMPLATES
    # =========================================================================
    "mindmap_basic": """\
mindmap
    root(({central_topic}))
{branches}
""",
    # =========================================================================
    # BLOCK DIAGRAM TEMPLATES
    # =========================================================================
    "block_diagram": """\
block-beta
    columns {num_columns}
{blocks}
""",
}

# Mapping from diagram types to recommended templates
DIAGRAM_TYPE_TO_TEMPLATES: dict[str, list[str]] = {
    "consort": ["consort_basic", "consort_with_followup"],
    "prisma": ["prisma_basic", "prisma_with_duplicates"],
    "flowchart": [
        "simple_flowchart_td",
        "simple_flowchart_lr",
        "simple_flowchart_bt",
        "simple_flowchart_rl",
        "decision_tree",
    ],
    "methods_flowchart": ["methods_pipeline", "data_processing_pipeline"],
    "sequence": ["sequence_basic", "sequence_three_party", "api_sequence"],
    "state": ["state_machine_basic", "state_machine_with_notes"],
    "class": ["class_diagram_basic"],
    "er": ["er_diagram_basic"],
    "timeline": ["timeline_basic", "study_timeline"],
    "decision": ["decision_tree", "algorithm_flowchart"],
    "pie": ["pie_chart"],
    "mindmap": ["mindmap_basic"],
    "block": ["block_diagram"],
}

# Template metadata for documentation and validation
TEMPLATE_METADATA: dict[str, TemplateInfo] = {
    # Study design templates
    "consort_basic": TemplateInfo(
        name="CONSORT Basic",
        description="Basic CONSORT flow diagram for randomized controlled trials",
        diagram_type="consort",
        required_fields=[
            "screened",
            "excluded",
            "randomized",
            "intervention",
            "control",
            "analyzed_intervention",
            "analyzed_control",
        ],
        optional_fields=[],
        example_output="flowchart TD\n    A[Assessed...] --> B{{Excluded...}}",
    ),
    "consort_with_followup": TemplateInfo(
        name="CONSORT with Follow-up",
        description="CONSORT flow with follow-up loss tracking",
        diagram_type="consort",
        required_fields=[
            "screened",
            "excluded",
            "randomized",
            "intervention",
            "control",
            "lost_intervention",
            "lost_control",
            "analyzed_intervention",
            "analyzed_control",
        ],
        optional_fields=[],
        example_output="flowchart TD\n    A[Assessed...] --> ...",
    ),
    "prisma_basic": TemplateInfo(
        name="PRISMA Basic",
        description="Basic PRISMA flow diagram for systematic reviews",
        diagram_type="prisma",
        required_fields=[
            "identified",
            "screened",
            "excluded_screening",
            "full_text",
            "excluded_full_text",
            "included",
        ],
        optional_fields=[],
        example_output="flowchart TD\n    A[Records identified...] --> B[...]",
    ),
    "prisma_with_duplicates": TemplateInfo(
        name="PRISMA with Duplicates",
        description="PRISMA flow with duplicate removal step",
        diagram_type="prisma",
        required_fields=[
            "database_records",
            "additional_records",
            "after_duplicates",
            "screened",
            "excluded_screening",
            "full_text",
            "excluded_full_text",
            "included",
        ],
        optional_fields=[],
        example_output="flowchart TD\n    A[Records from databases...] --> ...",
    ),
    # Process flow templates
    "simple_flowchart_td": TemplateInfo(
        name="Simple Flowchart (Top-Down)",
        description="Basic top-to-bottom flowchart with custom nodes and connections",
        diagram_type="flowchart",
        required_fields=["nodes", "connections"],
        optional_fields=[],
        example_output="flowchart TD\n    A[Start]\n    A --> B",
    ),
    "simple_flowchart_lr": TemplateInfo(
        name="Simple Flowchart (Left-Right)",
        description="Basic left-to-right flowchart with custom nodes and connections",
        diagram_type="flowchart",
        required_fields=["nodes", "connections"],
        optional_fields=[],
        example_output="flowchart LR\n    A[Start]\n    A --> B",
    ),
    "simple_flowchart_bt": TemplateInfo(
        name="Simple Flowchart (Bottom-Top)",
        description="Basic bottom-to-top flowchart with custom nodes and connections",
        diagram_type="flowchart",
        required_fields=["nodes", "connections"],
        optional_fields=[],
        example_output="flowchart BT\n    A[Start]\n    A --> B",
    ),
    "simple_flowchart_rl": TemplateInfo(
        name="Simple Flowchart (Right-Left)",
        description="Basic right-to-left flowchart with custom nodes and connections",
        diagram_type="flowchart",
        required_fields=["nodes", "connections"],
        optional_fields=[],
        example_output="flowchart RL\n    A[Start]\n    A --> B",
    ),
    "methods_pipeline": TemplateInfo(
        name="Methods Pipeline",
        description="Linear pipeline for methods section with subgraphs",
        diagram_type="methods_flowchart",
        required_fields=[
            "input_label",
            "step1_label",
            "step2_label",
            "step3_label",
            "output_label",
        ],
        optional_fields=[],
        example_output="flowchart LR\n    subgraph Input...",
    ),
    "data_processing_pipeline": TemplateInfo(
        name="Data Processing Pipeline",
        description="Data processing workflow with labeled subgraphs",
        diagram_type="methods_flowchart",
        required_fields=["source", "preprocess", "analysis", "results"],
        optional_fields=[],
        example_output="flowchart LR\n    subgraph Collection...",
    ),
    # Sequence diagram templates
    "sequence_basic": TemplateInfo(
        name="Sequence Diagram (2 Participants)",
        description="Basic sequence diagram with two participants",
        diagram_type="sequence",
        required_fields=["participant1", "participant2", "interactions"],
        optional_fields=[],
        example_output="sequenceDiagram\n    participant A\n    participant B",
    ),
    "sequence_three_party": TemplateInfo(
        name="Sequence Diagram (3 Participants)",
        description="Sequence diagram with three participants",
        diagram_type="sequence",
        required_fields=[
            "participant1",
            "participant2",
            "participant3",
            "interactions",
        ],
        optional_fields=[],
        example_output="sequenceDiagram\n    participant A\n    participant B\n    participant C",
    ),
    "api_sequence": TemplateInfo(
        name="API Sequence",
        description="Client-API-Database sequence pattern",
        diagram_type="sequence",
        required_fields=["request_label", "response_label"],
        optional_fields=[],
        example_output="sequenceDiagram\n    Client->>API: Request",
    ),
    # State diagram templates
    "state_machine_basic": TemplateInfo(
        name="State Machine (Basic)",
        description="Simple state machine with initial and final states",
        diagram_type="state",
        required_fields=["initial_state", "transitions", "final_state"],
        optional_fields=[],
        example_output="stateDiagram-v2\n    [*] --> Idle",
    ),
    "state_machine_with_notes": TemplateInfo(
        name="State Machine with Notes",
        description="State machine with annotation notes",
        diagram_type="state",
        required_fields=[
            "initial_state",
            "transitions",
            "final_state",
            "initial_note",
            "final_note",
        ],
        optional_fields=[],
        example_output="stateDiagram-v2\n    [*] --> Idle\n    note right of Idle: ...",
    ),
    # Class/ER diagram templates
    "class_diagram_basic": TemplateInfo(
        name="Class Diagram",
        description="UML class diagram with classes and relationships",
        diagram_type="class",
        required_fields=["class_definitions", "relationships"],
        optional_fields=[],
        example_output="classDiagram\n    class Animal { ... }",
    ),
    "er_diagram_basic": TemplateInfo(
        name="ER Diagram",
        description="Entity-relationship diagram",
        diagram_type="er",
        required_fields=["entities", "relationships"],
        optional_fields=[],
        example_output="erDiagram\n    CUSTOMER ||--o{ ORDER : places",
    ),
    # Timeline templates
    "timeline_basic": TemplateInfo(
        name="Timeline (Basic)",
        description="Simple timeline with title and events",
        diagram_type="timeline",
        required_fields=["title", "events"],
        optional_fields=[],
        example_output="timeline\n    title Project\n    2024 : Start",
    ),
    "study_timeline": TemplateInfo(
        name="Study Timeline",
        description="Clinical study timeline with phases",
        diagram_type="timeline",
        required_fields=[
            "study_name",
            "enrollment_start",
            "enrollment_desc",
            "treatment_start",
            "treatment_desc",
            "followup_start",
            "followup_desc",
            "analysis_start",
            "analysis_desc",
        ],
        optional_fields=[],
        example_output="timeline\n    title Study\n    section Enrollment...",
    ),
    # Decision/branching templates
    "decision_tree": TemplateInfo(
        name="Decision Tree",
        description="Binary decision tree with outcomes",
        diagram_type="decision",
        required_fields=[
            "start_label",
            "decision1",
            "yes_label",
            "no_label",
            "outcome1",
            "decision2",
            "outcome2",
            "outcome3",
        ],
        optional_fields=[],
        example_output="flowchart TD\n    A[Start] --> B{Decision}",
    ),
    "algorithm_flowchart": TemplateInfo(
        name="Algorithm Flowchart",
        description="Standard algorithm flowchart with I/O shapes",
        diagram_type="decision",
        required_fields=[
            "input_label",
            "process_label",
            "decision_label",
            "output_yes",
            "output_no",
        ],
        optional_fields=[],
        example_output="flowchart TD\n    START([Start]) --> INPUT[/Input/]",
    ),
    # Chart templates
    "pie_chart": TemplateInfo(
        name="Pie Chart",
        description="Pie chart with title and segments",
        diagram_type="pie",
        required_fields=["title", "segments"],
        optional_fields=[],
        example_output='pie showData\n    title Distribution\n    "A" : 50',
    ),
    # Mindmap templates
    "mindmap_basic": TemplateInfo(
        name="Mind Map",
        description="Mind map with central topic and branches",
        diagram_type="mindmap",
        required_fields=["central_topic", "branches"],
        optional_fields=[],
        example_output="mindmap\n    root((Topic))\n        Branch1",
    ),
    # Block diagram templates
    "block_diagram": TemplateInfo(
        name="Block Diagram",
        description="Block diagram with column layout",
        diagram_type="block",
        required_fields=["num_columns", "blocks"],
        optional_fields=[],
        example_output="block-beta\n    columns 3\n    a b c",
    ),
}


def fill_template(template_name: str, **kwargs: Any) -> str:
    """Fill a Mermaid template with provided values.

    Args:
        template_name: Name of the template (e.g., "consort_basic")
        **kwargs: Values to fill into template placeholders

    Returns:
        Filled Mermaid diagram code

    Raises:
        KeyError: If template_name not found
        ValueError: If required placeholder is missing

    Example:
        >>> code = fill_template(
        ...     "consort_basic",
        ...     screened=100, excluded=30, randomized=70,
        ...     intervention=35, control=35,
        ...     analyzed_intervention=32, analyzed_control=33
        ... )
    """
    if template_name not in TEMPLATES:
        available = ", ".join(sorted(TEMPLATES.keys()))
        raise KeyError(f"Template '{template_name}' not found. Available: {available}")

    template = TEMPLATES[template_name]

    try:
        return template.format(**kwargs)
    except KeyError as e:
        raise ValueError(f"Missing required placeholder: {e}") from e


def get_template_for_type(
    diagram_type: str,
    variant: Literal["basic", "detailed"] = "basic",
) -> str | None:
    """Get the appropriate template name for a diagram type.

    Args:
        diagram_type: Type of diagram (e.g., "consort", "flowchart")
        variant: "basic" or "detailed" version

    Returns:
        Template name if found, None otherwise

    Example:
        >>> template_name = get_template_for_type("consort")
        >>> template_name
        'consort_basic'
    """
    diagram_type_lower = diagram_type.lower()

    # Check direct mapping
    if diagram_type_lower in DIAGRAM_TYPE_TO_TEMPLATES:
        templates = DIAGRAM_TYPE_TO_TEMPLATES[diagram_type_lower]
        if variant == "basic":
            return templates[0]
        elif len(templates) > 1:
            return templates[1]
        return templates[0]

    # Check if exact template name was passed
    if diagram_type_lower in TEMPLATES:
        return diagram_type_lower

    return None


def get_template(template_name: str) -> str | None:
    """Get a template by exact name.

    Args:
        template_name: Exact template name

    Returns:
        Template string if found, None otherwise
    """
    return TEMPLATES.get(template_name)


def list_templates() -> list[str]:
    """Get list of all available template names.

    Returns:
        Sorted list of template names
    """
    return sorted(TEMPLATES.keys())


def list_diagram_types() -> list[str]:
    """Get list of supported diagram types.

    Returns:
        Sorted list of diagram type names
    """
    return sorted(DIAGRAM_TYPE_TO_TEMPLATES.keys())


def get_template_metadata(template_name: str) -> TemplateInfo | None:
    """Get metadata for a template.

    Args:
        template_name: Name of the template

    Returns:
        TemplateInfo if found, None otherwise
    """
    return TEMPLATE_METADATA.get(template_name)


def get_required_fields(template_name: str) -> list[str]:
    """Extract required placeholder fields from a template.

    Args:
        template_name: Name of the template

    Returns:
        List of required field names

    Example:
        >>> fields = get_required_fields("consort_basic")
        >>> 'screened' in fields
        True
    """
    import re

    template = TEMPLATES.get(template_name, "")
    # Find all {placeholder} patterns, excluding {{ and }}
    # which are escaped braces in Mermaid
    placeholders = re.findall(r"\{([a-z_][a-z0-9_]*)\}", template)
    return list(set(placeholders))


def validate_template_data(
    template_name: str,
    data: dict[str, Any],
) -> tuple[bool, list[str]]:
    """Validate that all required fields are present for a template.

    Args:
        template_name: Name of the template
        data: Dictionary of field values

    Returns:
        Tuple of (is_valid, list of missing fields)

    Example:
        >>> valid, missing = validate_template_data(
        ...     "consort_basic",
        ...     {"screened": 100}  # Missing other fields
        ... )
        >>> valid
        False
        >>> "excluded" in missing
        True
    """
    required = get_required_fields(template_name)
    missing = [field for field in required if field not in data]
    return len(missing) == 0, missing


def build_nodes_string(
    nodes: list[dict[str, str]],
    indent: str = "    ",
) -> str:
    """Build Mermaid nodes string from a list of node definitions.

    Args:
        nodes: List of dicts with 'id' and 'label' keys
        indent: Indentation string (default 4 spaces)

    Returns:
        Formatted node definitions string

    Example:
        >>> nodes = [
        ...     {"id": "A", "label": "Start"},
        ...     {"id": "B", "label": "Process"},
        ... ]
        >>> print(build_nodes_string(nodes))
            A[Start]
            B[Process]
    """
    lines = []
    for node in nodes:
        node_id = node.get("id", "")
        label = node.get("label", "")
        shape = node.get("shape", "rect")

        if shape == "rect":
            lines.append(f"{indent}{node_id}[{label}]")
        elif shape == "rounded":
            lines.append(f"{indent}{node_id}({label})")
        elif shape == "diamond":
            lines.append(f"{indent}{node_id}{{{{{label}}}}}")
        elif shape == "circle":
            lines.append(f"{indent}{node_id}(({label}))")
        elif shape == "stadium":
            lines.append(f"{indent}{node_id}([{label}])")
        else:
            lines.append(f"{indent}{node_id}[{label}]")

    return "\n".join(lines)


# Mermaid edge forms, keyed by the arrow-legend channel each one encodes.
# See "Canonical Arrow Legend" in ../../references/best_practices.md:
#   solid  (-->)  Activation / direct positive effect. THE DEFAULT: emitted
#                 whenever a connection does not explicitly declare a style.
#   dashed (-.->) "Indirect, hypothetical, or context-dependent effect" -- the
#                 canonical meaning of dashed in mechanism and pathway diagrams.
#   thick  (==>)  "Ordinal magnitude of one relationship (e.g. dominant vs minor
#                 flux) - legend-declared only".
# Each value is (plain_arrow, label_open, label_close); labelled forms follow
# Mermaid's documented syntax per link type (A -->|t| B, A -. t .-> B,
# A == t ==> B).
EDGE_STYLES: dict[str, tuple[str, str, str]] = {
    "solid": ("-->", "-->|", "|"),
    "dashed": ("-.->", "-. ", " .->"),
    "thick": ("==>", "== ", " ==>"),
}

# Convenience aliases; each resolves to a key of EDGE_STYLES. Names come from
# the canonical legend's own vocabulary so callers can declare meaning rather
# than glyphs.
#
# CAVEAT on "dotted": Mermaid has no dotted link distinct from its dashed one,
# so both collapse onto `-.->`. Elsewhere in this library dotted and dashed ARE
# distinct (matplotlib LineStyle DOTTED=":" vs DASHED="--"), where they serve as
# separate categorical series identifiers in data plots. In a Mermaid mechanism
# or pathway diagram there is only one non-solid path, and it carries the
# canonical meaning "indirect / hypothetical / context-dependent" -- so a caller
# reaching for "dotted" as a third series identifier will instead assert that
# canonical meaning. Use a data-plot renderer, not Mermaid, when you need three
# distinguishable categorical line styles.
EDGE_STYLE_ALIASES: dict[str, str] = {
    "direct": "solid",
    "dotted": "dashed",
    "indirect": "dashed",
    "hypothetical": "dashed",
    "bold": "thick",
}


def resolve_edge_style(style: str | None = None) -> tuple[str, str, str]:
    """Resolve an edge style name to its Mermaid edge form.

    Args:
        style: Style name or alias. None / "" resolves to "solid" (the default).

    Returns:
        Tuple of (plain_arrow, label_open, label_close)

    Raises:
        ValueError: If the style is not a known style or alias. Unknown styles
            are rejected rather than silently downgraded, because an undeclared
            edge channel is a defect, not a style choice.

    Example:
        >>> resolve_edge_style()[0]
        '-->'
        >>> resolve_edge_style("dashed")[0]
        '-.->'
        >>> resolve_edge_style("thick")[0]
        '==>'
    """
    key = (style or "solid").strip().lower()
    key = EDGE_STYLE_ALIASES.get(key, key)
    if key not in EDGE_STYLES:
        valid = ", ".join(sorted(EDGE_STYLES))
        aliases = ", ".join(sorted(EDGE_STYLE_ALIASES))
        raise ValueError(
            f"Unknown edge style {style!r}. Valid styles: {valid} (aliases: {aliases})"
        )
    return EDGE_STYLES[key]


def build_connections_string(
    connections: list[dict[str, str]],
    indent: str = "    ",
) -> str:
    """Build Mermaid connections string from a list of connection definitions.

    Args:
        connections: List of dicts with 'from', 'to', and optional 'label' and
            'style' keys. 'style' is optional and defaults to "solid" (-->);
            "dashed" (-.->) marks an indirect, hypothetical, or
            context-dependent effect, and "thick" (==>) carries
            legend-declared ordinal magnitude. See EDGE_STYLES.
        indent: Indentation string (default 4 spaces)

    Returns:
        Formatted connections string

    Example:
        >>> conns = [
        ...     {"from": "A", "to": "B", "label": "yes"},
        ...     {"from": "A", "to": "C", "label": "no"},
        ... ]
        >>> print(build_connections_string(conns))
            A -->|yes| B
            A -->|no| C

        >>> conns = [
        ...     {"from": "A", "to": "B"},
        ...     {"from": "B", "to": "C", "style": "dashed"},
        ...     {"from": "C", "to": "D", "style": "thick", "label": "major"},
        ... ]
        >>> print(build_connections_string(conns))
            A --> B
            B -.-> C
            C == major ==> D
    """
    lines = []
    for conn in connections:
        from_node = conn.get("from", "")
        to_node = conn.get("to", "")
        label = conn.get("label", "")
        arrow, label_open, label_close = resolve_edge_style(conn.get("style"))

        if label:
            lines.append(
                f"{indent}{from_node} {label_open}{label}{label_close} {to_node}"
            )
        else:
            lines.append(f"{indent}{from_node} {arrow} {to_node}")

    return "\n".join(lines)


def build_flowchart(
    nodes: list[dict[str, str]],
    connections: list[dict[str, str]],
    direction: Literal["TD", "LR", "BT", "RL"] = "TD",
) -> str:
    """Build a complete flowchart from nodes and connections.

    Args:
        nodes: List of node definitions
        connections: List of connection definitions
        direction: Flow direction (TD=top-down, LR=left-right, etc.)

    Returns:
        Complete Mermaid flowchart code

    Example:
        >>> code = build_flowchart(
        ...     nodes=[{"id": "A", "label": "Start"}, {"id": "B", "label": "End"}],
        ...     connections=[{"from": "A", "to": "B"}],
        ...     direction="TD"
        ... )
    """
    nodes_str = build_nodes_string(nodes)
    conns_str = build_connections_string(connections)

    return fill_template(
        f"simple_flowchart_{direction.lower()}",
        nodes=nodes_str,
        connections=conns_str,
    )
