# Bioinformatics Database Reference

> Comprehensive guide to programmatic data retrieval from core bioinformatics resources.
> Use this reference when constructing research queries involving biological databases.

---

## Sequence Databases

### NCBI Ecosystem

The National Center for Biotechnology Information hosts interconnected databases accessible through unified APIs.

#### GenBank
- **Content**: Nucleotide sequences with annotations
- **Identifiers**: Accession numbers (e.g., `NM_001126112.3`, `NC_000001.11`)
- **API Access**: Entrez E-utilities (`efetch`, `esearch`, `elink`)
- **Query Pattern**: `esearch -db nucleotide -query "BRCA1[Gene] AND human[Organism]"`

#### RefSeq
- **Content**: Curated, non-redundant reference sequences
- **Prefix Meanings**:
  - `NM_` = mRNA
  - `NP_` = protein
  - `NC_` = chromosome
  - `XM_`/`XP_` = predicted model
- **Key Advantage**: Version-tracked stable references for reproducible analysis

#### Sequence Read Archive (SRA)
- **Content**: Raw sequencing data (FASTQ files)
- **Identifiers**: SRR (run), SRX (experiment), SRP (project), SAMN (BioSample)
- **Access Tools**:
  - `prefetch` + `fasterq-dump` (SRA Toolkit)
  - Direct HTTPS/FTP download
- **Query Example**: `esearch -db sra -query "RNA-seq AND Homo sapiens AND single cell"`

#### Gene Expression Omnibus (GEO)
- **Content**: Processed gene expression data, metadata
- **Identifiers**: GSE (series), GSM (sample), GPL (platform)
- **Data Types**: Microarray, RNA-seq, ChIP-seq, ATAC-seq
- **R Access**: `GEOquery::getGEO("GSE12345")`
- **Python Access**: `GEOparse` library

#### API Patterns: Entrez E-utilities

```bash
# Search for records
esearch -db <database> -query "<query>" | efetch -format <format>

# Link between databases
esearch -db gene -query "TP53[Gene] AND human" | elink -target protein

# Batch retrieval with history
esearch -db nucleotide -query "..." -usehistory | efetch -format fasta
```

**Rate Limits**: 3 requests/second (10/second with API key)

---

### Ensembl

European genomics resource with comprehensive genome annotations.

#### Genome Browser Navigation
- **Assemblies**: GRCh38 (human), GRCm39 (mouse), plus 200+ species
- **Stable IDs**: `ENSG` (gene), `ENST` (transcript), `ENSP` (protein)
- **Version Notation**: `ENSG00000141510.18` (version 18)

#### BioMart for Bulk Queries

```r
# R example
library(biomaRt)
ensembl <- useEnsembl(biomart = "genes", dataset = "hsapiens_gene_ensembl")
getBM(
  attributes = c("hgnc_symbol", "ensembl_gene_id", "chromosome_name"),
  filters = "hgnc_symbol",
  values = c("TP53", "BRCA1", "EGFR"),
  mart = ensembl
)
```

#### REST API Patterns

```bash
# Get gene info
curl "https://rest.ensembl.org/lookup/id/ENSG00000141510?expand=1" \
  -H "Content-type: application/json"

# Sequence retrieval
curl "https://rest.ensembl.org/sequence/id/ENSG00000141510?type=cds"
```

#### Species Assemblies and Versioning

| Species | Assembly | Ensembl Notation | UCSC Notation |
|---------|----------|------------------|---------------|
| Human | GRCh38 | GRCh38.p14 | hg38 |
| Human (legacy) | GRCh37 | GRCh37.p13 | hg19 |
| Mouse | GRCm39 | GRCm39 | mm39 |
| Mouse (legacy) | GRCm38 | GRCm38.p6 | mm10 |

**Critical**: Always report which assembly coordinates refer to.

---

### UCSC Genome Browser

Interactive visualization and data extraction for genomic annotations.

#### Track Selection and Visualization
- **Core Tracks**: RefSeq genes, GENCODE, conservation, repeats
- **Custom Tracks**: Upload BED, bigWig, VCF files
- **Sessions**: Save and share browser configurations

#### Table Browser for Data Extraction

```
1. Navigate to Tools > Table Browser
2. Select: clade, genome, assembly, group, track, table
3. Define region: genome-wide or specific coordinates
4. Choose output format: BED, GTF, sequence, etc.
```

#### bigBed/bigWig Format Handling

- **bigBed**: Indexed BED format for annotations
- **bigWig**: Indexed signal tracks (coverage, scores)
- **Tools**: `bigBedToBed`, `bigWigToBedGraph` (Kent utilities)
- **Advantage**: Random access to large files without full download

---

## Protein Databases

### UniProt

Comprehensive protein sequence and annotation database.

#### Swiss-Prot vs TrEMBL Distinction

| Feature | Swiss-Prot | TrEMBL |
|---------|------------|--------|
| Curation | Manual | Automatic |
| Evidence | Reviewed | Unreviewed |
| Count | ~570K | ~200M |
| Use | High-confidence | Comprehensive coverage |

**Best Practice**: Use Swiss-Prot for well-characterized proteins; TrEMBL for completeness.

#### Programmatic Access Patterns

```python
# REST API
import requests
response = requests.get("https://rest.uniprot.org/uniprotkb/P04637.json")
protein = response.json()

# Batch ID mapping
requests.post(
    "https://rest.uniprot.org/idmapping/run",
    data={"from": "UniProtKB_AC-ID", "to": "Ensembl", "ids": "P04637,P53_HUMAN"}
)
```

#### ID Mapping Between Databases

UniProt provides cross-references to 180+ databases:
- **Sequence**: EMBL, RefSeq, CCDS
- **Structure**: PDB, AlphaFoldDB
- **Pathways**: KEGG, Reactome
- **Disease**: OMIM, ClinVar
- **GO**: Gene Ontology annotations

---

### Protein Data Bank (PDB)

Repository for 3D structural data of biological macromolecules.

#### Structure Retrieval

```bash
# Download structure file
curl -O https://files.rcsb.org/download/1TUP.pdb
curl -O https://files.rcsb.org/download/1TUP.cif

# Search API
curl "https://search.rcsb.org/rcsbsearch/v2/query?json={...}"
```

#### RCSB vs PDBe vs PDBj

| Mirror | Region | URL | Special Features |
|--------|--------|-----|------------------|
| RCSB | US | rcsb.org | Advanced search, 3D viewers |
| PDBe | Europe | ebi.ac.uk/pdbe | SIFTS mapping, validation |
| PDBj | Japan | pdbj.org | Asian mirror, ProMode |

**Content**: Identical structures; different interfaces and tools.

#### Integration with AlphaFold DB

- **PDB**: Experimental structures (X-ray, cryo-EM, NMR)
- **AlphaFoldDB**: Predicted structures for UniProt proteomes
- **Comparison**: Use experimental when available; AlphaFold for coverage

---

### AlphaFold Database

Deep learning-predicted protein structures for 200M+ proteins.

#### Predicted Structure Retrieval

```bash
# By UniProt ID
curl -O https://alphafold.ebi.ac.uk/files/AF-P04637-F1-model_v4.pdb
curl -O https://alphafold.ebi.ac.uk/files/AF-P04637-F1-model_v4.cif
```

#### Confidence Score Interpretation (pLDDT)

| pLDDT Score | Color | Interpretation |
|-------------|-------|----------------|
| > 90 | Blue | High confidence (well-resolved) |
| 70-90 | Cyan | Confident |
| 50-70 | Yellow | Low confidence (consider with caution) |
| < 50 | Orange | Very low (often disordered) |

**Critical**: Never use low-pLDDT regions for structural analysis without validation.

#### Bulk Download Patterns

```bash
# Full proteome downloads available via FTP
# Human proteome (~23K structures): ~25 GB
https://alphafold.ebi.ac.uk/download
```

---

## Pathway & Ontology Databases

### Gene Ontology (GO)

Structured vocabulary for gene/protein attributes.

#### BP/MF/CC Categories

| Namespace | Code | Description | Example |
|-----------|------|-------------|---------|
| Biological Process | BP | What the gene does | GO:0006915 (apoptotic process) |
| Molecular Function | MF | Biochemical activity | GO:0003700 (DNA-binding TF) |
| Cellular Component | CC | Where it localizes | GO:0005634 (nucleus) |

#### Evidence Codes and Their Reliability

| Code | Meaning | Reliability | Count |
|------|---------|-------------|-------|
| EXP | Experiment | High | Rare |
| IDA | Direct Assay | High | Common |
| IMP | Mutant Phenotype | High | Common |
| IGI | Genetic Interaction | Medium | Common |
| IEA | Electronic Annotation | Low | Most common |
| ND | No Data | None | Placeholder |

**Best Practice**: Filter by evidence code for high-confidence analyses (exclude IEA for strict analysis).

#### Enrichment Analysis Resources

| Tool | Type | Strengths |
|------|------|-----------|
| DAVID | Web/API | Comprehensive, functional clustering |
| Enrichr | Web/API | Fast, extensive libraries |
| clusterProfiler | R package | Publication-quality plots, GSEA |
| gProfiler | Web/API | Multi-species, ordered query support |
| PANTHER | Web | GO-slim, evolutionary context |

---

### KEGG

Kyoto Encyclopedia of Genes and Genomes for pathway analysis.

#### Pathway Maps
- **Metabolic**: Glycolysis, TCA cycle, amino acid metabolism
- **Signaling**: MAPK, PI3K-Akt, Wnt, Notch
- **Disease**: Cancer pathways, infectious disease
- **Drug**: Drug metabolism, targets

#### API Access

```bash
# Get pathway info (free)
curl "https://rest.kegg.jp/get/hsa04110"

# List all human pathways
curl "https://rest.kegg.jp/list/pathway/hsa"

# Convert gene IDs
curl "https://rest.kegg.jp/conv/ncbi-geneid/hsa:7157"
```

**Note**: Some features require subscription for commercial use.

#### KEGG Orthology (KO) Identifiers

- **Format**: K##### (e.g., K04451 for TP53)
- **Use**: Cross-species comparison, functional annotation
- **Mapping**: Gene → KO → Pathway

---

### Reactome

Manually curated pathway database focused on human biology.

#### Visualization Tools
- **Pathway Browser**: Interactive pathway diagrams
- **Fireworks**: Genome-wide pathway overview
- **Diagram**: Reaction-level detail

#### Analysis Service API

```python
import requests

# Overrepresentation analysis
response = requests.post(
    "https://reactome.org/AnalysisService/identifiers/",
    headers={"Content-Type": "text/plain"},
    data="P04637\nP53_HUMAN\nTP53"
)
token = response.json()["summary"]["token"]

# Retrieve results
results = requests.get(f"https://reactome.org/AnalysisService/token/{token}")
```

---

### MSigDB (Molecular Signatures Database)

Curated gene sets for Gene Set Enrichment Analysis (GSEA).

#### Hallmark Gene Sets

50 "refined" gene sets representing specific biological states:
- Hallmark_Hypoxia
- Hallmark_Inflammatory_Response
- Hallmark_P53_Pathway
- Hallmark_MYC_Targets_V1

#### C2 Curated vs C5 GO Sets

| Collection | Content | Use Case |
|------------|---------|----------|
| C2:CP | Canonical pathways (KEGG, Reactome, BioCarta) | Pathway analysis |
| C2:CGP | Chemical/genetic perturbations | Drug response |
| C5:GO | GO terms (BP, MF, CC) | Functional annotation |
| C6 | Oncogenic signatures | Cancer research |
| C7 | Immunologic signatures | Immunology |

#### GSEA Integration

```r
library(clusterProfiler)
library(msigdbr)

# Get hallmark gene sets
hallmark <- msigdbr(species = "Homo sapiens", category = "H")

# Run GSEA
gseaResult <- GSEA(
  geneList = ranked_genes,  # named vector: gene symbol -> ranking metric
  TERM2GENE = hallmark[, c("gs_name", "gene_symbol")]
)
```

---

## Disease & Variant Databases

### ClinVar

Repository linking human variants to clinical significance.

#### Variant Interpretation

```
# Query by rsID
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=clinvar&term=rs121913343

# Query by gene
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=clinvar&term=BRCA1[gene]
```

#### Significance Levels

| Classification | Meaning | Action |
|----------------|---------|--------|
| Pathogenic | Causes disease | Clinical action |
| Likely pathogenic | >90% certainty pathogenic | Clinical action |
| Uncertain significance (VUS) | Insufficient evidence | No action; monitor |
| Likely benign | >90% certainty benign | No action |
| Benign | Does not cause disease | No action |

#### Submission Sources and Conflicts

- **Review Status**: Stars (0-4) indicate evidence level
- **Conflicts**: When submissions disagree, listed as "conflicting"
- **Best Practice**: Check number of submissions and review status

---

### OMIM (Online Mendelian Inheritance in Man)

Catalog of human genes and genetic disorders.

#### Gene-Phenotype Relationships

- **MIM Numbers**: Unique identifiers for genes and phenotypes
  - `#` = Phenotype with known molecular basis
  - `*` = Gene with known sequence
  - `+` = Gene and phenotype combined entry
  - `%` = Mendelian phenotype, unknown molecular basis

#### Access Patterns

```bash
# API requires registration
curl "https://api.omim.org/api/entry?mimNumber=191170&format=json&apiKey=YOUR_KEY"
```

---

### GWAS Catalog

Curated database of genome-wide association studies.

#### Association Data Retrieval

```python
import requests

# Get associations for a trait
response = requests.get(
    "https://www.ebi.ac.uk/gwas/rest/api/efoTraits/EFO_0000384/associations"
)
associations = response.json()["_embedded"]["associations"]
```

#### Effect Size Interpretation

| Metric | Typical Range | Interpretation |
|--------|---------------|----------------|
| Odds Ratio (OR) | 1.1-1.5 | Modest effect (common variants) |
| Beta (continuous) | Varies by trait | Effect size in trait units |
| P-value | <5e-8 | Genome-wide significance threshold |

**Critical**: GWAS identifies associations, not causation. Fine-mapping and functional validation required.

---

## Common Patterns

### Identifier Mapping

#### Cross-Reference Strategies

| Tool | Strengths | Best For |
|------|-----------|----------|
| UniProt ID mapping | Comprehensive, reliable | Protein IDs |
| biomaRt | Bulk conversion, R integration | Ensembl ↔ external IDs |
| g:Profiler | Multi-species, organism-aware | Gene lists |
| HGNC | Authoritative gene symbols | Human genes |

```r
# biomaRt example
library(biomaRt)
ensembl <- useEnsembl(biomart = "genes", dataset = "hsapiens_gene_ensembl")
getBM(
  attributes = c("ensembl_gene_id", "hgnc_symbol", "entrezgene_id", "uniprot_gn_id"),
  filters = "hgnc_symbol",
  values = c("TP53", "BRCA1"),
  mart = ensembl
)
```

#### Gene Symbol Standardization (HGNC)

- **Authoritative Source**: genenames.org
- **Common Issues**:
  - Historical aliases (p53 → TP53)
  - Species confusion (human TP53 vs mouse Trp53)
  - Excel corruption (MARCH1 → date)
- **Best Practice**: Always map to current HGNC symbols before analysis

#### Version-Specific Identifiers

```
# Ensembl versioned ID
ENSG00000141510.18  # Version 18

# RefSeq versioned
NM_001126112.3      # Version 3

# Without version (may resolve to latest)
ENSG00000141510
NM_001126112
```

**Critical for Reproducibility**: Always record version numbers in methods.

---

### Bulk Data Retrieval

#### FTP vs API Trade-offs

| Approach | Best For | Limitations |
|----------|----------|-------------|
| FTP | Full database downloads | Overkill for small queries |
| REST API | Targeted queries | Rate limits, slower for bulk |
| BioMart | Structured bulk queries | Ensembl-centric |
| Cloud (AWS/GCP) | Large-scale analysis | Requires cloud setup |

#### Rate Limiting Considerations

| Database | Limit | With API Key |
|----------|-------|--------------|
| NCBI E-utilities | 3/sec | 10/sec |
| Ensembl REST | 15/sec | 15/sec |
| UniProt | 100/sec | Higher |
| RCSB PDB | None stated | Respectful use |

**Best Practice**: Implement exponential backoff; batch requests when possible.

#### Caching Strategies for Reproducibility

```python
# Local caching example
import requests_cache

# Cache responses for 24 hours
requests_cache.install_cache('bioinfo_cache', expire_after=86400)

# All requests now cached automatically
response = requests.get("https://rest.ensembl.org/...")
```

**For Reproducibility**:
1. Record database versions and download dates
2. Cache responses or save intermediate files
3. Use containerized environments (Docker) with fixed database versions

---

## Quick Reference Cards

### Database Selection by Data Type

| I Need... | Primary Database | Alternative |
|-----------|------------------|-------------|
| Gene sequences | RefSeq, Ensembl | GenBank |
| Protein sequences | UniProt | RefSeq |
| Protein structures | PDB | AlphaFoldDB |
| Gene expression | GEO | ArrayExpress |
| Pathways | KEGG, Reactome | WikiPathways |
| Gene Ontology | GO | QuickGO |
| Variants | ClinVar | gnomAD, dbSNP |
| GWAS results | GWAS Catalog | PhenoScanner |

### Common Query Patterns

```bash
# "I want all human kinase structures"
1. UniProt: search "kinase AND reviewed:true AND organism:9606"
2. Extract PDB cross-references
3. Download from RCSB: https://files.rcsb.org/download/{PDB_ID}.pdb

# "I want expression data for my gene list"
1. GEO: search for relevant GSE datasets
2. Download: GEOquery::getGEO() or direct download
3. Map probe IDs to genes using platform annotation

# "I want pathways enriched in my gene list"
1. Convert gene IDs to standard symbols
2. Submit to: Enrichr, DAVID, or clusterProfiler
3. Apply multiple testing correction (FDR < 0.05)
```

---

*Reference document for research-lookup skill bioinformatics queries.*
*Last updated: 2025-12-27*
