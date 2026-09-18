# Manuscript source

**Overlapping MoE Synchronization with Data Transfer through In-Network Coordination**

Compile `main.tex` using PDFLaTeX and BibTeX, or run:

```sh
make
```

The PDF is written to `build/main.pdf`. The document uses the `acmart` class in its
`sigplan` two-column configuration, which is part of a standard TeX Live installation.
This package includes `main.bbl`, the section sources, editable TikZ/PGFPlots figures,
and the tabulated baseline measurements. No network access or shell escape is required.
`make check` additionally uses Python 3; Poppler enables optional PDF dimension and font
checks.

Figure 1 is a schematic timing model with no measured time scale. Figure 2 is an
analytical sensitivity plot in which the added-overhead parameter is swept independently
rather than fitted. Neither represents measured in-network hardware performance. Figure 3
plots measured baseline durations only.

This is a design and measurement study. The baselines in Section 5 are measured on
unmodified DeepEP V2, the synchronization stages are established from source, and the
latency opportunity is analytical. No in-network prototype was built or evaluated, and no
number anywhere in the paper is a speedup. `data/PROVENANCE.md` records the source of
every printed value and the measurement conventions that constrain how each may be read.
