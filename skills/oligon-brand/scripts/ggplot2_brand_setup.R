#!/usr/bin/env Rscript
# =============================================================================
# Oligon Scientific Brand — ggplot2 Setup (v5.0 / Style Guide v2.3)
# =============================================================================
# Thin wrapper that sources `adapters/ggplot2_adapter.R` and sets the brand
# theme as the ggplot2 default. The adapter is the single source of truth
# for v2.3 Oklch ramps, cycles, and scales; this script does not duplicate
# tokens.
#
# Usage:
#   source("scripts/ggplot2_brand_setup.R")
#   # All plots now default to theme_brand()
#   ggplot(df, aes(x, y, color = group)) +
#     geom_point() +
#     scale_color_brand_treatment()
# =============================================================================

library(ggplot2)

# Locate the adapter relative to this script, even when sourced from
# another working directory.
.oligon_script_dir <- tryCatch({
  # Rscript path
  args <- commandArgs(trailingOnly = FALSE)
  file_arg <- sub("--file=", "", args[grepl("--file=", args)])
  if (length(file_arg) == 0 || file_arg == "") stop("not Rscript")
  dirname(normalizePath(file_arg))
}, error = function(e) {
  # Interactive source() — utils::getSrcDirectory on the calling frame
  src_dir <- tryCatch(
    utils::getSrcDirectory(function() {})[1],
    error = function(e2) NA_character_
  )
  if (is.na(src_dir) || src_dir == "") getwd() else src_dir
})

.oligon_adapter <- file.path(.oligon_script_dir, "..", "adapters",
                             "ggplot2_adapter.R")
if (!file.exists(.oligon_adapter)) {
  stop(sprintf("Could not locate ggplot2_adapter.R at %s", .oligon_adapter))
}
source(.oligon_adapter)

# Apply v5.0 brand theme as default for all plots.
theme_set(theme_brand())

message(
  "Oligon brand v5.0 loaded. Available scales: ",
  "scale_color_brand_treatment / scale_color_brand_peer / ",
  "scale_color_brand_focus / scale_color_brand_opposing / ",
  "scale_color_brand_multi / scale_color_volcano / ",
  "scale_fill_brand_divergent."
)
