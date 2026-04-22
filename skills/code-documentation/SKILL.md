---
name: code-documentation
description: "Documentation for scientific code. Docstrings (Python Google/NumPy, R roxygen2), README generation, notebook best practices, and inline commenting. Use when documenting analysis scripts, creating project READMEs, or writing reproducible notebooks."
---

<objective>
Generate clear, consistent documentation for scientific code that serves both human readers and automated tools. This skill covers function-level documentation (docstrings), project-level documentation (READMEs), and narrative documentation (notebooks).
</objective>

<scope>
**In Scope:**
- Docstring generation (Python: Google, NumPy, Sphinx styles; R: roxygen2)
- README templates for analysis projects, software tools, and data repositories
- Notebook best practices (Jupyter, R Markdown, Quarto)
- Inline commenting guidelines (when and how)
- API documentation for reusable packages

**Out of Scope:**
- Full documentation site generation (Sphinx/pkgdown setup and hosting)
- CI/CD integration for documentation builds
- Documentation translation or localization
</scope>

<setup>
## Dependencies

**Python Documentation:**
- `sphinx.ext.napoleon` - Renders NumPy/Google style docstrings in Sphinx
- `doctest` (stdlib) - Validates docstring examples execute correctly
- `pydocstyle` - Lints docstring format compliance

**R Documentation:**
- `roxygen2` - Standard R package documentation generator
- `devtools` - Package development workflow including doc generation

**Notebooks:**
- Jupyter with `nbconvert` for notebook export
- Quarto for multi-format notebook publishing
- `watermark` extension for environment versioning

**Installation:**
```bash
# Python
pip install sphinx sphinx-rtd-theme pydocstyle

# R
install.packages(c("roxygen2", "devtools"))

# Jupyter extension
pip install watermark
```
</setup>

<documentation_hierarchy>
## Levels of Documentation

### 1. Inline Comments
- **When**: Complex logic that isn't self-evident
- **Style**: Brief, explains "why" not "what"
- **Anti-pattern**: Commenting obvious code (`i += 1  # increment i`)

### 2. Docstrings
- **When**: Every public function, class, module
- **Style**: Structured format (Google, NumPy, or roxygen2)
- **Content**: Purpose, parameters, returns, examples

### 3. README
- **When**: Every project/repository
- **Content**: Purpose, installation, usage, examples, citation

### 4. Notebooks
- **When**: Analysis workflows, tutorials, exploratory work
- **Style**: Narrative flow with code cells

### 5. API Documentation
- **When**: Reusable packages/libraries
- **Tools**: Sphinx (Python), pkgdown (R)
</documentation_hierarchy>

<style_selection>
## Which Docstring Style?

| Context | Recommended Style | Why |
|---------|-------------------|-----|
| Scientific Python | NumPy style | Standard in numpy, scipy, pandas ecosystem |
| General Python | Google style | Clean, readable, less verbose |
| Sphinx documentation | NumPy or Google | Both have Sphinx extensions |
| R packages | roxygen2 | Required for CRAN submission |
| Quick scripts | Minimal | One-line description sufficient |

## Quick Style Decision

```
Is this code for a package/library?
├── Yes → Is it R?
│         ├── Yes → roxygen2
│         └── No → NumPy style (scientific) or Google style (general)
└── No → Is it a one-off script?
          ├── Yes → Minimal docstrings (one-liners)
          └── No → Match the existing codebase style
```
</style_selection>

<readme_structure>
## README Essential Sections

### For Analysis Projects
1. **Title & Description**: What analysis this contains
2. **Data Requirements**: Input data sources and formats
3. **Environment Setup**: How to recreate the environment
4. **Usage**: How to run the analysis
5. **Output**: What files/figures are produced
6. **Citation**: How to cite this work

### For Software Tools
1. **Title & Badges**: Name, CI status, version, license
2. **Description**: What the tool does (one paragraph)
3. **Installation**: pip/conda/source instructions
4. **Quick Start**: Minimal working example
5. **Documentation**: Link to full docs
6. **Contributing**: How to contribute
7. **License & Citation**: Legal and academic credit

### For Data Repositories
1. **Title & DOI**: Dataset name and persistent identifier
2. **Description**: What data this contains
3. **Data Dictionary**: Column/field descriptions
4. **Collection Methods**: How data was generated
5. **Usage Terms**: License and citation requirements
6. **Related Publications**: Papers using this data
</readme_structure>

<notebook_guidelines>
## Notebook Best Practices

### Structure
1. **Title cell**: Clear, descriptive title as H1
2. **Purpose cell**: What this notebook accomplishes
3. **Setup cell**: All imports at the top
4. **Sections**: Logical divisions with markdown headers
5. **Conclusion cell**: Summary of findings

### Code Cells
- One concept per cell
- Cells should be runnable in order
- Use markdown cells to explain complex logic
- Keep cells under 20-30 lines

### Reproducibility
- Set random seeds at the start
- Print package versions (`%load_ext watermark`)
- Use relative paths or document data locations
- Clear outputs before committing (optional, depends on use case)

### Output Management
- Hide code for reports: `#| echo: false` (Quarto)
- Show code for methods: Full visibility
- Limit large outputs with `.head()` or sampling
</notebook_guidelines>

<visualization_documentation>
## Documenting Plotting Code

Coordinate with **plotting-libraries** skill for implementation. This section provides docstring patterns for figure-generating functions.

### Python: NumPy-Style Docstring for Plotting Functions

```python
def plot_group_comparison(
    data: pd.DataFrame,
    x: str,
    y: str,
    hue: str = None,
    figsize: tuple = (8, 6),
    output_path: str = None
) -> plt.Figure:
    """Create a box plot with overlaid data points for group comparisons.

    Generates a publication-ready figure showing distribution of values
    across groups, suitable for t-test or ANOVA results visualization.

    Parameters
    ----------
    data : pd.DataFrame
        Tidy data with one row per observation.
    x : str
        Column name for grouping variable (x-axis).
    y : str
        Column name for continuous variable (y-axis).
    hue : str, optional
        Column name for color-coding subgroups.
    figsize : tuple, default (8, 6)
        Figure size in inches (width, height).
    output_path : str, optional
        If provided, saves figure to this path. Supports PDF, PNG, SVG.

    Returns
    -------
    plt.Figure
        Matplotlib Figure object for further customization.

    Examples
    --------
    >>> fig = plot_group_comparison(df, x='treatment', y='expression')
    >>> fig.savefig('results/expression_by_treatment.pdf')

    >>> # With statistical annotation (requires statannotations)
    >>> fig = plot_group_comparison(df, x='genotype', y='phenotype')

    See Also
    --------
    plotting-libraries : Full visualization patterns
    statistical-analysis : Test selection for group comparisons

    Notes
    -----
    - Uses seaborn boxplot with stripplot overlay
    - Applies oligon-brand color palette if configured
    - For significance annotations, use statannotations package
    """
    # Implementation...
```

### Python: Google-Style Docstring for Plotting Functions

```python
def create_volcano_plot(
    data: pd.DataFrame,
    log2fc_col: str = 'log2FoldChange',
    pval_col: str = 'padj',
    label_col: str = None,
    fc_threshold: float = 1.0,
    pval_threshold: float = 0.05
) -> plt.Figure:
    """Create a volcano plot for differential expression results.

    Args:
        data: DataFrame with log2 fold changes and p-values.
        log2fc_col: Column name for log2 fold change values.
        pval_col: Column name for (adjusted) p-values.
        label_col: Column name for gene labels. If None, no labels shown.
        fc_threshold: Log2 fold change threshold for significance.
        pval_threshold: P-value threshold for significance.

    Returns:
        Matplotlib Figure with volcano plot.

    Raises:
        ValueError: If required columns not found in data.

    Example:
        >>> results = pd.read_csv('deseq2_results.csv')
        >>> fig = create_volcano_plot(results, label_col='gene_symbol')
        >>> fig.savefig('volcano.pdf', dpi=300)
    """
    # Implementation...
```

### R: roxygen2 for Plotting Functions

```r
#' Create a survival curve plot
#'
#' Generates Kaplan-Meier survival curves with risk table and
#' optional confidence intervals, suitable for clinical publications.
#'
#' @param data A data frame with survival data.
#' @param time_col Name of column containing survival times.
#' @param event_col Name of column containing event indicators (0/1).
#' @param group_col Optional grouping variable for stratified curves.
#' @param conf_int Logical; show confidence intervals? Default TRUE.
#' @param risk_table Logical; show risk table below plot? Default TRUE.
#' @param palette Color palette name or vector. Default "npg" (Nature).
#'
#' @return A ggsurvplot object (list with plot and table components).
#'
#' @examples
#' library(survival)
#' fit <- survfit(Surv(time, status) ~ sex, data = lung)
#' plot_survival(lung, "time", "status", "sex")
#'
#' @seealso
#' \code{\link[survminer]{ggsurvplot}} for underlying implementation.
#' See statistical-analysis skill for survival analysis methods.
#'
#' @export
plot_survival <- function(data, time_col, event_col, group_col = NULL,
                          conf_int = TRUE, risk_table = TRUE,
                          palette = "npg") {
    # Implementation...
}
```

### Key Documentation Elements for Plots

| Element | Why It Matters |
|---------|----------------|
| **Parameter types** | Clarifies expected input format |
| **Defaults** | Shows what happens if omitted |
| **Output format** | Specifies return type (Figure, Axes, path) |
| **File formats** | Lists supported export formats |
| **Examples** | Shows typical usage pattern |
| **See Also** | Links to related skills/functions |
| **Notes** | Implementation details, dependencies |

### Anti-Patterns to Avoid

```python
# BAD: No documentation
def make_plot(data, x, y):
    return sns.boxplot(data=data, x=x, y=y)

# BAD: Useless documentation
def make_plot(data, x, y):
    """Makes a plot."""  # Says nothing useful
    return sns.boxplot(data=data, x=x, y=y)

# GOOD: Useful documentation (see examples above)
```

</visualization_documentation>

<usage_patterns>
## When to Apply This Skill

1. **Starting a new project**: "Create a README for my RNA-seq analysis project"
2. **Documenting functions**: "Write NumPy-style docstrings for these analysis functions"
3. **Code review preparation**: "Add appropriate documentation to this script"
4. **Publishing code**: "Prepare this code for a GitHub release with proper docs"
5. **Creating tutorials**: "Structure this notebook as a teaching resource"

## Integration with Other Skills

- After writing analysis code with `statistical-analysis`
- Before publishing with `reproducible-research`
- When preparing Methods sections with `scientific-writing`
</usage_patterns>

<validation>
## Verification Steps

### Automated Validation (Recommended)

Use the built-in validation scripts for consistent, deterministic checks:

```bash
# Validate Python docstrings (auto-detects or specify style)
uv run python skills/code-documentation/scripts/validate_documentation.py module.py
uv run python skills/code-documentation/scripts/validate_documentation.py module.py --style numpy

# Validate README completeness (auto-detects or specify project type)
uv run python skills/code-documentation/scripts/validate_documentation.py --readme README.md
uv run python skills/code-documentation/scripts/validate_documentation.py --readme README.md --project-type analysis

# Validate entire project (docstrings + README)
uv run python skills/code-documentation/scripts/validate_documentation.py /path/to/project --all

# Infer recommended docstring style for a project
uv run python skills/code-documentation/scripts/validate_documentation.py /path/to/project --infer-style

# Skip doctests for faster validation
uv run python skills/code-documentation/scripts/validate_documentation.py module.py --no-tests
```

**Validation outputs:**
- **Docstring coverage**: Percentage of public functions/classes documented
- **pydocstyle compliance**: Format errors by convention (NumPy/Google)
- **Doctest results**: Pass/fail for executable examples
- **README score**: 0-100 based on required (80%) and optional (20%) sections

### Manual Verification (Alternative)

If automated tools are unavailable:

1. **Validate examples execute:**
   ```bash
   python -m doctest -v <module.py>
   ```

2. **Check format compliance:**
   ```bash
   pydocstyle --convention=numpy <module.py>
   # or for Google style:
   pydocstyle --convention=google <module.py>
   ```

3. **Test Sphinx rendering** (if applicable):
   ```bash
   cd docs && make html
   # Review _build/html/index.html
   ```

### After Generating README

Verify all essential sections are present:

- [ ] Title clearly describes the project
- [ ] Purpose/description is concise (one paragraph)
- [ ] Installation instructions are copy-pasteable
- [ ] Quick start example actually runs
- [ ] All external links resolve
- [ ] Citation information included (if academic)
- [ ] License specified

### After Documenting Notebooks

- [ ] Kernel can "Restart and Run All" without errors
- [ ] Random seeds set for reproducibility
- [ ] Package versions documented (watermark or requirements)
- [ ] All markdown cells render correctly
- [ ] Outputs are appropriate (not truncated, not excessive)
- [ ] Relative paths work from repo root

### R Documentation Validation

```r
# Generate and check documentation
devtools::document()
devtools::check()  # Includes documentation checks
```
</validation>

<input_schema>
## Structured Input Format

For deterministic documentation generation, provide structured inputs:

### Docstring Generation Request

```yaml
task: generate_docstring
target:
  file: "path/to/module.py"
  function: "function_name"  # or class: "ClassName"
style: numpy | google | minimal  # Use --infer-style if unsure
include:
  - parameters      # Document all parameters
  - returns         # Document return value
  - raises          # Document exceptions (if any)
  - examples        # Include runnable example
  - see_also        # Cross-references (optional)
  - notes           # Implementation notes (optional)
```

### README Generation Request

```yaml
task: generate_readme
project_type: analysis | software | data_repo | compendium
project_path: "/path/to/project"
include:
  title: true
  description: true
  installation: true      # Required for software
  usage: true
  data_requirements: true # Required for analysis/data_repo
  output: true            # Required for analysis
  citation: true
  license: true
```

### Style Inference Request

```yaml
task: infer_style
project_path: "/path/to/project"
output: recommendation | detailed_report
```

### Batch Documentation Request

```yaml
task: document_project
project_path: "/path/to/project"
scope:
  - docstrings    # All public functions/classes
  - readme        # Project README
  - inline        # Inline comments for complex logic
style: auto       # Infer from project or specify
validation: true  # Run validation after generation
```
</input_schema>

<output_schema>
## Output Format Specifications

### Docstring Section Order

Documentation must follow canonical section ordering by style:

**NumPy Style:**
1. Short summary (required)
2. Extended summary (optional)
3. Parameters (required if function has params)
4. Returns (required if non-None return)
5. Yields (required if generator)
6. Raises (optional)
7. See Also (optional)
8. Notes (optional)
9. References (optional)
10. Examples (recommended)

**Google Style:**
1. Summary (required)
2. Args (required if function has params)
3. Returns (required if non-None return)
4. Raises (optional)
5. Example (recommended)

### README Section Order

**Analysis Projects:**
1. Title & Description
2. Data Requirements
3. Environment Setup
4. Usage
5. Output
6. Citation

**Software Tools:**
1. Title & Badges
2. Description
3. Installation
4. Quick Start
5. Documentation
6. Contributing
7. License & Citation

**Data Repositories:**
1. Title & DOI
2. Description
3. Data Dictionary
4. Collection Methods
5. Usage Terms
6. Related Publications

### Validation Report Format

```json
{
  "file": "path/to/module.py",
  "style": "numpy",
  "coverage": {
    "total_items": 10,
    "documented": 8,
    "percentage": 80.0
  },
  "pydocstyle": {
    "errors": 2,
    "warnings": 1,
    "issues": [
      {"code": "D100", "line": 1, "message": "Missing docstring in public module"}
    ]
  },
  "doctests": {
    "total": 5,
    "passed": 4,
    "failed": 1,
    "failures": [
      {"function": "calculate_mean", "error": "Expected 2.5, got 2.0"}
    ]
  },
  "readme_score": 85,
  "missing_sections": ["contributing"]
}
```
</output_schema>

<quality_standards>
## Documentation Quality Standards

### Density and Focus
- **Appropriate commenting**: Explain "why" not "what"—code should be self-documenting for mechanics
- **Complete public API**: Every public function, class, and module has a docstring
- **Current and accurate**: Documentation reflects actual behavior (update docs with code changes)

### Clarity and Accessibility
- **Include working examples**: Every function docstring contains a runnable example
- **Define domain terms**: Explain scientific terminology that may be unfamiliar
- **Consistent style**: Use one docstring style (NumPy or Google) throughout a project

### Quality Signals

Well-documented code:
- Can be understood without reading the implementation
- Includes examples that actually run
- Explains *why*, not just *what*
- Is updated when code changes
- Uses consistent formatting throughout

### Quick Self-Check

Before finalizing documentation, verify:
1. Would a new team member understand this without asking questions?
2. Do examples copy-paste and run successfully?
3. Are scientific terms defined or linked to definitions?
4. Does the style match the rest of the codebase?
</quality_standards>

<cross_references>
## Related Skills

**Skill Selection:** See `SKILL_ROUTER.md` for decision trees when multiple skills may apply.

| Skill | When to Use Together | Handoff Pattern |
|-------|---------------------|-----------------|
| **reproducible-research** | Setting up project structure | Use reproducible-research for directory layout and environment files, then code-documentation for README and docstrings |
| **scientific-writing** | Preparing Methods sections | Document code first, then use scientific-writing to translate implementation details into prose |
| **statistical-analysis** | Documenting analysis choices | Reference statistical-analysis for method selection rationale to include in docstrings |
| **plotting-libraries** | Figure-generating functions | See `<visualization_documentation>` section above for docstring patterns specific to plotting code |

### Workflow Integration

```
[Write Code] → code-documentation → [Docstrings, README]
                     ↓
              reproducible-research → [Environment, Structure]
                     ↓
              scientific-writing → [Methods Section]
```
</cross_references>
