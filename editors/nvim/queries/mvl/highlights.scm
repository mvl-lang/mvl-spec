; MVL Tree-sitter highlight queries
; Compatible with Zed (zed-extensions) and Neovim (nvim-treesitter)

; ============================================================
; Comments
; ============================================================

(line_comment) @comment

; ============================================================
; Keywords — declarations
; ============================================================

; BEGIN GENERATED KEYWORDS
; DO NOT EDIT THIS BLOCK BY HAND. Generated from mvl-spec
; grammar/keywords.yaml by tools/generators/gen_highlights.py. Run
; tools/generators/regen-all.sh after editing keywords.yaml.
;
; Literal keyword lists only. Node-anchored captures are hand-written
; below this region and survive regeneration.

; declarations
[
  "fn"
  "type"
  "const"
  "extern"
  "impl"
  "builtin"
  "struct"
  "enum"
  "actor"
  "effect"
  "test"
  "label"
  "relabel"
] @keyword

; imports
[
  "use"
  "pub"
] @keyword.import

; bindings and statements
[
  "let"
  "ghost"
  "if"
  "else"
  "for"
  "in"
  "while"
  "match"
  "return"
] @keyword

; refinement and contract clauses
[
  "where"
  "requires"
  "ensures"
  "invariant"
  "with"
  "decreases"
  "forall"
  "exists"
] @keyword.modifier

; operators
[
  "as"
  "consume"
] @keyword.operator

; concurrency
[
  "select"
] @keyword.control

; Captured via grammar nodes instead of literals, so they cannot be
; confused with same-spelled identifiers:
;   false, true -> (boolean_literal) @constant.builtin
;   iso, ref, tag, val -> (capability) @keyword.modifier
;   partial, total -> (totality) @keyword.modifier

; CONTEXTUAL — never highlight these as bare words. Each is an ordinary
; identifier outside its one position, so a flat list would highlight
; `let end = 5`. Anchor on the enclosing node if wanted at all:
;   self
;   old
;   end
;   timeout
; END GENERATED KEYWORDS


; ============================================================
; Keywords — totality (safety modifiers)
; ============================================================

(totality) @keyword.modifier

; ============================================================
; Keywords — security modifiers on functions
; ============================================================

(security_modifier) @keyword.modifier

; ============================================================
; Keywords — statements
; ============================================================


; ============================================================
; Keywords — expressions
; ============================================================




; #894 removed declassify()/sanitize() in favour of named relabel
; transitions. `relabel` itself is already captured as a keyword above;
; this highlights the transition name at the call site.
(relabel_expr (identifier) @function.macro)

; ============================================================
; Capability annotations (ownership/isolation)
; ============================================================

(capability) @keyword.modifier

; ============================================================
; Security labels — type-level information flow control
; ============================================================

(security_label) @type.qualifier

; ============================================================
; Built-in generic types
; ============================================================

(option_type "Option" @type.builtin)
(result_type "Result" @type.builtin)

; ============================================================
; Built-in effects (effect list)
; ============================================================

(effect) @keyword.effect

; ============================================================
; Pattern keywords
; ============================================================

(none_pattern) @constant.builtin
(some_pattern "Some" @constructor)
(ok_pattern "Ok" @constructor)
(err_pattern "Err" @constructor)

"_" @variable.builtin

; ============================================================
; Boolean literals
; ============================================================

(boolean_literal) @constant.builtin

; ============================================================
; Numeric literals
; ============================================================

(integer_literal) @number
(float_literal) @number.float

; ============================================================
; String and character literals
; ============================================================

(string_literal) @string
(char_literal) @character

; ============================================================
; Type declarations
; ============================================================

(type_decl
  (identifier) @type.definition)

(struct_body
  (field_decl
    (identifier) @variable.member))

(enum_body
  (variant
    (identifier) @constructor))

; ============================================================
; Function declarations
; ============================================================

(fn_decl
  (identifier) @function)

(param
  (identifier) @variable.parameter)

(const_decl
  (identifier) @constant)

; ============================================================
; Module imports
; ============================================================

(use_decl
  (module_path (identifier) @namespace))

(reexport_decl
  (module_path (identifier) @namespace))


; ============================================================
; Type expressions
; ============================================================

(base_type
  (identifier) @type)

; ============================================================
; Function calls
; ============================================================

(fn_call_expr
  function: (identifier) @function.call)

; Method calls — `x.method(...)`.  The grammar inlines this into `expr`
; with a `method:` field; anchor on that field so we don't confuse the
; method-call form with plain field access (`x.field`).
(expr
  method: (identifier) @function.method)

; ============================================================
; Struct construction
; ============================================================

(construct_expr
  type: (identifier) @constructor)

; ============================================================
; Operators
; ============================================================

(unary_expr operator: "!") @operator
(unary_expr operator: "~") @operator

; Remove | from punctuation.delimiter (now classified as operator above)

; ============================================================
; Punctuation
; ============================================================

; ============================================================
; Operators and punctuation — hand-written, not keyword-derived
; ============================================================

[
  "->"
  "=>"
  "="
  "+"
  "-"
  "*"
  "/"
  "%"
  "=="
  "!="
  "<"
  ">"
  "<="
  ">="
  "&&"
  "||"
  "&"
  "|"
  "<<"
  ">>"
  "^"
] @operator

[
  "("
  ")"
  "{"
  "}"
  "["
  "]"
] @punctuation.bracket

[
  ","
  ";"
  ":"
  "."
] @punctuation.delimiter
