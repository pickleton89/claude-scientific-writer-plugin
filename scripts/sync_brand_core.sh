#!/usr/bin/env bash
#
# sync_brand_core.sh — vendor oligon-brand-core into the plugin's oligon-brand skill.
#
# SINGLE SOURCE OF TRUTH: https://github.com/pickleton89/oligon-brand-core
#
# This script REGENERATES skills/oligon-brand/ from a local checkout of the
# canonical brand repo, then layers the plugin-only delegation overlay
# (default-on behavior + cross-references) on top. The shipped skill is a
# self-contained mirror named `oligon-brand`; the upstream repo is
# `oligon-brand-core`.
#
#   DO NOT hand-edit skills/oligon-brand/. Edit oligon-brand-core, push, then
#   re-run this script. A CI check fails if the vendored copy drifts from a
#   regeneration against the pinned core SHA.
#
# Usage:
#   scripts/sync_brand_core.sh <path-to-oligon-brand-core-checkout>
#
# Uses stdlib python3 only (no uv/venv) so any contributor can run it.
set -euo pipefail

CORE_DIR="${1:?usage: sync_brand_core.sh <oligon-brand-core checkout dir>}"
HERE="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="$(cd "$HERE/.." && pwd)"
SKILL_DIR="$PLUGIN_ROOT/skills/oligon-brand"
OVERLAY_DIR="$HERE/oligon-brand-overlay"

[ -f "$CORE_DIR/SKILL.md" ] || { echo "error: '$CORE_DIR' is not an oligon-brand-core checkout" >&2; exit 1; }
CORE_SHA="$(git -C "$CORE_DIR" rev-parse --short HEAD 2>/dev/null || echo unknown)"

echo "Vendoring oligon-brand-core@${CORE_SHA} -> skills/oligon-brand/ (+ overlay)"

# 1. Regenerate the skill directory as an exact mirror of core (brand canon),
#    excluding VCS / dev junk.
rsync -a --delete \
  --exclude='.git' --exclude='.gitignore' --exclude='__pycache__' \
  --exclude='*.pyc' --exclude='.DS_Store' --exclude='.pytest_cache' \
  --exclude='.ruff_cache' --exclude='.venv' \
  "$CORE_DIR"/ "$SKILL_DIR"/

# 2. Frontmatter rename (oligon-brand-core -> oligon-brand) + provenance banner.
python3 - "$SKILL_DIR/SKILL.md" "$CORE_SHA" <<'PY'
import sys, re
path, sha = sys.argv[1], sys.argv[2]
s = open(path, encoding="utf-8").read()
s = re.sub(r'(?m)^name:\s*oligon-brand-core\s*$', 'name: oligon-brand', s, count=1)
banner = (
    "\n<!-- GENERATED FILE - do not edit here.\n"
    f"     Vendored from https://github.com/pickleton89/oligon-brand-core@{sha}\n"
    "     Edit oligon-brand-core and re-run scripts/sync_brand_core.sh. -->\n"
)
parts = s.split("---", 2)
if len(parts) == 3:           # ---\nfrontmatter\n---\nbody
    s = "---" + parts[1] + "---" + banner + parts[2]
open(path, "w", encoding="utf-8").write(s)
PY

# 3. Inject the plugin delegation overlay into the vendored SKILL.md.
python3 - "$SKILL_DIR/SKILL.md" "$OVERLAY_DIR/default_behavior.md" "$OVERLAY_DIR/cross_references.md" <<'PY'
import sys
skill, db, xref = sys.argv[1:4]
s = open(skill, encoding="utf-8").read()
db_txt = open(db, encoding="utf-8").read().strip() + "\n"
xref_txt = open(xref, encoding="utf-8").read().strip() + "\n"
if "</overview>" not in s:
    sys.exit("error: no </overview> anchor in vendored SKILL.md")
s = s.replace("</overview>\n", "</overview>\n\n" + db_txt + "\n", 1)
if "<references>" in s:
    s = s.replace("<references>", xref_txt + "\n<references>", 1)
else:
    s = s.rstrip() + "\n\n" + xref_txt
open(skill, "w", encoding="utf-8").write(s)
PY

echo "Done: skills/oligon-brand/ regenerated from core@${CORE_SHA} + overlay."
echo "Review the diff, then commit."
