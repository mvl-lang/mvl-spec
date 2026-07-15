# mvl-lsp

MVL Language Server, Phase 1 — provides syntax-error diagnostics for `.mvl` files using the [MVL tree-sitter grammar](../tree-sitter/). No MVL compiler binary required.

**Version:** 0.1.0
**Tracks:** mvl-spec ≥ 0.1.0
**Depends on:** [`tree-sitter-mvl`](../tree-sitter/) (Python binding)
**Changelog:** [`CHANGELOG.md`](CHANGELOG.md)

## Install

```bash
pip install mvl-lsp
# Also install the MVL tree-sitter binding (once published to PyPI):
pip install tree-sitter-mvl
```

Until `tree-sitter-mvl` is on PyPI, install from source:

```bash
git clone https://github.com/mvl-lang/mvl-spec
pip install ./mvl-spec/tools/tree-sitter
```

## Run

The server is invoked over stdio per the LSP spec:

```bash
mvl-lsp
```

Editors don't run this by hand — they spawn `mvl-lsp` and speak LSP over its stdio. The editor extensions in [`../../editors/`](../../editors/) do this configuration automatically.

## What Phase 1 covers

- **Syntax errors** — tree-sitter parse failures surface as LSP diagnostics with line/column ranges
- **Nothing else** — no type checking, no effect inference, no IFC label validation, no refinement discharge

## What Phase 2 will cover ([#29](https://github.com/mvl-lang/mvl-spec/issues/29))

- Full 11-requirement diagnostics by shelling out to `mvl check --format=json`
- Type errors, effect violations, IFC label errors, refinement failures, contract violations
- Same LSP surface — the Phase 2 server is a superset, editors configure the same way

Phase 1 is fast (~ms per edit) and requires no compiler. Phase 2 trades speed for completeness.

## Editor integration

Snippets for common editors:

**Neovim** (nvim-lspconfig):
```lua
require('lspconfig').mvl.setup({
    cmd = { 'mvl-lsp' },
    filetypes = { 'mvl' },
    root_dir = require('lspconfig.util').root_pattern('mvl.toml', '.git'),
})
```

**VS Code**: the [`vscode-mvl`](../../editors/vscode/) extension in this repo spawns `mvl-lsp` automatically.

**Zed**: the [`zed-mvl`](../../editors/zed/) extension in this repo configures the LSP.

## Publishing

Per the [versioning policy](../../README.md#versioning-and-publishing) in this repo:

- Tag prefix: `lsp-v*` (e.g., `lsp-v0.1.0`)
- Registry: [PyPI as `mvl-lsp`](https://pypi.org/project/mvl-lsp/) *(when first published)*
- Publish workflow: `.github/workflows/publish-lsp.yml` (to be added)

## Origin

Migrated from `mvl-lang/mvl/tools/lsp_server.py` under [#28](https://github.com/mvl-lang/mvl-spec/issues/28). See the ticket for the rationale (spec-consuming tool with zero compiler coupling belongs alongside tree-sitter, pygments, editor extensions).

## License

Apache-2.0.
