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

.PHONY: all validate tex coq thy check-coq check-tex clean help

all: validate tex coq thy

help:
	@echo "MVL semantics build targets:"
	@echo "  make validate   syntax-check the Ott source"
	@echo "  make tex        generate LaTeX at $(GEN)/mvl.tex"
	@echo "  make coq        generate Coq at $(GEN)/mvl.v"
	@echo "  make thy        generate Isabelle at $(GEN)/mvl.thy"
	@echo "  make check-coq  additionally: coqc on generated Coq"
	@echo "  make check-tex  additionally: pdflatex on generated LaTeX"
	@echo "  make clean      remove $(GEN)/mvl.*"

## Syntax-only check — the fastest validation.  Ott parses the source
## and reports any grammar or rule inconsistencies without writing files.
validate: $(SRC)
	@command -v $(OTT) >/dev/null || { echo "error: 'ott' not on PATH — see semantics/README.md"; exit 1; }
	$(OTT) -i $(SRC) -o /dev/null

$(GEN):
	@mkdir -p $(GEN)

tex: $(GEN)/mvl.tex
$(GEN)/mvl.tex: $(SRC) | $(GEN)
	$(OTT) -i $(SRC) -o $@

coq: $(GEN)/mvl.v
$(GEN)/mvl.v: $(SRC) | $(GEN)
	$(OTT) -i $(SRC) -o $@

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

clean:
	rm -f $(GEN)/mvl.tex $(GEN)/mvl.v $(GEN)/mvl.thy
	rm -f $(GEN)/*.aux $(GEN)/*.log $(GEN)/*.pdf $(GEN)/*.vo $(GEN)/*.glob $(GEN)/*.vok $(GEN)/*.vos
