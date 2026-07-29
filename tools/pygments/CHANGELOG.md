# pygments-mvl Changelog

## [Unreleased]

## [0.1.5] — 2026-07-29

### Added

- First release. Pygments lexer for MVL, published to PyPI as `pygments-mvl`.
  Registers under the `mvl` alias and claims `*.mvl`, so ```` ```mvl ```` fences and
  `pygmentize -l mvl` work anywhere Pygments is installed — mkdocs-material,
  Sphinx, Hugo/Chroma, Jupyter.
- Keyword tables are **generated** from mvl-spec `grammar/grammar.ebnf` by
  `tools/generators/gen_pygments.py`. The lexer imports them rather than
  restating them; `publish-pygments.yml` refuses to publish a `keywords.py`
  without the generated banner. See ADR-0060 (mvl-lang/mvl#2050) — five earlier
  artifacts hand-transcribed these lists and all five drifted.
- Contextual keywords are matched only where the grammar admits them. `self`,
  `old`, `end`, `timeout` and `audit` are ordinary identifiers outside one
  syntactic position, so `let end = 5;` renders `end` as a name, not a keyword.
  This is covered by tests, because it is the exact regression that shipped in
  three `.scm` query sets, the VS Code TextMate grammar and the keywords manual.
- IFC labels highlight only in label position (`Tainted[T]`), since a module may
  declare its own with `label Foo;` and none of them are reserved. There is no
  `Public` label — unlabeled is public by absence.
- Handles effect lists (`! Console + Net + DB`), refinement predicates, contract
  clauses, reference capabilities, all four string forms (single, triple, raw,
  raw triple), char literals, doc vs line comments, and hex/binary/float/
  underscore-separated numerics.
- Published via PyPI Trusted Publishing (OIDC) — no API token or repository
  secret.

### Not yet

- `mvl-lang.org` still labels MVL blocks ```` ```rust ````. Swapping those 109
  fences is tracked separately and is what makes this visible.
