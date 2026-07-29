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

cd "$(dirname "$0")"

CHECK=""
TS_DIR=""
while [ $# -gt 0 ]; do
  case "$1" in
    --check) CHECK="--check"; shift ;;
    --tree-sitter-dir) TS_DIR="$2"; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

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

# gen_pygments.py lands with the lexer itself — mvl-lang/mvl-spec#1, targeted at
# 0.1.5. There is no tools/pygments/mvl_pygments/ package to generate into yet.

if [ -n "$CHECK" ]; then
  echo
  echo "All generated artifacts match grammar/grammar.ebnf."
else
  echo
  echo "Done. If grammar.js changed, rebuild the parser:"
  echo "  (cd ../../../tree-sitter-mvl && tree-sitter generate && tree-sitter test)"
fi
