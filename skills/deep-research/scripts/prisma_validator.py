#!/usr/bin/env python3
"""
PRISMA Flow Diagram Validator

Validates PRISMA 2020 flow diagram data for arithmetic consistency
and generates text-based flow diagrams.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional
import json


@dataclass
class PRISMAFlowData:
    """
    PRISMA 2020 flow diagram data with validation.

    Implements the PRISMA 2020 flow diagram structure with automatic
    validation of arithmetic consistency between stages.
    """

    # Identification - records from databases
    databases: dict[str, int] = field(default_factory=dict)
    # Identification - records from other sources (registers, websites, etc.)
    other_sources: dict[str, int] = field(default_factory=dict)

    # Pre-screening removal
    duplicates_removed: int = 0
    automation_excluded: int = 0  # Records removed by automation tools

    # Screening
    records_screened: int = 0
    records_excluded: int = 0  # Excluded after title/abstract screening

    # Retrieval
    reports_sought: int = 0
    reports_not_retrieved: int = 0  # Could not obtain full text

    # Eligibility (full-text assessment)
    reports_assessed: int = 0
    reports_excluded: int = 0  # Excluded after full-text review
    exclusion_reasons: dict[str, int] = field(default_factory=dict)

    # Included
    studies_included: int = 0
    reports_of_included: int = 0  # May differ if multiple reports per study
    studies_in_meta: Optional[int] = None  # Studies in quantitative synthesis

    def total_identified(self) -> int:
        """Total records identified from all sources."""
        return sum(self.databases.values()) + sum(self.other_sources.values())

    def total_from_databases(self) -> int:
        """Total records from database searches."""
        return sum(self.databases.values())

    def total_from_other(self) -> int:
        """Total records from other sources."""
        return sum(self.other_sources.values())

    def total_removed_before_screening(self) -> int:
        """Total records removed before screening."""
        return self.duplicates_removed + self.automation_excluded

    def validate(self) -> list[str]:
        """
        Validate PRISMA flow numbers are consistent.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Calculate expected values
        total_identified = self.total_identified()
        after_dedup = total_identified - self.total_removed_before_screening()

        # Check 1: Records screened = identified - removed
        if self.records_screened != after_dedup:
            errors.append(
                f"Records screened ({self.records_screened}) should equal "
                f"total identified ({total_identified}) minus removed "
                f"({self.total_removed_before_screening()}) = {after_dedup}"
            )

        # Check 2: Reports sought = screened - excluded
        after_screening = self.records_screened - self.records_excluded
        if self.reports_sought != after_screening:
            errors.append(
                f"Reports sought ({self.reports_sought}) should equal "
                f"screened ({self.records_screened}) minus excluded "
                f"({self.records_excluded}) = {after_screening}"
            )

        # Check 3: Reports assessed = sought - not retrieved
        after_retrieval = self.reports_sought - self.reports_not_retrieved
        if self.reports_assessed != after_retrieval:
            errors.append(
                f"Reports assessed ({self.reports_assessed}) should equal "
                f"sought ({self.reports_sought}) minus not retrieved "
                f"({self.reports_not_retrieved}) = {after_retrieval}"
            )

        # Check 4: Exclusion reasons sum = reports excluded
        if self.exclusion_reasons:
            reasons_sum = sum(self.exclusion_reasons.values())
            if reasons_sum != self.reports_excluded:
                errors.append(
                    f"Exclusion reasons sum ({reasons_sum}) should equal "
                    f"reports excluded ({self.reports_excluded})"
                )

        # Check 5: Studies included = assessed - excluded
        after_ft = self.reports_assessed - self.reports_excluded
        if self.studies_included != after_ft:
            errors.append(
                f"Studies included ({self.studies_included}) should equal "
                f"assessed ({self.reports_assessed}) minus excluded "
                f"({self.reports_excluded}) = {after_ft}"
            )

        # Check 6: Studies in meta-analysis <= studies included
        if self.studies_in_meta is not None:
            if self.studies_in_meta > self.studies_included:
                errors.append(
                    f"Studies in meta-analysis ({self.studies_in_meta}) cannot exceed "
                    f"studies included ({self.studies_included})"
                )

        # Check 7: Non-negative values
        for field_name, value in [
            ("duplicates_removed", self.duplicates_removed),
            ("automation_excluded", self.automation_excluded),
            ("records_screened", self.records_screened),
            ("records_excluded", self.records_excluded),
            ("reports_sought", self.reports_sought),
            ("reports_not_retrieved", self.reports_not_retrieved),
            ("reports_assessed", self.reports_assessed),
            ("reports_excluded", self.reports_excluded),
            ("studies_included", self.studies_included),
        ]:
            if value < 0:
                errors.append(f"{field_name} cannot be negative (got {value})")

        return errors

    def is_valid(self) -> bool:
        """Check if flow data passes all validation."""
        return len(self.validate()) == 0

    def generate_summary(self) -> dict:
        """Generate summary statistics."""
        return {
            "total_identified": self.total_identified(),
            "from_databases": self.total_from_databases(),
            "from_other_sources": self.total_from_other(),
            "duplicates_removed": self.duplicates_removed,
            "records_screened": self.records_screened,
            "full_text_assessed": self.reports_assessed,
            "studies_included": self.studies_included,
            "inclusion_rate": (
                round(self.studies_included / self.total_identified() * 100, 1)
                if self.total_identified() > 0
                else 0
            ),
            "screening_exclusion_rate": (
                round(self.records_excluded / self.records_screened * 100, 1)
                if self.records_screened > 0
                else 0
            ),
        }

    def generate_diagram(self) -> str:
        """
        Generate text-based PRISMA 2020 flow diagram.

        Returns:
            Formatted string representation of the PRISMA flow diagram
        """
        # Format database list
        db_lines = [f"    {db}: {n}" for db, n in self.databases.items()]
        db_text = "\n".join(db_lines) if db_lines else "    (none)"

        # Format other sources
        other_lines = [f"    {src}: {n}" for src, n in self.other_sources.items()]
        other_text = "\n".join(other_lines) if other_lines else "    (none)"

        # Format exclusion reasons
        reason_lines = [
            f"    {reason}: {n}" for reason, n in self.exclusion_reasons.items()
        ]
        reason_text = (
            "\n".join(reason_lines) if reason_lines else "    (not specified)"
        )

        # Meta-analysis line
        meta_line = ""
        if self.studies_in_meta is not None:
            meta_line = f"""
│                                                              │
│  Studies included in                                         │
│  quantitative synthesis                                      │
│  (meta-analysis)                                             │
│  (n = {self.studies_in_meta})                                              │"""

        diagram = f"""
╔══════════════════════════════════════════════════════════════╗
║                      PRISMA 2020 Flow Diagram                ║
╚══════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────┐
│                        IDENTIFICATION                         │
├──────────────────────────────────────────────────────────────┤
│  Records identified from databases (n = {self.total_from_databases():,})                  │
{db_text}
│                                                              │
│  Records from other sources (n = {self.total_from_other():,})                       │
{other_text}
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│  Records removed before screening:                           │
│    Duplicates removed (n = {self.duplicates_removed:,})                             │
│    Records removed by automation (n = {self.automation_excluded:,})                  │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                         SCREENING                            │
├──────────────────────────────────────────────────────────────┤
│  Records screened                     Records excluded       │
│  (n = {self.records_screened:,})                             (n = {self.records_excluded:,})              │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│  Reports sought for retrieval         Reports not retrieved  │
│  (n = {self.reports_sought:,})                              (n = {self.reports_not_retrieved:,})               │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                         ELIGIBILITY                          │
├──────────────────────────────────────────────────────────────┤
│  Reports assessed for eligibility     Reports excluded       │
│  (n = {self.reports_assessed:,})                              (n = {self.reports_excluded:,})               │
│                                                              │
│  Exclusion reasons:                                          │
{reason_text}
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                          INCLUDED                            │
├──────────────────────────────────────────────────────────────┤
│  Studies included in review                                  │
│  (n = {self.studies_included})                                                │
│  Reports of included studies                                 │
│  (n = {self.reports_of_included or self.studies_included})                                                │{meta_line}
└──────────────────────────────────────────────────────────────┘
"""
        return diagram

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "PRISMAFlowData":
        """Create instance from dictionary."""
        return cls(
            databases=data.get("databases", {}),
            other_sources=data.get("other_sources", {}),
            duplicates_removed=data.get("duplicates_removed", 0),
            automation_excluded=data.get("automation_excluded", 0),
            records_screened=data.get("records_screened", 0),
            records_excluded=data.get("records_excluded", 0),
            reports_sought=data.get("reports_sought", 0),
            reports_not_retrieved=data.get("reports_not_retrieved", 0),
            reports_assessed=data.get("reports_assessed", 0),
            reports_excluded=data.get("reports_excluded", 0),
            exclusion_reasons=data.get("exclusion_reasons", {}),
            studies_included=data.get("studies_included", 0),
            reports_of_included=data.get("reports_of_included", 0),
            studies_in_meta=data.get("studies_in_meta"),
        )


def load_prisma_from_json(filepath: str) -> PRISMAFlowData:
    """Load PRISMA flow data from a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return PRISMAFlowData.from_dict(data)


def save_prisma_to_json(prisma: PRISMAFlowData, filepath: str) -> None:
    """Save PRISMA flow data to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(prisma.to_dict(), f, indent=2)


def create_prisma_template() -> PRISMAFlowData:
    """Create a template PRISMA flow with placeholder values."""
    return PRISMAFlowData(
        databases={"PubMed": 0, "Scopus": 0, "Web of Science": 0},
        other_sources={"Citation searching": 0, "Grey literature": 0},
        duplicates_removed=0,
        automation_excluded=0,
        records_screened=0,
        records_excluded=0,
        reports_sought=0,
        reports_not_retrieved=0,
        reports_assessed=0,
        reports_excluded=0,
        exclusion_reasons={
            "Wrong population": 0,
            "Wrong intervention": 0,
            "Wrong outcome": 0,
            "Wrong study design": 0,
        },
        studies_included=0,
        reports_of_included=0,
        studies_in_meta=None,
    )


def main():
    """Example usage and validation."""
    import sys

    if len(sys.argv) > 1:
        # Load and validate from JSON file
        filepath = sys.argv[1]
        try:
            prisma = load_prisma_from_json(filepath)
            print(f"Loaded PRISMA data from {filepath}")

            errors = prisma.validate()
            if errors:
                print("\n❌ Validation FAILED:")
                for error in errors:
                    print(f"  - {error}")
            else:
                print("\n✓ Validation PASSED")

            print("\nSummary:")
            summary = prisma.generate_summary()
            for key, value in summary.items():
                print(f"  {key}: {value}")

            if "--diagram" in sys.argv:
                print(prisma.generate_diagram())

        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        # Demo mode with example data
        print("PRISMA Flow Diagram Validator Demo")
        print("=" * 60)

        # Create example with valid data
        prisma = PRISMAFlowData(
            databases={"PubMed": 1250, "Scopus": 890, "Web of Science": 720},
            other_sources={"Citation searching": 45, "Grey literature": 15},
            duplicates_removed=820,
            automation_excluded=0,
            records_screened=2100,
            records_excluded=1850,
            reports_sought=250,
            reports_not_retrieved=12,
            reports_assessed=238,
            reports_excluded=196,
            exclusion_reasons={
                "Wrong population": 45,
                "Wrong intervention": 62,
                "Wrong outcome": 38,
                "Wrong study design": 51,
            },
            studies_included=42,
            reports_of_included=42,
            studies_in_meta=35,
        )

        print("\nValidating example PRISMA flow...")
        errors = prisma.validate()

        if errors:
            print("\n❌ Validation errors found:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("✓ All validation checks passed!")

        print("\nSummary statistics:")
        summary = prisma.generate_summary()
        for key, value in summary.items():
            print(f"  {key}: {value}")

        print("\n" + "=" * 60)
        print("Generated PRISMA Flow Diagram:")
        print(prisma.generate_diagram())

        # Save template for reference
        print("\n" + "=" * 60)
        print("Template JSON structure:")
        template = create_prisma_template()
        print(json.dumps(template.to_dict(), indent=2))


if __name__ == "__main__":
    main()
