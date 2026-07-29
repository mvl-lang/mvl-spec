#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""grammar.ebnf -> tools/pygments/mvl_pygments/keywords.py.

The lexer imports these tables rather than restating them. pygments-mvl would
otherwise be the sixth artifact to hand-transcribe the keyword lists, and five
of the previous five drifted — see ADR-0060 (mvl-lang/mvl#2050).

`publish-pygments.yml` refuses to publish unless the generated banner is present
in the emitted file, so a hand-written keywords.py cannot reach PyPI.

Usage:
    python3 tools/generators/gen_pygments.py [--check]
"""

from __future__ import annotations

import argparse
import sys

import _keywords as K

SCRIPT = "gen_pygments.py"
OUT = K.SPEC_ROOT / "tools" / "pygments" / "mvl_pygments" / "keywords.py"


def _tuple(name: str, words: list[str], doc: str) -> list[str]:
    out = [f"{name}: tuple[str, ...] = ("]
    out += [f'    "{w}",' for w in words]
    out += [")", f'"""{doc}"""', ""]
    return out


def render(kw: K.Keywords) -> str:
    out = K.banner(SCRIPT, "#")
    out += [
        '"""Keyword tables for the MVL Pygments lexer.',
        "",
        "Generated from mvl-spec grammar/grammar.ebnf. Categories are NOT",
        "interchangeable — only RESERVED words may be highlighted as bare words.",
        "CONTEXTUAL words are ordinary identifiers outside one syntactic position,",
        "so highlighting them unconditionally renders `let end = 5` wrongly.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
    ]

    out += _tuple(
        "RESERVED",
        kw.reserved,
        f"The {len(kw.reserved)} words the MVL lexer rejects as identifiers.",
    )
    out += _tuple(
        "CONSTRUCTORS",
        kw.pattern,
        "Option/Result constructors. Matched as paths, not lexer keywords.",
    )
    out += _tuple(
        "CONTEXTUAL",
        kw.contextual,
        "Special in ONE syntactic position; ordinary identifiers elsewhere. "
        "Do NOT highlight as bare words.",
    )
    out += _tuple(
        "BUILTIN_TYPES",
        kw.builtin_types,
        "Reserved by convention only; the MVL lexer does not protect them.",
    )
    out += _tuple(
        "STDLIB_LABELS",
        kw.stdlib_labels,
        "IFC labels pre-seeded into the parser's known-label set. Ordinary "
        "identifiers. There is no `Public` label — unlabeled is public by absence.",
    )

    # Category-level groupings the lexer wants for distinct token types.
    for py_name, section, doc in (
        ("TOTALITY", "totality", "Termination modifiers."),
        ("OWNERSHIP", "ownership", "Reference capabilities plus `consume`."),
        ("REFINEMENTS", "refinements", "Contract and refinement clause keywords."),
        ("BOOLEAN", "boolean", "Boolean literals."),
    ):
        out += _tuple(py_name, kw.section(section), doc)

    out.append("__all__ = [")
    for n in (
        "RESERVED",
        "CONSTRUCTORS",
        "CONTEXTUAL",
        "BUILTIN_TYPES",
        "STDLIB_LABELS",
        "TOTALITY",
        "OWNERSHIP",
        "REFINEMENTS",
        "BOOLEAN",
    ):
        out.append(f'    "{n}",')
    out.append("]")
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    if not OUT.parent.exists():
        print(f"  skip (absent): {OUT.parent}", file=sys.stderr)
        return 0

    kw = K.load()
    new = render(kw)
    old = OUT.read_text() if OUT.exists() else ""

    if new == old:
        print("keywords.py: up to date")
        return 0
    if args.check:
        print(
            f"DRIFT — {OUT} is stale versus grammar.ebnf.\n"
            "Fix: tools/generators/regen-all.sh",
            file=sys.stderr,
        )
        return 1
    OUT.write_text(new)
    print(f"  wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
