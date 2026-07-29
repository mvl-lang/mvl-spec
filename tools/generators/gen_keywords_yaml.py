#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""grammar.ebnf -> grammar/keywords.yaml.

keywords.yaml used to be hand-maintained and self-described as the single source
of truth, while nothing read it and nothing could contradict it. It is now an
*artifact*: a machine-readable projection of the EBNF's category blocks, kept
because YAML is convenient for consumers that should not parse EBNF comments.

Consumers may read this file freely. Nobody edits it. See ADR-0060.

Usage:
    python3 tools/generators/gen_keywords_yaml.py [--check]
"""

from __future__ import annotations

import argparse
import sys

import _keywords as K

SCRIPT = "gen_keywords_yaml.py"

SNAKE = [
    ("declaration", "Declaration"),
    ("totality", "Totality"),
    ("cast", "Cast"),
    ("control_flow", "Control flow"),
    ("let_binding", "Let binding"),
    ("ownership", "Ownership"),
    ("ifc", "IFC"),
    ("boolean", "Boolean"),
    ("refinements", "Refinements"),
    ("pattern", "Pattern"),
]

# Words that must be quoted or YAML reads them as booleans.
YAML_UNSAFE = {"true", "false", "yes", "no", "on", "off", "null", "~"}


def _emit(name: str, words: list[str], note: str | None = None) -> list[str]:
    out: list[str] = []
    if note:
        out += [f"# {ln}" for ln in note.splitlines()]
    out.append(f"{name}:")
    for w in words:
        out.append(f'  - "{w}"' if w in YAML_UNSAFE else f"  - {w}")
    out.append("")
    return out


def render(kw: K.Keywords) -> str:
    out = K.banner(SCRIPT, "#")
    out += [
        "#",
        "# Categories, and what each means for a consumer:",
        "#",
        f"#   declaration..refinements  {len(kw.reserved):>3}  RESERVED — the lexer rejects these",
        "#                                  as identifiers.",
        f"#   pattern                  {len(kw.pattern):>3}  Constructors, matched as paths. NOT",
        "#                                  lexer keywords.",
        f"#   contextual               {len(kw.contextual):>3}  Special in one syntactic position,",
        "#                                  ordinary identifiers elsewhere. NEVER",
        "#                                  emit these as bare words.",
        f"#   builtin_types            {len(kw.builtin_types):>3}  Reserved by convention only.",
        f"#   stdlib_labels            {len(kw.stdlib_labels):>3}  Ordinary identifiers.",
        "#",
        "# `len` appears in no category: it is an ordinary identifier naming a",
        "# compiler-known method, which ref_atom admits as len(x) inside predicates.",
        "",
    ]
    for snake, _label in SNAKE:
        out += _emit(snake, kw.section(snake))

    out += _emit(
        "contextual",
        kw.contextual,
        "Not reserved. Anchor on the enclosing production, never the bare word —\n"
        "a flat list highlights `let end = 5` as a keyword.",
    )
    out += _emit(
        "builtin_types",
        kw.builtin_types,
        "Not enforced by the lexer; users should not shadow them.",
    )
    out += _emit(
        "stdlib_labels",
        kw.stdlib_labels,
        "Ordinary identifiers, pre-seeded into the parser's known-label set.\n"
        "There is no `Public` label — unlabeled is public by absence.",
    )
    return "\n".join(out).rstrip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    kw = K.load()
    new = render(kw)
    path = K.KEYWORDS_YAML
    old = path.read_text() if path.exists() else ""

    if new == old:
        print("keywords.yaml: up to date")
        return 0
    if args.check:
        print(
            f"DRIFT — {path} is stale versus grammar.ebnf.\n"
            "Fix: tools/generators/regen-all.sh",
            file=sys.stderr,
        )
        return 1
    path.write_text(new)
    print(f"  wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
