# Evidence provenance

## Current figures and table

| Item | Numeric source | Scope |
|:---|:---|:---|
| Pre-barrier duration/share, entry-cost.tex | h200/numbers/paired_control_share.json, pre fields | EP8; T=8/32/64/128 |
| Pre-barrier constants | h200/numbers/pre_min_fits_t64.json | EP4/8/16; all listed T |
| GPU-step shares, inference-share.tex | h200/numbers/e2e_prebarrier_expanded.json | Qwen3-30B-A3B; 1n8 and 2n4 C1/2/4/8/16/32/64/128/256 |
| Serving coverage, Table tab:serving-coverage | h200/numbers/e2e_prebarrier_expanded.json | Cross-node EP4/8/16 decode and EP8 prefill |
| Same-image trace check | h200/numbers/POST_STAGES.md | EP8/T8 total operator differences across three runs |

Numeric source files listed above are the maintained inputs for the current
figures. Other H100/H200 measurements and earlier figure sources remain
available as historical evidence in the repository.

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
average over ranks and three client windows on one server instance. This is a
GPU-step share, not the single-operator denominator used by entry-cost.tex.

The request-concurrency sweep reports concurrency 1/2/4/8/16/32/64/128/256
for both 1n8 and 2n4 at EP8. The 20260919 supplement adds 1n8 C2/4/8/16/32
and 2n4 C1/2/4/8/16/32/256; existing 20260912 rows provide 1n8 C1/64/128/256
and 2n4 C64/128. The 1n8 shares range from 7.61% to 14.91%; the 2n4 shares
range from 14.22% to 19.88%. C1 has one active rank, and 2n4 C8 has seven
active ranks in the sampled windows. These characterize the recorded software
baseline.

The expanded cross-node summary reports same-rank pre-barrier/GPU-step shares.
At 16 tokens/rank, EP4/8/16 decode shares are 14.75%, 15.19%, and 15.04%.
EP8 prefill shares are 2.64% at T512 and 3.13% at T2048. Decode samples one
active step per rank and window; prefill samples its single active step.

## Mechanism figures and model

The prebarrier-overview and prebarrier-timing figures are protocol schematics,
not measured traces. Both have native draw.io, SVG, and PDF sources.
The reference splits READY into local issue time, one-way traversal L, and
endpoint observation. INC retains local issue time and overlaps upload with
the readiness wait. Its reference saving is L + T_exit - T_extra;
T_extra includes retained readiness processing and additional buffering or
forwarding delays. The data-transfer and post-barrier work are held equal
in the reference. L is half the network RTT only for symmetric paths.

## Local revision history

The pre-barrier revision starts from checkpoint `47facf6` on
`codex/pre-barrier-focus`. Historical numeric files were not deleted or refitted.
