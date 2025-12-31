# Metadata Standards Reference Guide

> Domain-specific standards for reproducible scientific data reporting

---

## Overview

Metadata standards define the minimum information required to interpret and reproduce experiments. Journals and repositories increasingly require compliance with these standards.

### Key Standards by Domain

| Domain | Standard | Full Name | Key Publication |
|--------|----------|-----------|-----------------|
| Microarray | MIAME | Minimum Information About a Microarray Experiment | Brazma et al., 2001 |
| Sequencing | MINSEQE | Minimum Information about a high-throughput SEQuencing Experiment | FGED Society |
| qPCR | MIQE | Minimum Information for Publication of Quantitative Real-Time PCR Experiments | Bustin et al., 2009 |
| Proteomics | MIAPE | Minimum Information About a Proteomics Experiment | HUPO-PSI |
| Metabolomics | MSI | Metabolomics Standards Initiative | MSI Board |
| Imaging | REMBI | Recommended Metadata for Biological Images | Sarkans et al., 2021 |
| Metagenomics | MIxS | Minimum Information about any (x) Sequence | GSC |

---

## MIAME (Microarray)

### Overview
- **Purpose**: Ensure microarray data can be independently verified
- **Required by**: GEO, ArrayExpress, most journals
- **Published**: Nature Genetics, 2001

### Six Core Elements

#### 1. Experimental Design
```yaml
design_elements:
  experimental_factors:
    - factor: treatment
      values: [control, drug_A, drug_B]
    - factor: time_point
      values: [0h, 6h, 24h]

  biological_replicates: 3
  technical_replicates: 0

  hybridization_design: "direct comparison"
```

#### 2. Array Design
```yaml
array_design:
  platform: Affymetrix Human Genome U133 Plus 2.0
  platform_accession: GPL570
  probe_count: 54675
  annotation_version: "hgu133plus2.db v3.13.0"
```

#### 3. Samples
```yaml
sample_metadata:
  organism: Homo sapiens
  source: HeLa cells
  characteristics:
    - cell_line: HeLa
    - passage: "15-20"
    - treatment: "100 nM dexamethasone"

  extraction_protocol: |
    Total RNA was extracted using TRIzol (Invitrogen) following
    manufacturer's instructions. RNA integrity was verified by
    Bioanalyzer (Agilent) with RIN > 8 required for inclusion.
```

#### 4. Hybridizations
```yaml
hybridization_protocol:
  labeling_method: "One-Cycle Target Labeling (Affymetrix)"
  amount_labeled: "5 µg total RNA"
  hybridization_conditions:
    temperature: 45°C
    duration: "16 hours"
    buffer: "Affymetrix hybridization buffer"
```

#### 5. Measurements
```yaml
measurement_data:
  raw_data_format: CEL
  raw_data_availability: GEO

  normalization:
    method: RMA (Robust Multi-array Average)
    software: "affy package v1.76.0"

  quality_control:
    - "Visual inspection of array images"
    - "RNA degradation plots"
    - "NUSE and RLE plots"
```

#### 6. Normalization Controls
```yaml
controls:
  spike_in:
    - name: "Affymetrix Poly-A controls"
      purpose: "Labeling efficiency"

  quality_metrics:
    - metric: "Percent Present"
      threshold: "> 40%"
    - metric: "3'/5' ratio GAPDH"
      threshold: "< 3"
```

### MIAME Compliance Checklist

```markdown
## MIAME Compliance Checklist

### Experimental Design
- [ ] Type of experiment (e.g., comparison, time series)
- [ ] Experimental factors and their values
- [ ] Number of hybridizations performed
- [ ] Replicates (biological and technical)
- [ ] Quality control steps
- [ ] Sample preparation protocol

### Array Design
- [ ] Platform name and manufacturer
- [ ] Platform accession number
- [ ] Surface/substrate type
- [ ] Probe sequences or accession numbers

### Sample Information
- [ ] Source organism
- [ ] Source tissue/cell type
- [ ] Characteristics (genotype, treatments, etc.)
- [ ] Extraction protocol
- [ ] Labeling protocol

### Hybridization Information
- [ ] Hybridization protocol
- [ ] Hybridization parameters
- [ ] Blocking agents used
- [ ] Wash protocols

### Measurement Data
- [ ] Scanner type and parameters
- [ ] Image analysis software
- [ ] Spot quality measures
- [ ] Raw data files

### Normalization
- [ ] Normalization method used
- [ ] Software and version
- [ ] Processed data files
```

---

## MINSEQE (High-Throughput Sequencing)

### Overview
- **Purpose**: Extend MIAME principles to sequencing experiments
- **Required by**: GEO, SRA, ENA, most journals
- **Maintained by**: FGED Society

### Core Elements

#### 1. General Information
```yaml
experiment:
  title: "RNA-seq of drug response in cancer cell lines"
  description: |
    Time-course RNA-seq experiment examining transcriptional
    response to kinase inhibitor treatment in HeLa cells.

  experiment_type: "RNA-Seq"
  platform: "Illumina"
```

#### 2. Sample Metadata
```yaml
samples:
  - id: Sample_01
    name: Control_0h_Rep1
    organism: Homo sapiens
    taxon_id: 9606

    source:
      tissue: "cervix"
      cell_line: HeLa
      cell_type: "adenocarcinoma"

    characteristics:
      - treatment: DMSO
      - time_point: 0h
      - replicate: 1

    molecule: "polyA RNA"

    extraction:
      protocol: "TRIzol extraction"
      kit: "Direct-zol RNA MiniPrep (Zymo)"
```

#### 3. Library Preparation
```yaml
library:
  name: "Sample_01_lib"
  strategy: RNA-Seq
  source: TRANSCRIPTOMIC
  selection: "Poly-A"

  protocol:
    kit: "TruSeq Stranded mRNA Library Prep Kit"
    vendor: "Illumina"
    fragmentation: "enzymatic, 8 minutes"
    size_selection: "200-400 bp"

  construction:
    pcr_cycles: 12
    adapter_sequence: "AGATCGGAAGAGC"

  layout: PAIRED
  nominal_length: 300
```

#### 4. Sequencing
```yaml
sequencing:
  instrument: "Illumina NovaSeq 6000"
  platform: ILLUMINA

  run_parameters:
    flow_cell: "S4"
    read_length: "150 bp"
    read_type: "paired-end"

  output:
    total_reads: 50000000
    q30_percentage: 92.5

  files:
    - filename: "Sample_01_R1.fastq.gz"
      checksum: "md5:abc123..."
    - filename: "Sample_01_R2.fastq.gz"
      checksum: "md5:def456..."
```

#### 5. Data Processing
```yaml
data_processing:
  - step: "Quality filtering"
    software: "fastp v0.23.2"
    parameters: "--qualified_quality_phred 20 --length_required 50"

  - step: "Alignment"
    software: "STAR v2.7.10a"
    reference: "GRCh38 (Ensembl 107)"
    parameters: "--outSAMtype BAM SortedByCoordinate"

  - step: "Quantification"
    software: "featureCounts v2.0.3"
    annotation: "Ensembl 107 GTF"
    parameters: "-p -B -C -s 2"

  - step: "Normalization"
    software: "DESeq2 v1.38.0"
    method: "median of ratios"

processed_files:
  - filename: "counts_matrix.tsv"
    description: "Raw gene counts, genes x samples"
  - filename: "normalized_counts.tsv"
    description: "DESeq2 normalized counts"
```

### MINSEQE Checklist

```markdown
## MINSEQE Compliance Checklist

### Experiment Description
- [ ] Study title and abstract
- [ ] Experimental design (factors, levels)
- [ ] Biological question/hypothesis
- [ ] Quality control measures

### Sample Information
- [ ] Organism and strain/cultivar
- [ ] Sample characteristics (all relevant)
- [ ] Growth/treatment conditions
- [ ] Sample collection protocol

### Library Information
- [ ] Library construction protocol
- [ ] Library strategy (RNA-Seq, ChIP-Seq, etc.)
- [ ] Selection method (polyA, rRNA depletion)
- [ ] Strand specificity
- [ ] Fragment size distribution

### Sequencing Information
- [ ] Sequencing platform and instrument
- [ ] Read length and type (single/paired)
- [ ] Raw data files (FASTQ)
- [ ] Quality metrics (Q30, etc.)

### Data Processing
- [ ] Reference genome/transcriptome version
- [ ] Alignment software and version
- [ ] Quantification software and version
- [ ] All processing parameters
- [ ] Processed data files
```

---

## MIQE (Quantitative PCR)

### Overview
- **Purpose**: Standardize qPCR reporting for reproducibility
- **Required by**: Most journals publishing qPCR data
- **Published**: Clinical Chemistry, 2009

### Essential Information

#### 1. Experimental Design
```yaml
experimental_design:
  definition_of_control: "Untreated cells (DMSO vehicle)"
  definition_of_treatment: "100 nM kinase inhibitor, 24h"

  sample_size:
    per_group: 6
    justification: "Power analysis (α=0.05, power=0.8, d=1.5)"

  quality_control:
    no_template_control: "Included in each run"
    no_reverse_transcriptase: "Included per sample"
```

#### 2. Sample Information
```yaml
sample:
  description: "HeLa cells, passage 15-20"
  processing:
    method: "TRIzol extraction"
    dna_removal: "DNase I treatment (TURBO DNase)"

  contamination_assessment: |
    gDNA contamination assessed by intron-spanning primer
    design; no amplification in -RT controls.

  quantification:
    method: "NanoDrop"
    concentration: "500 ng/µL"
    quality:
      A260_280: 2.0
      A260_230: 2.1

  integrity:
    method: "Bioanalyzer"
    RIN: "> 8.0 for all samples"
```

#### 3. Reverse Transcription
```yaml
reverse_transcription:
  reagents:
    enzyme: "SuperScript IV"
    priming: "oligo(dT)18"

  conditions:
    temperature: 55°C
    duration: "20 minutes"

  amount_rna: "1 µg"
  volume_reaction: "20 µL"

  storage: "-80°C, used within 1 week"
```

#### 4. Target Information
```yaml
targets:
  - gene: GAPDH
    function: "reference gene"
    accession: NM_002046.7
    amplicon_location: "exon 7-8 boundary"
    amplicon_length: 95

  - gene: MYC
    function: "target gene"
    accession: NM_002467.6
    amplicon_location: "exon 2-3 boundary"
    amplicon_length: 112
```

#### 5. Primer and Probe Information
```yaml
primers:
  GAPDH:
    forward:
      sequence: "GAAGGTGAAGGTCGGAGTC"
      concentration: "300 nM"
    reverse:
      sequence: "GAAGATGGTGATGGGATTTC"
      concentration: "300 nM"
    probe:
      sequence: "CAAGCTTCCCGTTCTCAGCC"
      concentration: "200 nM"
      reporter: FAM
      quencher: TAMRA

  validation:
    efficiency: "98.5%"
    r_squared: 0.998
    dynamic_range: "10^2 - 10^8 copies"
    specificity: "Single peak in melt curve"
```

#### 6. qPCR Protocol
```yaml
qpcr_protocol:
  instrument: "QuantStudio 7 Flex"
  chemistry: "TaqMan"

  reaction_volume: 20
  template_volume: 2
  template_amount: "50 ng cDNA"

  master_mix: "TaqMan Universal Master Mix II"

  cycling:
    - step: "UNG incubation"
      temperature: 50°C
      duration: "2 min"
    - step: "Polymerase activation"
      temperature: 95°C
      duration: "10 min"
    - step: "Denaturation"
      temperature: 95°C
      duration: "15 sec"
      cycles: 40
    - step: "Annealing/Extension"
      temperature: 60°C
      duration: "1 min"
      cycles: 40
```

#### 7. Data Analysis
```yaml
data_analysis:
  cq_determination:
    method: "Automatic threshold"
    baseline: "Automatic"

  quantification:
    method: "ΔΔCt"
    reference_genes: ["GAPDH", "ACTB"]
    reference_selection: "geNorm, M < 0.5"

  normalization: "Geometric mean of reference genes"

  statistics:
    biological_replicates: 3
    technical_replicates: 2
    statistical_test: "Two-way ANOVA, Tukey post-hoc"
    software: "GraphPad Prism 9"
```

### MIQE Checklist

```markdown
## MIQE Checklist (Essential Items)

### Experimental Design
- [ ] Definition of experimental and control groups
- [ ] Number of biological and technical replicates
- [ ] Sample size justification

### Sample
- [ ] Sample source and processing
- [ ] RNA extraction method
- [ ] Contamination assessment (genomic DNA)
- [ ] RNA quantity and quality metrics
- [ ] RNA integrity (RIN)

### Reverse Transcription
- [ ] Complete reaction conditions
- [ ] Amount of RNA and reaction volume
- [ ] Priming method
- [ ] cDNA storage conditions

### qPCR Target Information
- [ ] Gene symbol and accession number
- [ ] Amplicon length and location
- [ ] Primer sequences
- [ ] Probe sequences (if applicable)

### qPCR Oligonucleotides
- [ ] Primer concentration
- [ ] Primer/probe location (exon spanning?)
- [ ] Specificity (BLAST, melt curve)

### qPCR Protocol
- [ ] Reaction volume and template amount
- [ ] Polymerase identity and concentration
- [ ] Complete thermocycling parameters
- [ ] Manufacturer of plates/tubes

### qPCR Validation
- [ ] Amplification efficiency
- [ ] R² of standard curve
- [ ] Cq variation at limit of detection
- [ ] No-template controls

### Data Analysis
- [ ] Quantification method (Cq determination)
- [ ] Normalization method
- [ ] Reference genes used and validation
- [ ] Statistical methods
```

---

## MIAPE (Proteomics)

### Overview
- **Purpose**: Ensure proteomics data interpretability
- **Required by**: PRIDE, ProteomeXchange
- **Maintained by**: HUPO-PSI

### Key Modules

| Module | Description |
|--------|-------------|
| MIAPE-MS | Mass spectrometry |
| MIAPE-GE | Gel electrophoresis |
| MIAPE-CE | Capillary electrophoresis |
| MIAPE-GI | Gel informatics |
| MIAPE-MSI | MS informatics |
| MIAPE-Quant | Quantification |

### MIAPE-MS Core Elements

```yaml
sample_preparation:
  fractionation: "SDS-PAGE, in-gel digestion"
  digestion_enzyme: "Trypsin, 1:50 enzyme:protein"
  reduction: "10 mM DTT, 56°C, 30 min"
  alkylation: "55 mM iodoacetamide, RT, 20 min"

chromatography:
  column: "Acclaim PepMap 100 C18"
  dimensions: "75 µm × 50 cm"
  particle_size: "2 µm"
  gradient: "5-35% ACN over 120 min"
  flow_rate: "300 nL/min"

mass_spectrometry:
  instrument: "Orbitrap Exploris 480"
  ionization: "nanoESI"

  ms1:
    resolution: 120000
    agc_target: 3e6
    max_injection: "50 ms"
    scan_range: "350-1500 m/z"

  ms2:
    resolution: 30000
    isolation_window: "1.4 m/z"
    fragmentation: "HCD, 30% NCE"
    agc_target: 1e5

data_processing:
  database: "UniProt Human (2023_03)"
  search_engine: "MaxQuant v2.2.0.0"

  parameters:
    enzyme: "Trypsin/P"
    missed_cleavages: 2
    fixed_modifications: ["Carbamidomethyl (C)"]
    variable_modifications: ["Oxidation (M)", "Acetyl (Protein N-term)"]
    peptide_fdr: 0.01
    protein_fdr: 0.01
```

---

## Quick Reference: Which Standard?

### Decision Tree

```
What data type?
│
├── Microarray → MIAME
│
├── Sequencing (HTS)
│   ├── Bulk RNA-seq → MINSEQE
│   ├── ChIP-seq → MINSEQE + encode guidelines
│   └── scRNA-seq → MINSEQE + HCA metadata
│
├── qPCR → MIQE
│
├── Mass Spectrometry
│   ├── Proteomics → MIAPE
│   └── Metabolomics → MSI reporting
│
├── Imaging
│   ├── Microscopy → REMBI
│   └── Flow cytometry → MIFlowCyt
│
└── Metagenomics → MIxS (MIG, MIMS, MIMARKS)
```

---

## Tools and Resources

### Metadata Templates

| Standard | Template/Tool | URL |
|----------|---------------|-----|
| MIAME | GEO Spreadsheet | ncbi.nlm.nih.gov/geo/info/spreadsheet.html |
| MINSEQE | ENA Checklist | ebi.ac.uk/ena/browser/checklists |
| MIQE | RDML | rdml.org |
| MIAPE | PSI formats | psidev.info |

### Validation Tools

| Standard | Validator | Purpose |
|----------|-----------|---------|
| MINSEQE | ENA Webin-CLI | Validate sequencing metadata |
| MIAPE | mzIdentML validator | Validate search results |
| General | ISA-API | Validate ISA-Tab metadata |

---

## References

- Brazma, A. et al. (2001). Minimum information about a microarray experiment (MIAME). Nature Genetics, 29, 365-371.
- Bustin, S. A. et al. (2009). The MIQE Guidelines. Clinical Chemistry, 55(4), 611-622.
- FGED Society: https://fged.org/projects/minseqe/
- Taylor, C. F. et al. (2007). MIAPE Guidelines. Nature Biotechnology, 25, 887-893.
