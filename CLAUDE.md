# mvl-spec — Instructions for LLM-assisted development

This file gives Claude and other coding assistants the context needed to
work in this repository without repeating mistakes we've already made.

## Repository layout

```
mvl-spec/
├── VERSION                         source of truth for the SPEC version
├── grammar/                        canonical EBNF grammar (grammar.ebnf)
├── semantics/                      inference rules, refinement calculus
├── editors/
│   ├── zed/                        Zed extension (schema_version 1)
│   ├── vscode/                     VS Code extension
│   └── nvim/                       Neovim plugin (thin ftdetect + ftplugin)
├── tools/
│   ├── check-versions.py           version alignment checker (see below)
│   ├── lsp/                        pygls-based Language Server
│   ├── tree-sitter/                LEGACY partial copy of the grammar,
│   │                               to be removed (see mvl-spec#34) — the
│   │                               canonical grammar lives in the sibling
│   │                               repo `mvl-lang/tree-sitter-mvl`
│   ├── generators/                 spec → code generators
│   └── pygments/                   Pygments lexer
└── .openspec/                      spec proposals and ADRs
```

## Related external repositories

- **`mvl-lang/tree-sitter-mvl`** — the canonical tree-sitter grammar,
  split out because Zed's extension resolver requires `grammar.js` at
  a repo root. When working on the grammar, `queries/*.scm`, corpus
  tests, or bindings, edit that repo (or its checkout). Do NOT edit
  the copy under `tools/tree-sitter/` — it's slated for removal.

  When Zed's extension pins a grammar revision, it goes in
  `editors/zed/extension.toml` as a **full 40-char SHA**. Short SHAs
  cause `zed: install dev extension` to hang silently at "checking out
  parser". See commit that added this note for the debugging story.

- **`mvl-lang/mvl`** — the compiler (Rust). This repo's spec drives
  compiler acceptance tests; compiler bugs are filed against `mvl`, not
  here.

## Versioning discipline

The spec's `VERSION` file is the coordination point. Artifacts each
carry their own version, but **at release checkpoints they are aligned
to the spec version**. Between releases they may drift as feature work
advances independently (e.g. the LSP was legitimately at `0.2.0`
during compiler-backed diagnostics work); the drift is reconciled
before the next release. This was formalised 2026-07-22 after we
caught a 4-way version drift.

To check drift or align versions, run:

```bash
python3 tools/check-versions.py                    # report drift
python3 tools/check-versions.py --fix              # align local files to VERSION
python3 tools/check-versions.py --target 0.1.3     # override target
python3 tools/check-versions.py --tree-sitter-dir /path/to/tree-sitter-mvl
python3 tools/check-versions.py --skip-tree-sitter # skip external checks
```

The script auto-locates `tree-sitter-mvl` in this order:
1. `--tree-sitter-dir` flag
2. `$MVL_TREE_SITTER_DIR` environment variable
3. `../tree-sitter-mvl/` (sibling of this repo)
4. Read-only fetch from `https://raw.githubusercontent.com/mvl-lang/tree-sitter-mvl/main/`

Remote-mode `--fix` cannot write; clone locally to align the grammar
repo. The check runs stdlib-only Python 3.11+ — no venv needed.

**Files the script tracks per artifact:**

| Artifact | Files |
|---|---|
| mvl-spec | `VERSION` |
| Zed extension | `editors/zed/extension.toml`, `editors/zed/CHANGELOG.md` |
| VS Code extension | `editors/vscode/package.json`, `editors/vscode/CHANGELOG.md` |
| Neovim plugin | `editors/nvim/VERSION`, `editors/nvim/CHANGELOG.md` |
| LSP | `tools/lsp/VERSION`, `tools/lsp/pyproject.toml`, `tools/lsp/CHANGELOG.md` |
| tree-sitter-mvl | `package.json`, `tree-sitter.json`, `Cargo.toml`, `pyproject.toml`, `CHANGELOG.md` |

CHANGELOG files are checked read-only: the top `## [X.Y.Z]` header
must be either the target version or `## [Unreleased]`. Release notes
are human-authored — `--fix` does not touch them.

## Editor-extension work

- The editor extensions are NOT split into separate repos. Trigger to
  split would be (a) a marketplace forcing per-repo publishing, (b) an
  extension growing past ~500 LOC of extension-specific logic, or
  (c) an outside maintainer wanting independent commit rights.
- **Zed** uses `editors/zed/languages/mvl/highlights.scm` and
  `indents.scm`. These are Zed-specific copies — the canonical query
  files live in `mvl-lang/tree-sitter-mvl/queries/`. When the grammar
  gains or loses node types, both copies must be updated.
- Query files reference the parser's actual named nodes. Before
  adding a `(node_type)` capture, verify it exists in
  `tree-sitter-mvl/src/node-types.json`. Bogus node types cause Zed's
  query loader to reject the file entirely — no partial highlighting.

## Common pitfalls we've hit

- **Zed extension install hangs silently** → check that
  `[grammars.mvl] rev` is a full 40-char SHA, not a short hash.
- **"Query error at N:M. Invalid node type X"** in Zed logs →
  the .scm file references a grammar node that doesn't exist.
  Regenerate the reference from `src/node-types.json`, don't guess.
- **Version drift between artifacts** → run
  `python3 tools/check-versions.py` before committing a release.
- **`tools/tree-sitter/` edits** → don't. That directory is a legacy
  partial copy. Edit `mvl-lang/tree-sitter-mvl` (external repo)
  instead.

## LLM etiquette in this repo

- The MVL taxonomy has FOUR Pony reference capabilities: `iso`, `val`,
  `ref`, `tag`. Not three. Rust-style `mut`/`&`/`&mut`/lifetimes do
  NOT exist in MVL — do not put them in highlight files or docs.
- The verifier's obligation-solver layer stack is L1 (trivial), L2
  (intervals), L3 (path enumeration), L4 (Cooper QE for Presburger),
  L5 (Z3 SMT), plus a runtime obligation fallback. Do not conflate
  Layer 5 with "SMT" as if it were the whole story.
- Commit messages: `feat(scope): ...`, `fix(scope): ...`, etc.
  Sign co-author lines with the actual model name.
- Do NOT create markdown documentation files unless explicitly asked
  (rule inherited from `~/.claude/CLAUDE.md`).
