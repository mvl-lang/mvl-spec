## MVL semantics — Ott build system
##
## Requires `ott` on PATH.  Install via opam:
##   opam install ott
## or from source: https://github.com/ott-lang/ott
##
## Targets:
##   make           — validate + build all outputs (default)
##   make validate  — run Ott without emitting anything; syntax check only
##   make tex       — LaTeX output for the paper
##   make coq       — Coq definitions (for Phase 9 mechanization)
##   make thy       — Isabelle/HOL definitions
##   make check-coq — additionally run coqc on the Coq output
##   make clean     — remove generated files
##
## The generated/ directory is committed *empty* — outputs are rebuilt
## from mvl.ott on demand.  CI (.github/workflows/semantics-build.yml)
## runs this on every PR that touches semantics/.

OTT      := ott
COQC     := coqc
PDFLATEX := pdflatex
SRC      := mvl.ott
GEN      := generated

.PHONY: all validate tex coq thy check-coq check-tex check-examples clean help

all: validate tex coq thy

help:
	@echo "MVL semantics build targets:"
	@echo "  make validate         syntax-check the Ott source"
	@echo "  make tex              generate LaTeX at $(GEN)/mvl.tex"
	@echo "  make coq              generate Coq at $(GEN)/mvl.v"
	@echo "  make thy              generate Isabelle at $(GEN)/mvl.thy"
	@echo "  make check-coq        additionally: coqc on generated Coq"
	@echo "  make check-examples   additionally: coqc on tests/examples.v"
	@echo "  make check-tex        additionally: pdflatex on generated LaTeX"
	@echo "  make clean            remove build artifacts"

## Syntax-only check — the fastest validation.  Ott parses the source
## and reports any grammar or rule inconsistencies.  It requires a real
## output file with a recognized extension, so we write to a temp path
## and discard it.
validate: $(SRC)
	@command -v $(OTT) >/dev/null || { echo "error: 'ott' not on PATH — see semantics/README.md"; exit 1; }
	@TMPDIR=$$(mktemp -d); \
	  trap "rm -rf $$TMPDIR" EXIT; \
	  $(OTT) -i $(SRC) -o $$TMPDIR/mvl.tex

$(GEN):
	@mkdir -p $(GEN)

tex: $(GEN)/mvl.tex
$(GEN)/mvl.tex: $(SRC) | $(GEN)
	$(OTT) -i $(SRC) -o $@

coq: $(GEN)/mvl.v
$(GEN)/mvl.v: $(SRC) | $(GEN)
	## -coq_expand_list_types true removes the dependency on Ott's
	## ott_list_core.v support library, which opam does not install
	## to a standard Coq load path.  For our purposes (small proofs,
	## no repeated list schemas) the expanded form is fine.
	$(OTT) -i $(SRC) -o $@ -coq_expand_list_types true

thy: $(GEN)/mvl.thy
$(GEN)/mvl.thy: $(SRC) | $(GEN)
	$(OTT) -i $(SRC) -o $@

## Deeper validation: pipe generated outputs through their respective
## typecheckers.  Catches inconsistencies Ott alone may not detect.
check-coq: coq
	@command -v $(COQC) >/dev/null || { echo "error: 'coqc' not on PATH"; exit 1; }
	$(COQC) $(GEN)/mvl.v

check-tex: tex
	@command -v $(PDFLATEX) >/dev/null || { echo "error: 'pdflatex' not on PATH"; exit 1; }
	cd $(GEN) && $(PDFLATEX) -interaction=nonstopmode mvl.tex

## Example proofs — a growing regression suite of well-typed
## MVL programs.  Every new typing rule should ideally get at
## least one example theorem.  Detects spec bugs immediately
## when a change breaks previously-working proofs.
check-examples: coq
	@command -v $(COQC) >/dev/null || { echo "error: 'coqc' not on PATH"; exit 1; }
	cp $(GEN)/mvl.v tests/mvl.v
	cd tests && $(COQC) mvl.v && $(COQC) examples.v
	@rm -f tests/mvl.v tests/*.glob tests/*.vok tests/*.vos

clean:
	rm -f $(GEN)/mvl.tex $(GEN)/mvl.v $(GEN)/mvl.thy
	rm -f $(GEN)/*.aux $(GEN)/*.log $(GEN)/*.pdf $(GEN)/*.vo $(GEN)/*.glob $(GEN)/*.vok $(GEN)/*.vos
	rm -f tests/*.vo tests/*.glob tests/*.vok tests/*.vos tests/mvl.v
