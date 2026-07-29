#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""keywords.yaml -> the keyword blocks of every highlights.scm.

Writes one generated region into all three copies — tree-sitter-mvl,
editors/nvim, editors/zed — so they cannot drift apart. Before this existed the
three had diverged by 22, 14 and 16 lines respectively, and between them
highlighted two words that are not keywords (`end`, `concurrently`) and two
contextual ones as if they were reserved (`old`, `timeout`).

Only *literal* keyword lists are generated. Node-anchored captures — anything of
the form `(some_node) @capture` — stay hand-written below the region, because a
generator cannot know grammar node names. Several keywords.yaml categories are
deliberately handled that way and must NOT also appear as literals, or they get
captured twice; NODE_HANDLED records which and why.

Usage:
    python3 tools/generators/gen_highlights.py [--check] [--tree-sitter-dir DIR]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import _keywords as K

SCRIPT = "gen_highlights.py"
MARKER = "KEYWORDS"

# keywords.yaml category -> tree-sitter capture for a literal keyword list.
# Splitting a category across captures is a presentation choice, so the mapping
# is explicit rather than derived: `use`/`pub` read as imports, `as`/`consume` as
# operators, and so on.
LITERAL_CAPTURES: list[tuple[str, str, list[str]]] = [
    # (heading, capture, members) — members resolved from keywords.yaml below.
    ("declarations", "@keyword", ["declaration:-use,pub", "ifc"]),
    ("imports", "@keyword.import", ["declaration:use,pub"]),
    ("bindings and statements", "@keyword", ["let_binding", "control_flow:-select"]),
    ("refinement and contract clauses", "@keyword.modifier", ["refinements"]),
    ("operators", "@keyword.operator", ["cast", "ownership:consume"]),
    ("concurrency", "@keyword.control", ["control_flow:select"]),
]

# Categories (or members) intentionally captured via grammar nodes instead.
# Every reserved word must appear in exactly one of LITERAL_CAPTURES or here;
# _verify_total_coverage enforces that.
NODE_HANDLED: dict[str, str] = {
    "totality:total": "(totality) @keyword.modifier",
    "totality:partial": "(totality) @keyword.modifier",
    "ownership:iso": "(capability) @keyword.modifier",
    "ownership:val": "(capability) @keyword.modifier",
    "ownership:ref": "(capability) @keyword.modifier",
    "ownership:tag": "(capability) @keyword.modifier",
    "boolean:true": "(boolean_literal) @constant.builtin",
    "boolean:false": "(boolean_literal) @constant.builtin",
}


def _resolve(spec: str, kw: K.Keywords) -> list[str]:
    """Resolve a member spec: 'cat', 'cat:a,b' (only these), 'cat:-a,b' (except)."""
    if ":" not in spec:
        return list(kw.section(spec))
    cat, sel = spec.split(":", 1)
    members = list(kw.section(cat))
    if sel.startswith("-"):
        drop = {s.strip() for s in sel[1:].split(",")}
        unknown = drop - set(members)
        if unknown:
            raise ValueError(f"{spec}: {sorted(unknown)} not in category '{cat}'")
        return [m for m in members if m not in drop]
    keep = [s.strip() for s in sel.split(",")]
    unknown = set(keep) - set(members)
    if unknown:
        raise ValueError(f"{spec}: {sorted(unknown)} not in category '{cat}'")
    return keep


def _verify_total_coverage(kw: K.Keywords) -> None:
    """Every reserved word is emitted exactly once, or declared node-handled.

    This is the check that makes the generator trustworthy: adding a keyword to
    keywords.yaml and forgetting to place it fails here rather than silently
    producing an artifact that omits it.
    """
    emitted: dict[str, str] = {}
    for heading, capture, specs in LITERAL_CAPTURES:
        for spec in specs:
            for word in _resolve(spec, kw):
                if word in emitted:
                    raise ValueError(
                        f"'{word}' emitted twice: {emitted[word]} and "
                        f"{heading}/{capture}. A word gets one capture."
                    )
                emitted[word] = f"{heading}/{capture}"

    node_words = {k.split(":", 1)[1] for k in NODE_HANDLED}
    covered = set(emitted) | node_words
    reserved = set(kw.reserved)

    missing = reserved - covered
    if missing:
        raise SystemExit(
            f"gen_highlights.py: {sorted(missing)} are reserved in keywords.yaml "
            "but not placed. Add each to LITERAL_CAPTURES or NODE_HANDLED."
        )
    stray = covered - reserved
    if stray:
        raise SystemExit(
            f"gen_highlights.py: {sorted(stray)} are placed but not reserved in "
            "keywords.yaml. Remove them, or add them to keywords.yaml."
        )
    overlap = set(emitted) & node_words
    if overlap:
        raise SystemExit(
            f"gen_highlights.py: {sorted(overlap)} are both emitted as literals "
            "and declared node-handled — that double-captures them."
        )


def render(kw: K.Keywords) -> str:
    _verify_total_coverage(kw)
    out: list[str] = []
    out += K.banner(SCRIPT, ";")
    out.append(";")
    out.append("; Literal keyword lists only. Node-anchored captures are hand-written")
    out.append("; below this region and survive regeneration.")

    for heading, capture, specs in LITERAL_CAPTURES:
        words: list[str] = []
        for spec in specs:
            words.extend(_resolve(spec, kw))
        out.append("")
        out.append(f"; {heading}")
        out.append("[")
        out += [f'  "{w}"' for w in words]
        out.append(f"] {capture}")

    out.append("")
    out.append("; Captured via grammar nodes instead of literals, so they cannot be")
    out.append("; confused with same-spelled identifiers:")
    for how in sorted(set(NODE_HANDLED.values())):
        words = sorted(k.split(":", 1)[1] for k, v in NODE_HANDLED.items() if v == how)
        out.append(f";   {', '.join(words)} -> {how}")

    out.append("")
    out.append("; CONTEXTUAL — never highlight these as bare words. Each is an ordinary")
    out.append("; identifier outside its one position, so a flat list would highlight")
    out.append('; `let end = 5`. Anchor on the enclosing node if wanted at all:')
    for w in kw.contextual:
        out.append(f";   {w}")

    return "\n".join(out)


TARGETS = [
    ("editors/nvim/queries/mvl/highlights.scm", None),
    ("editors/zed/languages/mvl/highlights.scm", None),
    ("queries/highlights.scm", "tree-sitter"),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="exit 1 if any file would change")
    ap.add_argument(
        "--tree-sitter-dir",
        type=Path,
        default=K.SPEC_ROOT.parent / "tree-sitter-mvl",
        help="path to a tree-sitter-mvl checkout (default: sibling of mvl-spec)",
    )
    args = ap.parse_args()

    # An explicitly-passed --tree-sitter-dir is a promise the target is there.
    # Skipping in that case turns a no-op into a green check — which is exactly
    # how this gate first passed while generating nothing.
    explicit = any(a.startswith("--tree-sitter-dir") for a in sys.argv[1:])

    kw = K.load()
    body = render(kw)

    drifted, written = [], []
    for rel, kind in TARGETS:
        root = args.tree_sitter_dir if kind == "tree-sitter" else K.SPEC_ROOT
        path = root / rel
        if not path.exists():
            if kind == "tree-sitter" and explicit:
                raise SystemExit(
                    f"  MISSING: {path}\n"
                    "--tree-sitter-dir was given, so this target is required. "
                    "Refusing to skip: a skipped generator must not read as a pass."
                )
            print(f"  skip (absent): {path}", file=sys.stderr)
            continue
        old = path.read_text()
        try:
            new = K.replace_region(old, MARKER, body, ";")
        except ValueError as e:
            raise SystemExit(f"{path}: {e}\nAdd the markers, then re-run.")
        if new == old:
            continue
        if args.check:
            drifted.append(str(path))
        else:
            path.write_text(new)
            written.append(str(path))

    if args.check:
        if drifted:
            print("DRIFT — these are stale versus keywords.yaml:", file=sys.stderr)
            for d in drifted:
                print(f"  {d}", file=sys.stderr)
            print("\nFix: tools/generators/regen-all.sh", file=sys.stderr)
            return 1
        print("highlights.scm: up to date")
        return 0

    for w in written:
        print(f"  wrote {w}")
    if not written:
        print("  highlights.scm: already current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
