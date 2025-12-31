# Docker and Containers Reference Guide

> Containerization for reproducible scientific computing

---

## Overview

Containers package software and dependencies into isolated, reproducible units. Docker is the standard for development; Singularity/Apptainer is the standard for HPC.

### When to Use Containers

| Scenario | Recommendation |
|----------|----------------|
| Local analysis | Conda environment often sufficient |
| Sharing with collaborators | Container recommended |
| HPC cluster | Singularity/Apptainer required |
| Cloud deployment | Docker required |
| Publication | Container strongly recommended |
| Complex dependencies | Container essential |

### Docker vs Singularity/Apptainer

| Feature | Docker | Singularity/Apptainer |
|---------|--------|----------------------|
| Root required | Build: No, Run: Yes (or rootless) | No |
| HPC compatible | Limited | Yes |
| GPU support | Good | Good |
| Security model | Daemon-based | User namespace |
| Image format | Layers | Single file (.sif) |

---

## Dockerfile Basics

### Minimal Dockerfile

```dockerfile
# Base image
FROM python:3.10-slim

# Install dependencies
RUN pip install numpy pandas scipy

# Set working directory
WORKDIR /app

# Copy analysis code
COPY . /app

# Default command
CMD ["python", "analysis.py"]
```

### Dockerfile for Bioinformatics

```dockerfile
# Use Miniconda base
FROM continuumio/miniconda3:23.5.2-0

# Metadata
LABEL maintainer="researcher@university.edu"
LABEL version="1.0.0"
LABEL description="RNA-seq analysis pipeline"

# Copy environment file
COPY environment.yml /tmp/environment.yml

# Create conda environment
RUN conda env create -f /tmp/environment.yml && \
    conda clean -afy && \
    rm /tmp/environment.yml

# Activate environment by default
ENV PATH=/opt/conda/envs/rnaseq/bin:$PATH
ENV CONDA_DEFAULT_ENV=rnaseq

# Set working directory
WORKDIR /data

# Default shell with conda
SHELL ["conda", "run", "-n", "rnaseq", "/bin/bash", "-c"]

# Verify installation
RUN python --version && \
    star --version && \
    samtools --version

# Entry point
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "rnaseq"]
CMD ["bash"]
```

### Multi-Stage Build (Smaller Images)

```dockerfile
# Build stage
FROM continuumio/miniconda3:23.5.2-0 AS builder

COPY environment.yml /tmp/
RUN conda env create -f /tmp/environment.yml && \
    conda clean -afy

# Pack environment
RUN conda install -c conda-forge conda-pack && \
    conda-pack -n rnaseq -o /tmp/env.tar.gz

# Runtime stage
FROM debian:bullseye-slim

# Install minimal runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1-mesa-glx \
        libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Unpack environment
COPY --from=builder /tmp/env.tar.gz /opt/conda/
RUN mkdir -p /opt/conda && \
    cd /opt/conda && \
    tar -xzf env.tar.gz && \
    rm env.tar.gz && \
    /opt/conda/bin/conda-unpack

ENV PATH=/opt/conda/bin:$PATH

WORKDIR /data
CMD ["bash"]
```

---

## Best Practices for Reproducibility

### 1. Pin Base Image Versions

```dockerfile
# BAD - changes over time
FROM python:3.10

# GOOD - specific digest
FROM python:3.10.12-slim-bullseye@sha256:abc123...

# ACCEPTABLE - specific tag
FROM python:3.10.12-slim-bullseye
```

### 2. Pin All Package Versions

```dockerfile
# BAD
RUN pip install numpy pandas

# GOOD - use requirements.txt with versions
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# requirements.txt:
# numpy==1.24.3
# pandas==2.0.2
```

### 3. Minimize Layers and Clean Up

```dockerfile
# BAD - multiple layers, no cleanup
RUN apt-get update
RUN apt-get install -y package1
RUN apt-get install -y package2
RUN rm -rf /var/lib/apt/lists/*

# GOOD - single layer with cleanup
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        package1 \
        package2 && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean
```

### 4. Use .dockerignore

```
# .dockerignore
.git/
.gitignore
*.pyc
__pycache__/
*.egg-info/
dist/
build/
.env
.venv/
data/raw/
results/
*.log
```

### 5. Add Metadata Labels

```dockerfile
LABEL org.opencontainers.image.title="RNA-seq Analysis"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.description="RNA-seq pipeline"
LABEL org.opencontainers.image.authors="researcher@university.edu"
LABEL org.opencontainers.image.source="https://github.com/user/repo"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.created="2024-01-15"
```

### 6. Non-Root User

```dockerfile
# Create non-root user
RUN groupadd -r analysis && \
    useradd -r -g analysis -d /home/analysis -m analysis

# Switch to non-root user
USER analysis

WORKDIR /home/analysis
```

---

## Building and Running

### Build Commands

```bash
# Basic build
docker build -t myimage:1.0 .

# Build with build arguments
docker build \
    --build-arg PYTHON_VERSION=3.10 \
    -t myimage:1.0 .

# Build with specific Dockerfile
docker build -f Dockerfile.analysis -t myimage:1.0 .

# Build and push
docker build -t username/myimage:1.0 .
docker push username/myimage:1.0

# Build for multiple platforms
docker buildx build \
    --platform linux/amd64,linux/arm64 \
    -t username/myimage:1.0 \
    --push .
```

### Run Commands

```bash
# Interactive shell
docker run -it myimage:1.0 bash

# Mount data directory
docker run -it \
    -v /path/to/data:/data \
    -v /path/to/results:/results \
    myimage:1.0 bash

# Run specific command
docker run \
    -v $(pwd)/data:/data \
    myimage:1.0 \
    python analysis.py --input /data/sample.fastq

# With GPU support
docker run --gpus all \
    -v $(pwd)/data:/data \
    myimage:1.0

# Resource limits
docker run \
    --memory=16g \
    --cpus=4 \
    -v $(pwd)/data:/data \
    myimage:1.0
```

### Docker Compose

```yaml
# docker-compose.yml
version: "3.8"

services:
  analysis:
    build:
      context: .
      dockerfile: Dockerfile
    volumes:
      - ./data:/data
      - ./results:/results
    environment:
      - PYTHONPATH=/app
    command: python analysis.py

  jupyter:
    build:
      context: .
    ports:
      - "8888:8888"
    volumes:
      - ./notebooks:/notebooks
      - ./data:/data
    command: jupyter notebook --ip=0.0.0.0 --allow-root
```

---

## Singularity/Apptainer for HPC

### Convert Docker to Singularity

```bash
# Pull from Docker Hub
singularity pull docker://username/myimage:1.0

# Creates: myimage_1.0.sif

# Pull from local Docker
singularity pull docker-daemon://myimage:1.0
```

### Singularity Definition File

```singularity
Bootstrap: docker
From: continuumio/miniconda3:23.5.2-0

%labels
    Author researcher@university.edu
    Version 1.0.0
    Description RNA-seq analysis container

%files
    environment.yml /opt/environment.yml

%post
    # Install conda environment
    conda env create -f /opt/environment.yml
    conda clean -afy
    rm /opt/environment.yml

    # Clean up
    apt-get clean
    rm -rf /var/lib/apt/lists/*

%environment
    export PATH=/opt/conda/envs/rnaseq/bin:$PATH
    export CONDA_DEFAULT_ENV=rnaseq

%runscript
    exec "$@"

%test
    python --version
    star --version
```

### Build Singularity Image

```bash
# Build (requires root or fakeroot)
sudo singularity build myimage.sif Singularity.def

# Build with fakeroot (no sudo)
singularity build --fakeroot myimage.sif Singularity.def

# Build in sandbox for testing
singularity build --sandbox myimage/ Singularity.def
```

### Run Singularity

```bash
# Interactive shell
singularity shell myimage.sif

# Execute command
singularity exec myimage.sif python analysis.py

# With bind mounts
singularity exec \
    --bind /scratch/data:/data \
    --bind /scratch/results:/results \
    myimage.sif python analysis.py

# With GPU
singularity exec --nv myimage.sif python gpu_analysis.py

# Run default runscript
singularity run myimage.sif
```

### HPC Job Script (SLURM)

```bash
#!/bin/bash
#SBATCH --job-name=rnaseq
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=24:00:00
#SBATCH --output=logs/%x_%j.out

# Load Singularity module (HPC-specific)
module load singularity

# Run analysis in container
singularity exec \
    --bind $SCRATCH/data:/data \
    --bind $SCRATCH/results:/results \
    --bind $TMPDIR:/tmp \
    $HOME/containers/rnaseq.sif \
    python /app/analysis.py \
        --input /data/sample.fastq \
        --output /results/output \
        --threads $SLURM_CPUS_PER_TASK
```

---

## Container Registries

### Public Registries

| Registry | URL | Best For |
|----------|-----|----------|
| Docker Hub | hub.docker.com | General, widely used |
| Quay.io | quay.io | Enterprise, security |
| GitHub Container Registry | ghcr.io | GitHub integration |
| BioContainers | biocontainers.pro | Bioinformatics tools |

### BioContainers

Pre-built containers for bioinformatics tools:

```bash
# Docker
docker pull biocontainers/star:2.7.10b--h9ee0642_0

# Singularity
singularity pull docker://biocontainers/star:2.7.10b--h9ee0642_0

# Multi-package containers
docker pull biocontainers/mulled-v2-xxx:tag
```

### Pushing to Registry

```bash
# Docker Hub
docker login
docker tag myimage:1.0 username/myimage:1.0
docker push username/myimage:1.0

# GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u username --password-stdin
docker tag myimage:1.0 ghcr.io/username/myimage:1.0
docker push ghcr.io/username/myimage:1.0
```

---

## Reproducibility Checklist

### Dockerfile Checklist

```markdown
## Container Reproducibility Checklist

### Base Image
- [ ] Using specific version tag (not :latest)
- [ ] Ideally using digest (@sha256:...)
- [ ] Using appropriate base (slim for size, full for development)

### Dependencies
- [ ] All packages have pinned versions
- [ ] Using requirements.txt or environment.yml
- [ ] Build arguments for configurable versions
- [ ] Cleanup of package manager caches

### Metadata
- [ ] LABEL with author, version, description
- [ ] LABEL with source repository URL
- [ ] LABEL with creation date

### Security
- [ ] Running as non-root user where possible
- [ ] Minimal packages installed
- [ ] No secrets in Dockerfile

### Documentation
- [ ] README with build instructions
- [ ] README with run examples
- [ ] Environment variables documented
- [ ] Volume mounts documented

### Testing
- [ ] Test stage or healthcheck
- [ ] CI/CD builds image
- [ ] Image pushed to registry
```

### Container Registry Checklist

```markdown
## Publication Checklist

- [ ] Container pushed to persistent registry
- [ ] Version tagged (not just :latest)
- [ ] Container referenced in publication
- [ ] DOI obtained (Zenodo for containers)
- [ ] Build files (Dockerfile) in repository
- [ ] README with usage instructions
```

---

## Common Patterns

### Jupyter Notebook Container

```dockerfile
FROM jupyter/scipy-notebook:python-3.10

USER root

# Install additional packages
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential && \
    rm -rf /var/lib/apt/lists/*

USER $NB_UID

# Set working directory
WORKDIR /home/jovyan/work

# Install Jupyter extensions
RUN pip install jupyter_contrib_nbextensions && \
    jupyter contrib nbextension install --user
```

### R Analysis Container

```dockerfile
FROM rocker/r-ver:4.2.3

# Install system dependencies for R packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libcurl4-openssl-dev \
        libssl-dev \
        libxml2-dev \
        libfontconfig1-dev \
        libharfbuzz-dev \
        libfribidi-dev && \
    rm -rf /var/lib/apt/lists/*

# Install R packages
RUN R -e "install.packages(c('tidyverse', 'DESeq2', 'pheatmap'), \
    repos='https://cloud.r-project.org')"

# Install Bioconductor packages
RUN R -e "BiocManager::install(c('DESeq2', 'edgeR', 'clusterProfiler'))"

WORKDIR /data
CMD ["R"]
```

### GPU Container (PyTorch)

```dockerfile
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

# Install additional packages
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /app
CMD ["python"]
```

---

## Troubleshooting

### Common Issues

```bash
# Permission denied on mounted volumes
# Solution: match UID/GID or use --user
docker run --user $(id -u):$(id -g) -v $(pwd):/data myimage

# Out of disk space
docker system prune -a --volumes

# Container exiting immediately
# Check if CMD/ENTRYPOINT is correct
docker run -it myimage bash

# GPU not available
# Ensure --gpus flag and nvidia-container-toolkit installed
docker run --gpus all myimage nvidia-smi
```

### Debugging

```bash
# Enter running container
docker exec -it <container_id> bash

# View logs
docker logs <container_id>

# Inspect image
docker inspect myimage:1.0

# History of layers
docker history myimage:1.0
```

---

## Quick Reference

```bash
# BUILD
docker build -t myimage:1.0 .
singularity build myimage.sif Singularity.def

# RUN
docker run -it -v $(pwd)/data:/data myimage:1.0 bash
singularity exec --bind data:/data myimage.sif bash

# PUSH
docker push username/myimage:1.0
singularity push myimage.sif library://user/collection/image:1.0

# CONVERT
singularity pull docker://username/myimage:1.0

# CLEAN
docker system prune -a --volumes
```
