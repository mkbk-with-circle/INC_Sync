# Manuscript source

**Overlapping MoE Synchronization and Data Transfer with In-Network Computing**

Compile with PDFLaTeX and BibTeX using `make`; the output is `build/main.pdf`.
`make check` additionally checks references and layout, with optional Poppler font
and paper-size checks. Overleaf should use the root `main.tex` and pdfLaTeX.

The seven section files are ordered in `main.tex`. Plots and timing diagrams use
TikZ/PGFPlots. The overview includes the supplied vector `figures/inc-overview.pdf`,
with editable `.drawio` and `.svg` sources alongside it. No external figure export
step is required to compile the paper.

Evaluation uses pre-barrier costs, post-barrier signal-window observations, and GPU-step pre-barrier
shares. Numeric sources and aggregation rules are listed in `data/PROVENANCE.md`.
The broad post envelope is excluded from synchronization fitting.

The `make archive` target packages manuscript sources and the generated `main.bbl`
for arXiv. The Git repository itself builds the bibliography from `references.bib`.
Author identities and affiliations remain to be supplied by the authors.
The baseline measurements motivate and characterize the proposed design; they do not
report measured INC acceleration.
