# =============================================================================
# Oligon Brand Adapter for ggplot2
#
# This script provides functions and scales for applying Oligon scientific
# brand identity to ggplot2 visualizations.
#
# Usage:
#   source("path/to/ggplot2_adapter.R")
#
#   ggplot(data, aes(x, y, color = group)) +
#     geom_point() +
#     scale_color_brand_treatment() +
#     theme_brand()
# =============================================================================

library(ggplot2)
library(scales)

# =============================================================================
# BRAND COLOR DEFINITIONS
# =============================================================================

brand_colors <- list(
  # Primary highlight
  brand_blue = "#2DB2E8",

  # Neutrals (for data)
  dark_gray = "#222222",
  medium_gray = "#666666",
  muted_gray = "#999999",
  light_gray = "#BDBDBD",  # annotations only

  # Contrast
  contrast_orange = "#E8622D",
  dark_warm = "#7D250F",

  # Supporting blues
  medium_blue = "#158BBB",
  dark_teal = "#0F5D7D",

  # Structure
  black = "#000000",
  white = "#FFFFFF",
  gridline = "#E5E5E5"
)

# =============================================================================
# COLOR CYCLES
# =============================================================================

# Cycle 1: Treatment vs Control (most common)
cycle_treatment_control <- c(
  "Control" = "#222222",
  "Treatment" = "#2DB2E8",
  "Secondary" = "#666666"
)

# Cycle 2: Neutrals only (no designated highlight)
cycle_neutrals <- c("#222222", "#666666", "#999999")

# Cycle 3: Opposing effects (blue vs orange)
cycle_opposing <- c(
  "Down" = "#2DB2E8",
  "Up" = "#E8622D",
  "NS" = "#222222"
)

# Cycle 4: Multiple categories
cycle_multi <- c("#222222", "#2DB2E8", "#666666", "#158BBB")

# Volcano plot colors
volcano_colors <- c(
  "NS" = "#BDBDBD",
  "Up" = "#E8622D",
  "Down" = "#2DB2E8"
)

# =============================================================================
# BRAND THEME
# =============================================================================

#' Oligon Brand Theme for ggplot2
#'
#' Apply Oligon scientific brand visual standards to ggplot2 plots.
#'
#' @param base_size Base font size in points (default: 8)
#' @param base_family Font family (default: "Arial")
#'
#' @return A ggplot2 theme object
#'
#' @examples
#' ggplot(mtcars, aes(wt, mpg)) +
#'   geom_point() +
#'   theme_brand()
#'
theme_brand <- function(base_size = 8, base_family = "Arial") {
  theme_minimal(base_size = base_size, base_family = base_family) %+replace%
    theme(
      # Background
      plot.background = element_rect(fill = "white", color = NA),
      panel.background = element_rect(fill = "white", color = NA),

      # Grid (off by default)
      panel.grid.major = element_blank(),
      panel.grid.minor = element_blank(),

      # Axes - despined style (only left and bottom)
      axis.line = element_line(color = "black", linewidth = 0.8 / .pt),
      axis.line.x = element_line(color = "black", linewidth = 0.8 / .pt),
      axis.line.y = element_line(color = "black", linewidth = 0.8 / .pt),
      axis.ticks = element_line(color = "black", linewidth = 0.4 / .pt),
      axis.text = element_text(color = "black", size = 7),
      axis.title = element_text(color = "black", size = 8),

      # Title
      plot.title = element_text(color = "black", size = 9, hjust = 0, face = "plain"),
      plot.subtitle = element_text(color = "#666666", size = 8, hjust = 0),

      # Legend
      legend.background = element_blank(),
      legend.key = element_blank(),
      legend.text = element_text(size = 7),
      legend.title = element_text(size = 8),
      legend.position = "right",

      # Facets
      strip.background = element_blank(),
      strip.text = element_text(color = "black", size = 8, face = "bold"),

      # Margins
      plot.margin = margin(10, 10, 10, 10)
    )
}

# =============================================================================
# COLOR SCALES
# =============================================================================

#' Scale for Treatment vs Control comparisons
#'
#' @param ... Additional arguments passed to scale_color_manual
#'
scale_color_brand_treatment <- function(...) {
  scale_color_manual(values = cycle_treatment_control, ...)
}

scale_fill_brand_treatment <- function(...) {
  scale_fill_manual(values = cycle_treatment_control, ...)
}

#' Scale for Neutrals only (equal weight groups)
#'
scale_color_brand_neutrals <- function(...) {
  scale_color_manual(values = cycle_neutrals, ...)
}

scale_fill_brand_neutrals <- function(...) {
  scale_fill_manual(values = cycle_neutrals, ...)
}

#' Scale for Opposing effects (up/down)
#'
scale_color_brand_opposing <- function(...) {
  scale_color_manual(values = cycle_opposing, ...)
}

scale_fill_brand_opposing <- function(...) {
  scale_fill_manual(values = cycle_opposing, ...)
}

#' Scale for Multiple categories (4 max)
#'
scale_color_brand_multi <- function(...) {
  scale_color_manual(values = cycle_multi, ...)
}

scale_fill_brand_multi <- function(...) {
  scale_fill_manual(values = cycle_multi, ...)
}

#' Scale for Volcano plots
#'
scale_color_volcano <- function(...) {
  scale_color_manual(values = volcano_colors, ...)
}

# =============================================================================
# DIVERGENT SCALE FOR HEATMAPS
# =============================================================================

#' Divergent color scale for heatmaps
#'
#' Creates a divergent color scale centered at white, suitable for
#' data centered around zero (z-scores, log2 fold changes, etc.)
#'
#' @param limits Numeric vector of length 2 giving the limits
#' @param ... Additional arguments passed to scale_fill_gradientn
#'
#' @examples
#' ggplot(data, aes(x, y, fill = zscore)) +
#'   geom_tile() +
#'   scale_fill_brand_divergent(limits = c(-3, 3))
#'
scale_fill_brand_divergent <- function(limits = NULL, ...) {
  scale_fill_gradientn(
    colors = c(
      brand_colors$dark_teal,
      brand_colors$brand_blue,
      brand_colors$white,
      brand_colors$contrast_orange,
      brand_colors$dark_warm
    ),
    values = rescale(c(-1, -0.5, 0, 0.5, 1)),
    limits = limits,
    ...
  )
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

#' Add panel label to a ggplot
#'
#' @param p A ggplot object
#' @param label The label text (e.g., "A", "B", "C")
#' @param x X position in npc coordinates (0-1)
#' @param y Y position in npc coordinates (0-1)
#' @param size Font size in points
#'
#' @return Modified ggplot object
#'
add_panel_label <- function(p, label, x = 0.02, y = 0.98, size = 10) {
  p + annotation_custom(
    grob = grid::textGrob(
      label = label,
      x = unit(x, "npc"),
      y = unit(y, "npc"),
      hjust = 0,
      vjust = 1,
      gp = grid::gpar(fontsize = size, fontface = "bold", col = "black")
    )
  )
}

#' Get a brand color by name
#'
#' @param name Color name (e.g., "brand_blue", "dark_gray")
#'
#' @return Hex color string
#'
get_brand_color <- function(name) {
  brand_colors[[name]]
}

# =============================================================================
# EXAMPLE USAGE
# =============================================================================

# Uncomment to run examples:

# # Example 1: Treatment vs Control
# library(ggplot2)
#
# df <- data.frame(
#   x = rep(1:10, 2),
#   y = c(rnorm(10, 5, 1), rnorm(10, 7, 1)),
#   group = rep(c("Control", "Treatment"), each = 10)
# )
#
# ggplot(df, aes(x, y, color = group)) +
#   geom_line(linewidth = 1.25) +
#   geom_point(size = 3) +
#   scale_color_brand_treatment() +
#   theme_brand() +
#   labs(
#     title = "Treatment vs Control Comparison",
#     x = "Time (days)",
#     y = "Response"
#   )
#
# ggsave("example_treatment_control.png", width = 5, height = 3.75, dpi = 300)

# # Example 2: Volcano Plot
# set.seed(42)
# volcano_df <- data.frame(
#   log2FC = rnorm(1000, 0, 1.5),
#   pval = 10^(-runif(1000, 0, 5))
# )
# volcano_df$category <- with(volcano_df, ifelse(
#   abs(log2FC) < 1 | pval > 0.05, "NS",
#   ifelse(log2FC > 0, "Up", "Down")
# ))
#
# ggplot(volcano_df, aes(x = log2FC, y = -log10(pval), color = category)) +
#   geom_point(aes(size = category, alpha = category)) +
#   scale_color_volcano() +
#   scale_size_manual(values = c("NS" = 1, "Up" = 2, "Down" = 2)) +
#   scale_alpha_manual(values = c("NS" = 0.5, "Up" = 0.8, "Down" = 0.8)) +
#   geom_hline(yintercept = -log10(0.05), linetype = "dashed",
#              color = "#666666", linewidth = 0.3) +
#   geom_vline(xintercept = c(-1, 1), linetype = "dashed",
#              color = "#666666", linewidth = 0.3) +
#   labs(x = expression(log[2](Fold~Change)),
#        y = expression(-log[10](p-value))) +
#   theme_brand() +
#   theme(legend.position = "none")
#
# ggsave("example_volcano.png", width = 4, height = 4, dpi = 300)
