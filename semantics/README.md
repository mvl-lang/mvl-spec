# MVL Semantics

**Status:** Planned. Empty for now.

This directory will hold the formal semantics of MVL, written in [Ott](https://www.cl.cam.ac.uk/~pes20/ott/).

## Planned structure

```
semantics/
├── mvl.ott                Ott source — typing rules, reduction semantics
├── generated/
│   ├── mvl.tex            LaTeX output for the paper
│   ├── mvl.v              Coq output for mechanization
│   └── mvl.thy            Isabelle/HOL output
└── proofs/                Lean 4 mechanization (Phase 9)
    └── Soundness.lean     Soundness theorem: well-typed → satisfies 11 requirements
```

## Why Ott

Ott is a specification language for programming-language semantics. You write typing and reduction rules once, in a LaTeX-like syntax, and Ott generates:

- Publication-quality LaTeX
- Coq definitions
- Isabelle/HOL definitions
- HOL4 definitions

This means the semantics doc, the paper, and the eventual mechanization all share one source. No manual translation, no drift.

## Scope

The initial Ott spec will cover:

- Types (base, ADTs, generics, refinements, capabilities, labels)
- Typing rules (Γ ⊢ e : T)
- Effect judgments (Γ ⊢ e : T ! ε)
- IFC lattice and label propagation
- Contract semantics (`requires` / `ensures`)
- Termination (structural recursion, decreases clauses)
- Actor semantics (spec 015) and sendability (Pony-style capabilities)
- Session type projection (spec 016)

## Timeline

- **Now:** empty.
- **Q3–Q4 2026:** Ott spec for the core language (types + effects + IFC).
- **Post-1.0:** Lean 4 mechanization, soundness theorem, Phase 9.

## Related work

- [WebAssembly reference interpreter](https://github.com/WebAssembly/spec/tree/main/interpreter) — Ott-adjacent style
- [CompCert](https://compcert.org/) — Coq semantics + verified compilation
- [RustBelt](https://plv.mpi-sws.org/rustbelt/) — Iris/Coq semantics for a Rust subset
- [Ott examples](https://www.cl.cam.ac.uk/~pes20/ott/examples/) — reference specs written in Ott
