# tree-sitter-mvl Changelog

## [Unreleased]

## [0.1.0] — 2026-07-13

Initial release. Migrated from `mvl-lang/mvl/etc/tree-sitter-mvl/`.

### Added

- Full `grammar.js` derived from `grammar/grammar.ebnf`
- Highlight queries (`queries/highlights.scm`) covering keywords, totality modifiers, security modifiers, capability annotations, security labels, built-in generics, effects, and special forms
- Fold queries (`queries/folds.scm`)
- Test corpus (`test/corpus/`)
- Published under package name `tree-sitter-mvl` (npm)

### Compatibility

Tracks **mvl-spec >= 0.1.0, < 0.5.0**.

---

[Unreleased]: https://github.com/mvl-lang/mvl-spec/compare/tree-sitter-v0.1.0...HEAD
[0.1.0]: https://github.com/mvl-lang/mvl-spec/releases/tag/tree-sitter-v0.1.0
