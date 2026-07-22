# vscode-mvl Changelog

## [Unreleased]

## [0.1.3] — 2026-07-22

Version aligned to mvl-spec `0.1.3`.  No functional changes to the
TextMate grammar (VS Code does not consume the tree-sitter grammar
that changed in this release).

## [0.1.0] — 2026-07-13

Initial release. Migrated from `mvl-lang/mvl/etc/vscode-mvl/`.

### Added

- TextMate grammar (`syntaxes/mvl.tmLanguage.json`) for syntax highlighting
- Language configuration (`language-configuration.json`) for bracket matching, comment toggling, folding markers
- Extension entry point (`extension.js`) with filetype registration
- Marketplace publish target under name `mvl` (publisher TBD)

### Compatibility

Tracks **mvl-spec >= 0.1.0, < 0.5.0**.
Requires **VS Code >= 1.75.0**.

---

[Unreleased]: https://github.com/mvl-lang/mvl-spec/compare/vscode-v0.1.0...HEAD
[0.1.0]: https://github.com/mvl-lang/mvl-spec/releases/tag/vscode-v0.1.0
