#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""grammar.ebnf -> the IFC label set in tree-sitter-mvl's grammar.js.

This is the specific list that started #2. `security_label` hardcoded
choice("Public", "Tainted", "Secret", "Clean") for two weeks after mvl-spec PR
#31 corrected the EBNF — `Public` and `Clean` are not labels, and the four #931
capability labels were missing. Five artifacts carried the wrong set; this one
was published to npm and consumed by three editor plugins.

It stays a closed set because a context-free grammar cannot express the EBNF's
side condition (`labeled_type = IDENT "[" type_expr "]"` where IDENT must be a
declared label). User-declared labels still parse — they match `base_type` — they
just get no label-specific highlight. So the closed set is a highlighting
convenience, and its only correct contents are the stdlib labels.

Usage:
    python3 tools/generators/gen_tree_sitter.py [--check] [--tree-sitter-dir DIR]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import _keywords as K

SCRIPT = "gen_tree_sitter.py"

# Located line-wise rather than by regex: the rule body may contain comments with
# parentheses (`// Capability labels (#931)`), which defeats paren-counting.
RULE_START = re.compile(r"^( *)security_label: \(\$\) =>\s*$")
RULE_END = re.compile(r"^ *\),\s*$")


def render_rule(kw: K.Keywords, indent: str) -> str:
    i = indent
    lines = [f"{i}security_label: ($) =>", f"{i}  choice("]
    for n, label in enumerate(kw.stdlib_labels):
        comma = "," if n < len(kw.stdlib_labels) - 1 else ""
        lines.append(f'{i}    "{label}"{comma}')
    lines.append(f"{i}  ),")
    banner = [f"{i}{ln}" for ln in K.banner(SCRIPT, "//")]
    return "\n".join(banner + lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument(
        "--tree-sitter-dir",
        type=Path,
        default=K.SPEC_ROOT.parent / "tree-sitter-mvl",
        help="path to a tree-sitter-mvl checkout (default: sibling of mvl-spec)",
    )
    args = ap.parse_args()

    path = args.tree_sitter_dir / "grammar.js"
    if not path.exists():
        print(f"  skip (absent): {path}", file=sys.stderr)
        return 0

    kw = K.load()
    old = path.read_text()
    lines = old.splitlines(keepends=True)

    start = end = indent = None
    for n, line in enumerate(lines):
        m = RULE_START.match(line)
        if m:
            start, indent = n, m.group(1)
            for j in range(n + 1, len(lines)):
                if RULE_END.match(lines[j]):
                    end = j
                    break
            break
    if start is None or end is None:
        raise SystemExit(
            f"{path}: could not locate the `security_label` rule. If it was "
            "renamed or removed, update RULE_START/RULE_END or retire this "
            "generator."
        )

    # Absorb any existing generated banner directly above the rule so it is not
    # duplicated on each run.
    while start > 0 and "DO NOT EDIT" in "".join(lines[max(0, start - 4) : start]) \
            and lines[start - 1].strip().startswith("//"):
        start -= 1

    new = "".join(lines[:start]) + render_rule(kw, indent) + "\n" + "".join(lines[end + 1 :])

    if new == old:
        print("grammar.js security_label: up to date")
        return 0
    if args.check:
        print(
            f"DRIFT — {path} security_label is stale versus grammar.ebnf.\n"
            "Fix: tools/generators/regen-all.sh && (cd tree-sitter-mvl && tree-sitter generate)",
            file=sys.stderr,
        )
        return 1
    path.write_text(new)
    print(f"  wrote {path} (run `tree-sitter generate` to rebuild the parser)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
