# Field-Specific Language and Terminology

> Reference guide for discipline-specific writing conventions
> Load this file when adapting writing for specific scientific fields

## Overview

Adapt language, terminology, and conventions to match the specific scientific discipline. Each field has established vocabulary, preferred phrasings, and domain-specific conventions that signal expertise and ensure clarity for the target audience.

**Identify Field-Specific Linguistic Conventions:**
- Review terminology used in recent high-impact papers in the target journal
- Note field-specific abbreviations, units, and notation systems
- Identify preferred terms (e.g., "participants" vs. "subjects," "compound" vs. "drug," "specimens" vs. "samples")
- Observe how methods, organisms, or techniques are typically described

---

## Biomedical and Clinical Sciences

- Use precise anatomical and clinical terminology (e.g., "myocardial infarction" not "heart attack" in formal writing)
- Follow standardized disease nomenclature (ICD, DSM, SNOMED-CT)
- Specify drug names using generic names first, brand names in parentheses if needed
- Use "patients" for clinical studies, "participants" for community-based research
- Follow Human Genome Variation Society (HGVS) nomenclature for genetic variants
- Report lab values with standard units (SI units in most international journals)

## Molecular Biology and Genetics

- Use italics for gene symbols (e.g., *TP53*), regular font for proteins (e.g., p53)
- Follow species-specific gene nomenclature (uppercase for human: *BRCA1*; sentence case for mouse: *Brca1*)
- Specify organism names in full at first mention, then use accepted abbreviations (e.g., *Escherichia coli*, then *E. coli*)
- Use standard genetic notation (e.g., +/+, +/-, -/- for genotypes)
- Employ established terminology for molecular techniques (e.g., "quantitative PCR" or "qPCR," not "real-time PCR")

## Bioinformatics Nomenclature

This section provides comprehensive nomenclature standards for bioinformatics and computational biology writing. Proper use of these conventions is essential for accuracy and reproducibility.

### Gene Naming Conventions

#### HGNC (Human Gene Nomenclature Committee)

Official human gene symbols follow strict formatting rules:
- **Genes**: Uppercase, italicized in text (e.g., *TP53*, *BRCA1*)
- **Protein products**: Uppercase, not italicized (e.g., TP53, BRCA1)
- Never use unofficial aliases in formal writing without defining them

#### Model Organism Conventions

| Organism | Gene | Protein | Example |
|----------|------|---------|---------|
| Human | *GENE* (italic, uppercase) | GENE (roman, uppercase) | *TP53* → TP53 |
| Mouse | *Gene* (italic, sentence case) | Gene (roman, sentence case) | *Trp53* → Trp53 |
| Zebrafish | *gene* (italic, lowercase) | Gene (roman, sentence case) | *tp53* → Tp53 |
| Drosophila | *gene* (italic, lowercase) | Gene (roman, sentence case) | *p53* → P53 |
| C. elegans | *gene-#* (italic, lowercase-number) | GENE-# (roman, uppercase) | *cep-1* → CEP-1 |
| Yeast | *GENE#* (italic, uppercase) | Gene#p (roman, sentence case + p) | *TRP1* → Trp1p |

#### Common Gene Naming Errors to Avoid

- Using unofficial aliases (p53 vs *TP53*)
- Inconsistent capitalization within a manuscript
- Missing italics for genes in running text
- Confusing gene and protein notation

### Variant Nomenclature (HGVS)

The Human Genome Variation Society (HGVS) nomenclature is the standard for describing sequence variants.

#### Sequence Type Prefixes

- `c.` - coding DNA reference sequence
- `g.` - genomic DNA reference sequence
- `m.` - mitochondrial DNA reference sequence
- `n.` - non-coding RNA reference sequence
- `p.` - protein reference sequence

#### Common Variant Notation

| Type | Format | Example | Meaning |
|------|--------|---------|---------|
| Substitution | c.76A>T | c.76A>T | Adenine to Thymine at position 76 |
| Deletion | c.76delA | c.76delA | Deletion of A at position 76 |
| Insertion | c.76_77insT | c.76_77insT | Insertion of T between positions 76 and 77 |
| Duplication | c.76dupA | c.76dupA | Duplication of A at position 76 |
| Frameshift | p.Arg97Profs*23 | p.Arg97Profs*23 | Frameshift at Arg97, stop at position 23 |

#### Protein Change Notation

- Three-letter amino acid codes are preferred in publications
- Use `Ter` or `*` for stop codons, never `X`
- Example: p.Arg248Gln (not p.R248Q in formal text)

### Genomic Coordinates

#### Genome Assembly Versions

**Always specify the assembly version in your Methods section:**
- Human: GRCh38 (preferred) or hg38 (UCSC notation)
- Mouse: GRCm39 or mm39
- Example Methods statement: "Coordinates are reported relative to GRCh38"

#### Coordinate Systems

Be explicit about which coordinate system you're using:

| System | Description | Used By |
|--------|-------------|---------|
| 1-based, fully-closed | First base is 1, both ends included | Ensembl, HGVS, VCF |
| 0-based, half-open | First base is 0, end not included | UCSC, BED, BAM |

**Important**: Always state which system when reporting coordinates, as the same genomic region has different numeric representations in each system.

### Species Conventions

- **First mention**: Full binomial name, italicized (*Homo sapiens*)
- **Subsequent mentions**: Abbreviated (*H. sapiens*) or common name (human)
- **Never**: Write genus/species without italics (*Homo sapiens* is correct; Homo sapiens is wrong)
- **Species abbreviations**: Only use after defining the full name (*D. melanogaster* after establishing *Drosophila melanogaster*)

### Sequence Data Conventions

#### Expression Units

| Unit | Use Case | Notes |
|------|----------|-------|
| Raw counts | DESeq2, edgeR input | Not directly comparable across samples |
| CPM | Simple library normalization | Counts per million mapped reads |
| TPM | Cross-sample comparison | Normalized for gene length and library size |
| FPKM/RPKM | Legacy unit | Less preferred than TPM for new analyses |

#### Quality and Coverage Reporting

- **Coverage**: Report as mean ± SD or median with range
- **Quality scores**: Use Phred scale (Q30 = 99.9% base call accuracy)
- **Read depth**: Specify minimum and average per-base coverage

---

## Chemistry and Pharmaceutical Sciences

- Follow IUPAC nomenclature for chemical compounds
- Use systematic names for novel compounds, common names for well-known substances
- Specify chemical structures using standard notation (e.g., SMILES, InChI for databases)
- Report concentrations with appropriate units (mM, μM, nM, or % w/v, v/v)
- Describe synthesis routes using accepted reaction nomenclature
- Use terms like "bioavailability," "pharmacokinetics," "IC50" consistently with field definitions

## Ecology and Environmental Sciences

- Use binomial nomenclature for species (italicized: *Homo sapiens*)
- Specify taxonomic authorities at first species mention when relevant
- Employ standardized habitat and ecosystem classifications
- Use consistent terminology for ecological metrics (e.g., "species richness," "Shannon diversity index")
- Describe sampling methods with field-standard terms (e.g., "transect," "quadrat," "mark-recapture")

## Physics and Engineering

- Follow SI units consistently unless field conventions dictate otherwise
- Use standard notation for physical quantities (scalars vs. vectors, tensors)
- Employ established terminology for phenomena (e.g., "quantum entanglement," "laminar flow")
- Specify equipment with model numbers and manufacturers when relevant
- Use mathematical notation consistent with field standards (e.g., ℏ for reduced Planck constant)

## Neuroscience

- Use standardized brain region nomenclature (e.g., refer to atlases like Allen Brain Atlas)
- Specify coordinates for brain regions using established stereotaxic systems
- Follow conventions for neural terminology (e.g., "action potential" not "spike" in formal writing)
- Use "neural activity," "neuronal firing," "brain activation" appropriately based on measurement method
- Describe recording techniques with proper specificity (e.g., "whole-cell patch clamp," "extracellular recording")

## Social and Behavioral Sciences

- Use person-first language when appropriate (e.g., "people with schizophrenia" not "schizophrenics")
- Employ standardized psychological constructs and validated assessment names
- Follow APA guidelines for reducing bias in language
- Specify theoretical frameworks using established terminology
- Use "participants" rather than "subjects" for human research

---

## General Principles

### Match Audience Expertise

- For specialized journals: Use field-specific terminology freely, define only highly specialized or novel terms
- For broad-impact journals (e.g., *Nature*, *Science*): Define more technical terms, provide context for specialized concepts
- For interdisciplinary audiences: Balance precision with accessibility, define terms at first use

### Define Technical Terms Strategically

- Define abbreviations at first use: "messenger RNA (mRNA)"
- Provide brief explanations for specialized techniques when writing for broader audiences
- Avoid over-defining terms well-known to the target audience (signals unfamiliarity with field)
- Create a glossary if numerous specialized terms are unavoidable

### Maintain Consistency

- Use the same term for the same concept throughout (don't alternate between "medication," "drug," and "pharmaceutical")
- Follow a consistent system for abbreviations (decide on "PCR" or "polymerase chain reaction" after first definition)
- Apply the same nomenclature system throughout (especially for genes, species, chemicals)

### Avoid Field Mixing Errors

- Don't use clinical terminology for basic science (e.g., don't call mice "patients")
- Avoid colloquialisms or overly general terms in place of precise field terminology
- Don't import terminology from adjacent fields without ensuring proper usage

### Verify Terminology Usage

- Consult field-specific style guides and nomenclature resources
- Check how terms are used in recent papers from the target journal
- Use domain-specific databases and ontologies (e.g., Gene Ontology, MeSH terms)
- When uncertain, cite a key reference that establishes terminology
