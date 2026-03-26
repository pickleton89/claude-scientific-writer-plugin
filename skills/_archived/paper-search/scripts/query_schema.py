#!/usr/bin/env python3
"""
Structured Query Schema for Academic Paper Search

Provides deterministic query specification through structured input,
eliminating variance from free-form query interpretation.

Usage:
    from query_schema import StructuredQuery, load_query_from_json

    # Programmatic query construction
    query = StructuredQuery(
        concepts=["CRISPR", "gene therapy"],
        operator="AND",
        synonyms={"CRISPR": ["CRISPR-Cas9", "CRISPR/Cas9"]},
        field_constraints={"author": "Doudna JA"},
        date_range={"start": "2020", "end": "2024"}
    )

    # Convert to database-specific query
    pubmed_query = query.to_pubmed_query()
    semantic_query = query.to_semantic_query()

    # Load from JSON file
    query = load_query_from_json("search_spec.json")
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import json
from pathlib import Path


@dataclass
class StructuredQuery:
    """
    Deterministic query specification.

    Attributes:
        concepts: Required search terms/concepts
        operator: Boolean operator between concepts ("AND" or "OR")
        synonyms: Term expansions as {term: [synonyms]}
        field_constraints: Field-specific filters as {field: value}
        date_range: Date filter as {"start": str, "end": str}
        publication_types: List of publication types (PubMed)
        fields_of_study: List of fields (Semantic Scholar)
        min_citations: Minimum citation count filter
        open_access: Filter for open access only
        exclude_terms: Terms to exclude from results
    """
    concepts: List[str]
    operator: str = "AND"
    synonyms: Optional[Dict[str, List[str]]] = None
    field_constraints: Optional[Dict[str, str]] = None
    date_range: Optional[Dict[str, str]] = None
    publication_types: Optional[List[str]] = None
    fields_of_study: Optional[List[str]] = None
    min_citations: Optional[int] = None
    open_access: bool = False
    exclude_terms: Optional[List[str]] = None

    def __post_init__(self):
        """Validate and normalize inputs."""
        # Normalize operator
        self.operator = self.operator.upper()
        if self.operator not in ("AND", "OR"):
            raise ValueError(f"Invalid operator: {self.operator}. Must be 'AND' or 'OR'")

        # Validate concepts
        if not self.concepts:
            raise ValueError("At least one concept is required")

        # Normalize field constraints keys
        if self.field_constraints:
            self.field_constraints = {
                k.lower(): v for k, v in self.field_constraints.items()
            }

    def _expand_concept(self, concept: str) -> str:
        """Expand a concept with its synonyms."""
        if self.synonyms and concept in self.synonyms:
            all_terms = [concept] + self.synonyms[concept]
            # Quote terms with spaces
            quoted_terms = [
                f'"{t}"' if ' ' in t else t for t in all_terms
            ]
            return f"({' OR '.join(quoted_terms)})"
        return f'"{concept}"' if ' ' in concept else concept

    def to_pubmed_query(self) -> str:
        """
        Convert to PubMed query syntax.

        Returns:
            PubMed-compatible query string

        Example:
            >>> q = StructuredQuery(concepts=["CRISPR", "therapy"], operator="AND")
            >>> q.to_pubmed_query()
            'CRISPR AND therapy'
        """
        # Expand concepts with synonyms
        parts = [self._expand_concept(c) for c in self.concepts]
        query = f" {self.operator} ".join(parts)

        # Add field constraints
        if self.field_constraints:
            field_mapping = {
                "author": "Author",
                "title": "Title",
                "abstract": "Abstract",
                "journal": "Journal",
                "affiliation": "Affiliation",
                "mesh": "MeSH Terms",
            }
            for field_key, value in self.field_constraints.items():
                pubmed_field = field_mapping.get(field_key, field_key.title())
                query += f" AND {value}[{pubmed_field}]"

        # Add date range
        if self.date_range:
            start = self.date_range.get("start", "1900")
            end = self.date_range.get("end", "3000")
            # Normalize date format for PubMed (YYYY/MM/DD)
            start = start.replace("-", "/")
            end = end.replace("-", "/")
            query += f" AND {start}:{end}[Publication Date]"

        # Add publication types
        if self.publication_types:
            type_clauses = [f"{pt}[Publication Type]" for pt in self.publication_types]
            query += f" AND ({' OR '.join(type_clauses)})"

        # Add exclusions
        if self.exclude_terms:
            for term in self.exclude_terms:
                query += f" NOT {term}"

        return query

    def to_semantic_query(self) -> str:
        """
        Convert to Semantic Scholar query syntax.

        Returns:
            Semantic Scholar compatible query string

        Note:
            Semantic Scholar uses simpler query syntax than PubMed.
            Field constraints and publication types are handled via API parameters.
        """
        # Expand concepts with synonyms
        parts = [self._expand_concept(c) for c in self.concepts]
        query = f" {self.operator} ".join(parts)

        # Add exclusions (using -)
        if self.exclude_terms:
            for term in self.exclude_terms:
                query += f" -{term}"

        return query

    def to_biorxiv_query(self) -> str:
        """
        Convert to bioRxiv query syntax.

        Returns:
            bioRxiv compatible query string

        Note:
            bioRxiv uses simple text matching, similar to Semantic Scholar.
        """
        # bioRxiv uses simple query syntax
        parts = [self._expand_concept(c) for c in self.concepts]
        query = f" {self.operator} ".join(parts)

        # Add exclusions
        if self.exclude_terms:
            for term in self.exclude_terms:
                query += f" -{term}"

        return query

    def get_api_params(self, source: str) -> Dict[str, Any]:
        """
        Get API parameters for a specific source.

        Args:
            source: Database source (pubmed, semantic, biorxiv)

        Returns:
            Dictionary of API parameters
        """
        params: Dict[str, Any] = {}

        if source == "semantic":
            if self.fields_of_study:
                params["fields_of_study"] = self.fields_of_study
            if self.min_citations is not None:
                params["min_citations"] = self.min_citations
            if self.open_access:
                params["open_access"] = True
            if self.date_range:
                if self.date_range.get("start"):
                    params["year_start"] = int(self.date_range["start"][:4])
                if self.date_range.get("end"):
                    params["year_end"] = int(self.date_range["end"][:4])

        elif source == "pubmed":
            if self.publication_types:
                params["publication_types"] = self.publication_types
            if self.date_range:
                params["date_start"] = self.date_range.get("start")
                params["date_end"] = self.date_range.get("end")

        elif source in ("biorxiv", "medrxiv"):
            if self.date_range:
                start = self.date_range.get("start", "")
                end = self.date_range.get("end", "")
                # Ensure YYYY-MM-DD format
                if start and len(start) == 4:
                    start = f"{start}-01-01"
                if end and len(end) == 4:
                    end = f"{end}-12-31"
                params["date_start"] = start
                params["date_end"] = end

        return params

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "concepts": self.concepts,
            "operator": self.operator,
        }
        if self.synonyms:
            result["synonyms"] = self.synonyms
        if self.field_constraints:
            result["field_constraints"] = self.field_constraints
        if self.date_range:
            result["date_range"] = self.date_range
        if self.publication_types:
            result["publication_types"] = self.publication_types
        if self.fields_of_study:
            result["fields_of_study"] = self.fields_of_study
        if self.min_citations is not None:
            result["min_citations"] = self.min_citations
        if self.open_access:
            result["open_access"] = self.open_access
        if self.exclude_terms:
            result["exclude_terms"] = self.exclude_terms
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StructuredQuery":
        """Create from dictionary."""
        return cls(
            concepts=data["concepts"],
            operator=data.get("operator", "AND"),
            synonyms=data.get("synonyms"),
            field_constraints=data.get("field_constraints"),
            date_range=data.get("date_range"),
            publication_types=data.get("publication_types"),
            fields_of_study=data.get("fields_of_study"),
            min_citations=data.get("min_citations"),
            open_access=data.get("open_access", False),
            exclude_terms=data.get("exclude_terms"),
        )


def load_query_from_json(filepath: str) -> StructuredQuery:
    """
    Load a structured query from a JSON file.

    Args:
        filepath: Path to JSON file

    Returns:
        StructuredQuery instance

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If JSON is invalid or missing required fields
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Query file not found: {filepath}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return StructuredQuery.from_dict(data)


def load_query_from_string(json_string: str) -> StructuredQuery:
    """
    Load a structured query from a JSON string.

    Args:
        json_string: JSON string

    Returns:
        StructuredQuery instance

    Raises:
        ValueError: If JSON is invalid or missing required fields
    """
    data = json.loads(json_string)
    return StructuredQuery.from_dict(data)


def validate_query_schema(data: Dict[str, Any]) -> tuple:
    """
    Validate a query specification dictionary.

    Args:
        data: Dictionary to validate

    Returns:
        Tuple of (is_valid: bool, errors: List[str])
    """
    errors = []

    # Required fields
    if "concepts" not in data:
        errors.append("Missing required field: 'concepts'")
    elif not isinstance(data["concepts"], list):
        errors.append("'concepts' must be a list")
    elif len(data["concepts"]) == 0:
        errors.append("'concepts' must contain at least one term")

    # Operator validation
    if "operator" in data:
        if data["operator"].upper() not in ("AND", "OR"):
            errors.append("'operator' must be 'AND' or 'OR'")

    # Synonyms validation
    if "synonyms" in data:
        if not isinstance(data["synonyms"], dict):
            errors.append("'synonyms' must be a dictionary")
        else:
            for key, value in data["synonyms"].items():
                if not isinstance(value, list):
                    errors.append(f"Synonyms for '{key}' must be a list")

    # Field constraints validation
    if "field_constraints" in data:
        if not isinstance(data["field_constraints"], dict):
            errors.append("'field_constraints' must be a dictionary")

    # Date range validation
    if "date_range" in data:
        if not isinstance(data["date_range"], dict):
            errors.append("'date_range' must be a dictionary")
        else:
            for key in data["date_range"]:
                if key not in ("start", "end"):
                    errors.append(f"Unknown date_range key: '{key}'")

    # Publication types validation
    if "publication_types" in data:
        if not isinstance(data["publication_types"], list):
            errors.append("'publication_types' must be a list")

    # Fields of study validation
    if "fields_of_study" in data:
        if not isinstance(data["fields_of_study"], list):
            errors.append("'fields_of_study' must be a list")

    # Min citations validation
    if "min_citations" in data:
        if not isinstance(data["min_citations"], int) or data["min_citations"] < 0:
            errors.append("'min_citations' must be a non-negative integer")

    # Open access validation
    if "open_access" in data:
        if not isinstance(data["open_access"], bool):
            errors.append("'open_access' must be a boolean")

    # Exclude terms validation
    if "exclude_terms" in data:
        if not isinstance(data["exclude_terms"], list):
            errors.append("'exclude_terms' must be a list")

    return len(errors) == 0, errors


# Example query schemas for documentation
EXAMPLE_SCHEMAS = {
    "basic": {
        "concepts": ["CRISPR", "gene therapy"],
        "operator": "AND"
    },
    "with_synonyms": {
        "concepts": ["TP53", "cancer"],
        "operator": "AND",
        "synonyms": {
            "TP53": ["p53", "tumor protein p53"]
        }
    },
    "with_filters": {
        "concepts": ["immunotherapy", "melanoma"],
        "operator": "AND",
        "field_constraints": {
            "author": "Ribas A"
        },
        "date_range": {
            "start": "2020",
            "end": "2024"
        },
        "publication_types": ["Review"]
    },
    "comprehensive": {
        "concepts": ["machine learning", "drug discovery"],
        "operator": "AND",
        "synonyms": {
            "machine learning": ["ML", "deep learning", "artificial intelligence"]
        },
        "date_range": {
            "start": "2022",
            "end": "2024"
        },
        "fields_of_study": ["Medicine", "Computer Science"],
        "min_citations": 10,
        "open_access": True,
        "exclude_terms": ["review", "survey"]
    }
}


def get_example_schema(name: str) -> Optional[Dict[str, Any]]:
    """Get an example schema by name."""
    return EXAMPLE_SCHEMAS.get(name)


def list_example_schemas() -> List[str]:
    """List available example schema names."""
    return list(EXAMPLE_SCHEMAS.keys())


# CLI support
if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Structured Query Schema for Paper Search",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Validate schema
    validate_parser = subparsers.add_parser("validate", help="Validate a query JSON file")
    validate_parser.add_argument("file", help="JSON file to validate")

    # Convert to query
    convert_parser = subparsers.add_parser("convert", help="Convert schema to query string")
    convert_parser.add_argument("file", help="JSON file to convert")
    convert_parser.add_argument(
        "--source", "-s",
        choices=["pubmed", "semantic", "biorxiv"],
        default="pubmed",
        help="Target database"
    )

    # Show examples
    examples_parser = subparsers.add_parser("examples", help="Show example schemas")
    examples_parser.add_argument(
        "name",
        nargs="?",
        choices=list_example_schemas(),
        help="Example name (omit for list)"
    )

    args = parser.parse_args()

    if args.command == "validate":
        try:
            with open(args.file, "r") as f:
                data = json.load(f)
            is_valid, errors = validate_query_schema(data)
            if is_valid:
                print(f"Valid query schema: {args.file}")
                # Also try to construct the query
                query = StructuredQuery.from_dict(data)
                print(f"PubMed query: {query.to_pubmed_query()}")
            else:
                print(f"Invalid schema: {args.file}")
                for error in errors:
                    print(f"  - {error}")
                sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}")
            sys.exit(1)
        except FileNotFoundError:
            print(f"File not found: {args.file}")
            sys.exit(1)

    elif args.command == "convert":
        try:
            query = load_query_from_json(args.file)
            if args.source == "pubmed":
                print(query.to_pubmed_query())
            elif args.source == "semantic":
                print(query.to_semantic_query())
            elif args.source == "biorxiv":
                print(query.to_biorxiv_query())

            # Also show API params
            params = query.get_api_params(args.source)
            if params:
                print(f"\nAPI parameters: {json.dumps(params, indent=2)}")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif args.command == "examples":
        if args.name:
            schema = get_example_schema(args.name)
            print(json.dumps(schema, indent=2))
        else:
            print("Available example schemas:")
            for name in list_example_schemas():
                print(f"  - {name}")
            print("\nUse 'examples <name>' to see a specific schema")

    else:
        parser.print_help()
