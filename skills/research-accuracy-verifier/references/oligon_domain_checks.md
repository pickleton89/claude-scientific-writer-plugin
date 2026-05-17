# Special domain handling — Oligon / aptamer-siRNA / immuno-oncology

When document content concerns aptamer-siRNA chimera biology, T-cell exhaustion, immune checkpoint biology, or oncology preclinical models, apply additional domain-specific checks on top of the standard pipeline.

## Aptamer claims

- Length, modifications (2′-F, 2′-OMe, LNA, PS backbone), chemistry are accurately described and consistent with cited source

## siRNA design

- Strand polarity (sense / antisense / guide / passenger usage)
- Modification chemistry
- IC50 reporting conventions
- Off-target predictions

## Cell-line provenance

- ATCC / JCRB / DSMZ IDs where relevant
- Flag known misidentified lines (cross-check via Cellosaurus in [Stage 6](./stages/stage_6_sanity.md))

## Mouse model nomenclature

- Official Jackson / Charles River strain designations
- Verify syngeneic model ↔ host strain compatibility:
  - CT26 ↔ BALB-c
  - MC38 ↔ C57BL-6
  - B16 ↔ C57BL-6
  - 4T1 ↔ BALB-c
  - ID8 ↔ C57BL-6

## Statistical tests

- Appropriateness for described data type (parametric vs. non-parametric, paired vs. unpaired, multiple-comparison correction)

## Antibody / clone identifiers

- RRIDs preferred
- Flag claims requiring validation when no clone is named
