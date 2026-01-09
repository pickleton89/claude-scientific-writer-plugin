#!/usr/bin/env python3
"""
Query Template Library for Academic Paper Search

Provides deterministic query construction from predefined templates,
reducing variance from free-form LLM query generation.

Usage:
    from query_templates import build_query, list_templates, get_template_info

    # Build a query from template
    query = build_query("review_search", topic="CRISPR gene therapy")

    # List available templates
    templates = list_templates()

    # Get template details
    info = get_template_info("author_papers")
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set
import re


@dataclass(frozen=True)
class QueryTemplate:
    """Immutable query template specification."""
    name: str
    pattern: str
    description: str
    required_params: tuple  # Immutable tuple instead of list
    optional_params: tuple = ()
    example: str = ""
    recommended_sources: tuple = ("pubmed",)


# Core query templates for common search patterns
QUERY_TEMPLATES: Dict[str, QueryTemplate] = {
    # Basic search patterns
    "topic_search": QueryTemplate(
        name="topic_search",
        pattern="{topic}",
        description="Simple topic search without filters",
        required_params=("topic",),
        example='topic="CRISPR gene therapy"',
        recommended_sources=("pubmed", "semantic"),
    ),

    # Review and synthesis searches
    "review_search": QueryTemplate(
        name="review_search",
        pattern="{topic} AND Review[Publication Type]",
        description="Find review articles on a topic (PubMed)",
        required_params=("topic",),
        example='topic="CAR-T cell therapy"',
        recommended_sources=("pubmed",),
    ),

    "systematic_review": QueryTemplate(
        name="systematic_review",
        pattern='"{topic}" AND (systematic review[Title] OR meta-analysis[Title])',
        description="Find systematic reviews and meta-analyses",
        required_params=("topic",),
        example='topic="immunotherapy efficacy"',
        recommended_sources=("pubmed",),
    ),

    # Time-based searches
    "recent_advances": QueryTemplate(
        name="recent_advances",
        pattern="{topic} AND {year_start}:{year_end}[Publication Date]",
        description="Find recent papers on a topic within date range",
        required_params=("topic", "year_start", "year_end"),
        example='topic="AlphaFold", year_start="2022", year_end="2024"',
        recommended_sources=("pubmed", "biorxiv"),
    ),

    "landmark_papers": QueryTemplate(
        name="landmark_papers",
        pattern="{topic}",
        description="Find highly-cited landmark papers (use with --min-citations)",
        required_params=("topic",),
        optional_params=("min_citations",),
        example='topic="deep learning" (use with --min-citations 1000)',
        recommended_sources=("semantic",),
    ),

    # Author-based searches
    "author_papers": QueryTemplate(
        name="author_papers",
        pattern="{author}[Author]",
        description="Find all papers by a specific author",
        required_params=("author",),
        example='author="Doudna JA"',
        recommended_sources=("pubmed", "semantic"),
    ),

    "author_topic": QueryTemplate(
        name="author_topic",
        pattern="{author}[Author] AND {topic}",
        description="Find papers by author on specific topic",
        required_params=("author", "topic"),
        example='author="Zhang F", topic="CRISPR"',
        recommended_sources=("pubmed",),
    ),

    # Clinical research
    "clinical_trials": QueryTemplate(
        name="clinical_trials",
        pattern="{topic} AND Clinical Trial[Publication Type]",
        description="Find clinical trial publications",
        required_params=("topic",),
        example='topic="pembrolizumab melanoma"',
        recommended_sources=("pubmed",),
    ),

    "randomized_controlled": QueryTemplate(
        name="randomized_controlled",
        pattern="{topic} AND Randomized Controlled Trial[Publication Type]",
        description="Find RCT publications specifically",
        required_params=("topic",),
        example='topic="metformin diabetes"',
        recommended_sources=("pubmed",),
    ),

    # Gene and protein searches
    "gene_function": QueryTemplate(
        name="gene_function",
        pattern="({gene} OR {aliases}) AND (function OR role OR mechanism)",
        description="Find papers on gene/protein function",
        required_params=("gene",),
        optional_params=("aliases",),
        example='gene="TP53", aliases="p53"',
        recommended_sources=("pubmed",),
    ),

    "gene_disease": QueryTemplate(
        name="gene_disease",
        pattern="({gene} OR {aliases}) AND {disease}",
        description="Find papers linking gene to disease",
        required_params=("gene", "disease"),
        optional_params=("aliases",),
        example='gene="BRCA1", disease="breast cancer"',
        recommended_sources=("pubmed",),
    ),

    # Drug and therapy searches
    "drug_target": QueryTemplate(
        name="drug_target",
        pattern="{drug} AND {target} AND (mechanism OR pathway OR binding)",
        description="Find papers on drug-target interactions",
        required_params=("drug", "target"),
        example='drug="imatinib", target="BCR-ABL"',
        recommended_sources=("pubmed",),
    ),

    "drug_comparison": QueryTemplate(
        name="drug_comparison",
        pattern="({drug1} AND {drug2}) AND (comparison OR versus OR efficacy)",
        description="Find comparative studies between drugs",
        required_params=("drug1", "drug2"),
        example='drug1="nivolumab", drug2="pembrolizumab"',
        recommended_sources=("pubmed",),
    ),

    # Methods and techniques
    "method_application": QueryTemplate(
        name="method_application",
        pattern="{method} AND {application}",
        description="Find applications of a specific method",
        required_params=("method", "application"),
        example='method="single-cell RNA-seq", application="tumor heterogeneity"',
        recommended_sources=("pubmed", "biorxiv"),
    ),

    "protocol_method": QueryTemplate(
        name="protocol_method",
        pattern="{method} AND (protocol OR methods OR procedure)",
        description="Find methodological papers and protocols",
        required_params=("method",),
        example='method="ChIP-seq"',
        recommended_sources=("pubmed",),
    ),

    # Preprint-focused
    "preprint_topic": QueryTemplate(
        name="preprint_topic",
        pattern="{topic}",
        description="Search preprints for cutting-edge research",
        required_params=("topic",),
        example='topic="cryo-EM structure"',
        recommended_sources=("biorxiv", "medrxiv"),
    ),

    # Cross-domain / AI
    "ml_biology": QueryTemplate(
        name="ml_biology",
        pattern="({ml_method} OR machine learning OR deep learning) AND {biology_topic}",
        description="Find ML/AI applications in biology",
        required_params=("biology_topic",),
        optional_params=("ml_method",),
        example='biology_topic="protein structure prediction", ml_method="transformer"',
        recommended_sources=("semantic", "biorxiv"),
    ),
}


class TemplateError(Exception):
    """Exception raised for template-related errors."""
    pass


def build_query(template_name: str, **kwargs) -> str:
    """
    Build a search query from a template with provided parameters.

    Args:
        template_name: Name of the template to use
        **kwargs: Parameter values to fill in the template

    Returns:
        Formatted query string ready for database search

    Raises:
        TemplateError: If template not found or required parameters missing

    Example:
        >>> build_query("review_search", topic="CRISPR")
        'CRISPR AND Review[Publication Type]'
    """
    if template_name not in QUERY_TEMPLATES:
        available = ", ".join(sorted(QUERY_TEMPLATES.keys()))
        raise TemplateError(
            f"Unknown template: '{template_name}'. "
            f"Available templates: {available}"
        )

    template = QUERY_TEMPLATES[template_name]

    # Check required parameters
    missing = [p for p in template.required_params if p not in kwargs]
    if missing:
        raise TemplateError(
            f"Missing required parameters for '{template_name}': {missing}. "
            f"Required: {list(template.required_params)}"
        )

    # Handle optional parameters with defaults
    params = dict(kwargs)
    for opt_param in template.optional_params:
        if opt_param not in params:
            # Provide sensible defaults for optional params
            if opt_param == "aliases":
                params[opt_param] = params.get("gene", "")
            elif opt_param == "ml_method":
                params[opt_param] = "machine learning"
            else:
                params[opt_param] = ""

    # Build the query
    try:
        query = template.pattern.format(**params)
    except KeyError as e:
        raise TemplateError(f"Missing parameter in template: {e}")

    # Clean up any empty OR clauses from optional params
    query = re.sub(r'\(\s*OR\s*\)', '', query)
    query = re.sub(r'\s+', ' ', query).strip()

    return query


def list_templates() -> List[str]:
    """
    Get list of all available template names.

    Returns:
        Sorted list of template names
    """
    return sorted(QUERY_TEMPLATES.keys())


def get_template_info(template_name: str) -> Optional[QueryTemplate]:
    """
    Get detailed information about a specific template.

    Args:
        template_name: Name of the template

    Returns:
        QueryTemplate object or None if not found
    """
    return QUERY_TEMPLATES.get(template_name)


def get_templates_for_source(source: str) -> List[str]:
    """
    Get templates recommended for a specific database source.

    Args:
        source: Database source (pubmed, semantic, biorxiv, etc.)

    Returns:
        List of template names recommended for that source
    """
    source_lower = source.lower()
    return [
        name for name, template in QUERY_TEMPLATES.items()
        if source_lower in template.recommended_sources
    ]


def format_template_help() -> str:
    """
    Generate formatted help text for all templates.

    Returns:
        Multi-line string describing all available templates
    """
    lines = ["Available Query Templates:", "=" * 50, ""]

    for name in sorted(QUERY_TEMPLATES.keys()):
        template = QUERY_TEMPLATES[name]
        lines.append(f"  {name}")
        lines.append(f"    {template.description}")
        lines.append(f"    Pattern: {template.pattern}")
        lines.append(f"    Required: {', '.join(template.required_params)}")
        if template.optional_params:
            lines.append(f"    Optional: {', '.join(template.optional_params)}")
        lines.append(f"    Example: {template.example}")
        lines.append(f"    Sources: {', '.join(template.recommended_sources)}")
        lines.append("")

    return "\n".join(lines)


def validate_template_params(template_name: str, params: Dict) -> tuple:
    """
    Validate parameters against a template without building the query.

    Args:
        template_name: Name of the template
        params: Dictionary of parameters to validate

    Returns:
        Tuple of (is_valid: bool, errors: List[str])
    """
    errors = []

    if template_name not in QUERY_TEMPLATES:
        return False, [f"Unknown template: {template_name}"]

    template = QUERY_TEMPLATES[template_name]

    # Check required parameters
    missing = [p for p in template.required_params if p not in params]
    if missing:
        errors.append(f"Missing required parameters: {missing}")

    # Check for unknown parameters
    all_known = set(template.required_params) | set(template.optional_params)
    unknown = [p for p in params if p not in all_known]
    if unknown:
        errors.append(f"Unknown parameters: {unknown}")

    return len(errors) == 0, errors


# CLI support
if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Query Template Library for Paper Search",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # List templates
    list_parser = subparsers.add_parser("list", help="List available templates")
    list_parser.add_argument(
        "--source", "-s",
        help="Filter by recommended source (pubmed, semantic, biorxiv)"
    )

    # Show template details
    show_parser = subparsers.add_parser("show", help="Show template details")
    show_parser.add_argument("template", help="Template name")

    # Build query
    build_parser = subparsers.add_parser("build", help="Build a query from template")
    build_parser.add_argument("template", help="Template name")
    build_parser.add_argument(
        "params",
        nargs="*",
        help="Parameters as key=value pairs"
    )

    args = parser.parse_args()

    if args.command == "list":
        if args.source:
            templates = get_templates_for_source(args.source)
            print(f"Templates for {args.source}:")
        else:
            templates = list_templates()
            print("All templates:")
        for t in templates:
            info = get_template_info(t)
            print(f"  {t}: {info.description}")

    elif args.command == "show":
        info = get_template_info(args.template)
        if info:
            print(f"Template: {info.name}")
            print(f"Description: {info.description}")
            print(f"Pattern: {info.pattern}")
            print(f"Required: {', '.join(info.required_params)}")
            if info.optional_params:
                print(f"Optional: {', '.join(info.optional_params)}")
            print(f"Example: {info.example}")
            print(f"Recommended sources: {', '.join(info.recommended_sources)}")
        else:
            print(f"Template not found: {args.template}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "build":
        # Parse key=value params
        params = {}
        for p in args.params:
            if "=" in p:
                key, value = p.split("=", 1)
                params[key] = value
            else:
                print(f"Invalid parameter format: {p} (expected key=value)",
                      file=sys.stderr)
                sys.exit(1)

        try:
            query = build_query(args.template, **params)
            print(query)
        except TemplateError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    else:
        print(format_template_help())
