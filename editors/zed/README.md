# zed-mvl

Zed extension for [MVL (Maximum Verifiable Language)](../../README.md).

Provides syntax highlighting, bracket matching, and smart indentation via
Zed's native tree-sitter integration.

**Version:** 0.1.0
**Tracks:** mvl-spec ≥ 0.1.0, < 0.5.0
**Depends on:** tree-sitter-mvl ≥ 0.1.0
**Changelog:** [`CHANGELOG.md`](CHANGELOG.md)

---

## Installation

### Option A — Install as a dev extension (recommended today)

Zed can load an extension directly from a local directory. This is the fastest path while the extension is not yet on the Zed registry.

1. **Clone the spec repo** (if you haven't already):

   ```bash
   git clone https://github.com/mvl-lang/mvl-spec.git ~/wc/mvl-spec
   ```

2. **Open Zed**, then open the command palette:
   - macOS: `Cmd+Shift+P`
   - Linux: `Ctrl+Shift+P`

3. Run: **`zed: install dev extension`**

4. Navigate to and select the folder:
   ```
   ~/wc/mvl-spec/editors/zed/
   ```

5. Zed installs the extension immediately. Open any `.mvl` file to verify highlighting works.

The extension is now active and will remain active across Zed restarts. To uninstall, run **`zed: extensions`** and remove `mvl` from the list.

### Option B — Install from the Zed Extension Registry

> **Not yet available.** Publishing to the [Zed Extensions](https://github.com/zed-industries/extensions) registry requires the tree-sitter grammar to be available at the root of a dedicated public repo. Until we split `tools/tree-sitter/` out of `mvl-spec` (or Zed adds subpath support), only the dev install (Option A) works.

Once available, install via:

1. `Cmd+Shift+P` → **`zed: extensions`**
2. Search for **MVL**
3. Click **Install**

Track the split in [mvl-spec#7](https://github.com/mvl-lang/mvl-spec/issues) *(to be filed if you want the registry install)*.

---

## Verifying it works

Create a file `hello.mvl` and paste:

```rust
total fn double(x: Int where self > 0) -> Int where self > 0 {
    x * 2
}

pub fn main() -> Unit ! Console {
    let result: Int = double(21);
    println(result.to_string())
}
```

Save. You should see:

- **Keywords** (`total`, `fn`, `pub`, `let`, `where`) coloured as keywords
- **Types** (`Int`, `Unit`) coloured as types
- **Effects** (`! Console`) coloured distinctly from regular identifiers
- **Refinements** (`where self > 0`) highlighted
- **Strings** and **numbers** coloured

If none of that happens, the extension is not loading — see Troubleshooting below.

---

## Features

- **Syntax highlighting** — keywords, types, security labels (`Public` / `Tainted` / `Secret`), capabilities (`iso` / `val` / `ref` / `tag`), totality modifiers (`total` / `partial`), effects (`! Console`, `! DB`), special forms (`sanitize`, `declassify`), refinements, operators
- **Bracket matching** — `{}`, `()`, `[]`, strings, char literals
- **Smart indentation** — increases after `{`, decreases before `}`
- **Filetype detection** — `.mvl` files automatically use MVL mode

---

## Troubleshooting

**"Zed says the extension installed but nothing is highlighted."**

Zed fetches and compiles the tree-sitter grammar the first time you open an MVL file. This can take 10–30 seconds. Check the status bar at the bottom for a progress indicator, or the Zed log (`zed: open log`).

**"Grammar failed to compile."**

The `extension.toml` points to a specific commit in `mvl-lang/mvl-spec` for the grammar source. If Zed cannot fetch that commit (network issue, or repo permissions), the extension will install but highlighting won't work.

Workaround: pull the latest `main` of `mvl-spec` and update the `commit` field in `extension.toml` to the current HEAD, then reinstall the dev extension.

**"`zed: install dev extension` doesn't appear in the command palette."**

You need Zed with extension support (any recent release should have it). Update Zed if you're on an older version.

---

## File structure

```
editors/zed/
├── extension.toml              # extension manifest + grammar Git ref
├── CHANGELOG.md
├── README.md                    # this file
└── languages/
    └── mvl/
        ├── config.toml         # file patterns, comments, bracket pairs
        ├── highlights.scm      # tree-sitter highlight queries
        └── indents.scm         # smart indentation queries
```

---

## Grammar sourcing

Zed fetches and compiles the tree-sitter grammar from a Git repository. The grammar source currently lives at `tools/tree-sitter/` in this same repo (`mvl-spec`). `extension.toml` pins a specific commit; bump the pin when the grammar advances.

For the Zed Extension Registry, `grammar.js` must be at the root of a dedicated repo — we'll split `tools/tree-sitter/` out when we're ready to publish there.

---

## Related

- [tools/tree-sitter/](../../tools/tree-sitter/) — the grammar source this extension consumes
- [editors/nvim/](../nvim/) — Neovim plugin (same tree-sitter grammar, different editor)
- [editors/vscode/](../vscode/) — VS Code extension (uses a TextMate grammar, not tree-sitter)
