# Evidence provenance

The manuscript now follows seven sections: Introduction, Background and Motivation,
Design, Latency Analysis, Evaluation, Related Work, and Conclusion. This revision
reorganizes existing material and uses the latest recorded summaries; it runs no new experiments.

## Values used by Evaluation

| Manuscript item | Source in this repository | Interpretation |
|:---|:---|:---|
| Pre-barrier duration and share plot, `figures/entry-cost.tex` | `h200/numbers/paired_control_share.json` | EP8, T8/32/64/128; pre only |
| Pre-barrier constants, Table `tab:entry-constants` | `h200/numbers/pre_min_fits_t64.json` | All listed T enter the estimate; no held-out claim |
| Post-barrier observations, `figures/completion-cost.tex` | `h200/numbers/signal_refit_20260914.json` and `signal_probe_20260914.json` | Main refit plus probes; T32 pools six process-run means |
| Decode GPU-step share, `figures/inference-share.tex` | `h200/numbers/outline_shares.json`, only `e2e[].pre_share_percent` | Same-rank GPU-step pairing, averaged over ranks and client windows |

The pre-barrier constants are 11.65/11.54 us (EP4), 14.96/14.94 us (EP8), and
18.36/18.28 us (EP16), for Dispatch/Combine. T96 participates in these estimates.
The later EP8/T64 batch also participates and used a different instrumentation variant
from the original cross-node fit campaign. These are descriptive per-configuration
constants, not general rank-scaling laws.

Post-barrier measurements report 13.97/13.56 us at T8, 13.98/13.78 at T16,
11.67/11.70 at T32, 11.81/11.76 at T64, 11.12/11.24 at T96, and
11.73/11.88 at T128. The two T32 batches contain six process runs in total.
Their pooled sample standard deviations are 0.94/1.43 us. No slow run was removed.
Each other point has three runs. Full values and the failed smooth-fit investigation are
retained in [SIGNAL_SYNTHESIS_20260914.md](h200/numbers/SIGNAL_SYNTHESIS_20260914.md).

The legacy `baseline-gates.csv` retains the earlier entry/signal paired snapshot.
Its signal rows are not the source of the current post-barrier plot.
Likewise, `CROSS_FITS.md`, `CROSS_MIN_FITS.md`, their JSON files, and the old
`h200_direct_sync_min_fit.pdf` remain historical material; their broad-post fits
are not used in the revised manuscript.

## Measurement conventions

Microbenchmarks use H200 cross-node Direct, H7168/topk8/E256/BF16,
balanced uniform routing, GDAKI3/TC162, and 200 active iterations per process run.
Phase shares use trace-on numerator and denominator from the selected rank and iteration.
Total operator timing uses trace-off. The two modes are not subtracted.

For each phase and iteration, the shortest duration across ranks is selected. This
rank-minimum statistic can still include waiting. Independently selected phases
are not additive segments of one rank's timeline.
Uncertainty is the sample standard deviation across run means.

The post-barrier signal window starts after the local flush/join, before signal issuance,
and ends after the expected signals are observed. It includes endpoint processing,
polling, and possible peer-readiness waiting. The broad post envelope can begin while
other warps are still transferring; it is not a pure synchronization measurement.

Serving uses Qwen3-30B-A3B BF16 (H2048, E128, topk8), vLLM 0.27, and Direct.
The implementation includes measurement instrumentation and the recorded expert-padding
correctness fix. GPU-step shares pair same-rank times, then average over ranks and three
client windows. These windows share a server instance and are not three server restarts.
The plotted share is not request latency; a post-barrier signal-window share was not collected per layer.

## Design and analysis figures

- `design-overview.tex`: schematic protocol participants and state; no measured time scale.
- `timing.tex`: unequal-readiness comparison first, aligned-readiness reference second.
- `analytical.tex` is a historical sensitivity plot, no longer included in the manuscript.
- The three evaluation plots contain measured baseline values and error bars.
- Swift motivates separating endpoint and network delay. The manuscript uses its own
  message-delay terms and does not reproduce Swift's packet timestamps.

The source-defined tail boundary is documented in [TAIL_PATH_AUDIT.md](TAIL_PATH_AUDIT.md).
No INC prototype, net speedup, non-regression guarantee, or direct measurement of the
destination-visible-to-release interval is claimed. Historical H100 summaries remain
available for context and are not pooled with H200 measurements.
