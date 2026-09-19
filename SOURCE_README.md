# Manuscript source

**Overlapping MoE Pre-Barriers with Data Transfer Using In-Network Computing**

Build with PDFLaTeX and BibTeX using `make check`. The output is `build/main.pdf`.
Overleaf uses the root `main.tex` with pdfLaTeX. The Git repository also provides
`manuscript.pdf` as a versioned review copy.

The seven sections cover Introduction, Background and Motivation, Design,
Latency Analysis, Evaluation, Related Work, and Conclusion.

The two mechanism figures use the supplied `figures/prebarrier-overview.pdf`
and `figures/prebarrier-timing.pdf`, with matching native draw.io and SVG sources.
The measurement plots use PGFPlots. A normal build needs no external figure export.

Evaluation reports H200 Direct pre-barrier durations, operator shares, EP-size
comparisons, and pre-barrier shares in Qwen3 inference. Numeric sources and
aggregation rules are recorded in `data/PROVENANCE.md`.

`make archive` packages the LaTeX sources, figures, and generated bibliography.
Author identities and affiliations are to be supplied before release.
