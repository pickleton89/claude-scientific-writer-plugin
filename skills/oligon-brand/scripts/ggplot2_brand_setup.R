#!/usr/bin/env Rscript
# =============================================================================
# Oligon Scientific Brand - ggplot2 Configuration
# =============================================================================
# Source this file to apply brand styling to all ggplot2 figures.
#
# Usage:
#   source("ggplot2_brand_setup.R")
#   
#   # Use theme_brand() for consistent styling
#   ggplot(data, aes(x, y)) + geom_point() + theme_brand()
#   
#   # Use scale_color_* and scale_fill_* for brand colors
# =============================================================================

library(ggplot2)

# =============================================================================
# BRAND COLOR DEFINITIONS
# =============================================================================

brand_colors <- list(
  # Primary brand color
  brand_blue = "#2DB2E8",
  

  # Neutral data colors
  dark_gray = "#222222",
  medium_gray = "#666666",
  muted_gray = "#999999",
  light_gray = "#BDBDBD",  # Annotations only, not for data
  
  # Contrast color
  contrast_orange = "#E8622D",
  
  # Supporting colors
  medium_blue = "#158BBB",
  dark_teal = "#0F5D7D",
  dark_warm = "#7D250F",
  
  # Structure
  black = "#000000",
  white = "#FFFFFF",
  gridline = "#E5E5E5"
)

# =============================================================================
# SCENARIO-SPECIFIC COLOR SCALES
# =============================================================================

# Cycle 1: Treatment vs Control (most common)
scale_treatment_control <- c(
  "Control" = "#222222",
  "Treatment" = "#2DB2E8",
  "Vehicle" = "#666666"
)

# Cycle 2: Neutrals only (all groups equal weight)
scale_neutrals <- c("#222222", "#666666", "#999999")

# Cycle 3: Opposing effects (up vs. down)
scale_opposing <- c(
  "Down" = "#2DB2E8",
  "Up" = "#E8622D",
  "NS" = "#222222"
)

# Cycle 4: Multiple categories (use with shapes)
scale_multi <- c("#222222", "#2DB2E8", "#666666", "#158BBB")

# Volcano plot specific
scale_volcano <- c(
  "NS" = "#BDBDBD",
  "Up" = "#E8622D",
  "Down" = "#2DB2E8"
)

# =============================================================================
# BRAND THEME
# =============================================================================

#' Oligon Brand Theme for ggplot2
#'
#' A clean, publication-ready theme following Oligon brand guidelines.
#' Uses despined layout (no top/right axes), Arial font, and white background.
#'
#' @param base_size Base font size (default: 8)
#' @param base_family Font family (default: "Arial")
#' @return A ggplot2 theme object
#'
#' @examples
#' ggplot(mtcars, aes(wt, mpg)) + geom_point() + theme_brand()
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
      
      # Axes (despined - left and bottom only)
      axis.line = element_line(color = "black", linewidth = 0.8 / .pt),
      axis.ticks = element_line(color = "black", linewidth = 0.4 / .pt),
      axis.text = element_text(color = "black", size = 7),
      axis.title = element_text(color = "black", size = 8),
      
      # Title
      plot.title = element_text(color = "black", size = 9, hjust = 0),
      plot.subtitle = element_text(color = "#666666", size = 8, hjust = 0),
      
      # Legend
      legend.background = element_blank(),
      legend.key = element_blank(),
      legend.text = element_text(size = 7),
      legend.title = element_text(size = 8),
      
      # Facets
      strip.background = element_blank(),
      strip.text = element_text(color = "black", size = 8)
    )
}

# =============================================================================
# COLOR SCALE FUNCTIONS
# =============================================================================

#' Discrete color scale for treatment vs control
#'
#' @param ... Additional arguments passed to scale_color_manual
#' @return A ggplot2 scale
scale_color_treatment <- function(...) {
  scale_color_manual(values = scale_treatment_control, ...)
}

#' Discrete fill scale for treatment vs control
scale_fill_treatment <- function(...) {
  scale_fill_manual(values = scale_treatment_control, ...)
}

#' Discrete color scale for volcano plots
scale_color_volcano <- function(...) {
  scale_color_manual(values = scale_volcano, ...)
}

#' Discrete fill scale for volcano plots
scale_fill_volcano <- function(...) {
  scale_fill_manual(values = scale_volcano, ...)
}

#' Discrete color scale for opposing effects (up/down)
scale_color_opposing <- function(...) {
  scale_color_manual(values = scale_opposing, ...)
}

#' Discrete fill scale for opposing effects
scale_fill_opposing <- function(...) {
  scale_fill_manual(values = scale_opposing, ...)
}

# =============================================================================
# DIVERGENT SCALE FOR HEATMAPS
# =============================================================================

#' Divergent fill scale for heatmaps (blue-white-orange)
#'
#' Centered at zero, suitable for z-scores and log2 fold changes.
#'
#' @param limits Numeric vector of length 2 for scale limits
#' @param ... Additional arguments passed to scale_fill_gradientn
#' @return A ggplot2 scale
scale_fill_brand_divergent <- function(limits = NULL, ...) {
  scale_fill_gradientn(
    colors = c(
      brand_colors$dark_teal,
      brand_colors$brand_blue,
      brand_colors$white,
      brand_colors$contrast_orange,
      brand_colors$dark_warm
    ),
    values = scales::rescale(c(-1, -0.5, 0, 0.5, 1)),
    limits = limits,
    ...
  )
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

#' Add panel label to a ggplot
#'
#' @param label Character label (e.g., "A", "B", "C")
#' @param x X position in npc coordinates (0-1)
#' @param y Y position in npc coordinates (0-1)
#' @param size Font size
#' @param fontface Font face (default: "bold")
#' @return A ggplot annotation layer
add_panel_label <- function(label, x = 0.02, y = 0.98, size = 10, fontface = "bold") {
  annotate("text", x = x, y = y, label = label,
           hjust = 0, vjust = 1,
           size = size / .pt, fontface = fontface)
}

# =============================================================================
# SET DEFAULT THEME
# =============================================================================

# Apply brand theme as default for all plots
theme_set(theme_brand())

# Print confirmation message
message("Oligon brand styling loaded. Use theme_brand() and scale_*_treatment/volcano/opposing functions.")
