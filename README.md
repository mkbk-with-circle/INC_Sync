# INC-Sync

本文仓库包含论文 **Overlapping MoE Synchronization with Data Transfer through
In-Network Coordination** 的 LaTeX 源码、outline、论文使用的图，以及经过整理和审查的
基线数据。

仓库有意不包含实验运行脚本、Dockerfile、第三方源码、原始 trace、临时文件和历史 build
产物；这里的数据均为正文所需的紧凑汇总、配置说明和来源校验信息。

## 本地编译

安装完整的 TeX Live 或 MacTeX，确保包含 `latexmk`、PDFLaTeX、BibTeX 和 ACM 的
`acmart` 宏包，然后执行：

```bash
git clone https://github.com/mkbk-with-circle/INC_Sync.git
cd INC_Sync
make
make check
```

输出 PDF 位于 `build/main.pdf`。`make check` 会检查引用、明显排版溢出、12 页技术正文限制；
若安装了 Poppler，还会检查页面尺寸和字体嵌入。

## 在 Overleaf 使用

直接从 GitHub 导入本仓库，主文件选择 `main.tex`，编译器选择 **pdfLaTeX**。编译不需要
shell escape、额外脚本或在线下载数据。

当前 `main.tex` 是作者可见的 arXiv 版本：

```latex
\documentclass[sigplan,twocolumn]{acmart}
```

准备 EuroSys 双盲投稿时，改为：

```latex
\documentclass[sigplan,twocolumn,review,anonymous]{acmart}
\acmSubmissionID{<PAPER_ID>}
```

EuroSys 允许公开预印本；但双盲投稿版本需要使用与公开版本显著不同的标题和系统名。

## 目录说明

正文按七章组织：引言、背景与动机、设计、时延分析、实验评估、相关工作、结论。三个
eval 图分别报告前同步开销、完成 signal 窗口和真实推理中的前同步占比；解析敏感性图
放在时延分析章。旧宽 post 拟合不再进入正文。

| 路径 | 内容 |
|:---|:---|
| `main.tex`、`sections/`、`figures/` | 可直接编译的论文正文与图形源码 |
| `references.bib` | 参考文献 |
| `data/PROVENANCE.md` | 文中数值的来源和可解释边界 |
| `data/h100/` | 用于背景和审计的 H100 汇总基线 |
| `data/h200/numbers/` | 论文使用的 H200 表格、配置、不确定性与来源 SHA |
| `outline/` | 当前 Markdown/PDF outline，以及可编辑和渲染后的图 |
| `SOURCE_README.md` | arXiv 源码与编译细节 |

章节源文件依次为 `sections/01-introduction.tex`、`02-background.tex`、`03-design.tex`、
`04-analysis.tex`、`05-evaluation.tex`、`06-related.tex` 和 `07-conclusion.tex`。

## 结论边界

本文测量的是现有 DeepEP V2 基线中的同步成本与阶段边界，并据此提出 INC 的时序重叠设计。
当前没有 INC 硬件原型的 A/B 测量，因此论文不声称已经观测到 INC 加速比。
