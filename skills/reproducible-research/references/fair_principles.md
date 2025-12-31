# FAIR Principles Reference Guide

> Findable, Accessible, Interoperable, Reusable
> The foundation for modern scientific data management

---

## Overview

The FAIR principles were published in 2016 (Wilkinson et al., Scientific Data) to provide guidelines for scientific data management. They apply to data, metadata, code, and computational workflows.

**Key Insight**: FAIR is about machine-actionability. Data should be findable and usable by both humans AND automated systems.

---

## F — Findable

Data and metadata should be easy to find for both humans and computers.

### F1: Globally Unique and Persistent Identifier

**Requirement**: Every dataset must have a globally unique and eternally persistent identifier.

**Implementation**:
| Identifier Type | Provider | Example |
|-----------------|----------|---------|
| DOI | Zenodo, Figshare, DataCite | `10.5281/zenodo.1234567` |
| Accession | NCBI, EBI | `GSE123456`, `PRJNA123456` |
| ORCID (people) | ORCID | `0000-0002-1825-0097` |
| ROR (institutions) | ROR | `https://ror.org/02mhbdp94` |

**Anti-pattern**: URLs alone are NOT persistent identifiers (they break).

### F2: Rich Metadata

**Requirement**: Data are described with rich metadata.

**Minimum Metadata**:
```yaml
title: "RNA-seq analysis of treatment response in cell lines"
description: "Bulk RNA sequencing of HeLa cells treated with..."
creators:
  - name: "Smith, Jane"
    orcid: "0000-0002-1234-5678"
keywords:
  - "RNA-seq"
  - "differential expression"
  - "drug response"
date_created: "2024-01-15"
license: "CC-BY-4.0"
related_publication: "10.1234/journal.12345"
```

### F3: Metadata Clearly Includes Identifier

**Requirement**: Metadata must include the data identifier it describes.

**Implementation**: Include accession numbers and DOIs within metadata files.

### F4: Registered in Searchable Resource

**Requirement**: Data/metadata are registered in a searchable resource.

**Repositories by Domain**:
| Domain | Repository | Search Interface |
|--------|------------|------------------|
| Genomics | GEO, SRA | NCBI Entrez |
| Proteomics | PRIDE | PRIDE Archive |
| Structures | PDB | RCSB PDB |
| General | Zenodo | Zenodo Search |
| Code | GitHub + Zenodo | GitHub Search |

---

## A — Accessible

Once found, data should be accessible (though not necessarily open).

### A1: Retrievable by Identifier

**Requirement**: Data are retrievable by their identifier using a standardized, open protocol.

**Standard Protocols**:
- HTTP/HTTPS (web download)
- FTP/SFTP (bulk transfer)
- API (programmatic access)
- S3/GCS (cloud storage)

**Example Access Patterns**:
```bash
# GEO data via HTTP
wget https://ftp.ncbi.nlm.nih.gov/geo/series/GSE200nnn/GSE200123/suppl/

# SRA data via SRA Toolkit
prefetch SRR1234567
fasterq-dump SRR1234567

# Zenodo via API
curl https://zenodo.org/api/records/1234567

# UniProt via REST
curl https://rest.uniprot.org/uniprotkb/P53_HUMAN.fasta
```

### A1.1: Authentication Where Needed

**Requirement**: Protocol allows authentication when necessary.

**Controlled Access Scenarios**:
- Patient data (dbGaP, EGA)
- Pre-publication embargos
- Proprietary datasets

**Example (EGA)**:
```bash
# Requires approved Data Access Committee application
pyega3 fetch EGAF00001234567 --output-dir ./data/
```

### A1.2: Metadata Always Accessible

**Requirement**: Metadata are accessible even when data is restricted or no longer available.

**Implementation**: Register metadata in public catalogs regardless of data access level.

### A2: Metadata Persist After Data Removal

**Requirement**: Metadata remain accessible even if data are removed.

**Why**: Enables citation and acknowledgment even for expired datasets.

---

## I — Interoperable

Data should work with other data and systems.

### I1: Formal Knowledge Representation

**Requirement**: Use formal, accessible, shared language for knowledge representation.

**Standard Formats by Data Type**:
| Data Type | Standard Format | Alternatives |
|-----------|-----------------|--------------|
| Sequences | FASTA, FASTQ | GenBank |
| Alignments | BAM, CRAM | SAM |
| Variants | VCF | BCF |
| Expression | TSV/CSV, HDF5 | MTX (sparse) |
| Metadata | JSON-LD, XML | YAML |
| Workflows | CWL, WDL | Nextflow, Snakemake |

### I2: FAIR Vocabularies

**Requirement**: Use vocabularies that follow FAIR principles.

**Key Ontologies**:
| Domain | Ontology | URI Prefix |
|--------|----------|------------|
| Genes | Gene Ontology (GO) | `GO:` |
| Diseases | Disease Ontology (DO) | `DOID:` |
| Anatomy | Uberon | `UBERON:` |
| Cell types | Cell Ontology (CL) | `CL:` |
| Experiments | Experimental Factor Ontology (EFO) | `EFO:` |
| Organisms | NCBI Taxonomy | `NCBITaxon:` |

**Example Annotation**:
```json
{
  "sample_type": {
    "label": "HeLa cell",
    "ontology": "CLO",
    "id": "CLO:0000015"
  },
  "organism": {
    "label": "Homo sapiens",
    "ontology": "NCBITaxon",
    "id": "NCBITaxon:9606"
  }
}
```

### I3: Qualified References

**Requirement**: Include qualified references to other data.

**Relationship Types**:
- `isPartOf` — This dataset is part of a larger study
- `isDerivedFrom` — This data was processed from raw data
- `references` — This analysis uses external data
- `isSupplementTo` — Supplementary data for publication
- `cites` — Citation relationship

**Example**:
```yaml
related_identifiers:
  - identifier: "10.1234/journal.12345"
    relation: "isSupplementTo"
    resource_type: "publication"
  - identifier: "GSE100000"
    relation: "isDerivedFrom"
    resource_type: "dataset"
```

---

## R — Reusable

Data should be usable for future research.

### R1: Rich, Accurate Metadata

**Requirement**: Meta(data) are richly described with a plurality of accurate and relevant attributes.

**Essential Attributes**:
```yaml
# Data description
title: ""
description: ""
keywords: []

# Provenance
creators: []
date_created: ""
date_modified: ""
methodology: ""

# Technical
format: ""
size: ""
checksum: ""

# Context
related_publication: ""
funding: ""
```

### R1.1: Clear Usage License

**Requirement**: Data are released with a clear and accessible data usage license.

**Common Licenses**:
| License | Use Case | Requirements |
|---------|----------|--------------|
| CC0 | Maximum reuse | None |
| CC-BY 4.0 | Academic default | Attribution |
| CC-BY-SA 4.0 | Share-alike | Attribution + same license |
| CC-BY-NC 4.0 | Non-commercial | Attribution + non-commercial |

**For Code**:
| License | Permissiveness | Copyleft |
|---------|----------------|----------|
| MIT | Very permissive | No |
| Apache 2.0 | Permissive + patent | No |
| GPL 3.0 | Permissive | Yes (strong) |
| LGPL 3.0 | Permissive | Yes (weak) |

**Anti-pattern**: No license = no permission to use (legally).

### R1.2: Detailed Provenance

**Requirement**: Data include detailed provenance information.

**Provenance Elements**:
```yaml
provenance:
  source_data:
    - accession: "SRR1234567"
      repository: "SRA"
      download_date: "2024-01-15"

  software:
    - name: "STAR"
      version: "2.7.10a"
      parameters: "--runMode alignReads --outSAMtype BAM"
    - name: "DESeq2"
      version: "1.38.0"
      parameters: "default"

  environment:
    - file: "environment.yml"
      hash: "sha256:abc123..."

  workflow:
    - file: "Snakefile"
      hash: "sha256:def456..."
```

### R1.3: Domain-Relevant Standards

**Requirement**: Data meet domain-relevant community standards.

**Standards by Domain**:
| Domain | Standard | Key Requirements |
|--------|----------|------------------|
| Microarray | MIAME | Sample annotation, protocols |
| Sequencing | MINSEQE | Library prep, sequencing details |
| qPCR | MIQE | Primer sequences, efficiency |
| Proteomics | MIAPE | Sample prep, MS settings |
| Metabolomics | MSI | Sample collection, processing |

---

## FAIR Assessment

### Quick Self-Assessment Checklist

**Findable**:
- [ ] Data has a persistent identifier (DOI, accession)
- [ ] Metadata includes title, description, keywords
- [ ] Data is registered in a searchable repository
- [ ] Metadata includes the identifier

**Accessible**:
- [ ] Data can be downloaded via standard protocol
- [ ] Access mechanism is clearly documented
- [ ] If restricted, access procedure is described
- [ ] Metadata is publicly accessible

**Interoperable**:
- [ ] Data uses standard file formats
- [ ] Metadata uses standard vocabularies/ontologies
- [ ] References to other data are qualified

**Reusable**:
- [ ] License is clearly stated
- [ ] Provenance is documented
- [ ] Domain standards are followed
- [ ] README explains data structure

### Automated FAIR Assessment Tools

| Tool | URL | Description |
|------|-----|-------------|
| F-UJI | https://f-uji.net | Automated FAIR assessment |
| FAIR Evaluator | https://fairsharing.github.io/FAIR-Evaluator-FrontEnd | Maturity indicators |
| FAIRshake | https://fairshake.cloud | Rubric-based assessment |

---

## Implementation Priorities

### Minimum Viable FAIR (Start Here)

1. **Deposit in appropriate repository** (F4, A1)
2. **Get a DOI** (F1)
3. **Add a license** (R1.1)
4. **Write a README** (R1)

### Standard FAIR (Publication Ready)

5. **Use standard file formats** (I1)
6. **Add structured metadata** (F2, R1)
7. **Document provenance** (R1.2)
8. **Use ontology terms** (I2)

### Advanced FAIR (Maximum Impact)

9. **Machine-readable metadata (JSON-LD)** (I1)
10. **Qualified cross-references** (I3)
11. **Automated validation** (R1.3)
12. **Persistent metadata landing page** (A2)

---

## References

- Wilkinson, M. D. et al. (2016). The FAIR Guiding Principles for scientific data management and stewardship. *Scientific Data*, 3, 160018. https://doi.org/10.1038/sdata.2016.18
- GO FAIR Initiative: https://www.go-fair.org/fair-principles/
- FAIRsharing: https://fairsharing.org/
