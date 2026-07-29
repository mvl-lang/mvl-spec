# SPDX-License-Identifier: Apache-2.0
"""Pygments lexer for MVL.

Keyword tables are imported from `keywords.py`, which is generated from
mvl-spec `grammar/grammar.ebnf` by `tools/generators/gen_pygments.py`. They are
deliberately not restated here — see ADR-0060 (mvl-lang/mvl#2050). Five earlier
artifacts hand-transcribed these lists and all five drifted.

The category distinction is load-bearing, not cosmetic:

  RESERVED     safe to match as bare words; the MVL lexer rejects them as
               identifiers, so a bare-word rule can never mis-fire
  CONTEXTUAL   `self old end timeout audit` — ordinary identifiers outside one
               syntactic position. Matched only where the grammar allows them,
               because a bare-word rule renders `let end = 5` as a keyword
  STDLIB_LABELS matched only in label position (`Tainted[T]`), since a module may
               declare its own labels and these are not reserved
"""

from __future__ import annotations

import re

from pygments.lexer import RegexLexer, bygroups, include, words
from pygments.token import (
    Comment,
    Keyword,
    Name,
    Number,
    Operator,
    Punctuation,
    String,
    Text,
)

from mvl_pygments.keywords import (
    BOOLEAN,
    BUILTIN_TYPES,
    CONSTRUCTORS,
    OWNERSHIP,
    REFINEMENTS,
    RESERVED,
    STDLIB_LABELS,
    TOTALITY,
)

__all__ = ["MvlLexer"]

# Reserved words that get a more specific token than plain Keyword. Order
# matters only for readability; the sets are disjoint by construction because
# gen_pygments.py emits them from disjoint EBNF categories.
_SPECIFIC = set(TOTALITY) | set(OWNERSHIP) | set(REFINEMENTS) | set(BOOLEAN)
_PLAIN = tuple(w for w in RESERVED if w not in _SPECIFIC)


class MvlLexer(RegexLexer):
    """Lexer for MVL (Maximum Verifiable Language) source."""

    name = "MVL"
    aliases = ["mvl"]
    filenames = ["*.mvl"]
    mimetypes = ["text/x-mvl"]
    url = "https://mvl-lang.org"
    version_added = "0.1.5"

    flags = re.MULTILINE

    tokens = {
        "root": [
            (r"\s+", Text.Whitespace),
            # Comments — /// doc before // line, or the doc form never matches.
            (r"///.*?$", Comment.Doc),
            (r"//.*?$", Comment.Single),
            # Strings, longest form first. MVL has no single-quoted strings;
            # '...' is a char literal.
            (r'r"""', String.Regex, "raw_triple"),
            (r'r"', String.Regex, "raw_single"),
            (r'"""', String.Double, "triple"),
            (r'"', String.Double, "single"),
            (r"'(?:\\.|[^\\'])'", String.Char),
            # Numbers before identifiers so 0x1f does not start as a name.
            (r"0[xX][0-9a-fA-F_]+", Number.Hex),
            (r"0[bB][01_]+", Number.Bin),
            (r"[0-9][0-9_]*\.[0-9][0-9_]*(?:[eE][+-]?[0-9]+)?", Number.Float),
            (r"[0-9][0-9_]*", Number.Integer),
            # Effect list: `! Console + Net + DB`. Needs a state — a single
            # lookahead rule tags only the first effect and drops the rest.
            # Only entered when an uppercase name follows, so `!flag` (logical
            # not) is unaffected.
            (r"!(?=\s*[A-Z])", Punctuation, "effects"),
            # IFC labels, only in label position: `Tainted[`. Not bare words —
            # they are ordinary identifiers and a module may declare more.
            (
                r"\b(%s)(?=\s*\[)" % "|".join(STDLIB_LABELS),
                Name.Decorator,
            ),
            # Contextual keywords, each only where the grammar admits it.
            # `self` and `old` appear inside refinement predicates; `old` always
            # as a call. `end` only in a session type. `timeout` only as a select
            # arm head. `audit` only as a trailing marker on relabel.
            (r"\b(old|len)(?=\s*\()", Name.Builtin),
            (r"\bself\b(?=\s*(?:[.\)\]]|[=!<>]=|[<>+\-*/%]))", Name.Builtin.Pseudo),
            (r"(?<=->)(\s*)(end)\b", bygroups(Text.Whitespace, Keyword.Type)),
            (r"^(\s*)(timeout)(?=\s*\()", bygroups(Text.Whitespace, Keyword)),
            # `audit` is a trailing marker on relabel_decl / relabel_expr only.
            # A lookahead like `audit(?=\s*;)` also matches `return audit;`, so
            # the marker is recognised inside a relabel statement instead.
            (r"\brelabel\b", Keyword, "relabel"),
            # Reserved words, by category.
            (words(TOTALITY, suffix=r"\b"), Keyword.Declaration),
            (words(OWNERSHIP, suffix=r"\b"), Keyword.Reserved),
            (words(REFINEMENTS, suffix=r"\b"), Keyword.Pseudo),
            (words(BOOLEAN, suffix=r"\b"), Keyword.Constant),
            (words(_PLAIN, suffix=r"\b"), Keyword),
            # Constructors and builtin types.
            (words(CONSTRUCTORS, suffix=r"\b"), Name.Constant),
            (words(BUILTIN_TYPES, suffix=r"\b"), Keyword.Type),
            # Declaration heads, so the name after them is highlighted as such.
            (
                r"\b(fn)(\s+)([a-zA-Z_][a-zA-Z0-9_]*)",
                bygroups(Keyword, Text.Whitespace, Name.Function),
            ),
            (
                r"\b(type|actor|effect|label)(\s+)([A-Za-z_][A-Za-z0-9_]*)",
                bygroups(Keyword, Text.Whitespace, Name.Class),
            ),
            # A capitalised identifier is a type by convention.
            (r"\b[A-Z][A-Za-z0-9_]*\b", Name.Class),
            (r"\b[a-z_][a-zA-Z0-9_]*\b", Name),
            # Operators. `->` and `=>` before `-`/`=`, `::` before `:`.
            (r"(?:->|=>|::|\?|==|!=|<=|>=|&&|\|\||<<|>>)", Operator),
            (r"[+\-*/%!<>=&|^~]", Operator),
            (r"[{}\[\]().,;:]", Punctuation),
        ],
        "effects": [
            (r"[ \t]+", Text.Whitespace),
            (r"\+", Operator),
            (r"[A-Z][A-Za-z0-9_]*", Name.Attribute),
            # Anything else ends the effect list — `{`, a newline, `where`, etc.
            (r"", Text, "#pop"),
        ],
        "relabel": [
            (r";", Punctuation, "#pop"),
            (r"\baudit\b", Keyword.Pseudo),
            include("root"),
        ],
        "single": [
            (r'[^"\\]+', String.Double),
            (r"\\.", String.Escape),
            (r'"', String.Double, "#pop"),
        ],
        "triple": [
            (r'[^"\\]+', String.Double),
            (r"\\.", String.Escape),
            (r'"""', String.Double, "#pop"),
            (r'"', String.Double),
        ],
        "raw_single": [
            (r'[^"]+', String.Regex),
            (r'"', String.Regex, "#pop"),
        ],
        "raw_triple": [
            (r'[^"]+', String.Regex),
            (r'"""', String.Regex, "#pop"),
            (r'"', String.Regex),
        ],
    }
