# Scientific Diagram Types Reference

> Catalog of scientific diagram types with use cases and prompt guidance

---

## Study Design & Methodology

### CONSORT Flowchart
**Use case:** Randomized controlled trial participant flow

**Key elements:**
- Enrollment/screening box at top
- Exclusion branch with itemized reasons
- Randomization split into treatment arms
- Follow-up losses per arm
- Final analysis counts

**Prompt keywords:** CONSORT, participant flow, RCT, randomized, exclusion criteria, lost to follow-up

---

### PRISMA Flowchart
**Use case:** Systematic review article screening

**Key elements:**
- Records identified from databases (with counts)
- Duplicates removed
- Records screened → excluded
- Full-text assessed → excluded with reasons
- Studies included in synthesis

**Prompt keywords:** PRISMA, systematic review, screening, inclusion, meta-analysis

---

### Methods Flowchart
**Use case:** General experimental procedure

**Key elements:**
- Sample collection/preparation
- Processing steps in sequence
- Decision points (if applicable)
- Analysis methods
- Output/results

**Prompt keywords:** methods, workflow, experimental procedure, protocol, pipeline

---

## Machine Learning & AI

### Transformer Architecture
**Use case:** Attention-based neural network models

**Key elements:**
- Encoder stack (left): embedding → positional encoding → self-attention → feed-forward
- Decoder stack (right): masked attention → cross-attention → feed-forward
- Cross-attention connections between stacks
- Add & Norm layers

**Prompt keywords:** Transformer, encoder-decoder, self-attention, multi-head attention, BERT, GPT

---

### CNN Architecture
**Use case:** Convolutional neural networks for image processing

**Key elements:**
- Input layer with image dimensions
- Convolutional layers with filter counts
- Pooling layers (max/average)
- Fully connected layers
- Output layer with class count

**Prompt keywords:** CNN, convolutional, pooling, feature maps, image classification, ResNet, VGG

---

### RNN/LSTM Architecture
**Use case:** Sequential data processing

**Key elements:**
- Input sequence representation
- Recurrent connections (loops)
- Hidden state flow
- Cell state (for LSTM)
- Gates: forget, input, output (for LSTM)

**Prompt keywords:** RNN, LSTM, GRU, recurrent, sequence, time series, hidden state

---

### General Neural Network
**Use case:** Multi-layer perceptron or custom architectures

**Key elements:**
- Input layer with feature count
- Hidden layers with neuron counts
- Activation functions
- Dropout layers (if applicable)
- Output layer

**Prompt keywords:** neural network, MLP, perceptron, layers, neurons, deep learning

---

## Biological Systems

### Signaling Pathway
**Use case:** Signal transduction cascades (MAPK, PI3K, Wnt, etc.)

**Key elements:**
- Receptor at membrane
- Kinase cascade (sequential phosphorylation)
- Transcription factor activation
- Nuclear translocation
- Gene expression outcome

**Prompt keywords:** signaling, pathway, phosphorylation, kinase, receptor, transduction, MAPK, PI3K

---

### Metabolic Pathway
**Use case:** Biochemical reaction networks

**Key elements:**
- Substrate → product transformations
- Enzyme names on arrows
- Cofactors (ATP, NAD+, etc.)
- Regulatory feedback loops
- Compartmentalization (cytoplasm, mitochondria)

**Prompt keywords:** metabolism, glycolysis, TCA cycle, enzyme, substrate, product, biochemical

---

### Gene Regulatory Network
**Use case:** Transcriptional regulation

**Key elements:**
- Transcription factors
- Promoter regions
- Activation/repression arrows
- Feedback loops
- Expression outcomes

**Prompt keywords:** gene regulation, transcription factor, promoter, enhancer, expression, network

---

### Protein Interaction Network
**Use case:** Protein-protein interactions

**Key elements:**
- Protein nodes (shapes vary by function)
- Interaction edges (binding, modification)
- Complex formation
- Functional modules/clusters

**Prompt keywords:** protein interaction, PPI, binding, complex, interactome, network

---

## Systems & Engineering

### System Architecture
**Use case:** Software or hardware component organization

**Key elements:**
- Component boxes with labels
- Data flow arrows
- API/interface connections
- External services/databases
- User interface layer

**Prompt keywords:** architecture, system, components, microservices, API, database, cloud

---

### Data Flow Diagram
**Use case:** Information processing flow

**Key elements:**
- Data sources (external entities)
- Processes (transformations)
- Data stores
- Data flows with labels

**Prompt keywords:** data flow, DFD, process, data store, transformation, ETL

---

### Block Diagram
**Use case:** High-level system overview

**Key elements:**
- Functional blocks
- Input/output connections
- Signal flow direction
- Grouping by subsystem

**Prompt keywords:** block diagram, functional, subsystem, signal flow, overview

---

### Circuit Schematic
**Use case:** Electronic circuit design

**Key elements:**
- Standard component symbols (resistor, capacitor, op-amp)
- Component values (1kOhm, 10uF)
- Power rails (Vcc, GND)
- Signal labels
- Node connections

**Prompt keywords:** circuit, schematic, op-amp, resistor, capacitor, electronics, analog, digital

---

## Abstract Concepts

### Conceptual Framework
**Use case:** Theoretical model visualization

**Key elements:**
- Core concepts as shapes
- Relationships between concepts
- Hierarchical organization
- Directional influence arrows

**Prompt keywords:** conceptual, framework, theory, model, relationships, concepts

---

### Hierarchy Diagram
**Use case:** Classification or organizational structure

**Key elements:**
- Root node at top
- Parent-child relationships
- Sibling groupings
- Leaf nodes at bottom

**Prompt keywords:** hierarchy, tree, classification, taxonomy, organizational, structure

---

### Venn Diagram
**Use case:** Set relationships and overlaps

**Key elements:**
- Overlapping circles/ellipses
- Labeled regions
- Intersection areas
- Counts or descriptions per region

**Prompt keywords:** Venn, sets, overlap, intersection, comparison, categories

---

## Complexity Guidelines

| Diagram Type | Max Nodes | Max Edges | Max Levels |
|--------------|-----------|-----------|------------|
| Flowchart | 15 | 20 | 4 |
| Neural network | 12 layers | - | 3 groups |
| Pathway | 10 molecules | 12 reactions | 3 cascades |
| System architecture | 12 components | 15 connections | 3 tiers |
| Block diagram | 10 blocks | 12 arrows | 2 levels |

**When exceeding limits:**
- Split into overview + detail figures
- Use figure panels (a, b, c)
- Create hierarchical zoom views
