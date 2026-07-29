# DO NOT EDIT THIS BLOCK BY HAND. Generated from mvl-spec
# grammar/grammar.ebnf by tools/generators/gen_pygments.py. Run
# tools/generators/regen-all.sh after editing the grammar.
"""Keyword tables for the MVL Pygments lexer.

Generated from mvl-spec grammar/grammar.ebnf. Categories are NOT
interchangeable — only RESERVED words may be highlighted as bare words.
CONTEXTUAL words are ordinary identifiers outside one syntactic position,
so highlighting them unconditionally renders `let end = 5` wrongly.
"""

from __future__ import annotations

RESERVED: tuple[str, ...] = (
    "fn",
    "type",
    "const",
    "use",
    "pub",
    "extern",
    "impl",
    "builtin",
    "struct",
    "enum",
    "actor",
    "effect",
    "test",
    "total",
    "partial",
    "as",
    "if",
    "else",
    "for",
    "in",
    "while",
    "match",
    "return",
    "select",
    "let",
    "ghost",
    "iso",
    "val",
    "ref",
    "tag",
    "consume",
    "label",
    "relabel",
    "true",
    "false",
    "where",
    "requires",
    "ensures",
    "invariant",
    "with",
    "decreases",
    "forall",
    "exists",
)
"""The 43 words the MVL lexer rejects as identifiers."""

CONSTRUCTORS: tuple[str, ...] = (
    "Some",
    "None",
    "Ok",
    "Err",
)
"""Option/Result constructors. Matched as paths, not lexer keywords."""

CONTEXTUAL: tuple[str, ...] = (
    "self",
    "old",
    "end",
    "timeout",
    "audit",
)
"""Special in ONE syntactic position; ordinary identifiers elsewhere. Do NOT highlight as bare words."""

BUILTIN_TYPES: tuple[str, ...] = (
    "Int",
    "Int8",
    "Int16",
    "Int32",
    "Int64",
    "UInt8",
    "UInt16",
    "UInt32",
    "UInt64",
    "Float",
    "Float32",
    "Float64",
    "Bool",
    "Char",
    "Byte",
    "String",
    "Unit",
    "Option",
    "Result",
    "List",
    "Array",
    "Map",
    "Set",
)
"""Reserved by convention only; the MVL lexer does not protect them."""

STDLIB_LABELS: tuple[str, ...] = (
    "Tainted",
    "Secret",
    "ConfigPath",
    "DbUrl",
    "ApiEndpoint",
    "AuditTarget",
)
"""IFC labels pre-seeded into the parser's known-label set. Ordinary identifiers. There is no `Public` label — unlabeled is public by absence."""

TOTALITY: tuple[str, ...] = (
    "total",
    "partial",
)
"""Termination modifiers."""

OWNERSHIP: tuple[str, ...] = (
    "iso",
    "val",
    "ref",
    "tag",
    "consume",
)
"""Reference capabilities plus `consume`."""

REFINEMENTS: tuple[str, ...] = (
    "where",
    "requires",
    "ensures",
    "invariant",
    "with",
    "decreases",
    "forall",
    "exists",
)
"""Contract and refinement clause keywords."""

BOOLEAN: tuple[str, ...] = (
    "true",
    "false",
)
"""Boolean literals."""

__all__ = [
    "RESERVED",
    "CONSTRUCTORS",
    "CONTEXTUAL",
    "BUILTIN_TYPES",
    "STDLIB_LABELS",
    "TOTALITY",
    "OWNERSHIP",
    "REFINEMENTS",
    "BOOLEAN",
]
