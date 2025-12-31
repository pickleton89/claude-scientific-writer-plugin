# Data Repositories Reference Guide

> Where and how to deposit scientific data for publication

---

## Repository Selection Quick Reference

| Data Type | Primary | Alternative | Notes |
|-----------|---------|-------------|-------|
| Raw sequencing (FASTQ) | SRA | ENA, DDBJ | Required for publication |
| Processed expression | GEO | ArrayExpress | Includes metadata |
| Single-cell RNA-seq | GEO + SRA | ENA | Raw in SRA, processed in GEO |
| Variants (clinical) | ClinVar | — | Requires interpretation |
| Variants (population) | EVA | dbSNP, dbVar | Large-scale studies |
| Protein structures | PDB | — | Required for structures |
| Cryo-EM maps | EMDB | — | Required for EM |
| Proteomics/MS | PRIDE | MassIVE, jPOST | ProteomeXchange partner |
| Metabolomics | MetaboLights | Metabolomics WB | Follow MSI standards |
| Flow cytometry | FlowRepository | — | FCS files |
| Images | BioImage Archive | IDR, Image Data Resource | REMBI metadata |
| General/Other | Zenodo | Figshare, Dryad | Accepts anything |
| Code | GitHub + Zenodo | GitLab + DOI | Archive for DOI |

---

## NCBI GEO (Gene Expression Omnibus)

### Overview
- **URL**: https://www.ncbi.nlm.nih.gov/geo/
- **Best for**: Processed expression data, microarrays, RNA-seq
- **Accession format**: GSE (Series), GSM (Sample), GPL (Platform)

### Submission Process

**Step 1: Prepare Metadata Spreadsheet**

Required fields per sample:
```
Sample name: Unique identifier (e.g., "Control_Rep1")
Organism: Homo sapiens
Source name: HeLa cells
Characteristics:
  - cell line: HeLa
  - treatment: DMSO
  - time point: 24h
Molecule: total RNA
Extract protocol: TRIzol extraction...
Library strategy: RNA-Seq
Library source: transcriptomic
Library selection: polyA
Instrument: Illumina NovaSeq 6000
Data processing: STAR 2.7.10a alignment, featureCounts...
```

**Step 2: Upload Raw Data to SRA**

Raw FASTQ files go to SRA (linked to GEO):
```bash
# Using Aspera (fast)
ascp -i aspera.openssh -QT -l100m -k1 \
  ./fastq_files/ \
  subasp@upload.ncbi.nlm.nih.gov:uploads/your_folder/

# Or FTP
ftp ftp-private.ncbi.nlm.nih.gov
# Use credentials from submission portal
```

**Step 3: Upload Processed Data**

Formats accepted:
- Expression matrix (tab-delimited, genes × samples)
- Normalized counts (TPM, FPKM, or raw counts + method)
- Peak files (BED for ChIP-seq, ATAC-seq)

**Step 4: Submit via GEO Submission Portal**
1. Go to https://submit.ncbi.nlm.nih.gov/geo/submission/
2. Upload metadata spreadsheet
3. Link to SRA raw data
4. Upload processed data files
5. Review and submit

### Timeline
- Initial response: 1-3 business days
- Curation review: 1-2 weeks
- Release: Immediate or hold until publication

### GEO Tips
- Use consistent sample naming
- Include processing software versions
- Provide clear data processing description
- Include a README for complex studies

---

## NCBI SRA (Sequence Read Archive)

### Overview
- **URL**: https://www.ncbi.nlm.nih.gov/sra
- **Best for**: Raw sequencing data (FASTQ, BAM)
- **Accession format**: SRX (Experiment), SRR (Run), SRP (Project)

### Submission via SRA Wizard

**Step 1: Create BioProject**
```yaml
Project type: Transcriptome or Gene expression
Sample scope: Multiisolate
Material: Transcriptome
Capture: Whole
Methodology: Sequencing
```

**Step 2: Create BioSample Entries**
One BioSample per biological sample:
```yaml
Sample name: Control_Rep1
Organism: Homo sapiens
Isolate/strain: HeLa
Age: N/A (cell line)
Cell line: HeLa
Sex: female
Tissue: cervix
```

**Step 3: Create SRA Metadata**
Required for each file:
```yaml
Library name: Control_Rep1_RNAseq
Library strategy: RNA-Seq
Library source: TRANSCRIPTOMIC
Library selection: Poly-A
Library layout: PAIRED
Platform: ILLUMINA
Instrument: Illumina NovaSeq 6000
Filetype: fastq
Filename: Control_Rep1_R1.fastq.gz
```

**Step 4: Upload Files**

Using Aspera (recommended for large files):
```bash
# Install Aspera Connect, then:
ascp -i ~/.aspera/connect/etc/asperaweb_id_dsa.openssh \
  -QT -l 500m -k 1 -d \
  ./fastq_files/ \
  subasp@upload.ncbi.nlm.nih.gov:uploads/your_email/

# Verify upload
md5sum *.fastq.gz > checksums.md5
```

### SRA Command-Line Tools

```bash
# Download SRA data
prefetch SRR1234567

# Convert to FASTQ
fasterq-dump SRR1234567 --split-files --threads 8

# Validate FASTQ integrity
vdb-validate SRR1234567
```

---

## European Nucleotide Archive (ENA)

### Overview
- **URL**: https://www.ebi.ac.uk/ena
- **Best for**: European submissions, programmatic access
- **Accession format**: ERX (Experiment), ERR (Run), PRJEB (Project)

### Advantages over SRA
- More structured metadata models
- Better programmatic submission API
- Direct BAM/CRAM submission

### Programmatic Submission

```bash
# Using Webin-CLI
java -jar webin-cli.jar \
  -context reads \
  -userName Webin-XXXXX \
  -password XXXXX \
  -manifest manifest.txt \
  -validate

# manifest.txt format:
STUDY   PRJEB12345
SAMPLE  ERS12345
NAME    sample_library_1
PLATFORM    ILLUMINA
INSTRUMENT  Illumina NovaSeq 6000
LIBRARY_SOURCE  TRANSCRIPTOMIC
LIBRARY_SELECTION   Poly-A
LIBRARY_STRATEGY    RNA-Seq
FASTQ   reads_1.fastq.gz
FASTQ   reads_2.fastq.gz
```

---

## Zenodo

### Overview
- **URL**: https://zenodo.org
- **Best for**: General data, code, supplementary materials
- **DOI**: Automatic DOI minting

### Use Cases
- Supplementary data too large for journal
- Code archiving (GitHub integration)
- Datasets without a domain-specific repository
- Preprint supplementary materials

### GitHub to Zenodo (Code Archiving)

**Step 1: Connect GitHub to Zenodo**
1. Log in to Zenodo with GitHub
2. Go to Settings → GitHub
3. Enable the repository

**Step 2: Create a Release**
```bash
# Tag a release
git tag -a v1.0.0 -m "Publication release"
git push origin v1.0.0
```

**Step 3: Configure Zenodo Metadata**

Create `.zenodo.json` in repository:
```json
{
  "title": "Analysis code for: Paper Title",
  "upload_type": "software",
  "description": "Code repository for reproducing analyses in...",
  "creators": [
    {
      "name": "Smith, Jane",
      "orcid": "0000-0002-1234-5678",
      "affiliation": "University of Example"
    }
  ],
  "keywords": ["RNA-seq", "differential expression"],
  "license": "MIT",
  "related_identifiers": [
    {
      "identifier": "10.1234/journal.12345",
      "relation": "isSupplementTo",
      "resource_type": "publication"
    }
  ]
}
```

### Direct Upload

```bash
# Using API
curl -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ZENODO_TOKEN" \
  --data '{"metadata": {"title": "Dataset Title", "upload_type": "dataset"}}' \
  "https://zenodo.org/api/deposit/depositions"

# Then upload files to the bucket URL returned
```

---

## PRIDE (Proteomics)

### Overview
- **URL**: https://www.ebi.ac.uk/pride/
- **Best for**: Mass spectrometry proteomics data
- **Accession format**: PXD (ProteomeXchange)

### Required Files
- Raw files (.raw, .wiff, .d)
- Search results (mzIdentML, mzTab)
- Peak lists (mgf, mzML)
- Sample metadata

### Submission Checklist

```yaml
Project metadata:
  - Title
  - Description
  - Keywords
  - Species
  - Instrument
  - Modification parameters
  - Publication reference (if available)

Files required:
  - [ ] Raw MS files
  - [ ] Peak list files (mgf/mzML)
  - [ ] Search result files (mzIdentML)
  - [ ] Protein/peptide summary (mzTab)
  - [ ] Sample-to-file mapping
  - [ ] Search parameters
```

---

## PDB (Protein Data Bank)

### Overview
- **URL**: https://www.rcsb.org (deposit at https://deposit.wwpdb.org)
- **Best for**: Protein/nucleic acid structures
- **Accession format**: 4-character PDB ID

### Required for Deposition
- Atomic coordinates (mmCIF or PDB format)
- Structure factors (X-ray) or maps (cryo-EM)
- Refinement statistics
- Sequence information
- Experimental details

### OneDep Submission
1. Create account at https://deposit.wwpdb.org
2. Upload coordinates and experimental data
3. Complete metadata questionnaire
4. Submit for validation
5. Address validation issues
6. Approve release

### Validation Checklist
- Geometry: bond lengths, angles, Ramachandran
- Fit to density: real-space correlation
- Clashes: all-atom contacts
- Sequence: matches deposited sequence

---

## Figshare

### Overview
- **URL**: https://figshare.com
- **Best for**: Figures, presentations, posters, supplementary data
- **DOI**: Automatic

### Advantages
- Generous file size limits (20 GB free)
- Good for multimedia (videos, 3D models)
- Institutional versions available
- Quick and easy upload

### Best Practices
- Use descriptive titles
- Add comprehensive metadata
- Link to related publications
- Choose appropriate license

---

## Repository Comparison

### Speed and Ease

| Repository | Submission Time | Curation Time | Ease of Use |
|------------|-----------------|---------------|-------------|
| Zenodo | Minutes | None | Very easy |
| Figshare | Minutes | None | Very easy |
| GEO | Hours | 1-2 weeks | Moderate |
| SRA | Hours | Days | Moderate |
| ENA | Hours | Days | Moderate |
| PRIDE | Hours | 1-2 weeks | Moderate |
| PDB | Days | 1-4 weeks | Complex |

### When to Use What

**Use GEO + SRA when**:
- Publishing processed expression data
- Need raw + processed together
- Standard RNA-seq, ChIP-seq, ATAC-seq

**Use Zenodo when**:
- No domain-specific repository exists
- Archiving code for DOI
- Quick turnaround needed
- Supplementary data for preprint

**Use ENA when**:
- European institution
- Need programmatic submission
- Complex metadata requirements

---

## Data Availability Statement Templates

### Template: Multiple Repositories
```
Raw sequencing data have been deposited in the NCBI Sequence Read Archive
under BioProject accession PRJNA12345. Processed gene expression data are
available from the Gene Expression Omnibus under accession GSE12345. Mass
spectrometry proteomics data have been deposited to the ProteomeXchange
Consortium via the PRIDE partner repository with dataset identifier
PXD012345. Analysis code is available at https://github.com/user/project
(archived at https://doi.org/10.5281/zenodo.12345).
```

### Template: Embargoed Data
```
Sequencing data generated in this study have been deposited in the Gene
Expression Omnibus under accession GSE12345 and will be publicly released
upon publication. Reviewer access is available via token: [token].
```

### Template: Controlled Access
```
Due to patient privacy considerations, raw sequencing data are available
through the European Genome-phenome Archive under accession EGAS0001234
following approval by the Data Access Committee. Summary statistics are
freely available at [URL].
```
