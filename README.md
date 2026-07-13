# mvl-spec

**Formal specification of the MVL (Maximum Verifiable Language) programming language.**

This repository is the source of truth for what MVL *is*, independent of any particular implementation of it. The compiler in [`mvl-lang/mvl`](https://github.com/mvl-lang/mvl) implements this specification; other tooling consumes it.

---

## Contents

```
mvl-spec/
├── grammar/          # Formal grammar
│   ├── grammar.ebnf     ISO 14977 EBNF — the authoritative grammar
│   └── keywords.yaml    Reserved keyword sets — single source of truth
├── semantics/        # Formal semantics (Ott → Coq/Isabelle/LaTeX) — planned
├── reference/        # Prose language reference — planned
├── tools/            # Language tooling that ships to package registries
│   ├── tree-sitter/     tree-sitter-mvl (published to npm)
│   ├── pygments/        pygments-mvl (published to PyPI) — planned
│   └── generators/      Scripts that derive tooling from grammar/keywords.yaml
└── editors/          # Editor integrations
    ├── nvim/            Neovim plugin
    ├── vscode/          VS Code extension
    └── zed/             Zed extension
```

---

## What lives here vs. in the compiler repo

**In this repo (`mvl-spec`):**

- The grammar (EBNF)
- The keyword source of truth (YAML)
- The semantics (Ott, LaTeX, Coq — planned)
- The prose language reference (planned)
- Every parser and syntax-highlighter derived from the grammar
- Editor integrations (Neovim, VS Code, Zed)

**In [`mvl-lang/mvl`](https://github.com/mvl-lang/mvl):**

- The MVL compiler (Rust)
- The self-hosted MVL-in-MVL compiler (`compiler/`)
- The standard library (`std/`)
- The test corpus
- ADRs (architectural decisions specific to the compiler implementation)

**Rule of thumb:** if it defines what MVL is, it lives here. If it implements how a particular tool understands MVL, it lives here too. If it is the compiler itself, it lives in the compiler repo. Same relationship as [`rust-lang/rust`](https://github.com/rust-lang/rust) ↔ [`rust-lang/reference`](https://github.com/rust-lang/reference).

---

## The single-source-of-truth discipline

`grammar/keywords.yaml` is the canonical list of MVL reserved keywords. Every consumer generates its keyword table from this file:

- `tools/tree-sitter/grammar.js` — via `tools/generators/gen_tree_sitter.js`
- `tools/pygments/mvl_pygments/lexer.py` — via `tools/generators/gen_pygments.py`
- `editors/vscode/syntaxes/*.json` — via `tools/generators/gen_vscode.js`

CI enforces this: adding a keyword to `keywords.yaml` without regenerating downstream artifacts is a hard failure. Adding a keyword to any downstream artifact without updating `keywords.yaml` is also a failure. There is one place to change; the rest is derived.

This discipline is the primary reason these artifacts live together in one repo rather than one repo each.

---

## Publishing

Each shippable artifact has its own version tag namespace:

| Artifact | Tag prefix | Registry | Directory |
|----------|-----------|----------|-----------|
| Full spec release | `spec-v*` | Zenodo (DOI) | *(repo root)* |
| tree-sitter grammar | `tree-sitter-v*` | npm as `tree-sitter-mvl` | `tools/tree-sitter/` |
| Pygments lexer | `pygments-v*` | PyPI as `pygments-mvl` | `tools/pygments/` |
| VS Code extension | `vscode-v*` | VS Code Marketplace | `editors/vscode/` |
| Zed extension | `zed-v*` | Zed Extensions | `editors/zed/` |
| Neovim plugin | `nvim-v*` | git only (users install by URL) | `editors/nvim/` |

CI workflows watch the tag prefix and publish from the matching subdirectory.

---

## Versioning policy

The spec itself is versioned independently of tooling. Each downstream tool declares which spec range it supports:

```
tree-sitter-mvl v0.3.2   tracks mvl-spec >= 0.55, < 0.70
pygments-mvl    v0.1.5   tracks mvl-spec >= 0.55
```

This lets tooling ship bug fixes without forcing a full spec revision, and lets the spec evolve without immediately breaking every downstream user.

---

## The 11 Requirements

MVL is defined by eleven properties the compiler verifies at compile time. The full statement lives at [mvl-lang.org/why/requirements](https://mvl-lang.org/why/requirements/). Every rule in `grammar.ebnf` and every semantic definition here exists in service of these eleven properties.

1. Type safety (ADTs)
2. Memory safety
3. Totality (exhaustive match)
4. Null elimination (Option)
5. Error visibility (Result)
6. Ownership (linearity)
7. Effect tracking
8. Termination checking
9. Data race freedom
10. Refinement types
11. Information flow control

---

## Roadmap for this repo

- ✅ Grammar (EBNF)
- ✅ Keyword source of truth
- ✅ Tree-sitter grammar
- ✅ Editor integrations (Neovim, VS Code, Zed)
- 🔄 Pygments lexer — [#1](https://github.com/mvl-lang/mvl-spec/issues/1)
- 🔄 Generator scripts (regenerate keyword tables from `keywords.yaml`) — [#2](https://github.com/mvl-lang/mvl-spec/issues/2)
- ⬜ Ott semantics (types, effects, IFC, contracts, actors) — [#3](https://github.com/mvl-lang/mvl-spec/issues/3)
- ⬜ Lean 4 mechanization + soundness theorem (Phase 9) — [#4](https://github.com/mvl-lang/mvl-spec/issues/4)
- ⬜ Prose language reference migrated from mvl repo — [#5](https://github.com/mvl-lang/mvl-spec/issues/5)

---

## Contributing

Grammar or keyword changes:

1. Update `grammar/grammar.ebnf` and `grammar/keywords.yaml` in the same PR
2. Run `tools/generators/regen-all.sh` (once the generators exist)
3. Verify that CI passes drift check
4. Reference the ADR that motivated the change (if any) from the mvl repo

Editor extensions and tooling releases are cut by tagging with the appropriate prefix (see Publishing above).

---

## License

Apache-2.0 — matches the MVL compiler and standard library.

---

## See also

- [mvl-lang.org](https://mvl-lang.org) — the project website
- [mvl-lang/mvl](https://github.com/mvl-lang/mvl) — the compiler
- [mvl-lang/mvl-lang.github.io](https://github.com/mvl-lang/mvl-lang.github.io) — the website source
