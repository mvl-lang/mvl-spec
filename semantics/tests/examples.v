(** * Example typings — validates the generated MVL semantics **

    Each theorem exhibits a well-typed MVL program encoded via the
    Ott-generated inductive types, together with a proof that the
    typing judgment holds.  Success here confirms:

      1. The generated `mvl.v` is well-formed Coq (imported cleanly).
      2. The typing rules discharge in obvious cases without any
         hidden well-formedness conditions.
      3. Future rule changes that break these proofs surface
         immediately in CI.

    These are the seed of a growing regression suite.  Every new
    typing rule should ideally come with at least one example proof.

    Corresponds to PR-5 of #3 (mvl-lang/mvl-spec).
*)

Require Import Arith.
Require Import Bool.
Require Import List.
Require Import String.
Require Import mvl.

(*---------------------------------------------------------------*)
(** ** Ground literals                                            *)
(*---------------------------------------------------------------*)

(** `42 : Int` in the empty environment. *)
Example ex_int_literal :
  typing G_Empty (e_Int 42) T_Int.
Proof. apply Ty_Int. Qed.

(** `true : Bool` in the empty environment. *)
Example ex_bool_true :
  typing G_Empty (e_Bool b_True) T_Bool.
Proof. apply Ty_True. Qed.

(** `false : Bool` in the empty environment. *)
Example ex_bool_false :
  typing G_Empty (e_Bool b_False) T_Bool.
Proof. apply Ty_False. Qed.

(** `unit : Unit`. *)
Example ex_unit :
  typing G_Empty e_Unit T_Unit.
Proof. apply Ty_Unit. Qed.

(*---------------------------------------------------------------*)
(** ** Arithmetic                                                 *)
(*---------------------------------------------------------------*)

(** `1 + 2 : Int` *)
Example ex_arith_plus :
  typing G_Empty (e_Plus (e_Int 1) (e_Int 2)) T_Int.
Proof. apply Ty_Plus; apply Ty_Int. Qed.

(** `(1 + 2) * 3 : Int` — arithmetic composes. *)
Example ex_arith_nested :
  typing G_Empty
    (e_Times (e_Plus (e_Int 1) (e_Int 2)) (e_Int 3))
    T_Int.
Proof.
  apply Ty_Times.
  - apply Ty_Plus; apply Ty_Int.
  - apply Ty_Int.
Qed.

(*---------------------------------------------------------------*)
(** ** Comparison and boolean logic                               *)
(*---------------------------------------------------------------*)

(** `1 < 2 : Bool` *)
Example ex_lt :
  typing G_Empty (e_Lt (e_Int 1) (e_Int 2)) T_Bool.
Proof. apply Ty_Lt; apply Ty_Int. Qed.

(** `(1 < 2) && (3 == 3) : Bool` — boolean logic + comparison. *)
Example ex_and_eq :
  typing G_Empty
    (e_And (e_Lt (e_Int 1) (e_Int 2))
           (e_Eq (e_Int 3) (e_Int 3)))
    T_Bool.
Proof.
  apply Ty_And.
  - apply Ty_Lt; apply Ty_Int.
  - apply Ty_EqInt; apply Ty_Int.
Qed.

(*---------------------------------------------------------------*)
(** ** Control flow                                               *)
(*---------------------------------------------------------------*)

(** `if true then 1 else 0 : Int` — both branches agree on `Int`. *)
Example ex_if :
  typing G_Empty
    (e_If (e_Bool b_True) (e_Int 1) (e_Int 0))
    T_Int.
Proof.
  apply Ty_If.
  - apply Ty_True.
  - apply Ty_Int.
  - apply Ty_Int.
Qed.

(*---------------------------------------------------------------*)
(** ** Local binding                                              *)
(*---------------------------------------------------------------*)

(** `let x : Int = 5 in x + 1 : Int` — variable lookup + binding. *)
Example ex_let :
  typing G_Empty
    (e_Let 0 T_Int (e_Int 5) (e_Plus (e_Var 0) (e_Int 1)))
    T_Int.
Proof.
  apply Ty_Let with (T5 := T_Int).
  - apply Ty_Int.
  - apply Ty_Plus.
    + apply Ty_Var. simpl. reflexivity.
    + apply Ty_Int.
Qed.

(*---------------------------------------------------------------*)
(** ** First-class functions                                      *)
(*---------------------------------------------------------------*)

(** `\x : Int . x : Int -> Int` — the identity function on Int. *)
Example ex_lam_identity :
  typing G_Empty
    (e_Lam 0 T_Int (e_Var 0))
    (T_Fn T_Int T_Int).
Proof.
  apply Ty_Abs.
  apply Ty_Var. simpl. reflexivity.
Qed.

(** `(\x : Int . x + 1) 5 : Int` — applied lambda. *)
Example ex_lam_applied :
  typing G_Empty
    (e_App (e_Lam 0 T_Int (e_Plus (e_Var 0) (e_Int 1))) (e_Int 5))
    T_Int.
Proof.
  apply Ty_App with (T1 := T_Int).
  - apply Ty_Abs. apply Ty_Plus.
    + apply Ty_Var. simpl. reflexivity.
    + apply Ty_Int.
  - apply Ty_Int.
Qed.

(*---------------------------------------------------------------*)
(** ** Top-level programs                                         *)
(*---------------------------------------------------------------*)

(** A program with one function declaration and a main expression.

      fn double(x : Int) -> Int { x + x }
      main double(21)

    Type-checks with main : Int. *)
Example ex_prog_double :
  prog G_Empty
    (P_Cons
       (fdecl_FnDecl 0 1 T_Int T_Int
          (e_Plus (e_Var 1) (e_Var 1)))
       (P_Main
          (e_App (e_Var 0) (e_Int 21))))
    T_Int.
Proof.
  apply Prog_FnDecl.
  - (* body of `double` typechecks *)
    apply Ty_Plus.
    + apply Ty_Var. simpl. reflexivity.
    + apply Ty_Var. simpl. reflexivity.
  - (* rest of program *)
    apply Prog_Main.
    apply Ty_App with (T1 := T_Int).
    + apply Ty_Var. simpl. reflexivity.
    + apply Ty_Int.
Qed.

(** A recursive function — factorial-shaped, though we can't yet
    typecheck the recursive branch structure without pattern matching.
    Instead, a simple recursive fn that just calls itself unconditionally.

      fn loop(x : Int) -> Int { loop(x) }
      main 0

    The recursion is legal at the type level (the semantics doesn't
    enforce termination yet — that's PR-14).  This exercises the
    "recursive-by-default" rule from PR-4. *)
Example ex_prog_recursive :
  prog G_Empty
    (P_Cons
       (fdecl_FnDecl 0 1 T_Int T_Int
          (e_App (e_Var 0) (e_Var 1)))
       (P_Main (e_Int 0)))
    T_Int.
Proof.
  apply Prog_FnDecl.
  - (* body: loop(x) — f is in scope by Prog-FnDecl's induction hypothesis *)
    apply Ty_App with (T1 := T_Int).
    + apply Ty_Var. simpl. reflexivity.
    + apply Ty_Var. simpl. reflexivity.
  - apply Prog_Main. apply Ty_Int.
Qed.
