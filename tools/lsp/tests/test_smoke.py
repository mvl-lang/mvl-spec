# SPDX-License-Identifier: Apache-2.0
"""Smoke tests — guard against upstream API breaks and compiler contract drift.

Run with `make test` or `pytest tests/`. Tests that need the `mvl` binary
skip cleanly if it isn't installed.
"""
from __future__ import annotations

import shutil

import pytest


def test_server_module_imports() -> None:
    from mvl_lsp import server
    assert server.SERVER_NAME == "mvl-lsp"


def test_severity_mapping_defaults_to_error() -> None:
    from lsprotocol import types as lsp

    from mvl_lsp.server import _severity_for
    assert _severity_for("E0001") == lsp.DiagnosticSeverity.Error
    assert _severity_for("W0002") == lsp.DiagnosticSeverity.Warning
    assert _severity_for("") == lsp.DiagnosticSeverity.Error


def test_diagnostic_from_json_converts_1_indexed_to_0_indexed() -> None:
    from lsprotocol import types as lsp

    from mvl_lsp.server import _diagnostic_from_json
    d = _diagnostic_from_json(
        {"code": "E0001", "message": "boom", "location": {"line": 3, "column": 5}},
        lsp.DiagnosticSeverity.Error,
    )
    assert d.range.start.line == 2
    assert d.range.start.character == 4
    assert d.code == "E0001"


mvl_required = pytest.mark.skipif(
    shutil.which("mvl") is None,
    reason="mvl binary not on PATH — end-to-end tests need the compiler",
)


@mvl_required
def test_check_wellformed_produces_no_diagnostics(tmp_path) -> None:
    from mvl_lsp.server import _check
    path = tmp_path / "main.mvl"
    path.write_text("fn main() -> Int {\n    42\n}\n")
    assert _check(str(path)) == []


@mvl_required
def test_check_type_mismatch_produces_diagnostic(tmp_path) -> None:
    from mvl_lsp.server import _check
    path = tmp_path / "main.mvl"
    path.write_text('fn main() -> Int {\n    let x: String = "hello";\n    x\n}\n')
    diagnostics = _check(str(path))
    assert len(diagnostics) >= 1
    assert any("type mismatch" in d.message.lower() or "expected" in d.message.lower()
               for d in diagnostics)


@mvl_required
def test_check_resolves_sibling_module_imports(tmp_path) -> None:
    """Regression test: checking the real path (not --stdin) must resolve
    `use` imports against sibling files in the same directory."""
    from mvl_lsp.server import _check
    (tmp_path / "helper.mvl").write_text(
        "pub fn double(x: Int) -> Int {\n    x * 2\n}\n"
    )
    main = tmp_path / "main.mvl"
    main.write_text(
        "use helper.{double}\n\nfn main() -> Int {\n    double(21)\n}\n"
    )
    assert _check(str(main)) == []
