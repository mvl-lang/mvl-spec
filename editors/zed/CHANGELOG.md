# zed-mvl Changelog

## [Unreleased]

## [0.1.3] — 2026-07-22

### Fixed

- Grammar `rev` pin bumped to pick up the tree-sitter-mvl `0.1.3`
  parser (qualified constructor patterns, method-call precedence,
  optional trailing commas).

### Changed

- Documentation now points at
  [`mvl-lang/tree-sitter-mvl`](https://github.com/mvl-lang/tree-sitter-mvl)
  as the single home of the grammar; the legacy
  `mvl-spec/tools/tree-sitter/` copy has been deleted.

## [0.1.0] — 2026-07-13

Initial release under the mvl-spec repo. Migrated from `mvl-lang/mvl/etc/zed-mvl/` (was `0.0.1` there).

### Changed

- Version bumped from `0.0.1` → `0.1.0` to align with the ecosystem's pre-1.0 versioning baseline

### Added

- Zed extension manifest (`extension.toml`)
- Language config (`languages/mvl/config.toml`) — brackets, indents, filetype detection
- Tree-sitter highlight and indent queries (imported from `tools/tree-sitter/`)

### Compatibility

Tracks **mvl-spec >= 0.1.0, < 0.5.0**.
Depends on **tree-sitter-mvl >= 0.1.0**.
Requires **Zed** with tree-sitter extension support.

---

[Unreleased]: https://github.com/mvl-lang/mvl-spec/compare/zed-v0.1.0...HEAD
[0.1.0]: https://github.com/mvl-lang/mvl-spec/releases/tag/zed-v0.1.0
