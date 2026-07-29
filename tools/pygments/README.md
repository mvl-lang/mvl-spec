# pygments-mvl

Pygments lexer for MVL source code.

```bash
pip install pygments-mvl
pygmentize -l mvl example.mvl
```

Registers under the `mvl` alias and claims `*.mvl`, so ```` ```mvl ```` fences work
anywhere Pygments is installed.

## Structure

```
tools/pygments/
├── pyproject.toml           Package manifest — publishes as `pygments-mvl` to PyPI
├── README.md
├── LICENSE                  Apache-2.0
├── mvl_pygments/
│   ├── __init__.py
│   ├── lexer.py             RegexLexer subclass; keyword sets generated from
│   │                        ../../grammar/keywords.yaml
│   └── keywords.py          Generated file — do NOT edit by hand
└── tests/
    ├── test_lexer.py
    └── corpus/              MVL example files for visual smoke-testing
```

## Design notes

- Keyword sets come from `grammar/keywords.yaml` via `tools/generators/gen_pygments.py`.
- Handle effect syntax (`! Console + Net`), refinements (`where x > 0`), contracts (`requires`, `ensures`, `invariant`, `decreases`), capabilities (`iso`, `val`, `ref`), IFC labels (`Tainted[T]`, `Secret[T]`, and the capability labels `ConfigPath[T]` / `DbUrl[T]` / `ApiEndpoint[T]` / `AuditTarget[T]`). There is no `Public` label — unlabeled is public by default.
- String literals: single-line, triple-quoted, raw (`r"..."`), raw triple.
- Comments: `//` line, `///` doc.

## Publishing

```bash
git tag pygments-v0.1.5
git push --tags
```

`.github/workflows/publish-pygments.yml` builds and uploads via PyPI Trusted
Publishing (OIDC) — no API token. It refuses to publish unless
`mvl_pygments/keywords.py` carries the generated banner, so hand-written keyword
tables cannot reach PyPI.

## Downstream consumers

- [mvl-lang.org](https://mvl-lang.org) — swaps `` ```rust `` fences back to `` ```mvl `` once this ships (tracked in [mvl-lang.github.io#5](https://github.com/mvl-lang/mvl-lang.github.io/issues/5))
- Any static-site generator using Pygments (Sphinx, mkdocs, Hugo with Chroma)
- Jupyter notebook code blocks
