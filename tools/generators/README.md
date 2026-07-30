# Generators

Scripts that regenerate downstream artifacts from **`grammar/grammar.ebnf`**.

## The direction

```
grammar/grammar.ebnf  ─┬─►  grammar/keywords.yaml                (gen_keywords_yaml.py)
                       ├─►  editors/nvim/queries/mvl/            (gen_highlights.py)
                       ├─►  editors/zed/languages/mvl/           (gen_highlights.py)
                       ├─►  tree-sitter-mvl queries/             (gen_highlights.py)
                       ├─►  tree-sitter-mvl grammar.js           (gen_tree_sitter.py)
                       └─►  editors/vscode/syntaxes/             (gen_vscode.py)
```

The EBNF is the source. **`keywords.yaml` is an artifact** — a machine-readable
projection, kept because YAML is convenient for consumers that should not parse
EBNF comments. Nobody edits it.

That is the reverse of what this file described before 0.1.4. `keywords.yaml` used
to be the declared source, and it was a verbatim transcription of the EBNF's own
`=== Reserved Keywords ===` block — two copies of one list, inside the source of
truth. See ADR-0060 (mvl-lang/mvl#2050).

## Why the EBNF and not the YAML

Because it can be contradicted. The EBNF is checked two ways against itself:

| Source within the EBNF | Gives |
|---|---|
| **Productions** | Which words are grammar syntax — extracted mechanically. All 43 reserved words appear as quoted terminals. |
| **Labelled comment blocks** | How each word is classified. Productions cannot express this: `"old"` and `"fn"` are identical as terminals. |

`_keywords.py` reconciles them. A declared word appearing in no production is an
error. A production terminal classified nowhere is an error. `keywords.yaml` had
no equivalent check — nothing read it, so nothing could fail because of it.

## Categories

Only the first is reserved. Conflating them is what caused the drift these
scripts exist to prevent.

| Block | Count | Nature |
|---|---:|---|
| `=== Reserved Keywords ===`, `Declaration`…`Refinements` | 43 | Lexer rejects them as identifiers |
| same block, `Pattern` | 4 | Constructors, matched as paths — not lexer keywords |
| `=== Contextual Keywords ===` | 5 | `self old end timeout audit` — special in one position, ordinary identifiers elsewhere |
| `=== Builtin Types ===` | 23 | Reserved by convention only |
| `=== Stdlib IFC Labels ===` | 6 | Ordinary identifiers |

**Contextual words must never be emitted as bare-word patterns.** Each is a legal
variable name — verified: `let end: Int = 1;` compiles, while `let fn = 1;` is
rejected. A flat keyword list highlights `let end = 5` as a keyword.

**`len` is in no category.** It is a quoted terminal in `ref_atom` only because the
refinement sub-grammar admits no arbitrary calls and must enumerate what it
allows. In ordinary code `len` is a compiler-known method (`x.len()`); the
free-function form `len(x)` exists only inside a predicate.

## Usage

```bash
tools/generators/regen-all.sh                          # regenerate everything
tools/generators/regen-all.sh --check                  # fail if anything is stale
tools/generators/check-drift.sh                        # alias for --check; used by CI
tools/generators/regen-all.sh --tree-sitter-dir ../ts  # non-sibling grammar checkout
```

Each generator also runs standalone and takes `--check`.

If `grammar.js` changed, rebuild the parser — the generators do not:

```bash
cd ../tree-sitter-mvl && tree-sitter generate && tree-sitter test
```

## Cross-repo

`gen_highlights.py` and `gen_tree_sitter.py` write into `mvl-lang/tree-sitter-mvl`,
defaulting to a sibling checkout — the layout `tools/check-versions.py` already
assumes. If it is absent they print a skip to stderr, so `check-drift.yml` asserts
both targets exist before running: **a skipped generator must not read as a pass.**

## Discipline

`.github/workflows/check-drift.yml` regenerates on every PR touching `grammar/`,
`tools/generators/` or `editors/`, and fails on any diff. Editing a generated file
directly is a CI failure. Edit the grammar and regenerate.

All generators are Python, not JavaScript as this file previously specified. Python
is already a dependency via `check-versions.py` and `tools/lsp`, so the drift check
needs no Node in CI. All are idempotent — running twice is a no-op, which is what
makes `--check` meaningful.

## Not here yet

Full-EBNF-driven codegen — parsing productions to generate whole grammar files
rather than keyword tables — remains a separate, later step.

(`gen_pygments.py` and the `tools/pygments/mvl_pygments/` package it targets
both shipped in 0.1.5, closing #1 — this section previously described them as
future work, stale as of that release.)
