# MVL Semantics

**Status:** Scaffold. Tracked in [#3](https://github.com/mvl-lang/mvl-spec/issues/3).

The formal semantics of MVL, written in [Ott](https://www.cl.cam.ac.uk/~pes20/ott/). One source (`mvl.ott`) generates:

- Publication-quality LaTeX (for the paper)
- Coq definitions (for the Phase 9 mechanization)
- Isabelle/HOL definitions (for cross-check)

The current file is a **scaffold**: metavariables, minimal syntax, and two example typing rules (T-Var, T-Int, T-Plus). Real semantic content — the full type system, effects, IFC, capabilities, contracts, termination — lands in follow-up PRs against #3.

---

## Layout

```
semantics/
├── mvl.ott              # Ott source — the source of truth
├── Makefile             # build targets: validate / tex / coq / thy
├── README.md            # this file
└── generated/           # build outputs (gitignored, not committed)
    ├── mvl.tex          # LaTeX (from `make tex`)
    ├── mvl.v            # Coq (from `make coq`)
    └── mvl.thy          # Isabelle (from `make thy`)
```

---

## Building

### Prerequisites

- **Ott** — the specification-generation tool. Install via [opam](https://opam.ocaml.org/):

  ```bash
  opam install ott
  ```

  Or from source: [github.com/ott-lang/ott](https://github.com/ott-lang/ott).

- **Coq** (optional, for `make check-coq`) — `opam install coq`
- **pdflatex** (optional, for `make check-tex`) — via TeX Live or MacTeX

### Common commands

```bash
cd semantics/
make validate     # syntax check — fastest, no output files
make tex          # generate generated/mvl.tex
make coq          # generate generated/mvl.v
make check-coq    # generate + run coqc on the Coq output
make clean        # remove generated files
make help         # list all targets
```

---

## How the semantics are validated

Four layers, from cheapest to strictest:

### 1. Ott's own parser — `make validate`

Ott parses `mvl.ott` and reports any grammar rule that is malformed, any judgment with unbound metavariables, or any inconsistency between the syntax section and the rules. **This is the primary gate — nothing lands without it passing.**

### 2. LaTeX generation — `make tex`

Ott emits `generated/mvl.tex`. This catches issues with the `tex` annotations on metavariables and terminals (`{{ tex \vdash }}` etc.) — malformed LaTeX escapes crash `pdflatex` in the next step.

### 3. Coq generation + typecheck — `make check-coq`

Ott emits `generated/mvl.v`, and then `coqc` type-checks it. Coq is stricter than Ott's own analysis: it catches inconsistencies in variable binding, judgment shape, and inductive definitions that Ott may accept but Coq rejects. **This is the closest thing to a proof-of-consistency for the semantics before Phase 9's actual soundness theorem.**

### 4. Round-trip on the corpus (future)

Once the semantics covers enough of the language to typecheck real programs, we'll validate that:

- The Ott-derived reduction relation agrees with the compiler's evaluator on the [mvl corpus](https://github.com/mvl-lang/mvl/tree/main/tests/corpus)
- Every accepted program reduces to a value or gets stuck in a way the type system predicts

This layer doesn't exist yet — it requires real reduction rules first.

### 5. CI on every PR — `.github/workflows/semantics-build.yml`

The above (layers 1–3) run automatically on every PR touching `semantics/`. The workflow uploads the generated LaTeX and Coq as artifacts for reviewers to inspect without needing Ott locally.

---

## Roadmap for the semantics

- ✅ **PR-1 (this scaffold)** — Ott stub, Makefile, CI, generated/ dir. Two example rules to prove the pipeline works.
- ⬜ **PR-2 — Core language** — Full syntax mirror of `grammar/grammar.ebnf`; typing rules for base types, ADTs, generics, `let`, `if`, `match`.
- ⬜ **PR-3 — Refinements** — `T where P`, refinement-typing judgment, solver-boundary specification.
- ⬜ **PR-4 — Effects** — Effect judgment `Γ ⊢ e : T ! ε`, subsumption, parametrized effects.
- ⬜ **PR-5 — IFC** — Label lattice, `Secret[T]` / `Tainted[T]`, `declassify` / `sanitize`, non-interference statement.
- ⬜ **PR-6 — Capabilities** — `val` / `ref` / `iso`, sendability at actor boundaries.
- ⬜ **PR-7 — Contracts** — `requires` / `ensures` / `invariant` / `decreases`; contract-typing judgment.
- ⬜ **PR-8 — Termination** — Structural recursion, `decreases` measure, `partial` opt-out.
- ⬜ **PR-9 — Actors** — Behaviors, mailboxes, message-send judgment (per spec 015).
- ⬜ **PR-10 — Session types** — Protocol projection (per spec 016).

Each PR is small and independently reviewable. The generated Coq accumulates; the Phase 9 mechanization ([#4](https://github.com/mvl-lang/mvl-spec/issues/4)) picks up from a stable snapshot when the core is done.

---

## Related work

- [Ott reference manual](https://www.cl.cam.ac.uk/~pes20/ott/ottv0.32/doc.pdf)
- [Ott examples](https://www.cl.cam.ac.uk/~pes20/ott/examples/) — reference specs for STLC, ML, and more
- [WebAssembly reference](https://github.com/WebAssembly/spec) — similar layered spec-and-implementation approach
- [CompCert](https://compcert.org/) — Coq semantics + verified compilation, the model MVL aims at long-term
- [RustBelt](https://plv.mpi-sws.org/rustbelt/) — Iris/Coq semantics for a Rust subset, closest ancestor in scope
