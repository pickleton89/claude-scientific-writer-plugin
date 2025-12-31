# Genome Track Visualization

> Visualizing genomic data along chromosomal coordinates
> Covers pyGenomeTracks (Python), Gviz (R), and IGV integration

---

## Overview

Genome track plots display multiple data types aligned to genomic coordinates:
- **Coverage tracks**: RNA-seq, ChIP-seq, ATAC-seq signal
- **Gene annotations**: Exons, introns, transcripts
- **Variants**: SNPs, indels, structural variants
- **Interactions**: Hi-C, ChIA-PET contact maps
- **Epigenetics**: Methylation, histone modifications

---

## Input File Formats

| Format | Type | Use Case |
|--------|------|----------|
| BED | Intervals | Peaks, regions of interest |
| bigWig | Signal | Coverage, continuous values |
| bigBed | Intervals | Indexed BED for large files |
| BAM/CRAM | Alignments | Read coverage, splicing |
| VCF | Variants | SNPs, indels |
| GTF/GFF | Annotations | Gene models |
| bedGraph | Signal | Simple coverage format |

---

## pyGenomeTracks (Python)

### Installation

```bash
pip install pyGenomeTracks
# or
conda install -c bioconda pygenometracks
```

### Configuration File Approach

pyGenomeTracks uses INI config files to define tracks:

```ini
# tracks.ini

[x-axis]
where = top

[spacer]
height = 0.5

[genes]
file = genes.gtf
title = Genes
fontsize = 10
height = 5
prefered_name = gene_name
merge_transcripts = true
style = UCSC
color = #1f77b4
labels = true
max_labels = 60

[spacer]
height = 0.5

[chip-seq]
file = H3K27ac.bigwig
title = H3K27ac ChIP-seq
height = 3
color = #2ca02c
min_value = 0
max_value = auto
number_of_bins = 500
nans_to_zeros = true
show_data_range = true

[atac-seq]
file = ATAC.bigwig
title = ATAC-seq
height = 3
color = #d62728
min_value = 0
number_of_bins = 500

[peaks]
file = peaks.bed
title = ATAC Peaks
height = 1
color = #9467bd
display = collapsed

[spacer]
height = 0.5

[hic]
file = hic_matrix.cool
title = Hi-C
depth = 200000
min_value = 5
max_value = 50
transform = log1p
colormap = RdYlBu_r
```

### Command Line Usage

```bash
# Generate plot
pyGenomeTracks --tracks tracks.ini \
               --region chr1:1000000-2000000 \
               --outFileName figure.pdf \
               --width 40 \
               --dpi 300

# With title
pyGenomeTracks --tracks tracks.ini \
               --region chr1:1000000-2000000 \
               --outFileName figure.png \
               --title "Genomic Region chr1:1-2Mb"
```

### Python API

```python
import pygenometracks.plotTracks as pygtk

# Create tracks from config file
tracks = pygtk.PlotTracks('tracks.ini', figsize=(40, 20), dpi=300)

# Plot region
fig = tracks.plot('chr1:1000000-2000000')
fig.savefig('figure.pdf', dpi=300, bbox_inches='tight')
```

### Track Types Reference

#### Gene Annotation Track

```ini
[genes]
file = gencode.v38.annotation.gtf
file_type = gtf
title = GENCODE v38
height = 8
fontsize = 8
style = UCSC
# or style = flybase for arrows
prefered_name = gene_name
merge_transcripts = false
labels = true
max_labels = 100
arrow_interval = 10
color = #1f77b4
border_color = black
```

#### BigWig Signal Track

```ini
[signal]
file = coverage.bw
title = RNA-seq Coverage
height = 4
color = #2ca02c
alpha = 0.8
min_value = 0
max_value = auto
# or max_value = 100 for fixed scale
number_of_bins = 700
nans_to_zeros = true
show_data_range = true
# Overlay another file
overlay_previous = share-y
```

#### BED Interval Track

```ini
[regions]
file = peaks.bed
title = Peaks
height = 1.5
color = bed_rgb
# or color = #e41a1c
display = collapsed
# or display = stacked, interleaved, triangles
border_color = none
labels = false
```

#### Hi-C Contact Matrix

```ini
[hic]
file = matrix.cool
title = Hi-C Contacts
min_value = 1
max_value = 100
transform = log1p
colormap = RdYlBu_r
depth = 500000
# for TAD-like triangular view
file_type = hic_matrix
show_masked_bins = false
```

#### Links/Arcs Track

```ini
[links]
file = interactions.bedpe
title = Enhancer-Promoter Links
height = 3
color = #9467bd
line_width = 1
links_type = arcs
# or links_type = triangles
```

### Multiple Regions

```bash
# Plot multiple regions using BED file
pyGenomeTracks --tracks tracks.ini \
               --BED regions.bed \
               --outFileName output_dir \
               --width 40
```

---

## Gviz (R/Bioconductor)

### Installation

```r
if (!require("BiocManager", quietly = TRUE))
    install.packages("BiocManager")
BiocManager::install("Gviz")
```

### Basic Usage

```r
library(Gviz)
library(GenomicRanges)

# Define region
chr <- "chr1"
start <- 1000000
end <- 2000000

# Create tracks
itrack <- IdeogramTrack(genome = "hg38", chromosome = chr)
gtrack <- GenomeAxisTrack()
atrack <- AnnotationTrack(range = genes_gr, name = "Genes")

# Plot
plotTracks(list(itrack, gtrack, atrack),
           from = start, to = end)
```

### Track Types

#### Ideogram Track

```r
# Chromosome ideogram
itrack <- IdeogramTrack(
  genome = "hg38",
  chromosome = "chr1",
  fontcolor = "black",
  fontsize = 12
)
```

#### Genome Axis Track

```r
# Coordinate axis
gtrack <- GenomeAxisTrack(
  fontcolor = "black",
  fontsize = 10,
  col = "black"
)
```

#### Gene Region Track

```r
library(TxDb.Hsapiens.UCSC.hg38.knownGene)

# From TxDb
grtrack <- GeneRegionTrack(
  TxDb.Hsapiens.UCSC.hg38.knownGene,
  genome = "hg38",
  chromosome = chr,
  name = "Genes",
  transcriptAnnotation = "symbol",
  collapseTranscripts = "meta",
  shape = "arrow",
  fill = "#1f77b4",
  col = "darkblue"
)

# From GTF file
grtrack <- GeneRegionTrack(
  range = "genes.gtf",
  genome = "hg38",
  chromosome = chr,
  name = "GENCODE"
)
```

#### Data Track (Coverage)

```r
# From BigWig
dtrack <- DataTrack(
  range = "coverage.bw",
  genome = "hg38",
  chromosome = chr,
  name = "RNA-seq",
  type = "histogram",  # or "polygon", "l" (line), "p" (points)
  fill = "#2ca02c",
  col = "#2ca02c",
  ylim = c(0, 100)
)

# From BAM (coverage)
dtrack <- DataTrack(
  range = "aligned.bam",
  genome = "hg38",
  type = "histogram",
  name = "Coverage"
)
```

#### Annotation Track

```r
# From GRanges
peaks_gr <- GRanges(
  seqnames = "chr1",
  ranges = IRanges(start = c(1100000, 1500000), end = c(1120000, 1520000)),
  name = c("Peak1", "Peak2")
)

atrack <- AnnotationTrack(
  range = peaks_gr,
  name = "ATAC Peaks",
  fill = "#d62728",
  col = "black",
  shape = "box"
)
```

#### Highlight Track

```r
# Highlight regions of interest
ht <- HighlightTrack(
  trackList = list(dtrack1, dtrack2, atrack),
  start = c(1200000, 1600000),
  end = c(1250000, 1650000),
  fill = "#FFFF00",
  alpha = 0.3
)
```

### Complete Example

```r
library(Gviz)
library(TxDb.Hsapiens.UCSC.hg38.knownGene)
library(org.Hs.eg.db)

# Region of interest
chr <- "chr17"
start <- 7565000
end <- 7590000  # TP53 region

# Build tracks
itrack <- IdeogramTrack(genome = "hg38", chromosome = chr)

gtrack <- GenomeAxisTrack()

# Gene track
grtrack <- GeneRegionTrack(
  TxDb.Hsapiens.UCSC.hg38.knownGene,
  genome = "hg38",
  chromosome = chr,
  name = "Genes",
  transcriptAnnotation = "symbol",
  background.title = "darkblue"
)

# ChIP-seq signal
chip_track <- DataTrack(
  range = "H3K27ac.bw",
  genome = "hg38",
  chromosome = chr,
  name = "H3K27ac",
  type = "histogram",
  fill = "#2ca02c",
  col = "#2ca02c"
)

# ATAC-seq signal
atac_track <- DataTrack(
  range = "ATAC.bw",
  genome = "hg38",
  chromosome = chr,
  name = "ATAC-seq",
  type = "histogram",
  fill = "#d62728",
  col = "#d62728"
)

# Plot all tracks
plotTracks(
  list(itrack, gtrack, chip_track, atac_track, grtrack),
  from = start,
  to = end,
  sizes = c(0.5, 1, 2, 2, 3),  # Relative heights
  background.panel = "white",
  background.title = "darkblue",
  fontcolor.title = "white",
  col.axis = "black",
  col.title = "white"
)
```

### Saving Plots

```r
# PDF
pdf("genome_tracks.pdf", width = 10, height = 8)
plotTracks(track_list, from = start, to = end)
dev.off()

# PNG
png("genome_tracks.png", width = 10, height = 8, units = "in", res = 300)
plotTracks(track_list, from = start, to = end)
dev.off()
```

### Multiple Panels

```r
# Plot multiple regions
regions <- data.frame(
  chr = c("chr1", "chr2", "chr3"),
  start = c(1000000, 2000000, 3000000),
  end = c(1100000, 2100000, 3100000)
)

pdf("multi_region.pdf", width = 12, height = 4)
par(mfrow = c(1, 3))
for (i in 1:nrow(regions)) {
  plotTracks(track_list,
             chromosome = regions$chr[i],
             from = regions$start[i],
             to = regions$end[i])
}
dev.off()
```

---

## IGV Integration

### IGV Batch Scripting

```
# igv_batch.txt
new
genome hg38
load H3K27ac.bw
load ATAC.bw
load peaks.bed
goto chr1:1000000-2000000
snapshot region1.png
goto chr2:5000000-6000000
snapshot region2.png
exit
```

```bash
# Run IGV batch
igv.sh -b igv_batch.txt
```

### Python IGV Control (igv-jupyter)

```python
import igv_notebook

# In Jupyter notebook
igv_notebook.init()

browser = igv_notebook.Browser({
    "genome": "hg38",
    "locus": "chr1:1000000-2000000"
})

# Add tracks
browser.load_track({
    "name": "H3K27ac",
    "url": "https://example.com/H3K27ac.bw",
    "type": "wig"
})

browser.load_track({
    "name": "Genes",
    "url": "https://example.com/genes.bed",
    "type": "annotation"
})
```

---

## Best Practices

### Track Ordering

Standard order from top to bottom:
1. Chromosome ideogram (optional)
2. Coordinate axis
3. Signal tracks (ChIP-seq, ATAC-seq, RNA-seq)
4. Peak/region tracks
5. Interaction tracks (Hi-C, arcs)
6. Gene annotations
7. Variants (if applicable)

### Color Consistency

| Track Type | Suggested Colors |
|------------|------------------|
| H3K27ac (active) | Green (#2ca02c) |
| H3K4me3 (promoter) | Red (#d62728) |
| H3K27me3 (repressive) | Blue (#1f77b4) |
| ATAC-seq | Orange (#ff7f0e) |
| RNA-seq | Purple (#9467bd) |
| DNA methylation | Teal (#17becf) |

### Scale Considerations

```ini
# Fixed scale for comparisons
[track1]
min_value = 0
max_value = 100

[track2]
min_value = 0
max_value = 100

# Auto scale per track
[track3]
max_value = auto
```

---

## Common Workflows

### ChIP-seq Visualization

```ini
# pyGenomeTracks config for ChIP-seq
[genes]
file = genes.gtf
height = 4
style = UCSC

[H3K27ac_treatment]
file = treatment_H3K27ac.bw
title = H3K27ac Treatment
height = 3
color = #2ca02c

[H3K27ac_control]
file = control_H3K27ac.bw
title = H3K27ac Control
height = 3
color = #1f77b4

[peaks]
file = differential_peaks.bed
title = Differential Peaks
height = 1
color = #d62728
```

### RNA-seq + ATAC-seq Integration

```ini
[genes]
file = genes.gtf
height = 5

[rna_seq]
file = rnaseq_coverage.bw
title = RNA-seq
height = 3
color = #9467bd

[atac_seq]
file = atac_coverage.bw
title = ATAC-seq
height = 3
color = #ff7f0e

[atac_peaks]
file = atac_peaks.narrowPeak
title = ATAC Peaks
height = 1
color = #e377c2
```

---

## Publication Checklist

- [ ] Coordinate system stated (0-based or 1-based)
- [ ] Genome assembly specified (hg38, mm10, etc.)
- [ ] Scale bars/y-axis values shown
- [ ] Track heights proportional to importance
- [ ] Colors consistent with other figures
- [ ] Gene names legible at publication size
- [ ] Region coordinates in figure legend
- [ ] Data processing described in methods
- [ ] Saved as vector format (PDF/SVG)

---

## Cross-References

- **[bioconductor_viz.md](bioconductor_viz.md)**: ggbio for genome visualization
- **[matplotlib.md](matplotlib.md)**: Python plotting fundamentals
- **[ggplot2.md](ggplot2.md)**: R plotting fundamentals
- **[../reproducible-research/SKILL.md](../../reproducible-research/SKILL.md)**: Data deposition standards
