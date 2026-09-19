# Evidence provenance

## Current figures and table

| Item | Numeric source | Scope |
|:---|:---|:---|
| Pre-barrier duration/share, entry-cost.tex | h200/numbers/paired_control_share.json, pre fields | EP8; T=8/32/64/128 |
| Pre-barrier constants | h200/numbers/pre_min_fits_t64.json | EP4/8/16; all listed T |
| GPU-step shares, inference-share.tex | h200/numbers/outline_shares.json, e2e[].pre_share_percent | Qwen3-30B-A3B; 1n8 and 2n4 |

Numeric source files are unchanged. Other H100/H200 measurements and earlier
figure sources remain available as historical evidence in the repository.

## Microbenchmarks

H200 Direct, H7168/topk8/E256/BF16, balanced uniform routing, GDAKI3/TC162.
Each point has three process runs, each with 200 active iterations. For each
iteration, select the rank with the shortest pre-barrier and divide by the same
rank's trace-on operator time. Average within runs and then over run means.
Error bars are the sample standard deviation of run means.

Constants are 11.65/11.54 us at EP4, 14.96/14.94 us at EP8, and 18.36/18.28 us
at EP16 (Dispatch/Combine). All listed token counts participate. EP8 T64 is a
later batch with different instrumentation. The constants describe each tested configuration.

## Inference

Qwen3-30B-A3B BF16, H2048/E128/topk8, TP1/EP8, vLLM 0.27 and DeepEP V2 Direct.
The serving build includes tracing and an expert-padding correctness fix.
Each active rank contributes 48 Dispatch and 48 Combine intervals per sampled
decode step. Sum pre-barriers and divide by the same rank's GPU-step time, then
average over ranks and three client windows on one server instance.

The 1n8 shares are 9.33% and 7.94% at concurrency 64 and 128; 2n4 shares are
16.72% and 15.19%. These characterize the recorded software baseline.

## Mechanism figures and model

The prebarrier-overview and prebarrier-timing figures are protocol schematics,
not measured traces. Both have native draw.io, SVG, and PDF sources.
The reference splits READY into local issue time, one-way traversal L, and
endpoint observation. INC retains local issue time and overlaps upload with
the readiness wait. Its reference saving is L + T_observe - T_extra;
T_extra includes retained readiness processing and additional buffering or
forwarding delays. The data-transfer and post-barrier work are held equal
in the reference. L is half the network RTT only for symmetric paths.

## Local revision history

The pre-barrier revision starts from checkpoint `47facf6` on
`codex/pre-barrier-focus`. Historical numeric files were not deleted or refitted.
