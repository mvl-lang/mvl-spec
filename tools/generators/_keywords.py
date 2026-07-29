#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Shared loader for grammar/keywords.yaml.

Every generator imports from here so there is exactly one place that knows the
file's shape. If a category is added to keywords.yaml and not handled here,
`load()` raises rather than silently dropping it — a generator that quietly
ignores a new category is how drift got in last time.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover
    sys.exit("PyYAML is required: pip install pyyaml")

SPEC_ROOT = Path(__file__).resolve().parent.parent.parent
KEYWORDS_YAML = SPEC_ROOT / "grammar" / "keywords.yaml"

# Sections whose members the lexer genuinely reserves, in file order.
RESERVED_SECTIONS = (
    "declaration",
    "totality",
    "cast",
    "control_flow",
    "let_binding",
    "ownership",
    "ifc",
    "boolean",
    "refinements",
)

# Everything else, each needing different downstream treatment.
OTHER_SECTIONS = ("pattern", "contextual", "builtin_types", "stdlib_labels")

BANNER = (
    "DO NOT EDIT THIS BLOCK BY HAND. Generated from mvl-spec "
    "grammar/keywords.yaml by tools/generators/{script}. "
    "Run tools/generators/regen-all.sh after editing keywords.yaml."
)


@dataclass(frozen=True)
class Keywords:
    """Parsed keywords.yaml, with the reserved/other distinction preserved."""

    by_section: dict[str, list[str]]

    @property
    def reserved(self) -> list[str]:
        """The 43 words the lexer will not accept as identifiers."""
        out: list[str] = []
        for s in RESERVED_SECTIONS:
            out.extend(self.by_section[s])
        return out

    @property
    def pattern(self) -> list[str]:
        return self.by_section["pattern"]

    @property
    def contextual(self) -> list[str]:
        """Special in one syntactic position; ordinary identifiers elsewhere.

        Must never be emitted into an unconditional keyword list — see the
        keywords.yaml header.
        """
        return self.by_section["contextual"]

    @property
    def builtin_types(self) -> list[str]:
        return self.by_section["builtin_types"]

    @property
    def stdlib_labels(self) -> list[str]:
        return self.by_section["stdlib_labels"]

    def section(self, name: str) -> list[str]:
        return self.by_section[name]


def load(path: Path = KEYWORDS_YAML) -> Keywords:
    raw = yaml.safe_load(path.read_text())
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: expected a mapping at the top level")

    expected = set(RESERVED_SECTIONS) | set(OTHER_SECTIONS)
    actual = set(raw)

    missing = expected - actual
    if missing:
        raise ValueError(f"{path}: missing section(s): {sorted(missing)}")

    # Fail loudly on a category this loader does not know about, so a new
    # section cannot be silently omitted from every generated artifact.
    unknown = actual - expected
    if unknown:
        raise ValueError(
            f"{path}: unknown section(s) {sorted(unknown)}. Add them to "
            f"RESERVED_SECTIONS or OTHER_SECTIONS in {Path(__file__).name} and "
            "decide how each generator should treat them."
        )

    by_section = {}
    for name in sorted(expected):
        vals = raw[name]
        if not isinstance(vals, list) or not vals:
            raise ValueError(f"{path}: section '{name}' must be a non-empty list")
        by_section[name] = [str(v) for v in vals]

    kw = Keywords(by_section=by_section)

    # Cheap invariant: nothing may be both reserved and contextual.
    both = set(kw.reserved) & set(kw.contextual)
    if both:
        raise ValueError(
            f"{path}: {sorted(both)} listed as both reserved and contextual. "
            "A word is one or the other."
        )
    return kw


def banner(script: str, comment: str = "#") -> list[str]:
    """Return the do-not-edit banner as comment lines in the target syntax."""
    text = BANNER.format(script=script)
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > 72:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return [f"{comment} {ln}" for ln in lines]


def replace_region(text: str, marker: str, body: str, comment: str = "#") -> str:
    """Swap the contents of a BEGIN/END GENERATED region, leaving the rest alone.

    Regions are delimited so hand-written logic in the same file survives
    regeneration — the .scm query sets carry node-anchored captures that no
    generator can produce.
    """
    begin = f"{comment} BEGIN GENERATED {marker}"
    end = f"{comment} END GENERATED {marker}"
    if begin not in text or end not in text:
        raise ValueError(f"missing region markers for {marker!r}")
    head, _, rest = text.partition(begin)
    _, _, tail = rest.partition(end)
    return f"{head}{begin}\n{body.rstrip()}\n{end}{tail}"
