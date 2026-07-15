# mvl-spec Changelog

All notable changes to the MVL specification will be documented here.

The spec is versioned independently of the compiler and the individual tools. See [README §Versioning policy](README.md#versioning-policy) for how tool versions relate to spec versions.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). While the spec is pre-1.0, MINOR bumps signal breaking changes; PATCH bumps signal additive or non-breaking changes.

---

## [Unreleased]

### Fixed

- **Grammar drift with compiler parser** — reconciled `grammar/grammar.ebnf` and
  `grammar/keywords.yaml` with the actual parser in `mvl-lang/mvl`:
  - Removed obsolete `security` prefix (`public` / `tainted` / `secret`) from
    `fn_decl`; security is expressed only via wrapper types (`Tainted[T]`, `Secret[T]`).
  - Removed obsolete `declassify(e)` and `sanitize(e)` expression forms; both
    were replaced by `relabel name(e, "TAG")` under #894. Also removed from
    `keywords.yaml` `ifc:` section.
  - Fixed `forall` / `exists` separator from `"."` to `","` to match the parser.
  - Dropped trailing `";"` from `label_decl`, `relabel_decl`, and `effect_decl`
    (the parser does not consume one).
  - Made trailing comma on `match_arm` optional (it is a separator, not terminator).
  - Clarified that `timeout` inside `select` is a *contextual* identifier, not a
    reserved keyword.

## [0.1.0] — 2026-07-13

Initial spec release. Content migrated from `mvl-lang/mvl` (see [mvl#1813](https://github.com/mvl-lang/mvl/issues/1813) for the corresponding cleanup on the compiler side).

### Added

- **Grammar**
  - `grammar/grammar.ebnf` — ISO 14977 EBNF, LL(1), ≈100 productions
  - `grammar/keywords.yaml` — single source of truth for reserved keywords, organized by semantic category (declaration, totality, control flow, ownership, IFC, refinements, patterns, builtin types, security labels)

- **Tree-sitter grammar** (`tools/tree-sitter/`)
  - Full `grammar.js`, query files (`highlights.scm`, `folds.scm`), test corpus
  - Published under package name `tree-sitter-mvl` at version `0.1.0`

- **Editor integrations**
  - Neovim plugin (`editors/nvim/`) — tree-sitter-backed highlighting, folds, indent, filetype detection
  - VS Code extension (`editors/vscode/`) — TextMate grammar, language configuration
  - Zed extension (`editors/zed/`) — tree-sitter integration, brackets, indents

- **Placeholder scaffolding**
  - `semantics/` — planned Ott spec + generated Coq/LaTeX (tracked in [#3](https://github.com/mvl-lang/mvl-spec/issues/3))
  - `reference/` — planned prose reference migration (tracked in [#5](https://github.com/mvl-lang/mvl-spec/issues/5))
  - `tools/pygments/` — planned Pygments lexer (tracked in [#1](https://github.com/mvl-lang/mvl-spec/issues/1))
  - `tools/generators/` — planned keyword-generator scripts (tracked in [#2](https://github.com/mvl-lang/mvl-spec/issues/2))

- **Versioning + publishing**
  - Independent semver per shippable artifact
  - Publish-workflow skeletons in `.github/workflows/` for each tag prefix (`spec-v*`, `tree-sitter-v*`, `pygments-v*`, `vscode-v*`, `zed-v*`, `nvim-v*`)
  - Root CHANGELOG (this file); per-tool CHANGELOGs alongside each tool

### Notes

The compiler repo still holds duplicate copies of the moved artifacts. That cleanup is tracked in [mvl-lang/mvl#1813](https://github.com/mvl-lang/mvl/issues/1813) and is expected to complete in a subsequent release.

Publishing credentials for npm / PyPI / VS Code Marketplace / Zed Extensions are **not yet configured** — the workflows exist as skeletons. First real publish will require credential setup.

---

[Unreleased]: https://github.com/mvl-lang/mvl-spec/compare/spec-v0.1.0...HEAD
[0.1.0]: https://github.com/mvl-lang/mvl-spec/releases/tag/spec-v0.1.0
