"""Tests for plotting parameter lookups."""

import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from plotting_params import (  # noqa: E402
    RANDOM_SEED,
    ClusteringParams,
    JournalFigureSpec,
    ThresholdPreset,
    VolcanoThresholds,
    classify_ecosystem,
    classify_plot_type,
    get_clustering_params,
    get_figsize_for_journal,
    get_journal_spec,
    get_palette,
    get_random_seed,
    get_volcano_colors,
    get_volcano_thresholds,
    mm_to_inches,
)


class TestVolcanoThresholds:
    """Tests for volcano plot threshold lookups."""

    def test_standard_preset(self):
        """Standard preset should return 0.05 pvalue and 1.0 log2fc."""
        t = get_volcano_thresholds("standard")
        assert t.pvalue == 0.05
        assert t.log2fc == 1.0
        assert isinstance(t, VolcanoThresholds)

    def test_exploratory_preset(self):
        """Exploratory preset should return 0.05 pvalue and 0.585 log2fc."""
        t = get_volcano_thresholds("exploratory")
        assert t.pvalue == 0.05
        assert t.log2fc == 0.585

    def test_stringent_preset(self):
        """Stringent preset should return 0.01 pvalue and 1.5 log2fc."""
        t = get_volcano_thresholds("stringent")
        assert t.pvalue == 0.01
        assert t.log2fc == 1.5

    def test_very_stringent_preset(self):
        """Very stringent preset should return 0.001 pvalue and 2.0 log2fc."""
        t = get_volcano_thresholds("very_stringent")
        assert t.pvalue == 0.001
        assert t.log2fc == 2.0

    def test_invalid_preset_returns_standard(self):
        """Invalid preset should fall back to standard."""
        t = get_volcano_thresholds("invalid")
        assert t.pvalue == 0.05
        assert t.log2fc == 1.0

    def test_default_is_standard(self):
        """Default (no argument) should return standard preset."""
        t = get_volcano_thresholds()
        assert t.pvalue == 0.05
        assert t.log2fc == 1.0

    def test_threshold_preset_enum(self):
        """ThresholdPreset enum should have correct values."""
        assert ThresholdPreset.STANDARD.value == "standard"
        assert ThresholdPreset.STRINGENT.value == "stringent"

    def test_volcano_thresholds_immutable(self):
        """VolcanoThresholds should be frozen/immutable."""
        t = get_volcano_thresholds("standard")
        with pytest.raises(AttributeError):
            t.pvalue = 0.1  # type: ignore


class TestJournalSpecs:
    """Tests for journal figure specifications."""

    def test_nature_specs(self):
        """Nature specs should match documented values."""
        spec = get_journal_spec("nature")
        assert spec.single_column_mm == 89
        assert spec.double_column_mm == 183
        assert spec.min_dpi == 300
        assert spec.preferred_format == "pdf"
        assert isinstance(spec, JournalFigureSpec)

    def test_cell_specs(self):
        """Cell specs should match documented values."""
        spec = get_journal_spec("cell")
        assert spec.single_column_mm == 85
        assert spec.double_column_mm == 174

    def test_science_specs(self):
        """Science specs should prefer EPS format."""
        spec = get_journal_spec("science")
        assert spec.preferred_format == "eps"

    def test_plos_specs(self):
        """PLOS specs should prefer TIFF format."""
        spec = get_journal_spec("plos")
        assert spec.preferred_format == "tiff"

    def test_case_insensitive(self):
        """Journal lookup should be case-insensitive."""
        assert get_journal_spec("Nature") == get_journal_spec("nature")
        assert get_journal_spec("NATURE") == get_journal_spec("nature")

    def test_unknown_journal_returns_default(self):
        """Unknown journal should return default specs."""
        spec = get_journal_spec("unknown_journal")
        default = get_journal_spec("default")
        assert spec == default

    def test_journal_spec_immutable(self):
        """JournalFigureSpec should be frozen/immutable."""
        spec = get_journal_spec("nature")
        with pytest.raises(AttributeError):
            spec.min_dpi = 150  # type: ignore


class TestMmToInches:
    """Tests for mm to inches conversion."""

    def test_nature_single_column(self):
        """89mm should convert to approximately 3.5 inches."""
        result = mm_to_inches(89)
        assert abs(result - 3.504) < 0.01

    def test_zero(self):
        """0mm should be 0 inches."""
        assert mm_to_inches(0) == 0

    def test_25_4_mm(self):
        """25.4mm should be exactly 1 inch."""
        assert mm_to_inches(25.4) == 1.0


class TestGetFigsizeForJournal:
    """Tests for journal figsize calculation."""

    def test_nature_single_column(self):
        """Nature single column should return correct figsize."""
        width, height = get_figsize_for_journal("nature", "single")
        assert abs(width - 3.504) < 0.01
        # Height should be golden ratio
        assert abs(height - width / 1.618) < 0.01

    def test_double_column(self):
        """Double column should use double_column_mm."""
        width, height = get_figsize_for_journal("nature", "double")
        assert width > get_figsize_for_journal("nature", "single")[0]

    def test_custom_height(self):
        """Custom height should be respected."""
        width, height = get_figsize_for_journal("nature", "single", height_mm=60)
        assert abs(height - mm_to_inches(60)) < 0.01


class TestColorPalettes:
    """Tests for color palette lookups."""

    def test_oligon_palette(self):
        """Oligon palette should be default."""
        p = get_palette("oligon")
        assert p.name == "Oligon Brand"
        assert p.colorblind_safe is True
        assert len(p.colors) == 5

    def test_okabe_ito_palette(self):
        """Okabe-Ito palette should have 7 colors."""
        p = get_palette("okabe_ito")
        assert len(p.colors) == 7
        assert p.colorblind_safe is True

    def test_volcano_palette(self):
        """Volcano palette should have 3 colors (Up, Down, NS)."""
        p = get_palette("volcano")
        assert len(p.colors) == 3

    def test_default_is_oligon(self):
        """Default palette should be Oligon."""
        p = get_palette()
        assert p.name == "Oligon Brand"

    def test_invalid_palette_returns_oligon(self):
        """Invalid palette name should return Oligon."""
        p = get_palette("nonexistent")
        assert p.name == "Oligon Brand"

    def test_case_insensitive(self):
        """Palette lookup should be case-insensitive."""
        assert get_palette("OKABE_ITO") == get_palette("okabe_ito")


class TestVolcanoColors:
    """Tests for volcano plot colors."""

    def test_volcano_colors_dict(self):
        """get_volcano_colors should return dict with Up, Down, NS keys."""
        colors = get_volcano_colors()
        assert "Up" in colors
        assert "Down" in colors
        assert "NS" in colors

    def test_colors_are_hex(self):
        """All colors should be valid hex codes."""
        colors = get_volcano_colors()
        for color in colors.values():
            assert color.startswith("#")
            assert len(color) == 7


class TestClusteringParams:
    """Tests for clustering parameter lookups."""

    def test_expression_params(self):
        """Expression clustering should use correlation metric."""
        params = get_clustering_params("expression")
        assert params.method == "ward"
        assert params.metric == "correlation"
        assert isinstance(params, ClusteringParams)

    def test_euclidean_params(self):
        """Euclidean clustering should use euclidean metric."""
        params = get_clustering_params("euclidean")
        assert params.metric == "euclidean"

    def test_robust_params(self):
        """Robust clustering should use average linkage."""
        params = get_clustering_params("robust")
        assert params.method == "average"
        assert params.metric == "manhattan"

    def test_default_is_expression(self):
        """Default should be expression clustering."""
        params = get_clustering_params()
        assert params.metric == "correlation"

    def test_invalid_returns_expression(self):
        """Invalid data type should return expression params."""
        params = get_clustering_params("invalid")
        assert params.metric == "correlation"


class TestPlotTypeClassifier:
    """Tests for plot type classification."""

    def test_volcano_detection(self):
        """Volcano-related keywords should classify as volcano."""
        assert classify_plot_type("create a volcano plot") == "volcano"
        assert classify_plot_type("DESeq2 results visualization") == "volcano"
        assert classify_plot_type("differential expression analysis") == "volcano"
        assert classify_plot_type("fold change plot") == "volcano"

    def test_heatmap_detection(self):
        """Heatmap-related keywords should classify as heatmap."""
        assert classify_plot_type("expression heatmap with clustering") == "heatmap"
        assert classify_plot_type("use ComplexHeatmap") == "heatmap"
        assert classify_plot_type("clustermap of genes") == "heatmap"

    def test_survival_detection(self):
        """Survival-related keywords should classify as survival."""
        assert classify_plot_type("Kaplan-Meier curve") == "survival"
        assert classify_plot_type("survival analysis plot") == "survival"
        assert classify_plot_type("cox regression visualization") == "survival"

    def test_genome_tracks_detection(self):
        """Genome track keywords should classify as genome_tracks."""
        assert classify_plot_type("genome browser view") == "genome_tracks"
        assert classify_plot_type("pygenometracks figure") == "genome_tracks"

    def test_statistical_detection(self):
        """Statistical plot keywords should classify as statistical."""
        assert classify_plot_type("boxplot with significance") == "statistical"
        assert classify_plot_type("violin plot comparison") == "statistical"
        assert classify_plot_type("correlation matrix") == "statistical"

    def test_pca_umap_detection(self):
        """Dimensionality reduction keywords should classify as pca_umap."""
        assert classify_plot_type("PCA plot of samples") == "pca_umap"
        assert classify_plot_type("UMAP embedding") == "pca_umap"

    def test_general_fallback(self):
        """Unrecognized requests should return general."""
        assert classify_plot_type("make me a chart") == "general"
        assert classify_plot_type("visualize data") == "general"

    def test_case_insensitive(self):
        """Classification should be case-insensitive."""
        assert classify_plot_type("VOLCANO PLOT") == "volcano"
        assert classify_plot_type("Heatmap") == "heatmap"


class TestEcosystemClassifier:
    """Tests for ecosystem classification."""

    def test_python_detection(self):
        """Python-related keywords should return python."""
        assert classify_ecosystem("use matplotlib") == "python"
        assert classify_ecosystem("seaborn heatmap") == "python"
        assert classify_ecosystem("pandas dataframe") == "python"
        assert classify_ecosystem("jupyter notebook") == "python"

    def test_r_detection(self):
        """R-related keywords should return r."""
        assert classify_ecosystem("ggplot2 figure") == "r"
        assert classify_ecosystem("ComplexHeatmap for my data") == "r"
        assert classify_ecosystem("Bioconductor package") == "r"
        assert classify_ecosystem("DESeq2 analysis") == "r"

    def test_auto_when_unclear(self):
        """Ambiguous requests should return auto."""
        assert classify_ecosystem("make a bar chart") == "auto"
        assert classify_ecosystem("create visualization") == "auto"

    def test_data_context(self):
        """Data context should influence classification."""
        assert classify_ecosystem("make plot", data_context="from DESeq2") == "r"
        assert classify_ecosystem("make plot", data_context="pandas df") == "python"


class TestRandomSeed:
    """Tests for random seed constant."""

    def test_random_seed_value(self):
        """RANDOM_SEED should be 42."""
        assert RANDOM_SEED == 42

    def test_get_random_seed(self):
        """get_random_seed should return 42."""
        assert get_random_seed() == 42

    def test_deterministic(self):
        """Random seed should always be the same value."""
        seeds = [get_random_seed() for _ in range(10)]
        assert all(s == 42 for s in seeds)
