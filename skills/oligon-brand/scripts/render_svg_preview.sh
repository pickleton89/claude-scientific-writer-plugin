#!/usr/bin/env bash
# render_svg_preview.sh — render an SVG to a PNG preview for visual verification.
#
# Why this exists: the brand SVG contract uses two grep checks (font-family,
# font-size) to verify textual compliance, but text-based checks can't catch
# layout issues — overlapping labels, clipped panel titles, mis-positioned
# arrowheads, illegible legend stacks. A rasterized preview lets a reader
# (Claude or human) visually confirm the figure is delivery-ready.
#
# Usage:
#   render_svg_preview.sh <input.svg> [output.png] [--scale N]
#
# Defaults:
#   - output: alongside input, replacing .svg with .preview.png
#   - scale: 2 (2x DPI for crisp viewing on standard displays)
#
# Examples:
#   render_svg_preview.sh figure.svg
#   render_svg_preview.sh figure.svg /tmp/preview.png
#   render_svg_preview.sh figure.svg --scale 3
#
# Requires: rsvg-convert (brew install librsvg).

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: $(basename "$0") <input.svg> [output.png] [--scale N]" >&2
    exit 2
fi

if ! command -v rsvg-convert >/dev/null 2>&1; then
    echo "Error: rsvg-convert not found on PATH. Install with: brew install librsvg" >&2
    exit 1
fi

input="$1"
shift

if [[ ! -f "$input" ]]; then
    echo "Error: input SVG not found: $input" >&2
    exit 1
fi

# Defaults
output=""
scale=2

# Parse remaining args
while [[ $# -gt 0 ]]; do
    case "$1" in
        --scale)
            scale="$2"
            shift 2
            ;;
        --scale=*)
            scale="${1#--scale=}"
            shift
            ;;
        -*)
            echo "Error: unknown flag: $1" >&2
            exit 2
            ;;
        *)
            if [[ -z "$output" ]]; then
                output="$1"
            else
                echo "Error: unexpected positional arg: $1" >&2
                exit 2
            fi
            shift
            ;;
    esac
done

if [[ -z "$output" ]]; then
    output="${input%.svg}.preview.png"
fi

# rsvg-convert: -z is the zoom/scale factor; output is PNG by default.
rsvg-convert -z "$scale" "$input" -o "$output"

echo "Preview written: $output" >&2
echo "$output"
