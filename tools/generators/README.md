# Generators

**Status:** Planned. Empty for now.

Scripts that regenerate downstream tooling artifacts from `grammar/keywords.yaml` (and eventually from `grammar/grammar.ebnf`).

## Planned scripts

```
tools/generators/
├── gen_pygments.py         keywords.yaml → tools/pygments/mvl_pygments/keywords.py
├── gen_tree_sitter.js      keywords.yaml → tools/tree-sitter/grammar.js (keyword sections)
├── gen_vscode.js           keywords.yaml → editors/vscode/syntaxes/mvl.tmLanguage.json
├── regen-all.sh            Run all generators; used by CI drift check
└── check-drift.sh          Verify no downstream artifact drifts from keywords.yaml
```

## The discipline

Grammar or keyword changes flow one direction:

```
grammar/keywords.yaml  ─┬─►  tools/pygments/          (via gen_pygments.py)
                       ├─►  tools/tree-sitter/       (via gen_tree_sitter.js)
                       └─►  editors/vscode/          (via gen_vscode.js)
```

Editing a generated file directly is a CI failure. The `check-drift.sh` script re-runs generators and diffs against committed output; any diff fails the build.

## Why not just parse the EBNF directly?

Long-term we should — a full EBNF parser feeding all tooling is the endgame. But keyword lists are the 80% case: they're what breaks first when the language evolves, and they're mechanical enough that a YAML file plus a few small generators is sufficient. Full-EBNF-driven codegen is a follow-up when the language stabilizes.
