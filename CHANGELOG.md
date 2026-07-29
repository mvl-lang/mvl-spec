# mvl-spec Changelog

All notable changes to the MVL specification will be documented here.

The spec is versioned independently of the compiler and the individual tools. See [README §Versioning policy](README.md#versioning-policy) for how tool versions relate to spec versions.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). While the spec is pre-1.0, MINOR bumps signal breaking changes; PATCH bumps signal additive or non-breaking changes.

---

## [Unreleased]

## [0.1.4] — 2026-07-29

### Added

- **`grammar/grammar.ebnf` is now the enforced source of truth (#2).** It was
  nominally authoritative for three releases while nothing read
  `grammar/keywords.yaml` — no tool consumed it, so no test could fail because of
  it. `keywords.yaml` turned out to be a verbatim transcription of the EBNF's own
  `=== Reserved Keywords ===` block: two copies of one list, inside the source of
  truth. See ADR-0060 (mvl-lang/mvl#2050).

  The EBNF is now read two ways and reconciled — productions give the *set* (all
  43 reserved words appear as quoted terminals), labelled comment blocks give the
  *classification* (productions cannot distinguish `"old"` from `"fn"`). A
  declared word appearing in no production is an error; a production terminal
  classified nowhere is an error.

  - `tools/generators/_keywords.py` — shared loader with that cross-check
  - `gen_keywords_yaml.py` — **`keywords.yaml` is now generated**
  - `gen_highlights.py` — writes the keyword blocks of all three `highlights.scm`
    copies, which had drifted by 22, 14 and 16 lines
  - `gen_vscode.py` — the TextMate keyword patterns
  - `gen_tree_sitter.py` — the `security_label` closed set
  - `regen-all.sh`, `check-drift.sh`, and `.github/workflows/check-drift.yml`

  New EBNF blocks: `=== Contextual Keywords ===`, `=== Builtin Types ===`,
  `=== Stdlib IFC Labels ===`.

- **PyPI Trusted Publishing (OIDC) for `mvl-lsp` and `pygments-mvl`.** No
  `PYPI_API_TOKEN`, no repository secret. Matches the stance ADR-0039 and
  ADR-0047 already take for `mvl publish --sign`. `mvl-lsp 0.1.4` is the first
  package published this way.

### Fixed

- **IFC label set propagated to every editor artifact.** PR #31 (0.1.2)
  corrected `grammar/grammar.ebnf` and `grammar/keywords.yaml` — dropping the
  closed `security_label` set and the bogus `Public` entry — but touched no
  grammar *implementation*. The wrong label set stayed live downstream for two
  weeks, in five separate hand-maintained copies. Now fixed:
  - `editors/nvim/queries/mvl/highlights.scm` and
    `editors/zed/languages/mvl/highlights.scm` — dropped the
    `declassify_expr` / `sanitize_expr` captures (#894 removed both
    constructs); added a capture for the transition name in `relabel_expr`.
  - `editors/vscode/syntaxes/mvl.tmLanguage.json` — TextMate, so both defects
    were reimplemented as regexes. `security-labels` matched
    `(Public|Tainted|Secret|Clean)`; it now matches the six `stdlib_labels`.
    `special-forms` matched `(sanitize|declassify)`; it now matches
    `relabel <name>`.
  - `editors/zed/extension.toml` — grammar `rev` bumped `dd51a5f` →
    `009a50a`, which is the first `tree-sitter-mvl` `main` commit carrying the
    corrected label set. The previous pin predated the fix.
  - READMEs for nvim, zed, vscode and pygments all documented `Public` and
    `Clean` as real labels and `sanitize`/`declassify` as live special forms.


- **`self` was misclassified in the EBNF's own reserved block.** It appears in
  zero productions and the lexer does not reserve it — `let self: Int = 1;`
  compiles. Moved to `contextual`.
- **`end`, `timeout` and `audit` were in no keyword list at all** despite being
  grammar syntax, so `let end = 5` highlighted `end` as a keyword. `audit` is also
  a stdlib module name (`std/audit.mvl`), recorded nowhere. Found by extracting
  terminals from productions.
- **`len` documented as not a keyword.** It is a quoted terminal in `ref_atom`
  only because the refinement sub-grammar admits no arbitrary calls and must
  enumerate what it allows; in ordinary code it names a compiler-known method.
- **Five phantom words removed from the VS Code TextMate grammar**: `mut`,
  `move`, and the lowercase `public`/`tainted`/`secret` fn-level security prefix
  that `grammar.ebnf:72-73` explicitly denies. None exist in the compiler.

  The grammar-side fix is mvl-lang/tree-sitter-mvl#1 / PR #2, which also found
  that `relabel_expr` was defined but referenced nowhere — so current IFC
  syntax did not parse at all while the two removed constructs did.

  Root cause was #2 — `tools/generators/` was README-only, so `keywords.yaml`
  generated nothing and every downstream artifact was hand-copied. #2 landed in
  this release; see below.

## [0.1.3] — 2026-07-22

### Fixed

- **Pattern grammar drift with compiler parser** — reconciled
  `grammar/grammar.ebnf` with the actual Rust parser:
  - Constructor and struct patterns now accept qualified variant heads
    (`Enum::Variant(...)` / `Enum::Variant { ... }`) via a new
    `ctor_path` production, plus a bare-variant alternative
    (`Enum::Variant` with no payload).  The compiler has always accepted
    these; the EBNF and hand-translated tree-sitter grammar had not.
  - `construct` and `struct_pattern` allow an optional trailing comma
    after the last field (matches the compiler's `if !self.eat(Comma) {
    break }` behaviour).  Introduces `field_init` and `field_pattern`
    productions.

### Removed

- **`tools/tree-sitter/`** — the legacy in-tree copy of the grammar is
  gone.  The canonical grammar lives in its own repo
  ([`mvl-lang/tree-sitter-mvl`](https://github.com/mvl-lang/tree-sitter-mvl))
  because Zed's extension registry needs `grammar.js` at a repo root.
  - `tools/check-versions.py` no longer tracks the removed files.
  - The `publish-tree-sitter.yml` workflow moves to the grammar repo.
  - `tools/generators/README.md`, `grammar/keywords.yaml`,
    `editors/zed/README.md`, and `CLAUDE.md` all now point at the
    external repo.

## [0.1.2] — 2026-07-15

### Fixed

- **`labeled_type` / `security_label` drift** — the EBNF restricted
  labeled types to a closed set of three names (`"Public" | "Tainted" |
  "Secret"`). That was wrong on two counts:
  - `Public` is not a stdlib label and never was — an unlabeled type is
    public by default.
  - The set is not closed — the parser pre-seeds six stdlib labels
    (`Tainted`, `Secret`, `ConfigPath`, `DbUrl`, `ApiEndpoint`,
    `AuditTarget`) and lets user code add more via `label Foo;`.
  The rule is now `labeled_type = IDENT "[" type_expr "]"` with a
  comment explaining the semantic constraint (IDENT must be in the
  declared-label set).
- **`keywords.yaml`** — replaced the misnamed `security_labels:` list
  (which claimed `Public` was a reserved-by-convention label) with a
  correctly-named `stdlib_labels:` list containing the six labels the
  parser actually pre-seeds.

## [0.1.1] — 2026-07-15

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
