# mvl-spec

**Formal specification of the MVL (Maximum Verifiable Language) programming language.**

**Version:** [0.1.2](VERSION) — see [CHANGELOG.md](CHANGELOG.md)
**License:** Apache-2.0

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
│   ├── lsp/             mvl-lsp Phase 1 language server (published to PyPI)
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

## Versioning and publishing

The spec's `VERSION` file (currently `0.1.2`) is the coordination point. Artifacts (editor extensions, LSP, tree-sitter grammar) each carry their own version, but **at release checkpoints they are aligned to the spec version**. Between releases they may drift as feature work advances independently — the drift is caught and reconciled before the next release.

Run the version checker to see the current state:

```bash
python3 tools/check-versions.py                        # report drift
python3 tools/check-versions.py --fix                  # align local files to VERSION
python3 tools/check-versions.py --target 0.1.3         # override target
python3 tools/check-versions.py --tree-sitter-dir PATH # explicit grammar checkout
python3 tools/check-versions.py --skip-tree-sitter     # skip external repo
```

The script is stdlib-only (Python 3.11+), no venv needed. It auto-locates the external tree-sitter grammar in this order: `--tree-sitter-dir` → `$MVL_TREE_SITTER_DIR` → `../tree-sitter-mvl/` → read-only fetch from `raw.githubusercontent.com/mvl-lang/tree-sitter-mvl/main/`. Remote mode cannot `--fix`; clone locally to touch the grammar repo.

CHANGELOG headers are checked read-only — the top `## [X.Y.Z]` must be either the target version or `## [Unreleased]`; `--fix` does not touch release notes.

### Tag manifest

| Artifact | Current | Tag prefix | Registry | Location |
|----------|---------|-----------|----------|----------|
| Full spec release | `0.1.2` | `spec-v*` | GitHub Releases (Zenodo DOI planned) | *(repo root)* |
| tree-sitter grammar | `0.1.2` | `v*` (own repo) | npm as `tree-sitter-mvl` | [`mvl-lang/tree-sitter-mvl`](https://github.com/mvl-lang/tree-sitter-mvl) (external) |
| Pygments lexer | *(pending #1)* | `pygments-v*` | PyPI as `pygments-mvl` | `tools/pygments/` |
| Language server | `0.1.2` | `lsp-v*` | PyPI as `mvl-lsp` | `tools/lsp/` |
| VS Code extension | `0.1.2` | `vscode-v*` | VS Code Marketplace + Open VSX | `editors/vscode/` |
| Zed extension | `0.1.2` | `zed-v*` | Zed Extensions | `editors/zed/` |
| Neovim plugin | `0.1.2` | `nvim-v*` | git only (users install by URL) | `editors/nvim/` |

The tree-sitter grammar lives in [its own repo](https://github.com/mvl-lang/tree-sitter-mvl) because Zed's extension resolver requires `grammar.js` at a repository root. The `tools/tree-sitter/` subdirectory here is a legacy partial copy slated for removal — see [#34](https://github.com/mvl-lang/mvl-spec/issues/34).

CI workflows in `.github/workflows/publish-*.yml` watch each tag prefix and publish from the matching subdirectory. Actual publish steps are currently gated behind `if: false` — the workflows validate, build, and release to GitHub, but do not push to external registries until publishing credentials are configured.

### Semver interpretation (pre-1.0)

Because everything is pre-1.0, MINOR bumps mark the breakpoint:

- `0.x.0` → `0.(x+1).0` — breaking change (grammar restructure, keyword rename, incompatible query change)
- `0.x.y` → `0.x.(y+1)` — additive or non-breaking change

At 1.0 we shift to real semver. Documented in [CHANGELOG.md](CHANGELOG.md).

### LLM-assisted development

See [`CLAUDE.md`](CLAUDE.md) for repo conventions, common pitfalls, and the MVL taxonomy notes that coding assistants need to work here without repeating mistakes.

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
- ✅ Phase 1 language server (`tools/lsp/`, `mvl-lsp` on PyPI) — moved from the compiler repo in [#28](https://github.com/mvl-lang/mvl-spec/issues/28)
- 🔄 Phase 2 language server (compiler-integrated diagnostics) — [#29](https://github.com/mvl-lang/mvl-spec/issues/29)
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
