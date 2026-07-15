# mvl-lsp Changelog

## [Unreleased]

## [0.1.0] — 2026-07-15

Initial release. Migrated from `mvl-lang/mvl/tools/lsp_server.py`
under [mvl-lang/mvl-spec#28](https://github.com/mvl-lang/mvl-spec/issues/28).

### Added

- Python package `mvl_lsp` with `mvl-lsp` console entry point
- Phase 1 LSP: syntax-error diagnostics via the MVL tree-sitter grammar
- `pyproject.toml` publishing under name `mvl-lsp` on PyPI
- Depends on `pygls`, `tree-sitter`, and (once published) `tree-sitter-mvl`

### Changed

- Docstring updated to reflect the new home (paths are relative to
  `mvl-spec/tools/lsp/` rather than mentioning the mvl-spec URL — the
  package IS in mvl-spec now)
- Invocation changed from `python tools/lsp_server.py` to
  `mvl-lsp` (via the console entry point)

### Compatibility

Tracks **mvl-spec >= 0.1.0**.
Requires **Python >= 3.10**.
Depends on `tree-sitter-mvl` (packaged from `../tree-sitter/`).

---

[Unreleased]: https://github.com/mvl-lang/mvl-spec/compare/lsp-v0.1.0...HEAD
[0.1.0]: https://github.com/mvl-lang/mvl-spec/releases/tag/lsp-v0.1.0
