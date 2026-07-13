# MVL Language Reference

**Status:** Planned. Empty for now.

The prose language reference — the human-readable companion to the formal grammar in `grammar/grammar.ebnf` and the formal semantics in `semantics/`.

The current reference lives on the website at [mvl-lang.org/docs/reference](https://mvl-lang.org/docs/reference/) (source in [`mvl-lang/mvl-lang.github.io`](https://github.com/mvl-lang/mvl-lang.github.io/blob/main/docs/docs/reference.md)). It will be moved here so all specification artifacts live in one place, and the website will pull from this repo.

## Planned structure

```
reference/
├── syntax.md         Full syntactic reference — every production explained
├── types.md          Type system: primitives, ADTs, generics, refinements
├── ownership.md      Capabilities (val/ref/iso), sendability, actor boundaries
├── effects.md        Effect system: declaration, subsumption, parametrization
├── ifc.md            Information flow control: labels, relabel, declassify, sanitize
├── contracts.md      requires / ensures / invariant / decreases
├── modules.md        Module system, imports, visibility
├── stdlib.md         Standard library surface (moved from mvl repo)
└── extern.md         FFI: extern "c" / extern "rust", bridge convention
```

## Migration

The existing reference at `mvl-lang.github.io/docs/docs/reference.md` will move here as-is initially, then split into the files above. The website will be updated to consume this via git submodule or CI-copied content.

## Style

The reference is authoritative but readable. Every construct is:

1. Named with its EBNF production
2. Shown with a minimal example
3. Cross-linked to the relevant ADR and specs in the compiler repo

No hidden features. No "the compiler also accepts…" — if it's here, it's specified.
