# SPDX-License-Identifier: Apache-2.0
"""Tests for the MVL Pygments lexer.

The contextual-keyword tests are the point of this file. Five earlier artifacts
highlighted `end`, `timeout` or `audit` as unconditional keywords, so `let end = 5`
rendered `end` as a language construct. These tests fail if that regresses.
"""

from __future__ import annotations

import pathlib

import pytest
from pygments.lexers import get_lexer_by_name
from pygments.token import Comment, Keyword, Name, Number, String

from mvl_pygments import keywords
from mvl_pygments.lexer import MvlLexer


@pytest.fixture(scope="module")
def lexer() -> MvlLexer:
    return MvlLexer()


def tokens_for(lexer: MvlLexer, src: str) -> list[tuple[object, str]]:
    return [(t, v) for t, v in lexer.get_tokens(src) if v.strip()]


def token_of(lexer: MvlLexer, src: str, word: str) -> list[object]:
    return [t for t, v in tokens_for(lexer, src) if v == word]


# ── Registration ──────────────────────────────────────────────────────────────


def test_registered_under_the_mvl_alias():
    """`pygmentize -l mvl` and ```mvl fences depend on this entry point."""
    assert get_lexer_by_name("mvl").name == "MVL"


def test_claims_the_mvl_extension():
    assert "*.mvl" in MvlLexer.filenames


# ── Keyword tables come from the generated module ─────────────────────────────


def test_keyword_tables_are_generated_not_transcribed():
    """ADR-0060: the lexer must not restate the lists."""
    src = (keywords.__file__ or "")
    with open(src, encoding="utf-8") as fh:
        assert "DO NOT EDIT" in fh.read(400)


def test_package_version_matches_the_manifest():
    """check-versions.py cannot read a Python source file, so assert it here."""
    import tomllib

    import mvl_pygments

    manifest = pathlib.Path(__file__).parent.parent / "pyproject.toml"
    with open(manifest, "rb") as fh:
        declared = tomllib.load(fh)["project"]["version"]
    assert mvl_pygments.__version__ == declared


def test_reserved_count_matches_the_compiler():
    """43 is what src/mvl/parser/lexer/mod.rs reserves."""
    assert len(keywords.RESERVED) == 43


def test_no_word_is_both_reserved_and_contextual():
    assert not (set(keywords.RESERVED) & set(keywords.CONTEXTUAL))


def test_public_and_clean_are_not_labels():
    """grammar.ebnf:139-140 — unlabeled is public by absence."""
    assert "Public" not in keywords.STDLIB_LABELS
    assert "Clean" not in keywords.STDLIB_LABELS


def test_removed_constructs_absent():
    """#894 deleted declassify() and sanitize()."""
    flat = set(keywords.RESERVED) | set(keywords.CONTEXTUAL)
    assert not flat & {"declassify", "sanitize", "mut", "move"}


# ── Reserved words highlight as keywords ─────────────────────────────────────


@pytest.mark.parametrize(
    "word,src",
    [
        ("fn", "total fn f() -> Unit { }"),
        ("let", "fn f() -> Unit { let x: Int = 1; }"),
        ("total", "total fn f() -> Unit { }"),
        ("ghost", "fn f() -> Unit { ghost let w: Int = 1; }"),
        ("requires", "total fn f(n: Int) -> Int requires n > 0 { n }"),
    ],
)
def test_reserved_words_are_keywords(lexer, word, src):
    got = token_of(lexer, src, word)
    assert got, f"{word!r} produced no token"
    assert all(t in Keyword for t in got), f"{word!r} -> {got}"


# ── Contextual words are NOT keywords when used as identifiers ────────────────


@pytest.mark.parametrize("word", ["end", "timeout", "audit"])
def test_contextual_words_as_variables_are_names(lexer, word):
    """`let end = 5` must not render `end` as a keyword.

    This is the regression that shipped in three .scm files, the VS Code
    TextMate grammar and the keywords manual.
    """
    src = f"fn f() -> Int {{ let {word}: Int = 5; return {word}; }}"
    got = token_of(lexer, src, word)
    assert got, f"{word!r} produced no token"
    assert all(t in Name for t in got), f"{word!r} -> {got}"
    assert not any(t in Keyword for t in got)


def test_self_in_a_refinement_is_not_a_plain_name(lexer):
    src = "type Positive = Int where self > 0"
    got = token_of(lexer, src, "self")
    assert got and all(t is Name.Builtin.Pseudo for t in got), got


def test_self_as_a_variable_is_an_ordinary_name(lexer):
    src = "fn f() -> Int { let self: Int = 1; return self; }"
    got = token_of(lexer, src, "self")
    assert got and not any(t in Keyword for t in got), got


def test_audit_as_a_relabel_marker_differs_from_audit_the_variable(lexer):
    """Same spelling, two roles — the marker and an ordinary binding."""
    src = "relabel trust: Tainted -> _ audit;\nfn f() -> Bool { let audit: Bool = true; }"
    got = token_of(lexer, src, "audit")
    assert len(got) == 2, got
    assert Keyword.Pseudo in got, got
    assert any(t in Name for t in got), got


def test_len_and_old_are_builtins_not_keywords(lexer):
    src = 'total fn f(s: String) -> Int ensures old(s) == s { len(s) }'
    for word in ("len", "old"):
        got = token_of(lexer, src, word)
        assert got and all(t is Name.Builtin for t in got), f"{word} -> {got}"


# ── IFC labels only in label position ────────────────────────────────────────


@pytest.mark.parametrize("label", ["Tainted", "Secret", "ConfigPath", "AuditTarget"])
def test_stdlib_labels_highlight_in_label_position(lexer, label):
    src = f"fn f(x: {label}[String]) -> Unit {{ }}"
    assert Name.Decorator in token_of(lexer, src, label)


def test_a_label_name_outside_label_position_is_not_a_label(lexer):
    """`Secret` as a plain type name must not get the label token."""
    src = "fn f() -> Unit { let Secret: Int = 1; }"
    assert Name.Decorator not in token_of(lexer, src, "Secret")


# ── Lexical forms ────────────────────────────────────────────────────────────


def test_doc_comment_distinct_from_line_comment(lexer):
    toks = dict((v, t) for t, v in tokens_for(lexer, "/// doc\n// plain\n"))
    assert toks["/// doc"] is Comment.Doc
    assert toks["// plain"] is Comment.Single


@pytest.mark.parametrize(
    "src",
    ['let s: String = "hi";', 'let s: String = """multi\nline""";', 'let s: String = r"raw \\x";'],
)
def test_string_forms_lex_without_error(lexer, src):
    toks = tokens_for(lexer, f"fn f() -> Unit {{ {src} }}")
    assert any(t in String for t, _ in toks)
    assert not any("Error" in str(t) for t, _ in toks)


def test_effect_list_names_are_attributes(lexer):
    src = "total fn f() -> Unit ! Console + DB { }"
    toks = tokens_for(lexer, src)
    got = [v for t, v in toks if t is Name.Attribute]
    assert "Console" in got and "DB" in got, got


def test_numeric_forms(lexer):
    toks = dict((v, t) for t, v in tokens_for(lexer, "let a = 0xff; let b = 1_000; let c = 1.5;"))
    assert toks["0xff"] is Number.Hex
    assert toks["1_000"] is Number.Integer
    assert toks["1.5"] is Number.Float


# ── No source in the corpus produces an error token ──────────────────────────


def test_corpus_lexes_without_errors(lexer):
    """Every .mvl file under tests/corpus/ must lex cleanly."""
    from pathlib import Path

    corpus = Path(__file__).parent / "corpus"
    files = sorted(corpus.glob("*.mvl"))
    assert files, "corpus is empty — add at least one sample"
    for f in files:
        toks = tokens_for(lexer, f.read_text(encoding="utf-8"))
        bad = [(str(t), v) for t, v in toks if "Error" in str(t)]
        assert not bad, f"{f.name}: {bad[:5]}"
