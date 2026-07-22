# mvl-lsp

MVL Language Server — full compiler-backed diagnostics for `.mvl` files. Shells out to `mvl check --stdin --format=json` and maps the result to LSP diagnostics.

**Version:** 0.2.0
**Tracks:** mvl-spec ≥ 0.1.0
**Depends on:** the `mvl` compiler binary on PATH (or `MVL_BIN`)
**Changelog:** [`CHANGELOG.md`](CHANGELOG.md)

## Install

```bash
pip install git+https://github.com/mvl-lang/mvl-spec#subdirectory=tools/lsp
```

For local development:

```bash
git clone https://github.com/mvl-lang/mvl-spec
uv pip install -e ./mvl-spec/tools/lsp
```

You also need the `mvl` compiler installed. Either put it on `PATH` (default) or point `MVL_BIN` at a specific build (useful when iterating on the compiler alongside the LSP):

```bash
export MVL_BIN=/path/to/mvl-lang/mvl/target/debug/mvl
```

## Run

The server is invoked over stdio per the LSP spec:

```bash
mvl-lsp
```

Editors don't run this by hand — they spawn `mvl-lsp` and speak LSP over its stdio. The editor extensions in [`../../editors/`](../../editors/) do this configuration automatically. For local dev see [`Makefile`](Makefile): `make run` sends an initialize handshake and prints the response.

## What it covers

Everything `mvl check` catches: syntax errors, type mismatches, effect violations, IFC label errors, refinement failures, contract violations, termination checks, ownership errors — the compiler's full 11-requirement diagnostic surface, no gaps between LSP and CLI.

Each LSP diagnostic carries the compiler's error code (`E0001`, etc.) and points at the exact line/column the compiler reported.

## Behavior

- **On open / change / save:** run `mvl check --stdin --format=json` with the current buffer.
- **On close:** clear diagnostics for that URI.
- **Timeout:** each check is capped at 10s (files that exceed it are probably not `.mvl` you want the LSP interpreting).
- **Env passed to child:** inherits the parent's env with `MVL_NO_REEXEC=1` added, so the LSP always runs the binary it was pointed at rather than being redirected by `requires-mvl`.

## Editor integration

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

**opencode**: add to `~/.config/opencode/opencode.jsonc`:
```json
{
  "lsp": {
    "mvl": {
      "command": ["/absolute/path/to/mvl-lsp"],
      "extensions": [".mvl"]
    }
  }
}
```

## Origin

Migrated from `mvl-lang/mvl/tools/lsp_server.py` under [#28](https://github.com/mvl-lang/mvl-spec/issues/28). Original design was a two-phase rollout (tree-sitter parse errors first, compiler-backed diagnostics later — [#29](https://github.com/mvl-lang/mvl-spec/issues/29)); since `mvl check --stdin --format=json` already exists, the phase-1 tree-sitter path was skipped and the server ships with full compiler-backed diagnostics from the start.

## License

Apache-2.0.
