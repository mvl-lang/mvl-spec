#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Schuberg Philis
"""
MVL Language Server — full 11-requirement diagnostics via the mvl compiler.

The server shells out to `mvl check --stdin --format=json` on every
buffer event and maps the compiler's JSON output to LSP Diagnostics.
Surfaces type, effect, IFC, refinement, contract, termination, and
ownership errors — everything the compiler catches.

Install:
    pip install mvl-lsp

Run (stdio, for editors):
    mvl-lsp

Requires the `mvl` binary on PATH (or MVL_BIN pointing at it). Set
MVL_BIN to a specific build when iterating on the compiler alongside
the LSP.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from urllib.parse import unquote

from lsprotocol import types as lsp
from pygls.lsp.server import LanguageServer

SERVER_NAME = "mvl-lsp"
SERVER_VERSION = "0.2.0"

MVL_TIMEOUT_SECONDS = 10


def _find_mvl_binary() -> str | None:
    """Locate the mvl compiler. MVL_BIN wins over PATH."""
    explicit = os.environ.get("MVL_BIN")
    if explicit:
        return explicit if os.path.isfile(explicit) and os.access(explicit, os.X_OK) else None
    return shutil.which("mvl")


_MVL_BIN = _find_mvl_binary()

if _MVL_BIN is None:
    print(
        "[mvl-lsp] WARNING: `mvl` binary not found — no diagnostics will be reported.\n"
        "  Install mvl (see https://github.com/mvl-lang/mvl) or set MVL_BIN=/path/to/mvl.",
        file=sys.stderr,
    )


def _severity_for(code: str) -> lsp.DiagnosticSeverity:
    """Map compiler error codes to LSP severities. Warnings use `W`-prefixed codes."""
    return (
        lsp.DiagnosticSeverity.Warning
        if code.startswith("W")
        else lsp.DiagnosticSeverity.Error
    )


def _diagnostic_from_json(entry: dict, severity: lsp.DiagnosticSeverity) -> lsp.Diagnostic:
    """Convert one entry from `mvl check --format=json` into an LSP Diagnostic.

    The compiler reports 1-indexed line/column; LSP expects 0-indexed. The
    compiler doesn't emit an end range, so highlight a single character starting
    at the reported position.
    """
    loc = entry.get("location", {})
    line = max(0, loc.get("line", 1) - 1)
    col = max(0, loc.get("column", 1) - 1)
    return lsp.Diagnostic(
        range=lsp.Range(
            start=lsp.Position(line=line, character=col),
            end=lsp.Position(line=line, character=col + 1),
        ),
        message=entry.get("message", ""),
        severity=severity,
        source=SERVER_NAME,
        code=entry.get("code", ""),
    )


def _check(source: str) -> list[lsp.Diagnostic]:
    """Run the compiler over `source` (via stdin) and return LSP diagnostics."""
    if _MVL_BIN is None:
        return []
    env = {**os.environ, "MVL_NO_REEXEC": "1"}
    try:
        result = subprocess.run(
            [_MVL_BIN, "check", "--stdin", "--format=json"],
            input=source,
            capture_output=True,
            text=True,
            env=env,
            timeout=MVL_TIMEOUT_SECONDS,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"[mvl-lsp] mvl check failed: {e}", file=sys.stderr)
        return []

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        # Non-JSON on stdout means the compiler emitted a parse-level error
        # before format=json engaged. Surface it as a single generic diagnostic.
        message = (result.stdout + result.stderr).strip() or "mvl check produced no output"
        return [lsp.Diagnostic(
            range=lsp.Range(start=lsp.Position(line=0, character=0),
                            end=lsp.Position(line=0, character=1)),
            message=message.splitlines()[0][:200],
            severity=lsp.DiagnosticSeverity.Error,
            source=SERVER_NAME,
            code="EPARSE",
        )]

    diagnostics: list[lsp.Diagnostic] = []
    for e in payload.get("errors", []):
        diagnostics.append(_diagnostic_from_json(e, _severity_for(e.get("code", ""))))
    for w in payload.get("warnings", []):
        diagnostics.append(_diagnostic_from_json(w, lsp.DiagnosticSeverity.Warning))
    return diagnostics


server = LanguageServer(SERVER_NAME, SERVER_VERSION)


def _uri_to_path(uri: str) -> str:
    return unquote(uri[7:]) if uri.startswith("file://") else uri


def _publish(ls: LanguageServer, uri: str, diagnostics: list[lsp.Diagnostic]) -> None:
    ls.publish_diagnostics(uri, diagnostics)


@server.feature(lsp.TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: LanguageServer, params: lsp.DidOpenTextDocumentParams) -> None:
    doc = params.text_document
    _publish(ls, doc.uri, _check(doc.text))


@server.feature(lsp.TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: LanguageServer, params: lsp.DidChangeTextDocumentParams) -> None:
    if not params.content_changes:
        return
    last = params.content_changes[-1]
    text = last.text if hasattr(last, "text") else ""
    if text:
        _publish(ls, params.text_document.uri, _check(text))


@server.feature(lsp.TEXT_DOCUMENT_DID_SAVE)
def did_save(ls: LanguageServer, params: lsp.DidSaveTextDocumentParams) -> None:
    path = _uri_to_path(params.text_document.uri)
    try:
        with open(path, encoding="utf-8") as f:
            source = f.read()
    except OSError:
        return
    _publish(ls, params.text_document.uri, _check(source))


@server.feature(lsp.TEXT_DOCUMENT_DID_CLOSE)
def did_close(ls: LanguageServer, params: lsp.DidCloseTextDocumentParams) -> None:
    _publish(ls, params.text_document.uri, [])


def main() -> None:
    """Console-script entry point (see pyproject.toml `[project.scripts]`).

    Runs the LSP server over stdio. Editors spawn this process and speak
    LSP over its stdin/stdout per the protocol.
    """
    print(f"Starting {SERVER_NAME} v{SERVER_VERSION}", file=sys.stderr)
    print(
        f"mvl binary: {_MVL_BIN or 'NOT FOUND — no diagnostics will be reported'}",
        file=sys.stderr,
    )
    server.start_io()


if __name__ == "__main__":
    main()
