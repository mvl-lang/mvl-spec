# mvl-lsp Changelog

## [Unreleased]

## [0.1.5] — 2026-07-29

### Changed

- Version aligned to mvl-spec `0.1.5`. No functional changes in this component;
  0.1.5 delivers the `pygments-mvl` lexer (#1).

## [0.1.4] — 2026-07-29

### Added

- **First release published to PyPI**: <https://pypi.org/project/mvl-lsp/>.
  Install with `pip install mvl-lsp`.
- Published via PyPI Trusted Publishing (OIDC) — no API token or repository
  secret is involved. See `.github/workflows/publish-lsp.yml`.

### Changed

- Version aligned to mvl-spec `0.1.4`. Diagnostics pick up the tree-sitter-mvl
  grammar carrying the corrected IFC label set and the wired `ghost let` rule.

## [0.1.3] — 2026-07-22

Version aligned to mvl-spec `0.1.3`.  No functional LSP changes;
diagnostics will pick up the tree-sitter-mvl `0.1.3` grammar
transitively when the server is reinstalled.

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
