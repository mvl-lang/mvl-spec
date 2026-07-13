# pygments-mvl

**Status:** Planned. Empty for now.

Pygments lexer for MVL source code. To be built per issue [mvl-lang/mvl#1812](https://github.com/mvl-lang/mvl/issues/1812).

## Planned structure

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
- Handle effect syntax (`! Console + Net`), refinements (`where x > 0`), contracts (`requires`, `ensures`, `invariant`, `decreases`), capabilities (`iso`, `val`, `ref`), IFC labels (`Public[T]`, `Tainted[T]`, `Secret[T]`).
- String literals: single-line, triple-quoted, raw (`r"..."`), raw triple.
- Comments: `//` line, `///` doc.

## Publishing

```
git tag pygments-v0.1.0
git push --tags
# CI: cd tools/pygments && python -m build && twine upload
```

## Downstream consumers

- [mvl-lang.org](https://mvl-lang.org) — swaps `` ```rust `` fences back to `` ```mvl `` once this ships (tracked in [mvl-lang.github.io#5](https://github.com/mvl-lang/mvl-lang.github.io/issues/5))
- Any static-site generator using Pygments (Sphinx, mkdocs, Hugo with Chroma)
- Jupyter notebook code blocks
