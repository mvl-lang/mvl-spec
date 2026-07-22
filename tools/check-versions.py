#!/usr/bin/env python3
"""
check-versions.py — validate MVL artifact versions against mvl-spec/VERSION.

Reads mvl-spec/VERSION as the source of truth by default. Compares every
tracked version-carrying file in this repo and, when reachable, in the
external tree-sitter-mvl grammar repo.

Usage:
    python3 tools/check-versions.py                    # check drift, exit 1 on mismatch
    python3 tools/check-versions.py --fix              # align local files to VERSION
    python3 tools/check-versions.py --target 0.1.3     # override target version
    python3 tools/check-versions.py --tree-sitter-dir PATH
                                                       # explicit grammar repo path
    python3 tools/check-versions.py --skip-tree-sitter # skip external repo entirely

Tree-sitter-mvl resolution order:
    1. --tree-sitter-dir CLI flag
    2. $MVL_TREE_SITTER_DIR
    3. ../tree-sitter-mvl (sibling of mvl-spec)
    4. https://raw.githubusercontent.com/mvl-lang/tree-sitter-mvl/main/
       (read-only; --fix cannot touch remote)

CHANGELOG entries are checked read-only: the top `## [X.Y.Z]` header must
be either the target version or `## [Unreleased]`. --fix does not touch
CHANGELOGs — release notes are human-authored.

Exit codes:
    0  everything aligned
    1  drift found (check mode) OR fix incomplete (fix mode)
    2  invocation / IO error
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tomllib
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REMOTE_BASE = "https://raw.githubusercontent.com/mvl-lang/tree-sitter-mvl/main/"


@dataclass
class VersionSite:
    """A single place a version string lives."""
    path: str          # display path, relative to whichever repo
    kind: str          # "plain" | "toml-package" | "toml-extension" | "json" | "tree-sitter-json" | "changelog"
    location: str      # "local" (mvl-spec) | "grammar-local" | "grammar-remote"
    reader: object     # callable(text) -> str | None (returns current version)
    writer: object     # callable(text, new) -> str (returns new file text), or None if read-only


def read_plain(text: str) -> str | None:
    return text.strip() or None


def write_plain(text: str, new: str) -> str:
    return new + ("\n" if text.endswith("\n") else "")


def read_toml_version(text: str, table: str = "package") -> str | None:
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError:
        return None
    # top-level [package] version for Cargo.toml / pyproject.toml PEP 621 [project]
    # For extension.toml, version is at the top level
    if "version" in data and isinstance(data["version"], str):
        return data["version"]
    for tbl in ("package", "project"):
        if tbl in data and isinstance(data[tbl], dict) and "version" in data[tbl]:
            return data[tbl]["version"]
    return None


VERSION_LINE_RE = re.compile(r'^(\s*version\s*=\s*)"[^"]*"', re.MULTILINE)


def write_toml_version(text: str, new: str) -> str:
    # Replace only the first `version = "..."` line — preserves comments and formatting.
    return VERSION_LINE_RE.sub(rf'\g<1>"{new}"', text, count=1)


def read_json_version(text: str) -> str | None:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    if isinstance(data, dict) and isinstance(data.get("version"), str):
        return data["version"]
    return None


JSON_VERSION_RE = re.compile(r'("version"\s*:\s*)"[^"]*"')


def write_json_version(text: str, new: str) -> str:
    return JSON_VERSION_RE.sub(rf'\g<1>"{new}"', text, count=1)


def read_tree_sitter_json_version(text: str) -> str | None:
    # tree-sitter.json puts version at metadata.version
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    md = data.get("metadata") if isinstance(data, dict) else None
    if isinstance(md, dict) and isinstance(md.get("version"), str):
        return md["version"]
    # Fallback: top-level version
    if isinstance(data, dict) and isinstance(data.get("version"), str):
        return data["version"]
    return None


TS_JSON_METADATA_VERSION_RE = re.compile(
    r'("metadata"\s*:\s*\{[^}]*?"version"\s*:\s*)"[^"]*"',
    re.DOTALL,
)


def write_tree_sitter_json_version(text: str, new: str) -> str:
    def repl(m):
        return m.group(1) + f'"{new}"'
    result, n = TS_JSON_METADATA_VERSION_RE.subn(repl, text, count=1)
    if n == 0:
        # fall back to top-level version
        return write_json_version(text, new)
    return result


CHANGELOG_TOP_VERSION_RE = re.compile(
    r'^##\s*\[(?P<v>[^\]]+)\]', re.MULTILINE
)


def read_changelog_top(text: str) -> str | None:
    m = CHANGELOG_TOP_VERSION_RE.search(text)
    return m.group("v") if m else None


# ----- File site definitions -----

LOCAL_SITES: list[VersionSite] = [
    VersionSite("VERSION", "plain", "local", read_plain, write_plain),
    # Editor: Zed
    VersionSite("editors/zed/extension.toml", "toml-extension", "local",
                lambda t: read_toml_version(t), write_toml_version),
    VersionSite("editors/zed/CHANGELOG.md", "changelog", "local",
                read_changelog_top, None),
    # Editor: VS Code
    VersionSite("editors/vscode/package.json", "json", "local",
                read_json_version, write_json_version),
    VersionSite("editors/vscode/CHANGELOG.md", "changelog", "local",
                read_changelog_top, None),
    # Editor: Neovim
    VersionSite("editors/nvim/VERSION", "plain", "local", read_plain, write_plain),
    VersionSite("editors/nvim/CHANGELOG.md", "changelog", "local",
                read_changelog_top, None),
    # Tools: LSP
    VersionSite("tools/lsp/VERSION", "plain", "local", read_plain, write_plain),
    VersionSite("tools/lsp/pyproject.toml", "toml-package", "local",
                read_toml_version, write_toml_version),
    VersionSite("tools/lsp/CHANGELOG.md", "changelog", "local",
                read_changelog_top, None),
]

# Tree-sitter-mvl external repo — canonical home of the grammar
GRAMMAR_SITE_SPECS = [
    ("package.json", "json", read_json_version, write_json_version),
    ("tree-sitter.json", "tree-sitter-json", read_tree_sitter_json_version, write_tree_sitter_json_version),
    ("Cargo.toml", "toml-package", read_toml_version, write_toml_version),
    ("pyproject.toml", "toml-package", read_toml_version, write_toml_version),
    ("CHANGELOG.md", "changelog", read_changelog_top, None),
]


# ----- I/O helpers -----

def fetch_local(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except OSError as e:
        print(f"error reading {path}: {e}", file=sys.stderr)
        return None


def fetch_remote(url: str) -> str | None:
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return resp.read().decode("utf-8")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
        print(f"remote fetch failed for {url}: {e}", file=sys.stderr)
        return None


def resolve_grammar_source(cli_dir: str | None, skip: bool) -> tuple[str, Path | None]:
    """
    Returns (mode, path):
      mode = "local" | "remote" | "skip"
      path = Path when local, None when remote or skip
    """
    if skip:
        return ("skip", None)
    if cli_dir:
        p = Path(cli_dir).expanduser().resolve()
        if not (p / "package.json").exists():
            print(f"--tree-sitter-dir '{p}' does not look like a tree-sitter-mvl checkout (missing package.json)",
                  file=sys.stderr)
            sys.exit(2)
        return ("local", p)
    env_dir = os.environ.get("MVL_TREE_SITTER_DIR")
    if env_dir:
        p = Path(env_dir).expanduser().resolve()
        if (p / "package.json").exists():
            return ("local", p)
        print(f"$MVL_TREE_SITTER_DIR='{env_dir}' does not exist or is not a checkout — falling back",
              file=sys.stderr)
    sibling = (REPO_ROOT.parent / "tree-sitter-mvl").resolve()
    if (sibling / "package.json").exists():
        return ("local", sibling)
    # remote fallback
    return ("remote", None)


# ----- Result table -----

@dataclass
class Result:
    site: VersionSite
    current: str | None      # None if file missing
    expected: str
    ok: bool
    changed: bool = False    # true if --fix edited this file


def evaluate_local(site: VersionSite, target: str) -> Result:
    path = REPO_ROOT / site.path
    text = fetch_local(path)
    if text is None:
        return Result(site, None, target, False)
    current = site.reader(text)
    if site.kind == "changelog":
        ok = current in (target, "Unreleased")
    else:
        ok = current == target
    return Result(site, current, target, ok)


def evaluate_grammar(mode: str, path: Path | None, target: str) -> list[Result]:
    """Build sites on the fly for the grammar repo."""
    results = []
    for filename, kind, reader, writer in GRAMMAR_SITE_SPECS:
        loc = "grammar-local" if mode == "local" else "grammar-remote"
        w = writer if mode == "local" else None
        display = f"[tree-sitter-mvl] {filename}"
        site = VersionSite(display, kind, loc, reader, w)
        if mode == "local":
            text = fetch_local(path / filename)
        else:
            text = fetch_remote(REMOTE_BASE + filename)
        if text is None:
            results.append(Result(site, None, target, False))
            continue
        current = reader(text)
        if kind == "changelog":
            ok = current in (target, "Unreleased")
        else:
            ok = current == target
        r = Result(site, current, target, ok)
        results.append(r)
    return results


# ----- Fix pass -----

def apply_fix_local(result: Result) -> bool:
    if result.site.writer is None or result.ok:
        return False
    path = REPO_ROOT / result.site.path
    text = fetch_local(path)
    if text is None:
        return False
    new_text = result.site.writer(text, result.expected)
    if new_text == text:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


def apply_fix_grammar(result: Result, grammar_path: Path) -> bool:
    if result.site.writer is None or result.ok or result.site.location != "grammar-local":
        return False
    # site.path is display like "[tree-sitter-mvl] package.json" — strip prefix
    filename = result.site.path.split("] ", 1)[-1]
    path = grammar_path / filename
    text = fetch_local(path)
    if text is None:
        return False
    new_text = result.site.writer(text, result.expected)
    if new_text == text:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


# ----- Presentation -----

def print_table(results: list[Result]) -> None:
    width = max((len(r.site.path) for r in results), default=20)
    print(f"{'file'.ljust(width)}  {'kind'.ljust(18)}  {'current'.ljust(15)}  {'target'.ljust(10)}  status")
    print("-" * (width + 60))
    for r in results:
        marker = "OK" if r.ok else ("MISSING" if r.current is None else "DRIFT")
        if r.changed:
            marker = "FIXED"
        cur = r.current if r.current is not None else "-"
        print(f"{r.site.path.ljust(width)}  {r.site.kind.ljust(18)}  {cur.ljust(15)}  {r.expected.ljust(10)}  {marker}")


# ----- Main -----

def repo_version() -> str:
    v = fetch_local(REPO_ROOT / "VERSION")
    if v is None:
        print("cannot read mvl-spec/VERSION", file=sys.stderr)
        sys.exit(2)
    return v.strip()


def main() -> int:
    p = argparse.ArgumentParser(description="Validate MVL artifact versions.")
    p.add_argument("--fix", action="store_true", help="align local files to target version")
    p.add_argument("--target", help="override target version (default: read mvl-spec/VERSION)")
    p.add_argument("--tree-sitter-dir", help="path to tree-sitter-mvl checkout")
    p.add_argument("--skip-tree-sitter", action="store_true", help="skip grammar-repo checks")
    args = p.parse_args()

    target = args.target or repo_version()
    print(f"target version: {target}")

    grammar_mode, grammar_path = resolve_grammar_source(args.tree_sitter_dir, args.skip_tree_sitter)
    if grammar_mode == "local":
        print(f"tree-sitter-mvl: local checkout at {grammar_path}")
    elif grammar_mode == "remote":
        print(f"tree-sitter-mvl: fetching from {REMOTE_BASE}")
    else:
        print("tree-sitter-mvl: SKIPPED")
    print()

    # Evaluate all sites
    results = [evaluate_local(s, target) for s in LOCAL_SITES]
    if grammar_mode != "skip":
        results.extend(evaluate_grammar(grammar_mode, grammar_path, target))

    # Apply fixes if requested
    if args.fix:
        for r in results:
            if r.site.location == "local":
                if apply_fix_local(r):
                    r.changed = True
                    r.ok = True
                    r.current = r.expected
            elif r.site.location == "grammar-local":
                if apply_fix_grammar(r, grammar_path):
                    r.changed = True
                    r.ok = True
                    r.current = r.expected

    print_table(results)

    drift = [r for r in results if not r.ok]
    if drift:
        print()
        print(f"{len(drift)} file(s) with drift or missing.")
        if not args.fix and any(r.current is not None for r in drift):
            print("Run with --fix to align local files.")
        if any(r.site.location == "grammar-remote" and not r.ok for r in results):
            print("Grammar repo is remote-only; --fix cannot touch it. Clone locally or use --tree-sitter-dir.")
        return 1

    print("\nall versions aligned.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
