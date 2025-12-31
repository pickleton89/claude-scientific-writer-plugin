# Workflow Documentation Reference Guide

> Documenting bioinformatics pipelines for reproducibility

---

## Overview

This guide focuses on **documenting** workflow systems (Snakemake, Nextflow) for publication and reproducibility, not on pipeline execution. Well-documented workflows enable others to understand, verify, and reproduce your analysis.

### Why Document Workflows?

1. **Reproducibility**: Others can rerun your analysis
2. **Transparency**: Reviewers can evaluate your methods
3. **Maintainability**: Future you can understand past decisions
4. **Citation**: Proper attribution of tools and methods

---

## Snakemake Documentation

### Snakefile Structure Documentation

```yaml
# workflow/README.md

# RNA-seq Analysis Workflow

## Overview

This Snakemake workflow performs RNA-seq analysis from raw FASTQ files
to differential expression results.

## Pipeline Steps

1. **Quality Control**: FastQC + MultiQC
2. **Trimming**: Trimmomatic (adapter removal, quality filtering)
3. **Alignment**: STAR (splice-aware alignment)
4. **Quantification**: featureCounts
5. **Differential Expression**: DESeq2

## Directory Structure

```
workflow/
├── Snakefile              # Main workflow definition
├── config.yaml            # Configuration parameters
├── envs/                  # Conda environment specifications
│   ├── alignment.yml
│   ├── qc.yml
│   └── analysis.yml
├── rules/                 # Modular rule definitions
│   ├── alignment.smk
│   ├── qc.smk
│   └── de.smk
├── scripts/               # Custom scripts
│   └── deseq2.R
└── report/                # Report templates
    └── workflow.rst
```

## Configuration

See `config.yaml` for all configurable parameters.

## Usage

```bash
# Dry run (preview commands)
snakemake -n

# Run with 8 cores
snakemake --cores 8 --use-conda

# Generate report
snakemake --report report.html
```
```

### Config Documentation

```yaml
# config.yaml - with documentation

# Sample information
# Format: sample_id -> [fastq_1, fastq_2]
samples:
  Control_1: ["data/raw/Control_1_R1.fastq.gz", "data/raw/Control_1_R2.fastq.gz"]
  Control_2: ["data/raw/Control_2_R1.fastq.gz", "data/raw/Control_2_R2.fastq.gz"]
  Treatment_1: ["data/raw/Treatment_1_R1.fastq.gz", "data/raw/Treatment_1_R2.fastq.gz"]
  Treatment_2: ["data/raw/Treatment_2_R1.fastq.gz", "data/raw/Treatment_2_R2.fastq.gz"]

# Experimental design for DESeq2
design:
  formula: "~ condition"
  conditions:
    control: ["Control_1", "Control_2"]
    treatment: ["Treatment_1", "Treatment_2"]

# Reference genome
reference:
  # ENSEMBL genome assembly
  species: "Homo_sapiens"
  build: "GRCh38"
  release: 107

  # Paths (downloaded by workflow)
  fasta: "resources/genome.fa"
  gtf: "resources/genes.gtf"
  star_index: "resources/star_index"

# Tool parameters
# All parameters documented with defaults and acceptable ranges

trimmomatic:
  # Adapter sequences
  adapters: "TruSeq3-PE-2.fa"
  # Leading quality threshold (remove bases < this from start)
  leading: 3
  # Trailing quality threshold (remove bases < this from end)
  trailing: 3
  # Sliding window size:quality
  slidingwindow: "4:20"
  # Minimum read length after trimming
  minlen: 50

star:
  # Number of threads per job
  threads: 8
  # Output type
  outSAMtype: "BAM SortedByCoordinate"
  # Quantification mode
  quantMode: "GeneCounts"
  # Maximum mismatches per pair
  outFilterMismatchNoverLmax: 0.04

featurecounts:
  # Count only primary alignments
  primary_only: true
  # Paired-end mode
  paired: true
  # Strand-specificity (0=unstranded, 1=stranded, 2=reversely stranded)
  strand: 2
  # Feature type in GTF
  feature_type: "exon"
  # Attribute type in GTF for grouping
  attribute_type: "gene_id"

deseq2:
  # Adjusted p-value threshold
  padj_threshold: 0.05
  # Log2 fold change threshold
  lfc_threshold: 1.0
  # Independent filtering
  independent_filtering: true
```

### Rule Documentation

```python
# rules/alignment.smk

"""
Alignment Rules
===============

Rules for aligning RNA-seq reads to reference genome using STAR.

Rules:
------
- star_index: Generate STAR genome index
- star_align: Align reads to genome

Dependencies:
-------------
- STAR 2.7.10b
- samtools 1.17
"""


rule star_index:
    """
    Generate STAR genome index.

    This rule generates the genome index required by STAR for alignment.
    The index is built from the reference genome FASTA and GTF annotation.

    Parameters
    ----------
    sjdbOverhang : int
        Read length - 1 (default: 100 for 101bp reads)
    genomeSAindexNbases : int
        Index sparsity parameter, calculated based on genome size

    Input
    -----
    fasta : str
        Reference genome FASTA file
    gtf : str
        Gene annotation GTF file

    Output
    ------
    directory : str
        Directory containing STAR index files

    Notes
    -----
    This step requires ~32 GB RAM for human genome.
    Index generation takes ~1 hour on 8 cores.
    """
    input:
        fasta=config["reference"]["fasta"],
        gtf=config["reference"]["gtf"]
    output:
        directory(config["reference"]["star_index"])
    threads: 8
    resources:
        mem_mb=32000
    conda:
        "../envs/alignment.yml"
    log:
        "logs/star_index.log"
    shell:
        """
        STAR --runMode genomeGenerate \
            --runThreadN {threads} \
            --genomeDir {output} \
            --genomeFastaFiles {input.fasta} \
            --sjdbGTFfile {input.gtf} \
            --sjdbOverhang 100 \
            2> {log}
        """


rule star_align:
    """
    Align paired-end reads with STAR.

    Two-pass mode is used for improved splice junction detection.
    Output is sorted BAM file.

    Parameters
    ----------
    See config.yaml for STAR parameters.

    Input
    -----
    reads : tuple
        Paired FASTQ files (R1, R2)
    index : str
        STAR genome index directory

    Output
    ------
    bam : str
        Coordinate-sorted BAM file
    counts : str
        Gene-level read counts (if quantMode enabled)

    Notes
    -----
    Memory usage: ~30 GB
    Runtime: ~30 min per sample (50M reads, 8 threads)
    """
    input:
        reads=get_fastq,
        index=config["reference"]["star_index"]
    output:
        bam="results/aligned/{sample}.bam",
        counts="results/aligned/{sample}.counts"
    threads: config["star"]["threads"]
    resources:
        mem_mb=30000
    params:
        outSAMtype=config["star"]["outSAMtype"],
        quantMode=config["star"]["quantMode"]
    conda:
        "../envs/alignment.yml"
    log:
        "logs/star/{sample}.log"
    shell:
        """
        STAR --runThreadN {threads} \
            --genomeDir {input.index} \
            --readFilesIn {input.reads} \
            --readFilesCommand zcat \
            --outFileNamePrefix results/aligned/{wildcards.sample}_ \
            --outSAMtype {params.outSAMtype} \
            --quantMode {params.quantMode} \
            2> {log}

        mv results/aligned/{wildcards.sample}_Aligned.sortedByCoord.out.bam {output.bam}
        mv results/aligned/{wildcards.sample}_ReadsPerGene.out.tab {output.counts}
        """
```

### Environment Documentation

```yaml
# envs/alignment.yml
# Conda environment for alignment step

name: alignment
channels:
  - conda-forge
  - bioconda
  - nodefaults

dependencies:
  # STAR: Spliced Transcripts Alignment to a Reference
  # https://github.com/alexdobin/STAR
  - star=2.7.10b

  # samtools: Tools for manipulating SAM/BAM files
  # http://www.htslib.org/
  - samtools=1.17

  # RSEQC: QC for RNA-seq data
  # https://rseqc.sourceforge.net/
  - rseqc=5.0.1

# Last updated: 2024-01-15
# Tested on: Linux x86_64, macOS ARM64
```

---

## Nextflow Documentation

### Pipeline README

```markdown
# RNA-seq Analysis Pipeline

A Nextflow pipeline for RNA-seq analysis from raw reads to differential expression.

## Quick Start

```bash
nextflow run main.nf \
    --reads 'data/raw/*_{R1,R2}.fastq.gz' \
    --genome GRCh38 \
    -profile docker
```

## Pipeline Overview

```
FASTQ → FastQC → Trimmomatic → STAR → featureCounts → DESeq2
         ↓                                     ↓
      MultiQC ←──────────────────────────────────
```

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--reads` | Path to input reads (glob pattern) | Required |
| `--genome` | Reference genome (GRCh38, GRCm39) | GRCh38 |
| `--outdir` | Output directory | `./results` |
| `--skip_qc` | Skip QC steps | `false` |

See `nextflow.config` for all parameters.

## Outputs

```
results/
├── fastqc/              # FastQC reports
├── trimmed/             # Trimmed FASTQ files
├── aligned/             # BAM files
├── counts/              # Gene count matrices
├── deseq2/              # DE results
├── multiqc/             # MultiQC report
└── pipeline_info/       # Execution reports
```

## Requirements

- Nextflow 23.04+
- Docker or Singularity
- 32 GB RAM minimum
- 100 GB disk space

## Citation

If you use this pipeline, please cite:

> Author et al. (Year). Pipeline Title. DOI
```

### Configuration Documentation

```groovy
// nextflow.config

/*
 * RNA-seq Pipeline Configuration
 * ==============================
 *
 * This file contains all configurable parameters for the pipeline.
 * Parameters can be overridden on the command line with --param value.
 */

params {
    // Input/Output
    reads           = null              // Input read files (required)
    outdir          = './results'       // Output directory
    tracedir        = "${params.outdir}/pipeline_info"

    // Reference genome
    genome          = 'GRCh38'          // Genome name
    genome_base     = 's3://ngi-igenomes/igenomes'

    // Pipeline options
    skip_qc         = false             // Skip QC steps
    skip_trimming   = false             // Skip read trimming

    // Trimmomatic settings
    adapter_file    = 'TruSeq3-PE-2.fa'
    trim_leading    = 3
    trim_trailing   = 3
    trim_minlen     = 50

    // STAR settings
    star_threads    = 8

    // DESeq2 settings
    padj_cutoff     = 0.05
    lfc_cutoff      = 1.0
}

// Genome-specific settings
genomes {
    'GRCh38' {
        fasta   = "${params.genome_base}/Homo_sapiens/Ensembl/GRCh38/Sequence/WholeGenomeFasta/genome.fa"
        gtf     = "${params.genome_base}/Homo_sapiens/Ensembl/GRCh38/Annotation/Genes/genes.gtf"
        star    = "${params.genome_base}/Homo_sapiens/Ensembl/GRCh38/Sequence/STARIndex/"
    }
    'GRCm39' {
        fasta   = "${params.genome_base}/Mus_musculus/Ensembl/GRCm39/Sequence/WholeGenomeFasta/genome.fa"
        gtf     = "${params.genome_base}/Mus_musculus/Ensembl/GRCm39/Annotation/Genes/genes.gtf"
        star    = "${params.genome_base}/Mus_musculus/Ensembl/GRCm39/Sequence/STARIndex/"
    }
}

// Execution profiles
profiles {
    docker {
        docker.enabled = true
        docker.runOptions = '-u $(id -u):$(id -g)'
    }
    singularity {
        singularity.enabled = true
        singularity.autoMounts = true
    }
    conda {
        conda.enabled = true
    }
    test {
        params.reads = 'test-data/*_{R1,R2}.fastq.gz'
        params.outdir = 'test-results'
    }
}

// Process resource requirements
process {
    withLabel: 'low_memory' {
        memory = 4.GB
        cpus = 2
    }
    withLabel: 'high_memory' {
        memory = 32.GB
        cpus = 8
    }
    withName: 'STAR_ALIGN' {
        memory = 30.GB
        cpus = 8
        time = '4.h'
    }
}

// Reporting
timeline {
    enabled = true
    file = "${params.tracedir}/timeline.html"
}
report {
    enabled = true
    file = "${params.tracedir}/report.html"
}
dag {
    enabled = true
    file = "${params.tracedir}/dag.svg"
}
```

### Process Documentation

```groovy
// modules/star.nf

/*
 * STAR Alignment Module
 * =====================
 *
 * Aligns RNA-seq reads to reference genome using STAR aligner.
 *
 * References:
 * - Dobin et al. (2013) Bioinformatics 29:15-21
 * - https://github.com/alexdobin/STAR
 */

process STAR_ALIGN {
    /*
     * Align paired-end reads with STAR.
     *
     * Performs two-pass alignment for improved splice junction detection.
     * Outputs coordinate-sorted BAM and gene-level counts.
     *
     * Input:
     *   tuple val(sample_id), path(reads) - Sample ID and paired FASTQ files
     *   path(index) - STAR genome index directory
     *   path(gtf) - Gene annotation GTF file
     *
     * Output:
     *   tuple val(sample_id), path("*.bam") - Aligned BAM file
     *   tuple val(sample_id), path("*.counts") - Gene counts
     *   path("*.Log.final.out") - STAR alignment log
     *
     * Resource requirements:
     *   Memory: 30 GB
     *   CPUs: 8
     *   Time: ~30 min per sample (50M reads)
     */

    tag "${sample_id}"
    label 'high_memory'

    container 'quay.io/biocontainers/star:2.7.10b--h9ee0642_0'

    publishDir "${params.outdir}/aligned", mode: 'copy'

    input:
    tuple val(sample_id), path(reads)
    path(index)
    path(gtf)

    output:
    tuple val(sample_id), path("*.bam"), emit: bam
    tuple val(sample_id), path("*.counts"), emit: counts
    path("*.Log.final.out"), emit: log

    script:
    """
    STAR \\
        --runThreadN ${task.cpus} \\
        --genomeDir ${index} \\
        --readFilesIn ${reads} \\
        --readFilesCommand zcat \\
        --outFileNamePrefix ${sample_id}. \\
        --outSAMtype BAM SortedByCoordinate \\
        --quantMode GeneCounts \\
        --twopassMode Basic

    mv ${sample_id}.Aligned.sortedByCoord.out.bam ${sample_id}.bam
    mv ${sample_id}.ReadsPerGene.out.tab ${sample_id}.counts
    """
}
```

---

## Methods Section Writing

### Template for Workflow-Based Methods

```markdown
## Methods

### Data Processing Pipeline

Raw sequencing data were processed using a custom Snakemake workflow
(v7.32.4) [1] with containerized environments for reproducibility.

#### Quality Control and Preprocessing

Raw reads were assessed for quality using FastQC (v0.12.1) [2].
Adapter sequences and low-quality bases were removed using Trimmomatic
(v0.39) [3] with the following parameters: ILLUMINACLIP:TruSeq3-PE-2.fa:2:30:10,
LEADING:3, TRAILING:3, SLIDINGWINDOW:4:20, MINLEN:50.

#### Alignment

Trimmed reads were aligned to the human reference genome (GRCh38,
Ensembl release 107) using STAR (v2.7.10b) [4] in two-pass mode with
default parameters. Alignment statistics are provided in Table S1.

#### Quantification

Gene-level read counts were generated using featureCounts (v2.0.3) [5]
with the following parameters: -p (paired-end), -s 2 (reverse stranded),
-B (require both ends mapped), -C (exclude chimeric fragments).

#### Differential Expression Analysis

Differential expression analysis was performed using DESeq2 (v1.38.0) [6]
in R (v4.2.3). Genes with fewer than 10 counts across all samples were
removed. Significant differential expression was defined as adjusted
p-value < 0.05 and |log2 fold change| > 1. Multiple testing correction
was performed using the Benjamini-Hochberg method.

### Data and Code Availability

The complete analysis workflow is available at [GitHub URL]
(archived at DOI: 10.5281/zenodo.xxxxx). Raw sequencing data have been
deposited in the Gene Expression Omnibus under accession GSExxxxx.

### References

[1] Mölder F, et al. (2021) Sustainable data analysis with Snakemake.
    F1000Research 10:33.
[2] Andrews S (2010) FastQC: A Quality Control Tool for High Throughput
    Sequence Data.
[3] Bolger AM, et al. (2014) Trimmomatic: a flexible trimmer for Illumina
    sequence data. Bioinformatics 30(15):2114-2120.
[4] Dobin A, et al. (2013) STAR: ultrafast universal RNA-seq aligner.
    Bioinformatics 29(1):15-21.
[5] Liao Y, et al. (2014) featureCounts: an efficient general purpose
    program for assigning sequence reads to genomic features.
    Bioinformatics 30(7):923-930.
[6] Love MI, et al. (2014) Moderated estimation of fold change and
    dispersion for RNA-seq data with DESeq2. Genome Biology 15:550.
```

---

## Workflow Diagrams

### DAG Generation

```bash
# Snakemake
snakemake --dag | dot -Tpdf > dag.pdf
snakemake --rulegraph | dot -Tpdf > rulegraph.pdf

# Nextflow (automatic with dag.enabled = true)
# Or manually:
nextflow run main.nf -with-dag dag.svg
```

### ASCII Diagram for README

```
┌─────────────────────────────────────────────────────────────────┐
│                     RNA-seq Analysis Pipeline                    │
└─────────────────────────────────────────────────────────────────┘

┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  FASTQ   │────▶│  FastQC  │────▶│ Trimming │────▶│   STAR   │
│  files   │     │    QC    │     │          │     │  Align   │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                                                         │
                                                         ▼
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  DESeq2  │◀────│  Counts  │◀────│ featureCounts│◀────│   BAM    │
│   DE     │     │  Matrix  │     │          │     │  files   │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
     │
     ▼
┌──────────┐     ┌──────────┐
│  Results │────▶│ MultiQC  │
│  Tables  │     │  Report  │
└──────────┘     └──────────┘
```

---

## Documentation Checklist

```markdown
## Workflow Documentation Checklist

### README
- [ ] Brief description of pipeline purpose
- [ ] Quick start example
- [ ] Full parameter table
- [ ] Output description
- [ ] System requirements
- [ ] Citation information

### Configuration
- [ ] All parameters documented with descriptions
- [ ] Default values specified
- [ ] Valid value ranges noted
- [ ] Examples provided

### Code Comments
- [ ] Each rule/process has docstring
- [ ] Complex logic explained
- [ ] Parameter rationale documented
- [ ] Resource requirements noted

### Environment
- [ ] All tools with versions
- [ ] Channel sources specified
- [ ] Container images documented
- [ ] Last tested date noted

### Reproducibility
- [ ] Random seeds documented
- [ ] Reference genome versions specified
- [ ] All software versions pinned
- [ ] DAG/rulegraph available

### Methods Writing
- [ ] All tools cited
- [ ] Parameters specified
- [ ] Thresholds documented
- [ ] Pipeline version noted
- [ ] Code repository linked
```

---

## Tool Comparison

### When to Use Which

| Scenario | Snakemake | Nextflow |
|----------|-----------|----------|
| Python-centric lab | ✓ | |
| Java/Groovy experience | | ✓ |
| Cloud deployment | ✓ | ✓✓ |
| HPC clusters | ✓✓ | ✓ |
| Container integration | ✓ | ✓✓ |
| nf-core pipelines | | ✓ |
| Learning curve | Lower | Higher |
| Community size | Large | Large |

### Common Pipelines to Reference

| Pipeline | URL | Description |
|----------|-----|-------------|
| nf-core/rnaseq | nf-co.re/rnaseq | RNA-seq analysis |
| nf-core/atacseq | nf-co.re/atacseq | ATAC-seq analysis |
| nf-core/chipseq | nf-co.re/chipseq | ChIP-seq analysis |
| nf-core/sarek | nf-co.re/sarek | Variant calling |
| snakemake-workflows | github.com/snakemake-workflows | Various workflows |

---

## References

- Mölder F, et al. (2021). Sustainable data analysis with Snakemake. F1000Research.
- Di Tommaso P, et al. (2017). Nextflow enables reproducible computational workflows. Nature Biotechnology.
- nf-core: https://nf-co.re/
- Snakemake documentation: https://snakemake.readthedocs.io/
