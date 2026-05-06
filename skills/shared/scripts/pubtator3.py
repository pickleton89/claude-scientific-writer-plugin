#!/usr/bin/env python3
"""PubTator3 REST wrapper — entity-grounded biomedical literature.

Four subcommands map 1:1 to NCBI PubTator3 endpoints. JSON to stdout.

Usage:
    uv run python pubtator3.py autocomplete BRAF [--concept gene] [--limit 5]
    uv run python pubtator3.py search --text "@GENE_BRAF AND @DISEASE_Melanoma" [--size 10] [--page 1]
    uv run python pubtator3.py search --gene BRAF --disease Melanoma
    uv run python pubtator3.py annotations --pmids 24200969,22663011 [--full]
    uv run python pubtator3.py relations --entity @GENE_BRAF [--type associate]

Add --summary on search/annotations/relations for a compact, token-cheap view.

API: https://www.ncbi.nlm.nih.gov/research/pubtator3-api/  (no auth, ~20 req/s).
Returns exit 0 on success, 1 on input error, 2 on remote/network error.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from typing import Any, Iterable

try:
    import requests
except ImportError:  # pragma: no cover
    sys.stderr.write("error: requests not installed; run with `uv run`\n")
    sys.exit(2)


BASE_URL = "https://www.ncbi.nlm.nih.gov/research/pubtator3-api"
DEFAULT_TIMEOUT = 30
THROTTLE_SECONDS = 0.05  # 20 req/s ceiling
USER_AGENT = "claude-scientific-writer-plugin/pubtator3 (+https://github.com/scientific-writer)"
MAX_RETRIES = 3
CONCEPT_TYPES = ("gene", "disease", "chemical", "variant", "species")


class PubTator3Error(Exception):
    """Network / remote error from PubTator3."""

    def __init__(self, status_code: int | None, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"PubTator3 {status_code}: {detail}")


@dataclass
class PubTator3Client:
    """Throttled HTTP client for the PubTator3 REST API.

    Reuses a `requests.Session` for connection pooling. Honors `Retry-After`
    on HTTP 429. Sleeps `THROTTLE_SECONDS` between calls.
    """

    base_url: str = BASE_URL
    timeout: int = DEFAULT_TIMEOUT
    user_agent: str = USER_AGENT
    _session: requests.Session = field(default_factory=requests.Session, repr=False)
    _last_call: float = field(default=0.0, repr=False)

    def __post_init__(self) -> None:
        self._session.headers.update({"User-Agent": self.user_agent, "Accept": "application/json"})

    def _throttle(self) -> None:
        elapsed = time.monotonic() - self._last_call
        if elapsed < THROTTLE_SECONDS:
            time.sleep(THROTTLE_SECONDS - elapsed)
        self._last_call = time.monotonic()

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = f"{self.base_url}{path}"
        for attempt in range(1, MAX_RETRIES + 1):
            self._throttle()
            try:
                resp = self._session.get(url, params=params or {}, timeout=self.timeout)
            except requests.RequestException as exc:
                if attempt >= MAX_RETRIES:
                    raise PubTator3Error(None, f"network error: {exc}") from exc
                time.sleep(0.5 * attempt)
                continue

            if resp.status_code == 429 and attempt < MAX_RETRIES:
                try:
                    wait = float(resp.headers.get("Retry-After", "1"))
                except ValueError:
                    wait = 1.0  # Retry-After was an HTTP-date, not delta-seconds
                time.sleep(min(wait, 30))
                continue
            if 500 <= resp.status_code < 600 and attempt < MAX_RETRIES:
                time.sleep(0.5 * attempt)
                continue
            if not resp.ok:
                detail = resp.text[:300]
                raise PubTator3Error(resp.status_code, detail)
            try:
                return resp.json()
            except ValueError as exc:
                raise PubTator3Error(resp.status_code, f"invalid JSON: {exc}") from exc
        raise PubTator3Error(None, "exhausted retries")  # pragma: no cover

    # ------------------------------------------------------------------ endpoints

    def autocomplete(self, query: str, concept: str | None = None, limit: int = 10) -> list[dict]:
        params: dict[str, Any] = {"query": query, "limit": limit}
        if concept:
            params["concept"] = concept
        return self._get("/entity/autocomplete/", params)

    def search(self, text: str, size: int = 10, page: int = 1) -> dict:
        return self._get("/search/", {"text": text, "size": size, "page": page})

    def annotations(self, pmids: Iterable[str | int], full: bool = False) -> dict:
        ids = ",".join(str(p) for p in pmids)
        params: dict[str, Any] = {"pmids": ids}
        if full:
            params["full"] = "true"
        return self._get("/publications/export/biocjson", params)

    def relations(self, entity: str, relation_type: str | None = None) -> list[dict]:
        params: dict[str, Any] = {"e1": entity}
        if relation_type:
            params["type"] = relation_type
        return self._get("/relations", params)


# ---------------------------------------------------------------- query composition


def compose_search_text(
    text: str | None,
    gene: list[str] | None,
    disease: list[str] | None,
    chemical: list[str] | None,
    variant: list[str] | None,
    species: list[str] | None,
) -> str:
    """Build a PubTator3 search expression from typed entity args.

    Bare symbols (e.g. "BRAF") are wrapped as `@GENE_BRAF`. Tokens that already
    start with `@` are passed through. Multiple entities are joined with AND.
    """

    def tag(prefix: str, items: list[str] | None) -> list[str]:
        out: list[str] = []
        for it in items or []:
            out.append(it if it.startswith("@") else f"@{prefix}_{it}")
        return out

    tokens: list[str] = []
    tokens += tag("GENE", gene)
    tokens += tag("DISEASE", disease)
    tokens += tag("CHEMICAL", chemical)
    tokens += tag("VARIANT", variant)
    tokens += tag("SPECIES", species)
    if text:
        tokens.append(text)
    if not tokens:
        raise ValueError("search requires at least one of --text/--gene/--disease/--chemical/--variant/--species")
    return " AND ".join(tokens)


# ---------------------------------------------------------------- summarizers


def summarize_search(payload: dict) -> dict:
    """Token-cheap view of a search response."""
    results = payload.get("results", []) or []
    return {
        "total": payload.get("count"),
        "page": payload.get("current"),
        "page_size": payload.get("page_size"),
        "total_pages": payload.get("total_pages"),
        "hits": [
            {
                "pmid": r.get("pmid"),
                "title": r.get("title"),
                "doi": r.get("doi"),
                "year": (r.get("date") or "")[:4] or None,
                "score": r.get("score"),
            }
            for r in results
        ],
    }


def summarize_annotations(payload: dict) -> list[dict]:
    """Per-PMID entity tally extracted from BioC-JSON."""
    out: list[dict] = []
    for doc in payload.get("PubTator3", []) or []:
        tally: dict[str, dict[str, int]] = {}
        for passage in doc.get("passages", []) or []:
            for ann in passage.get("annotations", []) or []:
                infons = ann.get("infons", {}) or {}
                btype = (infons.get("biotype") or infons.get("type") or "unknown").lower()
                accession = infons.get("accession") or infons.get("identifier") or ann.get("text")
                tally.setdefault(btype, {})
                tally[btype][accession] = tally[btype].get(accession, 0) + 1
        out.append({"pmid": doc.get("pmid"), "id": doc.get("id"), "entity_counts": tally})
    return out


def summarize_relations(payload: list[dict], top: int = 25) -> dict:
    """Top-N relations grouped by relation type."""
    by_type: dict[str, list[dict]] = {}
    for r in payload or []:
        by_type.setdefault(r.get("type", "unknown"), []).append(r)
    summary: dict[str, list[dict]] = {}
    for rtype, rels in by_type.items():
        rels_sorted = sorted(rels, key=lambda x: -(x.get("publications") or 0))
        summary[rtype] = rels_sorted[:top]
    return {"total_relations": len(payload or []), "by_type": summary}


# ---------------------------------------------------------------- CLI


def _print(obj: Any) -> None:
    json.dump(obj, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def cmd_autocomplete(args: argparse.Namespace, client: PubTator3Client) -> int:
    payload = client.autocomplete(args.query, concept=args.concept, limit=args.limit)
    _print(payload)
    return 0


def cmd_search(args: argparse.Namespace, client: PubTator3Client) -> int:
    try:
        text = compose_search_text(
            args.text, args.gene, args.disease, args.chemical, args.variant, args.species
        )
    except ValueError as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 1
    payload = client.search(text, size=args.size, page=args.page)
    _print(summarize_search(payload) if args.summary else payload)
    return 0


def cmd_annotations(args: argparse.Namespace, client: PubTator3Client) -> int:
    pmids = [p.strip() for p in args.pmids.split(",") if p.strip()]
    if not pmids:
        sys.stderr.write("error: --pmids requires at least one ID\n")
        return 1
    payload = client.annotations(pmids, full=args.full)
    _print(summarize_annotations(payload) if args.summary else payload)
    return 0


def cmd_relations(args: argparse.Namespace, client: PubTator3Client) -> int:
    payload = client.relations(args.entity, relation_type=args.type)
    _print(summarize_relations(payload, top=args.top) if args.summary else payload)
    return 0


def build_parser() -> argparse.ArgumentParser:
    description = (__doc__ or "PubTator3 REST wrapper").splitlines()[0]
    p = argparse.ArgumentParser(prog="pubtator3", description=description)
    p.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="HTTP timeout seconds")
    sub = p.add_subparsers(dest="command", required=True)

    ac = sub.add_parser("autocomplete", help="Resolve text to PubTator3 entity IDs")
    ac.add_argument("query")
    ac.add_argument("--concept", choices=CONCEPT_TYPES, default=None)
    ac.add_argument("--limit", type=int, default=10)
    ac.set_defaults(func=cmd_autocomplete)

    sr = sub.add_parser("search", help="Annotated PubMed search by entity IDs / text")
    sr.add_argument("--text", default=None, help="Free-text or pre-formed query")
    sr.add_argument("--gene", action="append", help="Gene token (bare or @GENE_X). Repeatable.")
    sr.add_argument("--disease", action="append")
    sr.add_argument("--chemical", action="append")
    sr.add_argument("--variant", action="append")
    sr.add_argument("--species", action="append")
    sr.add_argument("--size", type=int, default=10)
    sr.add_argument("--page", type=int, default=1)
    sr.add_argument("--summary", action="store_true", help="Compact view")
    sr.set_defaults(func=cmd_search)

    an = sub.add_parser("annotations", help="BioC-JSON entity spans for PMIDs")
    an.add_argument("--pmids", required=True, help="Comma-separated PMID list")
    an.add_argument("--full", action="store_true", help="Include full text where available")
    an.add_argument("--summary", action="store_true", help="Per-PMID entity-count tally")
    an.set_defaults(func=cmd_annotations)

    rel = sub.add_parser("relations", help="Co-mention / relation graph for an entity")
    rel.add_argument("--entity", required=True, help="Entity ID, e.g. @GENE_BRAF")
    rel.add_argument("--type", default=None, help="Relation type filter, e.g. associate, treat")
    rel.add_argument("--top", type=int, default=25, help="Top-N per relation type in --summary")
    rel.add_argument("--summary", action="store_true", help="Group by type, top-N each")
    rel.set_defaults(func=cmd_relations)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    client = PubTator3Client(timeout=args.timeout)
    try:
        return args.func(args, client)
    except PubTator3Error as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2


if __name__ == "__main__":
    sys.exit(main())
