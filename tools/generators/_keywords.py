#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Shared loader. grammar/grammar.ebnf is the source; keywords.yaml is output.

The EBNF is authoritative for two separate things, and both are read here:

  1. WHICH WORDS ARE GRAMMAR SYNTAX — extracted from the productions. This is
     mechanical and complete: every one of the 43 reserved words appears as a
     quoted terminal in some production.

  2. HOW EACH WORD IS CLASSIFIED — read from the labelled comment blocks
     (`=== Reserved Keywords ===`, `=== Contextual Keywords ===`, and so on).
     Productions cannot express this: `"old"` and `"fn"` are syntactically
     identical as terminals, but one is reserved and the other is not.

`load()` then CROSS-CHECKS the two against each other, which is the point of
reading the EBNF rather than a hand-written YAML file. A declared word that
appears in no production, or a production terminal that nothing classifies, is an
error. That is the property keywords.yaml never had: nothing could contradict it.

See ADR-0060 (mvl-lang/mvl#2050) for why the direction was inverted.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

SPEC_ROOT = Path(__file__).resolve().parent.parent.parent
GRAMMAR_EBNF = SPEC_ROOT / "grammar" / "grammar.ebnf"
KEYWORDS_YAML = SPEC_ROOT / "grammar" / "keywords.yaml"

# Comment-block heading -> the label prefixes inside it that carry word lists.
# Order matters only for reporting.
RESERVED_LABELS = (
    "Declaration",
    "Totality",
    "Cast",
    "Control flow",
    "Let binding",
    "Ownership",
    "IFC",
    "Boolean",
    "Refinements",
    "Pattern",
)

# Quoted terminals in productions that are not language words at all.
# Every entry needs a reason — this list is the only place extraction can be
# weakened, so it stays short and justified.
PRODUCTION_NOISE = {
    "A": "ALPHA character-class upper bound",
    "Z": "ALPHA character-class upper bound",
    "a": "ALPHA character-class lower bound",
    "z": "ALPHA character-class lower bound",
    "_": "wildcard pattern / ALPHA member, not a word",
    "len": (
        "not a keyword: ordinary identifier naming a compiler-known method "
        "(x.len()); ref_atom enumerates the free-function form len(x) because "
        "the refinement sub-grammar admits no arbitrary calls"
    ),
    # mvl-lang/mvl-spec#38: numeric-literal syntax markers, not identifiers or
    # keywords. Case-insensitive by lexer design (numbers.rs matches Some('x')
    # | Some('X') etc.), so both cases appear as literal terminals in INTEGER.
    "x": "hex-literal prefix marker (0x...), case-insensitive",
    "X": "hex-literal prefix marker (0X...), case-insensitive",
    "b": "binary-literal prefix marker (0b...), case-insensitive",
    "B": "binary-literal prefix marker (0B...), case-insensitive",
    "o": "octal-literal prefix marker (0o...), case-insensitive",
    "O": "octal-literal prefix marker (0O...), case-insensitive",
    "e": "float exponent marker (1e10), case-insensitive",
    "E": "float exponent marker (1E10), case-insensitive",
    "f": "HEX_DIGIT character-class upper bound",
    "F": "HEX_DIGIT character-class upper bound",
}

BANNER = (
    "DO NOT EDIT THIS BLOCK BY HAND. Generated from mvl-spec "
    "grammar/grammar.ebnf by tools/generators/{script}. "
    "Run tools/generators/regen-all.sh after editing the grammar."
)


@dataclass(frozen=True)
class Keywords:
    reserved_by_label: dict[str, list[str]]
    contextual: list[str]
    builtin_types: list[str]
    stdlib_labels: list[str]
    production_terminals: set[str]

    @property
    def reserved(self) -> list[str]:
        """The words the lexer will not accept as identifiers.

        Excludes `Pattern` — Some/None/Ok/Err are constructors matched as paths,
        not lexer keywords (verified against src/mvl/parser/lexer/mod.rs).
        """
        out: list[str] = []
        for label in RESERVED_LABELS:
            if label == "Pattern":
                continue
            out.extend(self.reserved_by_label.get(label, []))
        return out

    @property
    def pattern(self) -> list[str]:
        return list(self.reserved_by_label.get("Pattern", []))

    def section(self, name: str) -> list[str]:
        """Access a reserved label by its keywords.yaml-style snake_case name."""
        label = {
            "declaration": "Declaration",
            "totality": "Totality",
            "cast": "Cast",
            "control_flow": "Control flow",
            "let_binding": "Let binding",
            "ownership": "Ownership",
            "ifc": "IFC",
            "boolean": "Boolean",
            "refinements": "Refinements",
            "pattern": "Pattern",
        }[name]
        return list(self.reserved_by_label[label])


def _block(text: str, heading: str) -> str:
    """Return the comment block introduced by `=== heading ===`."""
    start = text.find(f"=== {heading} ===")
    if start == -1:
        raise ValueError(f"grammar.ebnf: missing `=== {heading} ===` block")
    rest = text[start:]
    # A block ends at the next `=== ... ===` heading or the first non-comment line.
    nxt = rest.find("(* === ", 4)
    return rest[:nxt] if nxt != -1 else rest


def _labelled_words(block: str, labels: tuple[str, ...]) -> dict[str, list[str]]:
    """Parse `(* Label:  word  word  *)` lines, including continuation lines."""
    out: dict[str, list[str]] = {}
    current: str | None = None
    for raw in block.splitlines():
        line = raw.strip()
        if not line.startswith("(*"):
            continue
        body = line.removeprefix("(*").removesuffix("*)").strip()
        if not body or body.startswith("==="):
            continue
        matched = next((l for l in labels if body.startswith(f"{l}:")), None)
        if matched:
            current = matched
            body = body[len(matched) + 1 :]
            out.setdefault(current, [])
        elif current is None:
            continue
        elif ":" in body and body.split(":", 1)[0].strip().isalpha() and "  " in body:
            # A new label this parser does not know about — stop accumulating
            # rather than silently appending its words to the previous label.
            current = None
            continue
        if current is not None:
            # Continuation lines are prose unless they are bare words.
            words = [w for w in body.split() if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", w)]
            if len(words) != len(body.split()):
                continue  # prose line inside the block (a NOTE, etc.)
            out[current].extend(words)
    return out


def production_terminals(text: str) -> set[str]:
    """Identifier-shaped quoted terminals in productions, comments stripped."""
    prods = re.sub(r"\(\*.*?\*\)", "", text, flags=re.S)
    return set(re.findall(r'"([A-Za-z_][A-Za-z0-9_]*)"', prods))


def load(path: Path = GRAMMAR_EBNF) -> Keywords:
    text = path.read_text()

    reserved_by_label = _labelled_words(
        _block(text, "Reserved Keywords"), RESERVED_LABELS
    )
    missing_labels = set(RESERVED_LABELS) - set(reserved_by_label)
    if missing_labels:
        raise ValueError(
            f"{path}: Reserved Keywords block is missing label(s): "
            f"{sorted(missing_labels)}"
        )

    ctx = _labelled_words(_block(text, "Contextual Keywords"), ("Contextual",))
    builtins = _labelled_words(_block(text, "Builtin Types"), ("Builtin types",))
    labels = _labelled_words(_block(text, "Stdlib IFC Labels"), ("Stdlib labels",))

    kw = Keywords(
        reserved_by_label=reserved_by_label,
        contextual=ctx.get("Contextual", []),
        builtin_types=builtins.get("Builtin types", []),
        stdlib_labels=labels.get("Stdlib labels", []),
        production_terminals=production_terminals(text),
    )
    _cross_check(kw, path)
    return kw


def _cross_check(kw: Keywords, path: Path) -> None:
    """Reconcile the declared classification against the productions.

    This is what makes the EBNF a falsifiable source rather than an assertion.
    """
    declared = (
        set(kw.reserved)
        | set(kw.pattern)
        | set(kw.contextual)
        | set(kw.builtin_types)
        | set(kw.stdlib_labels)
    )
    errs: list[str] = []

    overlap = set(kw.reserved) & set(kw.contextual)
    if overlap:
        errs.append(
            f"{sorted(overlap)} declared both reserved and contextual — "
            "a word is one or the other"
        )

    # Every reserved word must actually be used by a production. A reserved word
    # the grammar never mentions is either dead or a typo.
    orphans = set(kw.reserved) - kw.production_terminals
    if orphans:
        errs.append(
            f"{sorted(orphans)} declared reserved but appear in no production. "
            "Either the grammar is missing them or the declaration is wrong."
        )

    # Every production terminal must be classified, or explicitly declared noise.
    unclassified = kw.production_terminals - declared - set(PRODUCTION_NOISE)
    if unclassified:
        errs.append(
            f"{sorted(unclassified)} appear as terminals in productions but are "
            "classified nowhere. Add each to a category block in grammar.ebnf, "
            "or to PRODUCTION_NOISE with a reason."
        )

    if errs:
        raise SystemExit(
            f"{path}: grammar and its keyword declarations disagree.\n\n"
            + "\n\n".join(f"  - {e}" for e in errs)
        )


def banner(script: str, comment: str = "#") -> list[str]:
    text = BANNER.format(script=script)
    lines, cur = [], ""
    for w in text.split():
        if len(cur) + len(w) + 1 > 72:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return [f"{comment} {ln}" for ln in lines]


def replace_region(text: str, marker: str, body: str, comment: str = "#") -> str:
    begin = f"{comment} BEGIN GENERATED {marker}"
    end = f"{comment} END GENERATED {marker}"
    if begin not in text or end not in text:
        raise ValueError(f"missing region markers for {marker!r}")
    head, _, rest = text.partition(begin)
    _, _, tail = rest.partition(end)
    return f"{head}{begin}\n{body.rstrip()}\n{end}{tail}"


if __name__ == "__main__":
    k = load()
    print(f"reserved      {len(k.reserved):>3}")
    print(f"pattern       {len(k.pattern):>3}  {' '.join(k.pattern)}")
    print(f"contextual    {len(k.contextual):>3}  {' '.join(k.contextual)}")
    print(f"builtin_types {len(k.builtin_types):>3}")
    print(f"stdlib_labels {len(k.stdlib_labels):>3}  {' '.join(k.stdlib_labels)}")
    print(f"production terminals {len(k.production_terminals):>3}")
    sys.exit(0)
