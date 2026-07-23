use zed_extension_api::{self as zed, Command, LanguageServerId, Result, Worktree};

const MVL_LSP_PATH: &str =
    "/Users/iheitlager/wc/mvl-lang/mvl-spec/tools/lsp/.venv/bin/mvl-lsp";
// Zed (a GUI app) doesn't reliably inherit the shell PATH, so point the LSP
// at the mvl compiler explicitly rather than relying on PATH lookup.
const MVL_BIN_PATH: &str = "/Users/iheitlager/.local/bin/mvl";

struct MvlExtension;

impl zed::Extension for MvlExtension {
    fn new() -> Self {
        MvlExtension
    }

    fn language_server_command(
        &mut self,
        _language_server_id: &LanguageServerId,
        _worktree: &Worktree,
    ) -> Result<Command> {
        Ok(Command {
            command: MVL_LSP_PATH.to_string(),
            args: vec![],
            env: vec![("MVL_BIN".to_string(), MVL_BIN_PATH.to_string())],
        })
    }
}

zed::register_extension!(MvlExtension);
