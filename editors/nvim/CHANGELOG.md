# nvim-mvl Changelog

## [Unreleased]

## [0.1.0] — 2026-07-13

Initial release. Migrated from `mvl-lang/mvl/etc/nvim-mvl/`.

### Added

- Filetype detection for `.mvl` files (`plugin/mvl.lua`)
- Filetype settings (`after/ftplugin/mvl.lua`) — commentstring, indent width, fold method
- Optional LSP client integration (`lua/mvl/lsp.lua`) — attaches to the mvl-lsp server when installed
- Health check (`lua/mvl/health.lua`)
- Tree-sitter query files (`queries/mvl/`) for highlights, indents, folds

### Compatibility

Tracks **mvl-spec >= 0.1.0, < 0.5.0**.
Depends on **tree-sitter-mvl >= 0.1.0** and **nvim-treesitter**.
Requires **Neovim >= 0.9**.

### Installation

Neovim has no standard registry — install by git URL:

```lua
-- lazy.nvim
{ "mvl-lang/mvl-spec", branch = "main", config = function()
  vim.opt.rtp:prepend(vim.fn.stdpath("data") .. "/lazy/mvl-spec/editors/nvim")
end }
```

---

[Unreleased]: https://github.com/mvl-lang/mvl-spec/compare/nvim-v0.1.0...HEAD
[0.1.0]: https://github.com/mvl-lang/mvl-spec/releases/tag/nvim-v0.1.0
