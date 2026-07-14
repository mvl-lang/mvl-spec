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
├── Makefile             # build targets: validate / tex / coq / thy / check-*
├── README.md            # this file
├── tests/
│   └── examples.v       # regression suite of example typing proofs
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

## Corpus alignment

`tests/examples.v` mirrors [`mvl-lang/mvl/tests/corpus/`](https://github.com/mvl-lang/mvl/tree/main/tests/corpus) so that every corpus test file has a corresponding semantic theorem (when the rules exist) or a TODO pointer (when they don't yet). This is the empirical side of the correspondence work discussed in the personal notes at `work/mvl_correspondence.md` (Ben) and cross-referenced from mvl#1823.

| Corpus suite | Files | Semantically covered? | Blocker (if any) |
|--------------|-------|----------------------|------------------|
| `00_smoke` | arithmetic, assertions, hello | Arithmetic ✅; assertions + hello ⏳ | PR-11 (effects, #18) for println/assert_eq |
| `01_expressions` | bool, int, precedence | ✅ Fully covered | — |
| `02_control_flow` | if, early return, match, while | `if` ✅; rest ⏳ | PR-9 (#16) for match; new rules for `while`/`return` |
| `03_functions` | basic, HOF, generic, total/partial | Basic + HOF ✅ | PR-8 (#15) for generics; PR-15 (#22) for total/partial |
| `04_types` | struct, enum, enum-payload, Option/Result | ⏳ | PR-6 (#13) for ADTs; PR-8 (#15) for Option/Result generics |
| `05_collections` | list, map, set, iter | (library, not language) | Not a semantics target |

**Current coverage: ~40%** of corpus suites have semantic-side proofs. Every future semantic PR should grow `examples.v` alongside the rules it adds. When a rule lands here and the corresponding corpus test starts passing under a hypothetical `mvl/semantics` backend column (see mvl#1823), the correspondence for that feature is confirmed.

---

## Roadmap for the semantics

- ✅ **PR-1 (scaffold)** — Ott stub, Makefile, CI, generated/ dir. Two example rules to prove the pipeline works. Merged as [#7](https://github.com/mvl-lang/mvl-spec/pull/7).
- ✅ **PR-2 (core language)** — Base types (`Int`, `Bool`, `String`, `Unit`), literals, arithmetic (`+ - * / %`), comparison (`== != < > <= >=`), logical (`&& || !`), `if`/`else`, `let` binding, environment-lookup semantics. 22 typing rules. Merged as [#8](https://github.com/mvl-lang/mvl-spec/pull/8).
- ✅ **PR-3 (unary functions)** — Function type `T1 -> T2`, lambda `\ x : T . e` (MVL surface: `|x: T| e`), unary application `e1 ( e2 )`. Two rules (T-Abs, T-App); 24 total.
- ✅ **PR-4 (top-level fn declarations)** — `program` and `fdecl` grammar; recursive `fn f(x: T1) -> T2 { e }`; program well-formedness judgment `G |- P : T`. Two rules (Prog-Main, Prog-FnDecl); 26 total.
- ✅ **PR-5 (example theorems + corpus alignment)** — `tests/examples.v` is now organized to mirror [mvl-lang/mvl/tests/corpus/](https://github.com/mvl-lang/mvl/tree/main/tests/corpus). 24 proven typing examples cover corpus suites 00_smoke, 01_expressions, 02_control_flow (if only), and 03_functions (basic + HOF). Each section names the corpus file it mirrors; sections without semantic coverage carry TODO markers pointing to the future PR that unlocks them. `make check-examples` compiles all proofs. Together with mvl#1823's uniform corpus, this is the empirical foundation for the differential-testing correspondence. Original PR-5 (n-ary parameters via Ott lists) is deferred as [#11](https://github.com/mvl-lang/mvl-spec/issues/11).
- ⬜ **PR-6 — ADTs (structs + enums)** — `type Point = struct { x: Int, y: Int }`, struct construction, field access, enum variants.
- ⬜ **PR-6 — ADTs (structs + enums)** — [#13](https://github.com/mvl-lang/mvl-spec/issues/13). `type Point = struct { x: Int, y: Int }`, struct construction, field access, enum variants.
- ⬜ **PR-7 — Reduction semantics** — [#14](https://github.com/mvl-lang/mvl-spec/issues/14). Small-step operational semantics `e --> e'`, values, structural congruence, β-reduction (needs Ott's binding + substitution machinery).
- ⬜ **PR-8 — Generics** — [#15](https://github.com/mvl-lang/mvl-spec/issues/15). Type parameters on `fn` and `type` declarations, polymorphic types.
- ⬜ **PR-9 — Pattern matching** — [#16](https://github.com/mvl-lang/mvl-spec/issues/16). `match` with exhaustiveness side condition, pattern types.
- ⬜ **PR-10 — Refinements** — [#17](https://github.com/mvl-lang/mvl-spec/issues/17). `T where P`, refinement-typing judgment, solver-boundary specification.
- ⬜ **PR-11 — Effects** — [#18](https://github.com/mvl-lang/mvl-spec/issues/18). Effect judgment `Γ ⊢ e : T ! ε`, subsumption, parametrized effects.
- ⬜ **PR-12 — IFC** — [#19](https://github.com/mvl-lang/mvl-spec/issues/19). Label lattice, `Secret[T]` / `Tainted[T]`, `declassify` / `sanitize`, non-interference statement.
- ⬜ **PR-13 — Capabilities** — [#20](https://github.com/mvl-lang/mvl-spec/issues/20). `val` / `ref` / `iso`, sendability at actor boundaries (Pony-derived, NOT Rust borrow checker).
- ⬜ **PR-14 — Contracts** — [#21](https://github.com/mvl-lang/mvl-spec/issues/21). `requires` / `ensures` / `invariant` / `decreases`; contract-typing judgment.
- ⬜ **PR-15 — Termination** — [#22](https://github.com/mvl-lang/mvl-spec/issues/22). Structural recursion, `decreases` measure, `partial` opt-out.
- ⬜ **PR-16 — Actors** — [#23](https://github.com/mvl-lang/mvl-spec/issues/23). Behaviors, mailboxes, message-send judgment (per spec 015).
- ⬜ **PR-17 — Session types** — [#24](https://github.com/mvl-lang/mvl-spec/issues/24). Protocol projection (per spec 016).
- ⬜ (Deferred) **N-ary parameters** — [#11](https://github.com/mvl-lang/mvl-spec/issues/11). Blocked on either Ott upstream fix or a semantic workaround (encode as tuples).

Each PR is small and independently reviewable. The generated Coq accumulates; the Phase 9 mechanization ([#4](https://github.com/mvl-lang/mvl-spec/issues/4)) picks up from a stable snapshot when the core is done.

---

## Related work

- [Ott reference manual](https://www.cl.cam.ac.uk/~pes20/ott/ottv0.32/doc.pdf)
- [Ott examples](https://www.cl.cam.ac.uk/~pes20/ott/examples/) — reference specs for STLC, ML, and more
- [WebAssembly reference](https://github.com/WebAssembly/spec) — similar layered spec-and-implementation approach
- [CompCert](https://compcert.org/) — Coq semantics + verified compilation, the model MVL aims at long-term
- [RustBelt](https://plv.mpi-sws.org/rustbelt/) — Iris/Coq semantics for a Rust subset, closest ancestor in scope
