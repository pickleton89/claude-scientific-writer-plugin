#!/usr/bin/env python3
"""
Search Syntax Validator

Validates search query syntax for different academic databases.
Supports PubMed, Cochrane Library, Web of Science, Scopus, CINAHL,
PsycINFO, Embase, and IEEE Xplore.
"""

from dataclasses import dataclass, field
from typing import Literal, Optional, Any
import re
import json


# Type definitions
DatabaseType = Literal[
    "pubmed", "cochrane", "wos", "scopus", "cinahl",
    "psycinfo", "embase", "ieee", "semantic_scholar"
]

# Database-specific configurations
DATABASE_CONFIGS: dict[str, dict[str, Any]] = {
    "pubmed": {
        "name": "PubMed",
        "boolean_operators": ["AND", "OR", "NOT"],
        "field_tags": {
            "[tiab]": "Title/Abstract",
            "[ti]": "Title",
            "[ab]": "Abstract",
            "[mh]": "MeSH Terms",
            "[majr]": "MeSH Major Topic",
            "[pt]": "Publication Type",
            "[au]": "Author",
            "[ad]": "Affiliation",
            "[dp]": "Date of Publication",
            "[la]": "Language",
            "[sb]": "Subset",
            "[sh]": "Subheading",
            "[tw]": "Text Word",
        },
        "truncation": "*",
        "phrase_operator": '""',
        "proximity_supported": False,
        "case_sensitive_bool": True,
    },
    "cochrane": {
        "name": "Cochrane Library",
        "boolean_operators": ["AND", "OR", "NOT"],
        "field_tags": {
            ":ti": "Title",
            ":ab": "Abstract",
            ":ti,ab": "Title and Abstract",
            ":kw": "Keywords",
            ":au": "Author",
            ":so": "Source",
        },
        "truncation": "*",
        "phrase_operator": '""',
        "proximity_supported": True,
        "proximity_operator": "NEAR/",
        "case_sensitive_bool": True,
    },
    "wos": {
        "name": "Web of Science",
        "boolean_operators": ["AND", "OR", "NOT"],
        "field_tags": {
            "TS=": "Topic",
            "TI=": "Title",
            "AB=": "Abstract",
            "AU=": "Author",
            "SO=": "Source",
            "PY=": "Publication Year",
            "LA=": "Language",
            "DT=": "Document Type",
            "WC=": "Web of Science Category",
        },
        "truncation": "*",
        "phrase_operator": '""',
        "proximity_supported": True,
        "proximity_operator": "NEAR/",
        "case_sensitive_bool": True,
    },
    "scopus": {
        "name": "Scopus",
        "boolean_operators": ["AND", "OR", "AND NOT"],
        "field_tags": {
            "TITLE-ABS-KEY": "Title, Abstract, Keywords",
            "TITLE": "Title",
            "ABS": "Abstract",
            "KEY": "Keywords",
            "AUTH": "Author",
            "AFFIL": "Affiliation",
            "SRCTITLE": "Source Title",
            "PUBYEAR": "Publication Year",
        },
        "truncation": "*",
        "phrase_operator": '{}',
        "proximity_supported": True,
        "proximity_operator": "W/",
        "case_sensitive_bool": True,
    },
    "cinahl": {
        "name": "CINAHL",
        "boolean_operators": ["AND", "OR", "NOT"],
        "field_tags": {
            "TI": "Title",
            "AB": "Abstract",
            "MW": "Word in Subject Heading",
            "MH": "Exact Subject Heading",
            "AU": "Author",
            "SO": "Source",
        },
        "truncation": "*",
        "phrase_operator": '""',
        "proximity_supported": True,
        "proximity_operator": "N",
        "case_sensitive_bool": True,
    },
    "psycinfo": {
        "name": "PsycINFO",
        "boolean_operators": ["AND", "OR", "NOT"],
        "field_tags": {
            "TI": "Title",
            "AB": "Abstract",
            "DE": "Subjects",
            "ID": "Identifiers",
            "AU": "Author",
            "SO": "Source",
        },
        "truncation": "*",
        "phrase_operator": '""',
        "proximity_supported": True,
        "proximity_operator": "N",
        "case_sensitive_bool": True,
    },
    "embase": {
        "name": "Embase",
        "boolean_operators": ["AND", "OR", "NOT"],
        "field_tags": {
            ":ti": "Title",
            ":ab": "Abstract",
            ":ti,ab": "Title and Abstract",
            ":kw": "Keywords",
            ":au": "Author",
            "/exp": "Exploded term",
            "/mj": "Major focus",
        },
        "truncation": "*",
        "phrase_operator": "''",
        "proximity_supported": True,
        "proximity_operator": "NEAR/",
        "case_sensitive_bool": True,
    },
    "ieee": {
        "name": "IEEE Xplore",
        "boolean_operators": ["AND", "OR", "NOT"],
        "field_tags": {
            '"Document Title":': "Document Title",
            '"Abstract":': "Abstract",
            '"Author Keywords":': "Author Keywords",
            '"IEEE Terms":': "IEEE Terms",
            '"Authors":': "Authors",
        },
        "truncation": "*",
        "phrase_operator": '""',
        "proximity_supported": True,
        "proximity_operator": "ONEAR/",
        "case_sensitive_bool": True,
    },
    "semantic_scholar": {
        "name": "Semantic Scholar",
        "boolean_operators": ["+", "-", "|"],
        "field_tags": {},  # Limited field search
        "truncation": None,
        "phrase_operator": '""',
        "proximity_supported": False,
        "case_sensitive_bool": False,
    },
}


@dataclass
class ValidationIssue:
    """Individual validation issue."""

    severity: Literal["error", "warning", "info"]
    message: str
    position: Optional[int] = None
    suggestion: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "severity": self.severity,
            "message": self.message,
            "position": self.position,
            "suggestion": self.suggestion,
        }


@dataclass
class SearchQuery:
    """
    Search query with validation.

    Stores the query string, target database, and validation results.
    """

    query: str
    database: DatabaseType
    label: str = ""
    line_number: int = 0
    issues: list[ValidationIssue] = field(default_factory=list)

    def validate(self) -> list[ValidationIssue]:
        """
        Validate the search query for the target database.

        Returns list of validation issues found.
        """
        self.issues = []

        if not self.query or not self.query.strip():
            self.issues.append(
                ValidationIssue(
                    severity="error",
                    message="Query is empty",
                )
            )
            return self.issues

        config = DATABASE_CONFIGS.get(self.database)
        if not config:
            self.issues.append(
                ValidationIssue(
                    severity="error",
                    message=f"Unknown database: {self.database}",
                )
            )
            return self.issues

        # Run all validations
        self._check_parentheses_balance()
        self._check_quote_balance()
        self._check_boolean_operators(config)
        self._check_field_tags(config)
        self._check_truncation(config)
        self._check_common_errors()

        return self.issues

    def _check_parentheses_balance(self) -> None:
        """Check that parentheses are balanced."""
        count = 0
        for i, char in enumerate(self.query):
            if char == "(":
                count += 1
            elif char == ")":
                count -= 1
                if count < 0:
                    self.issues.append(
                        ValidationIssue(
                            severity="error",
                            message="Unmatched closing parenthesis",
                            position=i,
                            suggestion="Check parentheses balance",
                        )
                    )
                    return

        if count > 0:
            self.issues.append(
                ValidationIssue(
                    severity="error",
                    message=f"Missing {count} closing parenthesis(es)",
                    suggestion="Add closing parentheses",
                )
            )

    def _check_quote_balance(self) -> None:
        """Check that quotes are balanced."""
        # Count double quotes
        double_quotes = self.query.count('"')
        if double_quotes % 2 != 0:
            self.issues.append(
                ValidationIssue(
                    severity="error",
                    message="Unbalanced double quotes",
                    suggestion="Ensure all phrases are properly quoted",
                )
            )

        # Count single quotes (for Embase)
        if self.database == "embase":
            single_quotes = self.query.count("'")
            if single_quotes % 2 != 0:
                self.issues.append(
                    ValidationIssue(
                        severity="error",
                        message="Unbalanced single quotes",
                        suggestion="Ensure all phrases are properly quoted",
                    )
                )

    def _check_boolean_operators(self, config: dict) -> None:
        """Check Boolean operator usage."""
        query_upper = self.query.upper()

        # Check for lowercase Boolean operators (common error)
        if config.get("case_sensitive_bool", True):
            lowercase_pattern = r"\b(and|or|not)\b"
            matches = re.finditer(lowercase_pattern, self.query)
            for match in matches:
                self.issues.append(
                    ValidationIssue(
                        severity="error",
                        message=f"Boolean operator '{match.group()}' should be uppercase",
                        position=match.start(),
                        suggestion=f"Use '{match.group().upper()}' instead",
                    )
                )

        # Check for adjacent Boolean operators
        adj_pattern = r"\b(AND|OR|NOT)\s+(AND|OR|NOT)\b"
        adj_matches = re.finditer(adj_pattern, query_upper)
        for match in adj_matches:
            self.issues.append(
                ValidationIssue(
                    severity="error",
                    message=f"Adjacent Boolean operators: {match.group()}",
                    position=match.start(),
                    suggestion="Add search term between operators",
                )
            )

        # Check for Boolean at start (except NOT)
        start_pattern = r"^\s*(AND|OR)\b"
        if re.match(start_pattern, query_upper):
            self.issues.append(
                ValidationIssue(
                    severity="error",
                    message="Query cannot start with AND or OR",
                    position=0,
                    suggestion="Remove leading Boolean operator",
                )
            )

        # Check for Boolean at end
        end_pattern = r"\b(AND|OR|NOT)\s*$"
        if re.search(end_pattern, query_upper):
            self.issues.append(
                ValidationIssue(
                    severity="error",
                    message="Query cannot end with Boolean operator",
                    suggestion="Add search term after operator or remove it",
                )
            )

    def _check_field_tags(self, config: dict) -> None:
        """Check field tag usage."""
        field_tags = config.get("field_tags", {})

        if not field_tags:
            return

        # Database-specific field tag patterns
        if self.database == "pubmed":
            # Check for PubMed field tags
            tag_pattern = r"\[([a-z]+)\]"
            matches = re.finditer(tag_pattern, self.query)
            for match in matches:
                tag = f"[{match.group(1)}]"
                if tag not in field_tags:
                    self.issues.append(
                        ValidationIssue(
                            severity="warning",
                            message=f"Unknown PubMed field tag: {tag}",
                            position=match.start(),
                            suggestion=f"Valid tags: {', '.join(list(field_tags.keys())[:5])}...",
                        )
                    )

        elif self.database in ["cochrane", "embase"]:
            # Check for Ovid-style field tags
            tag_pattern = r":([a-z,]+)"
            matches = re.finditer(tag_pattern, self.query)
            for match in matches:
                tag = f":{match.group(1)}"
                if tag not in field_tags:
                    self.issues.append(
                        ValidationIssue(
                            severity="warning",
                            message=f"Unknown field tag: {tag}",
                            position=match.start(),
                            suggestion=f"Valid tags: {', '.join(list(field_tags.keys())[:5])}",
                        )
                    )

        elif self.database == "wos":
            # Check for Web of Science field tags
            tag_pattern = r"([A-Z]{2})="
            matches = re.finditer(tag_pattern, self.query)
            for match in matches:
                tag = f"{match.group(1)}="
                if tag not in field_tags:
                    self.issues.append(
                        ValidationIssue(
                            severity="warning",
                            message=f"Unknown Web of Science field tag: {tag}",
                            position=match.start(),
                            suggestion=f"Valid tags: {', '.join(list(field_tags.keys())[:5])}",
                        )
                    )

    def _check_truncation(self, config: dict) -> None:
        """Check truncation symbol usage."""
        truncation = config.get("truncation")

        if not truncation:
            # Database doesn't support truncation
            if "*" in self.query or "?" in self.query:
                self.issues.append(
                    ValidationIssue(
                        severity="warning",
                        message=f"{config['name']} may not support truncation symbols",
                        suggestion="Use full word forms",
                    )
                )
            return

        # Check for truncation on very short stems
        trunc_pattern = rf"(\b\w{{1,2}})\{truncation}"
        matches = re.finditer(trunc_pattern, self.query)
        for match in matches:
            self.issues.append(
                ValidationIssue(
                    severity="warning",
                    message=f"Very short truncation stem: '{match.group()}'",
                    position=match.start(),
                    suggestion="Short stems may retrieve too many irrelevant results",
                )
            )

    def _check_common_errors(self) -> None:
        """Check for common search errors."""
        # Check for multiple spaces
        if "  " in self.query:
            self.issues.append(
                ValidationIssue(
                    severity="info",
                    message="Multiple consecutive spaces found",
                    suggestion="Consider normalizing whitespace",
                )
            )

        # Check for very long unbroken strings (possible missing operators)
        words = self.query.split()
        for i, word in enumerate(words):
            # Skip if it contains operators or is quoted
            if word.upper() in ["AND", "OR", "NOT"]:
                continue
            # Check for potential missing operators between concepts
            if len(word) > 50:
                self.issues.append(
                    ValidationIssue(
                        severity="info",
                        message=f"Very long term found: '{word[:20]}...'",
                        suggestion="Check for missing spaces or operators",
                    )
                )

        # Check for empty parentheses
        if "()" in self.query:
            self.issues.append(
                ValidationIssue(
                    severity="error",
                    message="Empty parentheses found",
                    suggestion="Add search terms or remove empty parentheses",
                )
            )

    def is_valid(self) -> bool:
        """Check if query has no errors (warnings/info are OK)."""
        if not self.issues:
            self.validate()
        return not any(i.severity == "error" for i in self.issues)

    def get_errors(self) -> list[ValidationIssue]:
        """Get only error-level issues."""
        return [i for i in self.issues if i.severity == "error"]

    def get_warnings(self) -> list[ValidationIssue]:
        """Get only warning-level issues."""
        return [i for i in self.issues if i.severity == "warning"]

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "query": self.query,
            "database": self.database,
            "label": self.label,
            "line_number": self.line_number,
            "is_valid": self.is_valid(),
            "issues": [i.to_dict() for i in self.issues],
            "error_count": len(self.get_errors()),
            "warning_count": len(self.get_warnings()),
        }


@dataclass
class SearchStrategy:
    """
    Complete search strategy with multiple queries.

    Represents a full search strategy for a database with line numbering.
    """

    database: DatabaseType
    queries: list[SearchQuery] = field(default_factory=list)
    title: str = ""
    notes: str = ""

    def add_query(self, query_str: str, label: str = "") -> SearchQuery:
        """Add a query to the strategy."""
        line_number = len(self.queries) + 1
        query = SearchQuery(
            query=query_str,
            database=self.database,
            label=label,
            line_number=line_number,
        )
        self.queries.append(query)
        return query

    def validate_all(self) -> list[ValidationIssue]:
        """Validate all queries and return combined issues."""
        all_issues = []
        for query in self.queries:
            query.validate()
            for issue in query.issues:
                # Prefix issue message with line number
                prefixed_issue = ValidationIssue(
                    severity=issue.severity,
                    message=f"Line {query.line_number}: {issue.message}",
                    position=issue.position,
                    suggestion=issue.suggestion,
                )
                all_issues.append(prefixed_issue)
        return all_issues

    def is_valid(self) -> bool:
        """Check if all queries are valid."""
        self.validate_all()
        return all(q.is_valid() for q in self.queries)

    def get_summary(self) -> dict:
        """Get validation summary."""
        if not self.queries:
            return {
                "database": self.database,
                "total_queries": 0,
                "valid_queries": 0,
                "error_count": 0,
                "warning_count": 0,
            }

        self.validate_all()

        return {
            "database": self.database,
            "database_name": DATABASE_CONFIGS.get(self.database, {}).get("name", self.database),
            "title": self.title,
            "total_queries": len(self.queries),
            "valid_queries": sum(1 for q in self.queries if q.is_valid()),
            "error_count": sum(len(q.get_errors()) for q in self.queries),
            "warning_count": sum(len(q.get_warnings()) for q in self.queries),
        }

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "database": self.database,
            "title": self.title,
            "notes": self.notes,
            "queries": [q.to_dict() for q in self.queries],
            "summary": self.get_summary(),
        }


def validate_query(query: str, database: DatabaseType) -> dict:
    """
    Validate a single search query.

    Args:
        query: The search query string
        database: Target database type

    Returns:
        Dictionary with validation results
    """
    sq = SearchQuery(query=query, database=database)
    sq.validate()
    return sq.to_dict()


def parse_search_strategy(text: str, database: DatabaseType) -> SearchStrategy:
    """
    Parse a multi-line search strategy.

    Args:
        text: Multi-line search strategy text
        database: Target database

    Returns:
        SearchStrategy object with parsed queries
    """
    strategy = SearchStrategy(database=database)

    lines = text.strip().split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Skip comment lines (# followed by space or just #)
        # But preserve lines like "#1 AND #2" (line references)
        if line.startswith("# ") or line == "#":
            continue

        # Check for numbered line format (e.g., "1. query" or "#1 query")
        match = re.match(r"^(?:\d+\.\s*|#\d+\s+)?(.+)$", line)
        if match:
            query_text = match.group(1)
            strategy.add_query(query_text)

    return strategy


def get_database_info(database: DatabaseType) -> dict:
    """
    Get information about a database's search syntax.

    Args:
        database: Database type

    Returns:
        Dictionary with database configuration
    """
    config = DATABASE_CONFIGS.get(database, {})
    if not config:
        return {"error": f"Unknown database: {database}"}

    return {
        "database": database,
        "name": config.get("name", database),
        "boolean_operators": config.get("boolean_operators", []),
        "field_tags": config.get("field_tags", {}),
        "truncation_symbol": config.get("truncation"),
        "phrase_operator": config.get("phrase_operator"),
        "proximity_supported": config.get("proximity_supported", False),
        "case_sensitive_bool": config.get("case_sensitive_bool", True),
    }


def get_supported_databases() -> list[str]:
    """Get list of supported databases."""
    return list(DATABASE_CONFIGS.keys())


def translate_query(query: str, from_db: DatabaseType, to_db: DatabaseType) -> dict:
    """
    Attempt to translate query syntax between databases.

    Note: This is a best-effort translation and may not be perfect.

    Args:
        query: Source query
        from_db: Source database
        to_db: Target database

    Returns:
        Dictionary with translated query and notes
    """
    from_config = DATABASE_CONFIGS.get(from_db, {})
    to_config = DATABASE_CONFIGS.get(to_db, {})

    if not from_config or not to_config:
        return {"error": "Unknown database"}

    translated = query
    notes = []

    # Translate field tags (simplified mapping)
    field_translations = {
        # PubMed to others
        ("[tiab]", "pubmed"): {
            "wos": "TS=",
            "scopus": "TITLE-ABS-KEY(",
            "cochrane": ":ti,ab",
        },
        ("[ti]", "pubmed"): {
            "wos": "TI=",
            "scopus": "TITLE(",
            "cochrane": ":ti",
        },
        ("[mh]", "pubmed"): {
            "cochrane": ":kw",
            "embase": "/exp",
        },
    }

    for (tag, source), targets in field_translations.items():
        if from_db == source and tag in query:
            if to_db in targets:
                translated = translated.replace(tag, targets[to_db])
                notes.append(f"Translated {tag} to {targets[to_db]}")
            else:
                notes.append(f"No direct translation for {tag}")

    # Note about phrase operators
    if from_config.get("phrase_operator") != to_config.get("phrase_operator"):
        notes.append(
            f"Phrase syntax differs: {from_config.get('phrase_operator')} vs "
            f"{to_config.get('phrase_operator')}"
        )

    return {
        "original": query,
        "translated": translated,
        "from_database": from_db,
        "to_database": to_db,
        "notes": notes,
        "requires_manual_review": len(notes) > 0,
    }


def load_strategy_from_json(filepath: str) -> SearchStrategy:
    """Load search strategy from JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    strategy = SearchStrategy(
        database=data.get("database", "pubmed"),
        title=data.get("title", ""),
        notes=data.get("notes", ""),
    )

    for q_data in data.get("queries", []):
        strategy.add_query(q_data.get("query", ""), q_data.get("label", ""))

    return strategy


def save_strategy_to_json(strategy: SearchStrategy, filepath: str) -> None:
    """Save search strategy to JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(strategy.to_dict(), f, indent=2)


def generate_validation_report(strategy: SearchStrategy) -> str:
    """
    Generate a text-based validation report.

    Args:
        strategy: SearchStrategy to report on

    Returns:
        Formatted report string
    """
    strategy.validate_all()
    summary = strategy.get_summary()

    lines = [
        "SEARCH STRATEGY VALIDATION REPORT",
        "=" * 60,
        "",
        f"Database: {summary['database_name']}",
        f"Title: {strategy.title or 'Untitled'}",
        "",
        "SUMMARY",
        "-" * 40,
        f"Total queries: {summary['total_queries']}",
        f"Valid queries: {summary['valid_queries']}",
        f"Errors: {summary['error_count']}",
        f"Warnings: {summary['warning_count']}",
        "",
    ]

    if summary["error_count"] == 0 and summary["warning_count"] == 0:
        lines.append("STATUS: All queries valid")
    else:
        lines.append("ISSUES")
        lines.append("-" * 40)

        for query in strategy.queries:
            if query.issues:
                lines.append(f"\nLine {query.line_number}: {query.query[:50]}...")
                for issue in query.issues:
                    icon = "ERROR" if issue.severity == "error" else "WARN" if issue.severity == "warning" else "INFO"
                    lines.append(f"  [{icon}] {issue.message}")
                    if issue.suggestion:
                        lines.append(f"         Suggestion: {issue.suggestion}")

    lines.append("")
    return "\n".join(lines)


def main():
    """Example usage and demonstration."""
    print("Search Syntax Validator Demo")
    print("=" * 60)

    # Show supported databases
    print("\nSupported databases:")
    for db in get_supported_databases():
        info = get_database_info(db)
        print(f"  - {info['name']}")

    # Example PubMed query with errors
    print("\n" + "=" * 60)
    print("Example: Validating PubMed query with errors")
    print("-" * 40)

    bad_query = '(depression[tiab] or anxiety[tiab) and treatment[ti]'
    result = validate_query(bad_query, "pubmed")

    print(f"Query: {bad_query}")
    print(f"Valid: {result['is_valid']}")
    print("Issues:")
    for issue in result["issues"]:
        print(f"  [{issue['severity'].upper()}] {issue['message']}")
        if issue["suggestion"]:
            print(f"          Suggestion: {issue['suggestion']}")

    # Example valid query
    print("\n" + "=" * 60)
    print("Example: Validating correct PubMed query")
    print("-" * 40)

    good_query = '(depression[tiab] OR anxiety[tiab]) AND treatment[ti]'
    result = validate_query(good_query, "pubmed")

    print(f"Query: {good_query}")
    print(f"Valid: {result['is_valid']}")
    if result["issues"]:
        print("Issues:")
        for issue in result["issues"]:
            print(f"  [{issue['severity'].upper()}] {issue['message']}")
    else:
        print("No issues found!")

    # Example search strategy
    print("\n" + "=" * 60)
    print("Example: Full search strategy validation")
    print("-" * 40)

    strategy_text = """
    (CRISPR[tiab] OR "gene editing"[tiab])
    (cancer[tiab] OR tumor[tiab] OR neoplasm[mh])
    #1 AND #2
    #3 AND humans[mh]
    """

    strategy = parse_search_strategy(strategy_text, "pubmed")
    strategy.title = "CRISPR in Cancer Research"

    print(generate_validation_report(strategy))


if __name__ == "__main__":
    main()
