#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""grammar.ebnf -> the keyword patterns in editors/vscode/syntaxes/mvl.tmLanguage.json.

VS Code does not use tree-sitter, so its TextMate grammar restates every keyword
list as its own regex. That independence is why it drifted furthest: before this
generator it highlighted five words that do not exist in MVL (`mut`, `move`, and
the lowercase `public`/`tainted`/`secret` fn-level security prefix that
grammar.ebnf:72-73 explicitly denies), listed 5 of 13 declaration keywords, and
had no pattern for the refinement clauses at all. `{alt}` is the alternation;
templates differ because a label only counts when followed by `[`.

Only the `match` strings of keyword-derived repository entries are rewritten.
Scopes, ordering, and the hand-written entries (strings, numbers, operators,
begin/end blocks) are untouched.

Usage:
    python3 tools/generators/gen_vscode.py [--check]
"""

from __future__ import annotations

import argparse
import json
import sys

import _keywords as K

SCRIPT = "gen_vscode.py"
COMMENT = f"Generated from grammar.ebnf by {SCRIPT} — do not edit the matches."
TM_PATH = K.SPEC_ROOT / "editors" / "vscode" / "syntaxes" / "mvl.tmLanguage.json"

# (repository key, TextMate scope, member specs, regex template)
# Keyed by scope as well as entry, because several entries carry more than one
# pattern with different scopes — `use`/`pub` are scoped as module keywords, and
# `None` is a null constant rather than a constructor.
GENERATED: list[tuple[str, str, list[str], str]] = [
    ("keywords-declaration", "keyword.other.declaration.mvl",
     ["declaration:-use,pub", "ifc"], r"\b({alt})\b"),
    ("keywords-declaration", "keyword.other.module.mvl",
     ["declaration:use,pub"], r"\b({alt})\b"),
    ("keywords-control", "keyword.control.mvl",
     ["control_flow", "let_binding"], r"\b({alt})\b"),
    ("keywords-refinement", "keyword.other.refinement.mvl",
     ["refinements"], r"\b({alt})\b"),
    ("keywords-expression", "keyword.operator.expression.mvl",
     ["cast", "ownership:consume"], r"\b({alt})\b"),
    ("totality-modifiers", "storage.modifier.totality.mvl",
     ["totality"], r"\b({alt})\b"),
    ("capability-annotations", "storage.modifier.capability.mvl",
     ["ownership:-consume"], r"\b({alt})\b"),
    ("constants", "constant.language.boolean.mvl",
     ["boolean"], r"\b({alt})\b"),
    ("constants", "constant.language.null.mvl",
     ["pattern:None"], r"\b({alt})\b"),
    ("constructors", "entity.name.tag.constructor.mvl",
     ["pattern:-None"], r"\b({alt})\b"),
    ("security-labels", "storage.type.security-label.mvl",
     ["@stdlib_labels"], r"\b({alt})(?=\s*\[)"),
    ("builtin-types", "support.type.builtin.mvl",
     ["@builtin_types"], r"\b({alt})\b"),
]

# Repository entries that existed only to highlight constructs MVL does not have.
# Removed rather than regenerated; each needs a reason.
PHANTOM_ENTRIES = {
    "security-modifiers": (
        "highlighted lowercase public/tainted/secret as a fn-level security "
        "prefix. grammar.ebnf:72-73 states there is no such prefix and that "
        "these are NOT reserved words; the compiler has no such tokens."
    ),
}


def _resolve(spec: str, kw: K.Keywords) -> list[str]:
    if spec == "@stdlib_labels":
        return list(kw.stdlib_labels)
    if spec == "@builtin_types":
        return list(kw.builtin_types)
    if ":" not in spec:
        return kw.section(spec)
    cat, sel = spec.split(":", 1)
    members = kw.section(cat)
    if sel.startswith("-"):
        drop = {s.strip() for s in sel[1:].split(",")}
        return [m for m in members if m not in drop]
    keep = [s.strip() for s in sel.split(",")]
    unknown = set(keep) - set(members)
    if unknown:
        raise ValueError(f"{spec}: {sorted(unknown)} not in '{cat}'")
    return keep


def _verify_coverage(kw: K.Keywords) -> None:
    """Every reserved word and constructor lands in exactly one pattern."""
    seen: dict[str, str] = {}
    for key, scope, specs, _t in GENERATED:
        for spec in specs:
            if spec.startswith("@"):
                continue
            for w in _resolve(spec, kw):
                if w in seen:
                    raise SystemExit(
                        f"gen_vscode.py: '{w}' emitted in both {seen[w]} and "
                        f"{key}/{scope}"
                    )
                seen[w] = f"{key}/{scope}"
    missing = (set(kw.reserved) | set(kw.pattern)) - set(seen)
    if missing:
        raise SystemExit(
            f"gen_vscode.py: {sorted(missing)} are declared in grammar.ebnf but "
            "land in no TextMate pattern. Add them to GENERATED."
        )
    leaked = set(kw.contextual) & set(seen)
    if leaked:
        raise SystemExit(
            f"gen_vscode.py: contextual word(s) {sorted(leaked)} would be "
            "emitted as bare words — they are ordinary identifiers outside "
            "their one position."
        )


def render(kw: K.Keywords) -> str:
    _verify_coverage(kw)
    text = TM_PATH.read_text()
    data = json.loads(text)
    repo = data.get("repository", {})

    for key, reason in PHANTOM_ENTRIES.items():
        if key in repo:
            del repo[key]
        data["patterns"] = [
            p for p in data.get("patterns", []) if p.get("include") != f"#{key}"
        ]
        data.setdefault("_removed", {})[key] = reason

    for key, scope, specs, template in GENERATED:
        words: list[str] = []
        for spec in specs:
            words.extend(_resolve(spec, kw))
        match = template.format(alt="|".join(words))
        entry = repo.get(key)
        if entry is None:
            repo[key] = {
                "comment": COMMENT,
                "patterns": [{"name": scope, "match": match}],
            }
            data["patterns"].append({"include": f"#{key}"})
            continue
        entry["comment"] = COMMENT
        target = [p for p in entry.get("patterns", []) if p.get("name") == scope]
        if len(target) == 1:
            target[0]["match"] = match
        elif not target:
            entry["patterns"].append({"name": scope, "match": match})
        else:
            raise SystemExit(
                f"gen_vscode.py: repository['{key}'] has {len(target)} patterns "
                f"scoped {scope}; expected at most 1."
            )

    data.pop("_removed", None)
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    kw = K.load()
    new = render(kw)
    old = TM_PATH.read_text()

    if new == old:
        print("mvl.tmLanguage.json: up to date")
        return 0
    if args.check:
        print(
            f"DRIFT — {TM_PATH} is stale versus grammar.ebnf.\n"
            "Fix: tools/generators/regen-all.sh",
            file=sys.stderr,
        )
        return 1
    json.loads(new)  # never write invalid JSON
    TM_PATH.write_text(new)
    print(f"  wrote {TM_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
