# INC-Sync

LaTeX source, outline, figures, and paper-facing baseline data for
**Overlapping MoE Synchronization with Data Transfer through In-Network
Coordination**.

This repository intentionally excludes experiment runners, Dockerfiles, third-party
source trees, raw traces, temporary files, and historical build artifacts. The included
data are the compact, audited summaries used by the manuscript.

## Compile locally

Install a full TeX Live or MacTeX distribution with `latexmk`, PDFLaTeX, BibTeX, and
the ACM `acmart` package. Then run:

```bash
git clone https://github.com/mkbk-with-circle/INC_Sync.git
cd INC_Sync
make
make check
```

The PDF is written to `build/main.pdf`. `make check` verifies citations, material
overflow, the 12-page technical-content limit, and, if Poppler is installed, PDF page
size and embedded fonts.

## Open in Overleaf

Import this GitHub repository, set `main.tex` as the main document, and select
**pdfLaTeX**. No shell escape, external scripts, or data download is required to compile.

The current `main.tex` is the author-visible arXiv version:

```latex
\documentclass[sigplan,twocolumn]{acmart}
```

For EuroSys double-blind submission, switch it to:

```latex
\documentclass[sigplan,twocolumn,review,anonymous]{acmart}
\acmSubmissionID{<PAPER_ID>}
```

EuroSys permits public preprints, but its submission rules require the anonymized
submission to use a substantially different title and system name from the public draft.

## Repository map

| Path | Purpose |
|:---|:---|
| `main.tex`, `sections/`, `figures/` | Compilable manuscript source |
| `references.bib` | Bibliography |
| `data/PROVENANCE.md` | Meaning and provenance of each manuscript value |
| `data/h100/` | Compact H100 baseline summaries used for context/audit |
| `data/h200/numbers/` | Compact H200 tables, configuration, uncertainty, and SHA-pinned sources |
| `outline/` | Current outline in Markdown/PDF plus editable and rendered figures |
| `SOURCE_README.md` | arXiv-source and compilation details |

## Scope boundary

The measurements establish baseline synchronization costs and stage boundaries; they do
not evaluate an INC hardware prototype. The manuscript therefore does not claim an
observed INC speedup.

