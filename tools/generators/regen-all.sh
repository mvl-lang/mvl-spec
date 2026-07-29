#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
#
# Regenerate every artifact derived from grammar/grammar.ebnf.
#
# The EBNF is the source (ADR-0060 / mvl-lang/mvl#2050). Editing a generated
# file directly is a CI failure — edit the grammar and run this.
#
# Usage:
#   tools/generators/regen-all.sh [--check] [--tree-sitter-dir DIR]
#
# --check exits non-zero if any artifact is stale, changing nothing.
set -euo pipefail

# Parse args BEFORE changing directory. A relative --tree-sitter-dir must resolve
# against the caller's cwd, not this script's location. Getting this wrong made
# both cross-repo generators silently skip while CI reported success.
CHECK=""
TS_DIR=""
while [ $# -gt 0 ]; do
  case "$1" in
    --check) CHECK="--check"; shift ;;
    --tree-sitter-dir)
      [ -d "$2" ] || { echo "--tree-sitter-dir: no such directory: $2" >&2; exit 2; }
      TS_DIR="$(cd "$2" && pwd)"
      shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

cd "$(dirname "$0")"

TS_ARG=()
[ -n "$TS_DIR" ] && TS_ARG=(--tree-sitter-dir "$TS_DIR")

# keywords.yaml first — it is the projection consumers read, and generating it
# runs the EBNF cross-check before anything else depends on the result.
echo "keywords.yaml"
python3 gen_keywords_yaml.py $CHECK

echo "highlights.scm (tree-sitter-mvl, nvim, zed)"
python3 gen_highlights.py $CHECK "${TS_ARG[@]+"${TS_ARG[@]}"}"

echo "mvl.tmLanguage.json (vscode)"
python3 gen_vscode.py $CHECK

echo "grammar.js security_label (tree-sitter-mvl)"
python3 gen_tree_sitter.py $CHECK "${TS_ARG[@]+"${TS_ARG[@]}"}"

echo "keywords.py (pygments)"
python3 gen_pygments.py $CHECK

if [ -n "$CHECK" ]; then
  echo
  echo "All generated artifacts match grammar/grammar.ebnf."
else
  echo
  echo "Done. If grammar.js changed, rebuild the parser:"
  echo "  (cd ../../../tree-sitter-mvl && tree-sitter generate && tree-sitter test)"
fi
