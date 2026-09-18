# Manuscript source

**Overlapping MoE Synchronization with Data Transfer through In-Network Coordination**

Compile with PDFLaTeX and BibTeX using `make`; the output is `build/main.pdf`.
`make check` additionally checks references and layout, with optional Poppler font
and paper-size checks. Overleaf should use the root `main.tex` and pdfLaTeX.

The seven section files are ordered in `main.tex`. Figures are native TikZ/PGFPlots
sources compiled with the paper. No experiment runner or external plot-generation
step is required.

Evaluation uses entry costs, narrow completion-signal observations, and GPU-step entry
shares. Numeric sources and aggregation rules are listed in `data/PROVENANCE.md`.
The broad post envelope is excluded from synchronization fitting.

The `make archive` target packages manuscript sources and the generated `main.bbl`
for arXiv. The Git repository itself builds the bibliography from `references.bib`.
Author identities and affiliations remain to be supplied by the authors.
The baseline measurements motivate and characterize the proposed design; they do not
report measured INC acceleration.
