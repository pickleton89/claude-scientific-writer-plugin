#!/usr/bin/env python3
"""
Database Selection

Provides algorithmic database selection based on research domain, subdomain,
and review type with enforced minimum requirements.
"""

from dataclasses import dataclass
from typing import Literal


# Type definitions
Domain = Literal[
    "biomedical",
    "physical_sciences",
    "computer_science",
    "social_sciences",
    "multidisciplinary",
]
ReviewType = Literal["systematic", "scoping", "narrative", "rapid"]

# Database matrix by domain and subdomain
DATABASE_MATRIX: dict[str, dict[str, list[str]]] = {
    "biomedical": {
        "clinical": ["PubMed", "Cochrane Library", "CINAHL", "Embase"],
        "basic_biology": ["PubMed", "bioRxiv", "Web of Science"],
        "genomics": ["PubMed", "bioRxiv", "GEO", "UniProt"],
        "pharmacology": ["PubMed", "Embase", "Web of Science", "MEDLINE"],
        "nursing": ["PubMed", "CINAHL", "Cochrane Library"],
        "public_health": ["PubMed", "Global Health", "CINAHL", "Cochrane Library"],
        "structural_biology": ["PubMed", "PDB", "bioRxiv", "Web of Science"],
        "default": ["PubMed", "Embase", "Web of Science", "Cochrane Library"],
    },
    "physical_sciences": {
        "physics": ["arXiv", "Web of Science", "ADS", "INSPIRE-HEP"],
        "chemistry": ["PubMed", "SciFinder", "Web of Science", "Reaxys"],
        "engineering": ["IEEE Xplore", "Scopus", "Web of Science", "Compendex"],
        "materials": ["Web of Science", "Scopus", "Materials Science Database"],
        "earth_science": ["GeoRef", "Web of Science", "Scopus"],
        "default": ["Web of Science", "Scopus", "arXiv"],
    },
    "computer_science": {
        "ml_ai": ["arXiv", "Semantic Scholar", "ACM DL", "IEEE Xplore"],
        "software": ["ACM DL", "IEEE Xplore", "arXiv", "DBLP"],
        "hci": ["ACM DL", "IEEE Xplore", "Scopus"],
        "security": ["IEEE Xplore", "ACM DL", "arXiv", "DBLP"],
        "bioinformatics": ["PubMed", "arXiv", "ACM DL", "bioRxiv"],
        "default": ["ACM DL", "IEEE Xplore", "arXiv", "DBLP"],
    },
    "social_sciences": {
        "psychology": ["PsycINFO", "Scopus", "SSRN", "Web of Science"],
        "education": ["ERIC", "PsycINFO", "Scopus", "Education Source"],
        "economics": ["EconLit", "SSRN", "Scopus", "Web of Science"],
        "sociology": ["Sociological Abstracts", "Scopus", "SSRN"],
        "default": ["SSRN", "Scopus", "Web of Science"],
    },
    "multidisciplinary": {
        "default": ["Semantic Scholar", "Web of Science", "Scopus", "Google Scholar"],
    },
}

# Minimum database requirements by review type
REVIEW_MINIMUMS: dict[str, int] = {
    "systematic": 3,
    "scoping": 2,
    "narrative": 2,
    "rapid": 2,
}

# Preprint servers by domain
PREPRINT_SERVERS: dict[str, str] = {
    "biomedical": "bioRxiv/medRxiv",
    "physical_sciences": "arXiv",
    "computer_science": "arXiv",
    "social_sciences": "SSRN",
    "multidisciplinary": "Zenodo",
}

# Grey literature sources by domain
GREY_LITERATURE: dict[str, list[str]] = {
    "biomedical": [
        "ClinicalTrials.gov",
        "WHO ICTRP",
        "OpenGrey",
        "ProQuest Dissertations",
    ],
    "physical_sciences": [
        "OpenGrey",
        "ProQuest Dissertations",
        "Conference proceedings",
    ],
    "computer_science": [
        "OpenGrey",
        "ProQuest Dissertations",
        "GitHub",
        "Conference proceedings",
    ],
    "social_sciences": [
        "OpenGrey",
        "ProQuest Dissertations",
        "Government reports",
        "NGO publications",
    ],
    "multidisciplinary": [
        "OpenGrey",
        "ProQuest Dissertations",
        "BASE",
    ],
}


@dataclass
class DatabaseSelection:
    """Result of database selection algorithm."""

    domain: str
    subdomain: str
    review_type: str
    required: list[str]
    recommended: list[str]
    optional: list[str]
    minimum_required: int
    preprint_required: bool
    preprint_server: str
    grey_literature: list[str]

    def validate(self) -> list[str]:
        """Validate the selection meets requirements."""
        errors = []

        # Check minimum requirement met
        if len(self.required) < self.minimum_required:
            errors.append(
                f"{self.review_type} review requires at least {self.minimum_required} "
                f"databases, but only {len(self.required)} selected"
            )

        # Systematic reviews need preprint coverage
        if self.preprint_required and self.preprint_server not in self.required:
            # Check if any preprint is in the list
            preprint_terms = ["arxiv", "biorxiv", "medrxiv", "ssrn"]
            has_preprint = any(
                any(term in db.lower() for term in preprint_terms)
                for db in self.required + self.recommended
            )
            if not has_preprint:
                errors.append(
                    f"Systematic/scoping reviews should include preprint search "
                    f"(suggested: {self.preprint_server})"
                )

        return errors

    def is_valid(self) -> bool:
        """Check if selection has no validation errors."""
        # Allow warnings about preprints but require minimum databases
        errors = self.validate()
        critical_errors = [e for e in errors if "at least" in e]
        return len(critical_errors) == 0

    def get_all_databases(self) -> list[str]:
        """Get all databases in order of priority."""
        return self.required + self.recommended + self.optional

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "domain": self.domain,
            "subdomain": self.subdomain,
            "review_type": self.review_type,
            "required": self.required,
            "recommended": self.recommended,
            "optional": self.optional,
            "minimum_required": self.minimum_required,
            "preprint_required": self.preprint_required,
            "preprint_server": self.preprint_server,
            "grey_literature": self.grey_literature,
        }


def select_databases(
    domain: str,
    subdomain: str = "default",
    review_type: str = "systematic",
) -> DatabaseSelection:
    """
    Select databases based on domain and review type.

    Args:
        domain: Research domain (biomedical, physical_sciences, etc.)
        subdomain: Specific subdomain within the domain
        review_type: Type of review (systematic, scoping, narrative, rapid)

    Returns:
        DatabaseSelection with categorized database lists
    """
    # Normalize inputs
    domain = domain.lower().strip()
    subdomain = subdomain.lower().strip() if subdomain else "default"
    review_type = review_type.lower().strip()

    # Get domain databases or fallback to multidisciplinary
    domain_dbs = DATABASE_MATRIX.get(domain, DATABASE_MATRIX["multidisciplinary"])
    subdomain_dbs = domain_dbs.get(subdomain, domain_dbs.get("default", []))

    # Get minimum requirement
    minimum = REVIEW_MINIMUMS.get(review_type, 3)

    # Split databases into categories
    required = subdomain_dbs[:minimum]
    remaining = subdomain_dbs[minimum:]
    recommended = remaining[:2] if len(remaining) >= 2 else remaining
    optional = remaining[2:] if len(remaining) > 2 else []

    # Get preprint and grey literature
    preprint_required = review_type in ["systematic", "scoping"]
    preprint_server = PREPRINT_SERVERS.get(domain, "Zenodo")
    grey_lit = GREY_LITERATURE.get(domain, GREY_LITERATURE["multidisciplinary"])

    return DatabaseSelection(
        domain=domain,
        subdomain=subdomain,
        review_type=review_type,
        required=required,
        recommended=recommended,
        optional=optional,
        minimum_required=minimum,
        preprint_required=preprint_required,
        preprint_server=preprint_server,
        grey_literature=grey_lit,
    )


def get_available_domains() -> list[str]:
    """Get list of available domains."""
    return list(DATABASE_MATRIX.keys())


def get_available_subdomains(domain: str) -> list[str]:
    """Get list of available subdomains for a domain."""
    domain = domain.lower().strip()
    if domain not in DATABASE_MATRIX:
        return []
    return list(DATABASE_MATRIX[domain].keys())


def get_database_url(database: str) -> str:
    """
    Get the URL for a database.

    Args:
        database: Name of the database

    Returns:
        URL string or empty if unknown
    """
    urls = {
        "PubMed": "https://pubmed.ncbi.nlm.nih.gov/",
        "Cochrane Library": "https://www.cochranelibrary.com/",
        "CINAHL": "https://www.ebsco.com/products/research-databases/cinahl-database",
        "Embase": "https://www.embase.com/",
        "bioRxiv": "https://www.biorxiv.org/",
        "medRxiv": "https://www.medrxiv.org/",
        "Web of Science": "https://www.webofscience.com/",
        "Scopus": "https://www.scopus.com/",
        "arXiv": "https://arxiv.org/",
        "IEEE Xplore": "https://ieeexplore.ieee.org/",
        "ACM DL": "https://dl.acm.org/",
        "Semantic Scholar": "https://www.semanticscholar.org/",
        "DBLP": "https://dblp.org/",
        "Google Scholar": "https://scholar.google.com/",
        "PsycINFO": "https://www.apa.org/pubs/databases/psycinfo",
        "ERIC": "https://eric.ed.gov/",
        "SSRN": "https://www.ssrn.com/",
        "ClinicalTrials.gov": "https://clinicaltrials.gov/",
        "GEO": "https://www.ncbi.nlm.nih.gov/geo/",
        "UniProt": "https://www.uniprot.org/",
        "PDB": "https://www.rcsb.org/",
        "ADS": "https://ui.adsabs.harvard.edu/",
    }
    return urls.get(database, "")


def detect_domain(keywords: list[str]) -> str:
    """
    Detect likely domain from research keywords.

    Args:
        keywords: List of research keywords

    Returns:
        Detected domain string
    """
    keywords_lower = [k.lower() for k in keywords]
    text = " ".join(keywords_lower)

    # Domain indicators
    biomedical_terms = [
        "clinical",
        "patient",
        "disease",
        "therapy",
        "treatment",
        "cell",
        "protein",
        "gene",
        "drug",
        "medical",
        "health",
        "cancer",
        "hospital",
        "diagnosis",
    ]
    cs_terms = [
        "algorithm",
        "software",
        "machine learning",
        "neural network",
        "database",
        "computing",
        "artificial intelligence",
        "programming",
        "code",
    ]
    physical_terms = [
        "physics",
        "chemistry",
        "material",
        "engineering",
        "quantum",
        "electron",
        "molecule",
        "synthesis",
        "spectroscopy",
    ]
    social_terms = [
        "psychology",
        "social",
        "behavior",
        "education",
        "economic",
        "policy",
        "society",
        "cultural",
    ]

    # Count matches
    bio_score = sum(1 for term in biomedical_terms if term in text)
    cs_score = sum(1 for term in cs_terms if term in text)
    phys_score = sum(1 for term in physical_terms if term in text)
    social_score = sum(1 for term in social_terms if term in text)

    # Return highest scoring domain
    scores = {
        "biomedical": bio_score,
        "computer_science": cs_score,
        "physical_sciences": phys_score,
        "social_sciences": social_score,
    }

    max_domain = max(scores, key=scores.get)
    if scores[max_domain] == 0:
        return "multidisciplinary"
    return max_domain


def generate_search_strategy(selection: DatabaseSelection) -> str:
    """
    Generate a text-based search strategy document.

    Args:
        selection: DatabaseSelection object

    Returns:
        Formatted search strategy string
    """
    lines = [
        "SEARCH STRATEGY",
        "=" * 60,
        "",
        f"Domain: {selection.domain}",
        f"Subdomain: {selection.subdomain}",
        f"Review Type: {selection.review_type}",
        "",
        "REQUIRED DATABASES (minimum coverage)",
        "-" * 40,
    ]

    for i, db in enumerate(selection.required, 1):
        url = get_database_url(db)
        url_str = f" ({url})" if url else ""
        lines.append(f"  {i}. {db}{url_str}")

    if selection.recommended:
        lines.extend(
            [
                "",
                "RECOMMENDED DATABASES (enhanced coverage)",
                "-" * 40,
            ]
        )
        for i, db in enumerate(selection.recommended, 1):
            url = get_database_url(db)
            url_str = f" ({url})" if url else ""
            lines.append(f"  {i}. {db}{url_str}")

    if selection.optional:
        lines.extend(
            [
                "",
                "OPTIONAL DATABASES (comprehensive coverage)",
                "-" * 40,
            ]
        )
        for i, db in enumerate(selection.optional, 1):
            url = get_database_url(db)
            url_str = f" ({url})" if url else ""
            lines.append(f"  {i}. {db}{url_str}")

    if selection.preprint_required:
        lines.extend(
            [
                "",
                "PREPRINT SERVERS",
                "-" * 40,
                f"  Suggested: {selection.preprint_server}",
            ]
        )

    lines.extend(
        [
            "",
            "GREY LITERATURE SOURCES",
            "-" * 40,
        ]
    )
    for i, source in enumerate(selection.grey_literature, 1):
        lines.append(f"  {i}. {source}")

    # Add validation warnings
    errors = selection.validate()
    if errors:
        lines.extend(
            [
                "",
                "WARNINGS",
                "-" * 40,
            ]
        )
        for error in errors:
            lines.append(f"  ! {error}")

    lines.append("")
    return "\n".join(lines)


def main():
    """Example usage and demonstration."""

    print("Database Selection Demo")
    print("=" * 60)

    # Show available domains and subdomains
    print("\nAvailable domains and subdomains:")
    for domain in get_available_domains():
        subdomains = get_available_subdomains(domain)
        print(f"  {domain}: {', '.join(subdomains)}")

    # Example selections
    print("\n" + "=" * 60)
    print("Example database selections:")

    examples = [
        ("biomedical", "clinical", "systematic"),
        ("computer_science", "ml_ai", "scoping"),
        ("social_sciences", "psychology", "narrative"),
    ]

    for domain, subdomain, review_type in examples:
        print(f"\n--- {domain}/{subdomain} ({review_type} review) ---")
        selection = select_databases(domain, subdomain, review_type)
        print(f"Required ({len(selection.required)}): {', '.join(selection.required)}")
        print(
            f"Recommended ({len(selection.recommended)}): {', '.join(selection.recommended)}"
        )
        print(f"Valid: {selection.is_valid()}")

    # Domain detection demo
    print("\n" + "=" * 60)
    print("Domain detection from keywords:")
    test_keywords = [
        ["cancer", "treatment", "clinical trial", "patient outcomes"],
        ["machine learning", "neural network", "algorithm", "classification"],
        ["quantum", "physics", "electron", "spectroscopy"],
        ["psychology", "behavior", "social", "education"],
    ]
    for keywords in test_keywords:
        detected = detect_domain(keywords)
        print(f"  {keywords[:3]}... -> {detected}")

    # Full search strategy
    print("\n" + "=" * 60)
    print("Full search strategy example:\n")
    selection = select_databases("biomedical", "clinical", "systematic")
    print(generate_search_strategy(selection))


if __name__ == "__main__":
    main()
