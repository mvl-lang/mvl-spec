(** * Corpus-aligned example typings **

    Each section corresponds to one file in [mvl-lang/mvl/tests/corpus/].
    For every corpus test that the current semantics can express, we
    prove the typing judgment holds.  Corpus tests that need not-yet-
    landed semantic PRs are marked with a TODO pointing at the ticket.

    This is the **semantic side** of the correspondence with the
    compiler-side corpus (see mvl-lang/mvl#1823 and the correspondence
    doc).  When a semantic PR lands, its tests here should mirror the
    corresponding corpus file, and running both against every backend
    (compiler + Coq-extracted typechecker) is the differential check.

    Coverage summary as of this file:
      - 00_smoke:       arithmetic ✅  assertions ⏳ effects  hello ⏳ effects
      - 01_expressions: bool ✅       int ✅        precedence ✅
      - 02_control_flow: if ✅        return ⏳    match ⏳    while ⏳
      - 03_functions:   basic ✅     hof ✅        generic ⏳  total/partial ⏳
      - 04_types:       (none — needs PR-6 ADTs)
      - 05_collections: (library, not language semantics)
*)

Require Import Arith.
Require Import Bool.
Require Import List.
Require Import String.
Require Import mvl.

(*===============================================================*)
(** ** 00_smoke                                                   *)
(*===============================================================*)

(** *** 00_smoke/arithmetic_test.mvl

    Corpus tests: arithmetic_smoke_int_add / _sub / _mul / _div / _rem.
    Each is `assert_eq(a OP b, expected)`.  The semantic side only
    proves well-typedness; that OP evaluates to `expected` needs the
    reduction relation from PR-7 (#14).
*)

Example smoke_arithmetic_add :
  typing G_Empty (e_Plus (e_Int 1) (e_Int 2)) T_Int.
Proof. apply Ty_Plus; apply Ty_Int. Qed.

Example smoke_arithmetic_sub :
  typing G_Empty (e_Minus (e_Int 10) (e_Int 3)) T_Int.
Proof. apply Ty_Minus; apply Ty_Int. Qed.

Example smoke_arithmetic_mul :
  typing G_Empty (e_Times (e_Int 4) (e_Int 5)) T_Int.
Proof. apply Ty_Times; apply Ty_Int. Qed.

Example smoke_arithmetic_div :
  typing G_Empty (e_Div (e_Int 20) (e_Int 4)) T_Int.
Proof. apply Ty_Div; apply Ty_Int. Qed.

Example smoke_arithmetic_rem :
  typing G_Empty (e_Mod (e_Int 17) (e_Int 5)) T_Int.
Proof. apply Ty_Mod; apply Ty_Int. Qed.

(** *** 00_smoke/assertions_test.mvl

    TODO: needs PR-11 (effects, #18) to model [assert_eq] as a
    call with an assertion effect, and PR-7 (reduction, #14) to
    prove the assertion actually holds.  Currently we only type
    integers; [assert_eq(true, true)] is trivial when everything
    is a value.
*)

(** *** 00_smoke/hello_test.mvl

    TODO: needs PR-11 (effects, #18) to model [println] as a call
    with the [Console] effect.
*)

(*===============================================================*)
(** ** 01_expressions                                             *)
(*===============================================================*)

(** *** 01_expressions/bool_ops_test.mvl

    Corpus tests: bool_ops_and_truth_table, bool_ops_or_truth_table,
    bool_ops_not, bool_ops_combined.
*)

Example expr_and_tt :
  typing G_Empty (e_And (e_Bool b_True) (e_Bool b_True)) T_Bool.
Proof. apply Ty_And; apply Ty_True. Qed.

Example expr_and_tf :
  typing G_Empty (e_And (e_Bool b_True) (e_Bool b_False)) T_Bool.
Proof. apply Ty_And. apply Ty_True. apply Ty_False. Qed.

Example expr_or_tf :
  typing G_Empty (e_Or (e_Bool b_True) (e_Bool b_False)) T_Bool.
Proof. apply Ty_Or. apply Ty_True. apply Ty_False. Qed.

Example expr_not :
  typing G_Empty (e_Not (e_Bool b_True)) T_Bool.
Proof. apply Ty_Not; apply Ty_True. Qed.

Example expr_bool_combined :
  typing G_Empty
    (e_And (e_Bool b_True) (e_Not (e_Bool b_False)))
    T_Bool.
Proof.
  apply Ty_And.
  - apply Ty_True.
  - apply Ty_Not; apply Ty_False.
Qed.

(** *** 01_expressions/int_ops_test.mvl

    Comparison operators (<, <=, >, >=, ==, !=), all Int → Bool.
*)

Example expr_int_lt :
  typing G_Empty (e_Lt (e_Int 1) (e_Int 2)) T_Bool.
Proof. apply Ty_Lt; apply Ty_Int. Qed.

Example expr_int_le :
  typing G_Empty (e_Le (e_Int 1) (e_Int 1)) T_Bool.
Proof. apply Ty_Le; apply Ty_Int. Qed.

Example expr_int_gt :
  typing G_Empty (e_Gt (e_Int 2) (e_Int 1)) T_Bool.
Proof. apply Ty_Gt; apply Ty_Int. Qed.

Example expr_int_ge :
  typing G_Empty (e_Ge (e_Int 1) (e_Int 1)) T_Bool.
Proof. apply Ty_Ge; apply Ty_Int. Qed.

Example expr_int_eq :
  typing G_Empty (e_Eq (e_Int 42) (e_Int 42)) T_Bool.
Proof. apply Ty_EqInt; apply Ty_Int. Qed.

Example expr_int_neq :
  typing G_Empty (e_Neq (e_Int 42) (e_Int 43)) T_Bool.
Proof. apply Ty_NeqInt; apply Ty_Int. Qed.

(** Negation is [0 - x] in the current semantics (no unary [-]).
    This mirrors the corpus test that says `assert_eq(-5, 0 - 5);`. *)
Example expr_int_negation_via_sub :
  typing G_Empty (e_Minus (e_Int 0) (e_Int 5)) T_Int.
Proof. apply Ty_Minus; apply Ty_Int. Qed.

(** *** 01_expressions/precedence_test.mvl

    Precedence is entirely a parser concern.  The AST already
    reflects the intended precedence, so the semantic proof just
    typechecks the resulting nested structure.

    Corpus example: `assert_eq(2 + 3 * 4, 14)` parses as
    `e_Plus 2 (e_Times 3 4)`.
*)

Example expr_prec_mul_over_add :
  typing G_Empty
    (e_Plus (e_Int 2) (e_Times (e_Int 3) (e_Int 4)))
    T_Int.
Proof.
  apply Ty_Plus.
  - apply Ty_Int.
  - apply Ty_Times; apply Ty_Int.
Qed.

Example expr_prec_and_over_or :
  typing G_Empty
    (e_Or (e_And (e_Bool b_True) (e_Bool b_False)) (e_Bool b_True))
    T_Bool.
Proof.
  apply Ty_Or.
  - apply Ty_And. apply Ty_True. apply Ty_False.
  - apply Ty_True.
Qed.

(*===============================================================*)
(** ** 02_control_flow                                            *)
(*===============================================================*)

(** *** 02_control_flow/if_expr_test.mvl

    Corpus test: `if_expr_returns_int` proves
    `assert_eq(if true { 1 } else { 0 }, 1);`.
*)

Example ctrl_if_int :
  typing G_Empty
    (e_If (e_Bool b_True) (e_Int 1) (e_Int 0))
    T_Int.
Proof.
  apply Ty_If.
  - apply Ty_True.
  - apply Ty_Int.
  - apply Ty_Int.
Qed.

(** if branches must agree on type — this is the semantic version
    of the "both arms return the same T" discipline. *)
Example ctrl_if_bool :
  typing G_Empty
    (e_If (e_Lt (e_Int 1) (e_Int 2)) (e_Bool b_True) (e_Bool b_False))
    T_Bool.
Proof.
  apply Ty_If.
  - apply Ty_Lt; apply Ty_Int.
  - apply Ty_True.
  - apply Ty_False.
Qed.

(** *** 02_control_flow/early_return_test.mvl

    TODO: needs a semantic rule for early return.  Currently the
    semantics is purely functional (last expression is the value).
    Filing as follow-up: model `return e` as either syntactic sugar
    for nested if-else or add a control-flow exit judgment.
    See #14 (PR-7 reduction) — natural place to add it.
*)

(** *** 02_control_flow/match_test.mvl

    TODO: needs PR-9 (pattern matching, #16).  Match with
    exhaustiveness is the first place we enforce Requirement 3
    at the type level.
*)

(** *** 02_control_flow/while_test.mvl

    TODO: needs [while] in the expression grammar with a decreases
    measure.  Currently omitted from the semantics; grammar has it
    but no typing rule.  See PR-15 (termination, #22) — [while] in
    total functions requires a decreases annotation.
*)

(*===============================================================*)
(** ** 03_functions                                               *)
(*===============================================================*)

(** *** 03_functions/basic_test.mvl

    Corpus `basic_add`: [fn add(x, y) = x + y] then [assert_eq(add(2, 3), 5)].
    Semantic version: lambda + application; top-level fn decl proven
    in a separate example.
*)

Example fn_basic_add_lambda :
  typing G_Empty
    (e_App (e_Lam 0 T_Int (e_Lam 1 T_Int (e_Plus (e_Var 0) (e_Var 1))))
           (e_Int 2))
    (T_Fn T_Int T_Int).
Proof.
  apply Ty_App with (T1 := T_Int).
  - apply Ty_Abs. apply Ty_Abs. apply Ty_Plus.
    + apply Ty_Var. simpl. reflexivity.
    + apply Ty_Var. simpl. reflexivity.
  - apply Ty_Int.
Qed.

(** Corpus `basic_add` as a top-level program.

      fn add(x : Int) -> Int -> Int { |y| x + y }   -- curried form
      main add(2)(3)

    Semantic-side program well-formedness. *)
Example fn_basic_add_program :
  prog G_Empty
    (P_Cons
       (fdecl_FnDecl 0 1 T_Int (T_Fn T_Int T_Int)
          (e_Lam 2 T_Int (e_Plus (e_Var 1) (e_Var 2))))
       (P_Main (e_App (e_App (e_Var 0) (e_Int 2)) (e_Int 3))))
    T_Int.
Proof.
  apply Prog_FnDecl.
  - apply Ty_Abs. apply Ty_Plus.
    + apply Ty_Var. simpl. reflexivity.
    + apply Ty_Var. simpl. reflexivity.
  - apply Prog_Main. apply Ty_App with (T1 := T_Int).
    + apply Ty_App with (T1 := T_Int).
      * apply Ty_Var. simpl. reflexivity.
      * apply Ty_Int.
    + apply Ty_Int.
Qed.

(** *** 03_functions/higher_order_test.mvl

    Corpus `hof_apply_lambda`: [let f = |x| x + 1 in f(5)].
    STLC already covers HOF trivially — every lambda is HO.
*)

Example fn_hof_apply :
  typing G_Empty
    (e_Let 0 (T_Fn T_Int T_Int)
       (e_Lam 1 T_Int (e_Plus (e_Var 1) (e_Int 1)))
       (e_App (e_Var 0) (e_Int 5)))
    T_Int.
Proof.
  apply Ty_Let with (T5 := T_Fn T_Int T_Int).
  - apply Ty_Abs. apply Ty_Plus.
    + apply Ty_Var. simpl. reflexivity.
    + apply Ty_Int.
  - apply Ty_App with (T1 := T_Int).
    + apply Ty_Var. simpl. reflexivity.
    + apply Ty_Int.
Qed.

(** *** 03_functions/generic_test.mvl

    TODO: needs PR-8 (generics, #15).  Corpus tests [id[T](x: T) -> T]
    with T-Type-Abs and T-Type-App rules.  Currently monomorphic.
*)

(** *** 03_functions/total_partial_test.mvl

    TODO: needs PR-15 (termination, #22).  Corpus tests that a
    recursive [factorial] is provably total via a decreases measure,
    while an unbounded [loop] must be marked [partial].  Semantics
    doesn't distinguish total from partial yet.
*)

(*===============================================================*)
(** ** 04_types                                                   *)
(*===============================================================*)

(** *** 04_types/struct_test.mvl, enum_test.mvl, enum_payload_test.mvl

    TODO: all four files need PR-6 (ADTs, #13).  This is the biggest
    single unlock — enables Option, Result, and the pattern-match
    tests in 04.
*)

(** *** 04_types/option_result_test.mvl

    TODO: needs PR-6 (ADTs, #13) + PR-8 (generics, #15) + PR-9
    (pattern matching, #16).  This is the first test that exercises
    the full ADT + generics + match stack.
*)

(*===============================================================*)
(** ** 05_collections                                             *)
(*===============================================================*)

(** *** 05_collections/{list,map,set}_test.mvl

    TODO: NOT applicable to language semantics.  Collections are
    stdlib, verified by testing rather than by typing rules.
    The corresponding semantic work is stdlib theorems (a separate
    body of work, not part of #3).  Listed here for completeness.

    Once PR-7 (reduction, #14) lands, we could add example theorems
    like "[1, 2, 3].len() reduces to 3" — but that's evaluation-
    semantics coverage of stdlib, not language semantics.
*)
