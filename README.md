# INC 前同步论文

**Overlapping MoE Pre-Barriers with Data Transfer Using In-Network Computing**

本地就绪的 rank 提前上传，INC 同时汇总 READY，并在目标 buffer 可写后转发。

| 章 | 内容 |
|:---|:---|
| 1 Introduction | 问题、测量观察、提前上传思想 |
| 2 Background and Motivation | EP 通信、Direct pre-barrier、INC 机会 |
| 3 Design | READY、symmetric buffer、提前上传与 PFC |
| 4 Latency Analysis | 完整操作参考模型、时序重叠、错峰与回压 |
| 5 Evaluation | pre-barrier 时长与占比、EP 规模、真实推理 |
| 6 Related Work | EP 通信、INC、同步和时延分析 |
| 7 Conclusion | 主要观察与机制 |

运行 `make check`，PDF 输出在 `build/main.pdf`。依赖为 TeX Live/MacTeX、
latexmk、pdfLaTeX、BibTeX、acmart 和 PGFPlots；Poppler 用于字体和纸张检查。
Overleaf 主文件为 `main.tex`。

机制图使用 `figures/prebarrier-overview.pdf` 和 `prebarrier-timing.pdf`，
同目录提供 draw.io/SVG 源文件。实测图由 `entry-cost.tex` 和
`inference-share.tex` 编译。来源见 [PROVENANCE.md](data/PROVENANCE.md)。

本仓库当前本地修订分支为 `codex/pre-barrier-focus`。
修改前检查点为 `47facf6`，保留源文件和 PDF；本轮修订不推送远程。
