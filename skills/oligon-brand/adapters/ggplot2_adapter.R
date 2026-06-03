# =============================================================================
# Oligon Brand Adapter for ggplot2 (v5.0 — Style Guide v2.3)
#
# Applies the Oligon Digital Style Guide v2.3 (April 2026) to ggplot2 plots.
# Features Oklch tonal ramps (Blue / Orange / Neutral × 10 steps), same-hue
# Cycle 1, Peer vs Focus cycle split, and a divergent blue.700 → white →
# orange.700 fill scale.
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
  # Brand anchor
  brand_blue = "#2DB2E8",

  # Blue ramp (10 steps)
  blue_50   = "#EFFBFF",  blue_100 = "#DBF3FF",  blue_200 = "#B3E3FC",
  blue_300  = "#76CAF3",  blue_400 = "#1FACE3",  blue_500 = "#008ECB",
  blue_600  = "#006EA6",  blue_700 = "#00507E",  blue_800 = "#003454",
  blue_900  = "#001A2E",

  # Orange ramp (10 steps)
  orange_50   = "#FFF5F1",  orange_100 = "#FFE8E0",  orange_200 = "#FFCEBD",
  orange_300  = "#F0AA92",  orange_400 = "#DD8363",  orange_500 = "#C45E39",
  orange_600  = "#A0421D",  orange_700 = "#772E11",  orange_800 = "#4F1B06",
  orange_900  = "#2B0901",

  # Neutral ramp (10 steps)
  neutral_50   = "#F3FAFD",  neutral_100 = "#E9F0F3",  neutral_200 = "#D6DCDF",
  neutral_300  = "#B9BFC2",  neutral_400 = "#9A9FA2",  neutral_500 = "#7C8184",
  neutral_600  = "#5F6467",  neutral_700 = "#44494B",  neutral_800 = "#2A2F31",
  neutral_900  = "#121719",

  # Structure
  black = "#000000",
  white = "#FFFFFF"
)

# Semantic tokens — light theme (preferred for new code)
semantic_light <- list(
  page       = "#FFFFFF",
  surface    = "#F3FAFD",   # neutral.50
  border     = "#D6DCDF",   # neutral.200
  text       = "#121719",   # neutral.900
  text_muted = "#44494B",   # neutral.700
  accent     = "#00507E",   # blue.700
  brand      = "#2DB2E8",
  signal     = "#772E11"    # orange.700
)

# =============================================================================
# COLOR CYCLES (Rule 1 — choose from data structure)
# =============================================================================

# Cycle 1 — Treatment / Control: same-hue, lightness hierarchy.
# CI bands: matching-hue tint of each arm's line at alpha ≈ 0.18 — NOT a
# shared blue.100 fill (that produces muddy overlap). See brand-colors-full.md §4.
cycle_treatment_control <- c(
  "Treatment" = "#2DB2E8",  # brand.blue
  "Control"   = "#76CAF3"   # blue.300
)
# Use geom_ribbon(aes(fill = arm), alpha = 0.18) with the same palette
# to get per-arm matching-hue CI bands.

# Cycle 2 — Peer: equal-weight arms, no promotion.
cycle_peer_4 <- c("#003454", "#006EA6", "#1FACE3", "#B3E3FC")
cycle_peer_3 <- c("#00507E", "#008ECB", "#76CAF3")

# Cycle 2 — Focus: N arms with one promoted.
cycle_focus_receding <- c("#008ECB", "#76CAF3", "#B3E3FC")
focus_variants <- list(
  default       = "#C45E39",  # orange.500 — categorical focus
  soft          = "#DD8363",  # orange.400 — softer promotion
  monochromatic = "#003454"   # blue.800   — more-of-the-same promotion
)
cycle_focus <- c(cycle_focus_receding, focus_variants$default)

# Cycle 3 — Opposing: signed/directional effects.
cycle_opposing <- c(
  "Down" = "#006EA6",   # blue.600
  "Up"   = "#A0421D",   # orange.600
  "NS"   = "#B9BFC2"    # neutral.300
)

# Cycle 4 — Multi-Category: 3–4 categories with one conceptual outlier.
cycle_multi <- c("#003454", "#008ECB", "#76CAF3", "#C45E39")

# Volcano plot (Cycle 3 convention)
volcano_colors <- c(
  "NS"   = "#B9BFC2",
  "Up"   = "#A0421D",
  "Down" = "#006EA6"
)

# Deprecated alias — routes to Peer 3
cycle_neutrals <- cycle_peer_3

# =============================================================================
# BRAND THEME
# =============================================================================

#' Oligon Brand Theme for ggplot2 (v5.0 / Style Guide v2.3)
#'
#' Figure Type Scale: title 12pt bold, axis label 10pt, tick label 9pt,
#' legend 8.5–9pt. Axis furniture in neutral.200; text in neutral.900.
#'
#' @param base_size Base font size in points (default: 9)
#' @param base_family Font family (default: "Arial")
#'
theme_brand <- function(base_size = 9, base_family = "Arial") {
  theme_minimal(base_size = base_size, base_family = base_family) %+replace%
    theme(
      plot.background = element_rect(fill = "white", color = NA),
      panel.background = element_rect(fill = "white", color = NA),

      panel.grid.major = element_blank(),
      panel.grid.minor = element_blank(),

      axis.line = element_line(color = brand_colors$neutral_900, linewidth = 0.8 / .pt),
      axis.line.x = element_line(color = brand_colors$neutral_900, linewidth = 0.8 / .pt),
      axis.line.y = element_line(color = brand_colors$neutral_900, linewidth = 0.8 / .pt),
      axis.ticks = element_line(color = brand_colors$neutral_900, linewidth = 0.4 / .pt),
      axis.text = element_text(color = brand_colors$neutral_900, size = 9),
      axis.title = element_text(color = brand_colors$neutral_900, size = 10),

      plot.title = element_text(
        color = brand_colors$neutral_900, size = 12, hjust = 0, face = "bold"
      ),
      plot.subtitle = element_text(
        color = brand_colors$neutral_600, size = 10, hjust = 0
      ),

      legend.background = element_blank(),
      legend.key = element_blank(),
      legend.text = element_text(size = 8.5),
      legend.title = element_text(size = 9),
      legend.position = "right",

      strip.background = element_blank(),
      strip.text = element_text(color = brand_colors$neutral_900, size = 10, face = "bold"),

      plot.margin = margin(10, 10, 10, 10)
    )
}

# =============================================================================
# COLOR SCALES
# =============================================================================

scale_color_brand_treatment <- function(...) {
  scale_color_manual(values = cycle_treatment_control, ...)
}
scale_fill_brand_treatment <- function(...) {
  scale_fill_manual(values = cycle_treatment_control, ...)
}

scale_color_brand_peer <- function(n = 4, ...) {
  vals <- if (n <= 3) cycle_peer_3 else cycle_peer_4
  scale_color_manual(values = vals, ...)
}
scale_fill_brand_peer <- function(n = 4, ...) {
  vals <- if (n <= 3) cycle_peer_3 else cycle_peer_4
  scale_fill_manual(values = vals, ...)
}

scale_color_brand_focus <- function(...) {
  scale_color_manual(values = cycle_focus, ...)
}
scale_fill_brand_focus <- function(...) {
  scale_fill_manual(values = cycle_focus, ...)
}

scale_color_brand_opposing <- function(...) {
  scale_color_manual(values = cycle_opposing, ...)
}
scale_fill_brand_opposing <- function(...) {
  scale_fill_manual(values = cycle_opposing, ...)
}

scale_color_brand_multi <- function(...) {
  scale_color_manual(values = cycle_multi, ...)
}
scale_fill_brand_multi <- function(...) {
  scale_fill_manual(values = cycle_multi, ...)
}

scale_color_volcano <- function(...) {
  scale_color_manual(values = volcano_colors, ...)
}

# Deprecated — routes to Peer 3
scale_color_brand_neutrals <- function(...) {
  scale_color_manual(values = cycle_peer_3, ...)
}
scale_fill_brand_neutrals <- function(...) {
  scale_fill_manual(values = cycle_peer_3, ...)
}

# =============================================================================
# DIVERGENT SCALE FOR HEATMAPS
# =============================================================================

#' Divergent color scale centered at zero: blue.700 → white → orange.700.
#'
#' Matched lightness curves on both ramps keep perceptual distance from zero
#' symmetric. Interpolation in linear sRGB.
#'
scale_fill_brand_divergent <- function(limits = NULL, ...) {
  scale_fill_gradientn(
    colors = c(brand_colors$blue_700, brand_colors$white, brand_colors$orange_700),
    values = rescale(c(-1, 0, 1)),
    limits = limits,
    ...
  )
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

#' Add a bold panel label (A, B, C, ...) at the top-left of a plot.
add_panel_label <- function(p, label, x = 0.02, y = 0.98, size = 10) {
  p + annotation_custom(
    grob = grid::textGrob(
      label = label,
      x = unit(x, "npc"),
      y = unit(y, "npc"),
      hjust = 0,
      vjust = 1,
      gp = grid::gpar(fontsize = size, fontface = "bold",
                      col = brand_colors$neutral_900)
    )
  )
}

#' Look up a brand color by name (ramp step or brand anchor).
get_brand_color <- function(name) {
  brand_colors[[name]]
}

#' Resolve a semantic token (page, surface, text, accent, brand, signal, border).
get_semantic <- function(token) {
  semantic_light[[token]]
}
