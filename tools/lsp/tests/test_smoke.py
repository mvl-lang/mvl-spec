# SPDX-License-Identifier: Apache-2.0
"""Import smoke tests — guard against upstream API breaks.

Both bugs #35 (pygls 2.x moved `LanguageServer`) and the tree-sitter
binding install path were silent regressions that only surfaced when
someone actually ran `mvl-lsp`. These tests catch the same class
of failure at CI time.
"""
from __future__ import annotations


def test_server_module_imports() -> None:
    from mvl_lsp import server
    assert server.SERVER_NAME == "mvl-lsp"


def test_tree_sitter_parser_loads() -> None:
    from mvl_lsp.server import _PARSER
    assert _PARSER is not None, "tree-sitter-mvl not installed correctly"


def test_check_wellformed_produces_no_diagnostics() -> None:
    from mvl_lsp.server import _check
    assert _check("fn main() -> Int { 42 }") == []


def test_check_malformed_produces_diagnostic() -> None:
    from mvl_lsp.server import _check
    diagnostics = _check("fn main( -> Int { 42 }")
    assert len(diagnostics) >= 1
