.PHONY: all pdf check archive clean
all: pdf

pdf:
	latexmk -silent -pdf -outdir=build -interaction=nonstopmode -halt-on-error -file-line-error main.tex

check: pdf
	python3 tools/check_build.py

# The archive contains a ready-to-use .bbl so arXiv need not invoke BibTeX.
archive: check
	@set -eu; \
	stage=$$(mktemp -d build/arxiv-source.XXXXXX); \
	cp main.tex macros.tex references.bib Makefile SOURCE_README.md build/main.bbl "$$stage/"; \
	cp SOURCE_README.md "$$stage/README.md"; \
	cp -R sections figures tools "$$stage/"; \
	mkdir -p "$$stage/data"; \
	cp data/baseline-gates.csv "$$stage/data/"; \
	COPYFILE_DISABLE=1 tar -czf build/inc-moe-arxiv-source.tar.gz -C "$$stage" .

clean:
	latexmk -c -outdir=build main.tex
