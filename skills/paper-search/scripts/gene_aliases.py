"""
Gene Alias Lookup Module for Paper Search.

Provides deterministic gene symbol to alias expansion for improved search recall.
Supports loading from JSON data files and HGNC format.

Phase 3 Implementation - Determinism Audit
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar


@dataclass
class GeneInfo:
    """Information about a gene including its aliases."""

    symbol: str
    name: str
    aliases: list[str]
    category: str = "unknown"

    def all_terms(self) -> list[str]:
        """Return all searchable terms for this gene."""
        return [self.symbol] + self.aliases


@dataclass
class GeneAliasDatabase:
    """
    Database of gene symbols and their aliases.

    Provides deterministic expansion of gene symbols in search queries
    to improve recall without relying on LLM knowledge.
    """

    genes: dict[str, GeneInfo] = field(default_factory=dict)
    _symbol_index: dict[str, str] = field(default_factory=dict, repr=False)

    # Default data file path
    DEFAULT_DATA_PATH: ClassVar[Path] = (
        Path(__file__).parent.parent / "references" / "gene_aliases.json"
    )

    def __post_init__(self) -> None:
        """Build case-insensitive index after initialization."""
        self._rebuild_index()

    def _rebuild_index(self) -> None:
        """Rebuild the case-insensitive symbol index."""
        self._symbol_index = {}
        for symbol in self.genes:
            self._symbol_index[symbol.upper()] = symbol

    def add_gene(self, gene: GeneInfo) -> None:
        """Add a gene to the database."""
        self.genes[gene.symbol] = gene
        self._symbol_index[gene.symbol.upper()] = gene.symbol

    def get_gene(self, symbol: str) -> GeneInfo | None:
        """Get gene info by symbol (case-insensitive)."""
        canonical = self._symbol_index.get(symbol.upper())
        if canonical:
            return self.genes.get(canonical)
        return None

    def has_gene(self, symbol: str) -> bool:
        """Check if a gene symbol exists (case-insensitive)."""
        return symbol.upper() in self._symbol_index

    def get_aliases(self, symbol: str) -> list[str]:
        """Get aliases for a gene symbol."""
        gene = self.get_gene(symbol)
        if gene:
            return gene.aliases
        return []

    def get_all_terms(self, symbol: str) -> list[str]:
        """Get all searchable terms for a gene (symbol + aliases)."""
        gene = self.get_gene(symbol)
        if gene:
            return gene.all_terms()
        return [symbol]

    def list_symbols(self) -> list[str]:
        """List all gene symbols in the database."""
        return sorted(self.genes.keys())

    def list_categories(self) -> list[str]:
        """List all unique categories."""
        return sorted(set(g.category for g in self.genes.values()))

    def genes_by_category(self, category: str) -> list[GeneInfo]:
        """Get all genes in a category."""
        return [g for g in self.genes.values() if g.category == category]

    def search_by_alias(self, alias: str) -> list[GeneInfo]:
        """Find genes that have a matching alias."""
        alias_lower = alias.lower()
        matches = []
        for gene in self.genes.values():
            for gene_alias in gene.aliases:
                if alias_lower in gene_alias.lower():
                    matches.append(gene)
                    break
        return matches

    @classmethod
    def load_from_json(cls, filepath: Path | None = None) -> "GeneAliasDatabase":
        """
        Load gene aliases from JSON file.

        Args:
            filepath: Path to JSON file. Uses default if not specified.

        Returns:
            GeneAliasDatabase instance
        """
        if filepath is None:
            filepath = cls.DEFAULT_DATA_PATH

        if not filepath.exists():
            return cls()

        with open(filepath) as f:
            data = json.load(f)

        db = cls()
        genes_data = data.get("genes", {})

        for symbol, info in genes_data.items():
            gene = GeneInfo(
                symbol=symbol,
                name=info.get("name", ""),
                aliases=info.get("aliases", []),
                category=info.get("category", "unknown"),
            )
            db.add_gene(gene)

        return db

    @classmethod
    def load_from_hgnc(cls, filepath: Path) -> "GeneAliasDatabase":
        """
        Load gene aliases from HGNC tab-separated file.

        Expected columns: symbol, name, alias_symbol, prev_symbol

        Args:
            filepath: Path to HGNC TSV file

        Returns:
            GeneAliasDatabase instance
        """
        db = cls()

        if not filepath.exists():
            return db

        with open(filepath) as f:
            # Skip header
            header = f.readline().strip().split("\t")
            col_map = {name: i for i, name in enumerate(header)}

            symbol_idx = col_map.get("symbol", col_map.get("hgnc_id", 0))
            name_idx = col_map.get("name", 1)
            alias_idx = col_map.get("alias_symbol", col_map.get("prev_symbol"))
            prev_idx = col_map.get("prev_symbol")

            for line in f:
                fields = line.strip().split("\t")
                if len(fields) <= symbol_idx:
                    continue

                symbol = fields[symbol_idx]
                name = fields[name_idx] if name_idx < len(fields) else ""

                aliases = []
                if alias_idx is not None and alias_idx < len(fields):
                    alias_str = fields[alias_idx]
                    if alias_str:
                        aliases.extend(
                            a.strip() for a in alias_str.split("|") if a.strip()
                        )
                if prev_idx is not None and prev_idx < len(fields):
                    prev_str = fields[prev_idx]
                    if prev_str:
                        aliases.extend(
                            a.strip() for a in prev_str.split("|") if a.strip()
                        )

                gene = GeneInfo(symbol=symbol, name=name, aliases=aliases)
                db.add_gene(gene)

        return db

    def merge(self, other: "GeneAliasDatabase") -> None:
        """
        Merge another database into this one.

        For existing genes, aliases are combined.
        """
        for symbol, gene in other.genes.items():
            if symbol in self.genes:
                existing = self.genes[symbol]
                new_aliases = set(existing.aliases) | set(gene.aliases)
                existing.aliases = list(new_aliases)
            else:
                self.add_gene(gene)


# Global database instance (lazy loaded)
_database: GeneAliasDatabase | None = None


def get_database() -> GeneAliasDatabase:
    """Get the global gene alias database (lazy loaded)."""
    global _database
    if _database is None:
        _database = GeneAliasDatabase.load_from_json()
    return _database


def reload_database(filepath: Path | None = None) -> GeneAliasDatabase:
    """Reload the global database from file."""
    global _database
    _database = GeneAliasDatabase.load_from_json(filepath)
    return _database


def expand_gene_terms(query: str, database: GeneAliasDatabase | None = None) -> str:
    """
    Expand gene symbols in a query with their aliases.

    This is the primary entry point for query expansion. It detects
    gene symbols in the query and adds OR clauses for known aliases.

    Args:
        query: Original search query
        database: Gene database to use (uses global if not specified)

    Returns:
        Query with gene symbols expanded to include aliases

    Example:
        >>> expand_gene_terms("TP53 mutation")
        '("TP53" OR "p53" OR "tumor protein p53") mutation'
    """
    if database is None:
        database = get_database()

    # Track which genes we've already expanded to avoid duplicates
    expanded_genes: set[str] = set()
    result = query

    # Find potential gene symbols (uppercase letters/numbers, 2-10 chars)
    # Common pattern for gene symbols
    gene_pattern = re.compile(r"\b([A-Z][A-Z0-9]{1,9})\b")

    for match in gene_pattern.finditer(query):
        symbol = match.group(1)
        symbol_upper = symbol.upper()

        # Skip if already expanded or not in database
        if symbol_upper in expanded_genes:
            continue

        if not database.has_gene(symbol):
            continue

        expanded_genes.add(symbol_upper)

        # Get all terms for this gene
        all_terms = database.get_all_terms(symbol)
        if len(all_terms) <= 1:
            continue

        # Build OR clause with quoted terms
        quoted_terms = [f'"{term}"' for term in all_terms]
        alias_clause = " OR ".join(quoted_terms)
        expansion = f"({alias_clause})"

        # Replace the first occurrence of this symbol
        # Use word boundary to avoid partial matches
        pattern = re.compile(rf"\b{re.escape(symbol)}\b", re.IGNORECASE)
        result = pattern.sub(expansion, result, count=1)

    return result


def expand_gene_terms_pubmed(
    query: str, database: GeneAliasDatabase | None = None
) -> str:
    """
    Expand gene symbols specifically for PubMed syntax.

    Similar to expand_gene_terms but formats output for PubMed's
    search syntax with field tags where appropriate.

    Args:
        query: Original search query
        database: Gene database to use

    Returns:
        PubMed-formatted query with gene expansions
    """
    if database is None:
        database = get_database()

    expanded_genes: set[str] = set()
    result = query

    gene_pattern = re.compile(r"\b([A-Z][A-Z0-9]{1,9})\b")

    for match in gene_pattern.finditer(query):
        symbol = match.group(1)
        symbol_upper = symbol.upper()

        if symbol_upper in expanded_genes:
            continue

        if not database.has_gene(symbol):
            continue

        expanded_genes.add(symbol_upper)

        all_terms = database.get_all_terms(symbol)
        if len(all_terms) <= 1:
            continue

        # For PubMed, we can optionally add [Title/Abstract] tags
        # but keeping it simple for now
        quoted_terms = [f'"{term}"' for term in all_terms]
        alias_clause = " OR ".join(quoted_terms)
        expansion = f"({alias_clause})"

        pattern = re.compile(rf"\b{re.escape(symbol)}\b", re.IGNORECASE)
        result = pattern.sub(expansion, result, count=1)

    return result


def detect_genes_in_query(
    query: str, database: GeneAliasDatabase | None = None
) -> list[str]:
    """
    Detect gene symbols present in a query.

    Args:
        query: Search query to analyze
        database: Gene database to use

    Returns:
        List of gene symbols found in the query
    """
    if database is None:
        database = get_database()

    found: list[str] = []
    gene_pattern = re.compile(r"\b([A-Z][A-Z0-9]{1,9})\b")

    for match in gene_pattern.finditer(query):
        symbol = match.group(1)
        if database.has_gene(symbol) and symbol not in found:
            found.append(symbol)

    return found


def get_expansion_explanation(
    query: str, database: GeneAliasDatabase | None = None
) -> dict[str, list[str]]:
    """
    Get an explanation of what genes would be expanded.

    Useful for transparency and debugging.

    Args:
        query: Search query
        database: Gene database to use

    Returns:
        Dict mapping gene symbols to their aliases
    """
    if database is None:
        database = get_database()

    explanation: dict[str, list[str]] = {}
    genes = detect_genes_in_query(query, database)

    for symbol in genes:
        aliases = database.get_aliases(symbol)
        if aliases:
            explanation[symbol] = aliases

    return explanation


# Convenience functions for common operations


def list_supported_genes() -> list[str]:
    """List all supported gene symbols."""
    return get_database().list_symbols()


def list_gene_categories() -> list[str]:
    """List all gene categories."""
    return get_database().list_categories()


def get_gene_info(symbol: str) -> GeneInfo | None:
    """Get information about a specific gene."""
    return get_database().get_gene(symbol)
