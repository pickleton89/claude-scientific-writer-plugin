# Citation Management Output Templates

Standard templates for documenting search strategies and validation reports.

## Search Strategy Documentation

Use this template to document your literature search for reproducibility:

```markdown
## Search Strategy

**Date:** {{YYYY-MM-DD}}
**Databases searched:** {{list databases}}

### Database 1: {{Name}}
**Query:** {{exact query string}}
**Filters:** {{date range, article types, etc.}}
**Results:** {{N}} papers retrieved

### Database 2: {{Name}}
**Query:** {{exact query string}}
**Filters:** {{filters applied}}
**Results:** {{N}} papers retrieved

**Total unique papers after deduplication:** {{N}}
```

### Example

```markdown
## Search Strategy

**Date:** 2024-12-30
**Databases searched:** PubMed, Google Scholar

### Database 1: PubMed
**Query:** "CRISPR"[MeSH] AND "gene editing"[Title] AND 2023:2024[PDAT]
**Filters:** Journal Article, English, Human
**Results:** 245 papers retrieved

### Database 2: Google Scholar
**Query:** intitle:"CRISPR gene editing" 2023..2024
**Filters:** Since 2023
**Results:** 312 papers retrieved

**Total unique papers after deduplication:** 398
```

## Validation Report

JSON format for machine-readable validation results:

```json
{
  "file": "{{references.bib}}",
  "validation_date": "{{YYYY-MM-DD}}",
  "total_entries": {{N}},
  "valid_entries": {{N}},
  "errors": [
    {
      "citation_key": "{{key}}",
      "error_type": "{{missing_field|invalid_doi|duplicate}}",
      "field": "{{affected field}}",
      "severity": "{{high|medium|low}}",
      "fix": "{{suggested fix}}"
    }
  ],
  "warnings": [
    {
      "citation_key": "{{key}}",
      "warning_type": "{{type}}",
      "message": "{{description}}"
    }
  ]
}
```

### Example

```json
{
  "file": "references.bib",
  "validation_date": "2024-12-30",
  "total_entries": 45,
  "valid_entries": 43,
  "errors": [
    {
      "citation_key": "Smith2024",
      "error_type": "missing_field",
      "field": "journal",
      "severity": "high",
      "fix": "Add journal field: Nature Methods"
    },
    {
      "citation_key": "Jones2023protein",
      "error_type": "invalid_doi",
      "field": "doi",
      "severity": "high",
      "fix": "DOI does not resolve - verify correct DOI"
    }
  ],
  "warnings": [
    {
      "citation_key": "Chen2024",
      "warning_type": "missing_recommended",
      "message": "Missing recommended field: volume"
    }
  ]
}
```

## Usage

These templates are used by:
- Stage 1 (Paper Discovery) - Search strategy documentation
- Stage 4 (Validation) - Validation report output
- `validate_citations.py` script - Generates JSON reports
