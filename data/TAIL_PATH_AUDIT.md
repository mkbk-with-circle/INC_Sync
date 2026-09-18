# Tail synchronization audit — 2026-09-05, Direct-focused revision

## Current conclusion and scope

**Cross-node DeepEP V2 Direct Dispatch and Combine are the primary two-sided coordination scenario.** Both finish their data-transfer loops and enter a separate `gpu_barrier` that waits for sender-side progress/local joins and exchanges signals across the World team. Hybrid Dispatch is the secondary pre-overlap scenario. NCCL EP HT/LL delimit the background and non-target cases.

The earlier revision demanded “receiver first observes every inbound DATA, then originates a new exchange.” That criterion was too narrow to identify the sender-completion-based tail coordination actually present in Direct. It has been replaced by two separate questions:

1. Does the implementation have a sender completion/join stage followed by an independently initiated cross-rank completion exchange? **Confirmed for Direct.**
2. How far does signal-based successor release lag required input visibility? **Not measured for cross-node Direct; a fixed half RTT does not follow from the stage's existence.**

No new GPU experiment was run. The code establishes the scenario; the latency model establishes what to measure.

## Concrete roles

| Path | Actual tail order | Role |
|---|---|---|
| Cross-node Direct Dispatch/Combine | Data-transfer loop; TMA/local join; GIN QP flush and join; World-team signal/wait | Primary two-sided scenario; preserve source ownership and local bypass completion. |
| Hybrid Dispatch | Finish remote forwarding; TMA/local join; SU completion barrier | Secondary pre-overlap scenario; no second SO barrier. |
| Hybrid Combine | Last RDMA; per-channel flush; SO tails; inbound-tail wait | Related channel-completion path, not the primary two-sided case. |
| NCCL EP HT Dispatch | Data-context chunk signals; tail SU completion and next-round guard publication | Metadata-path comparison; guard is not a current-operation receive-completion exchange. |
| NCCL EP LL Dispatch | Local PUT issuance wait; per-expert-channel count signal | Non-target for the primary design. |

## Why the flush contract does not exclude Direct

GIN's API promises source-buffer reuse after flush and does not promise remote GPU visibility. The inspected GDAKI backend nevertheless reads the send queue's reserved index and waits for completion-queue progress before returning. DeepEP's local join and later signal publication are therefore real control steps after this sender-progress wait. This supports studying their replacement on the target-notification path without asserting that flush equals remote arrival. Source-buffer completion remains necessary for safe reuse even when the target receives DONE earlier.

## Fixed-source anchors

The following line numbers refer to the upstream base commits, checked using `git show`, not the instrumented working copies.

- [DeepEP Hybrid Dispatch, lines 661–668](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaac82068020353dce2c302e38153c0bfaa/deep_ep/include/deep_ep/impls/hybrid_dispatch.cuh#L661-L668): explicitly disables SO at the final barrier because forwarders have consumed the SO tokens.
- [DeepEP Hybrid Combine, lines 574–623](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaac82068020353dce2c302e38153c0bfaa/deep_ep/include/deep_ep/impls/hybrid_combine.cuh#L574-L623): final RDMA, flush at 590, remote tail publication at 593–595, then inbound tail wait at 599 onward.
- [DeepEP common barrier, lines 143–164](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaac82068020353dce2c302e38153c0bfaa/deep_ep/include/deep_ep/common/comm.cuh#L143-L164): sender QP flush, system fence for the World path, local join, then GIN signals.
- [NCCL LL, lines 825–850](https://github.com/NVIDIA/nccl/blob/7b83616df3ae082a1f32bb74c27458bfe8153a13/contrib/nccl_ep/device/ll_ep.cuh#L825-L850): waits for local sends to be issued before sending counts. The zero-byte PUT/SignalAdd implementation is at lines 394–431.
- [NCCL HT, lines 1554–1576](https://github.com/NVIDIA/nccl/blob/7b83616df3ae082a1f32bb74c27458bfe8153a13/contrib/nccl_ep/device/hybrid_ep.cuh#L1554-L1576): chunk signal on the data communication context, then final sender flush.
- [NCCL HT guard, lines 3803–3831](https://github.com/NVIDIA/nccl/blob/7b83616df3ae082a1f32bb74c27458bfe8153a13/contrib/nccl_ep/device/hybrid_ep.cuh#L3803-L3831): explicit cross-round WAR guard. The wait is at the Dispatch head, lines 3915–3924; the publication is at the tail, lines 4085–4099, alongside local completion at 4070–4082.
- [NCCL GIN header, lines 321–325](https://github.com/NVIDIA/nccl/blob/7b83616df3ae082a1f32bb74c27458bfe8153a13/src/include/nccl_device/gin.h#L321-L325): flush guarantees source-buffer reuse, not settling in remote memory. [Online API documentation](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/api/device_gin.html) confirms this distinction (checked September 2026).

- [Direct Dispatch, lines 397–403](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaac82068020353dce2c302e38153c0bfaa/deep_ep/include/deep_ep/impls/dispatch.cuh#L397-L403): standalone tail barrier before copy epilogue.
- [Direct Combine, lines 239–242](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaac82068020353dce2c302e38153c0bfaa/deep_ep/include/deep_ep/impls/combine.cuh#L239-L242): standalone final barrier.
- [GDAKI flush/wait, lines 308–362](https://github.com/NVIDIA/nccl/blob/7b83616df3ae082a1f32bb74c27458bfe8153a13/src/include/nccl_device/gin/gdaki/gin_gdaki.h#L308-L362): send-queue index snapshot and CQ wait. The flush dispatcher at lines 648–677 invokes this per peer.
- [DOCA wait, lines 901–915](https://github.com/NVIDIA/nccl/blob/7b83616df3ae082a1f32bb74c27458bfe8153a13/src/transport/net_ib/gdaki/doca-gpunetio/include/device/doca_gpunetio_dev_verbs_onesided.cuh#L901-L915): waits on the send completion queue for the selected ticket.

## Modeling and evidence boundary

Let c_j be sender completion/join time, w_j,d subsequent signal initiation/propagation, and z_d the completion of the required tail-signal join. Let tau_d be required input visibility. The exposed tail wait is max(0,z_d−tau_d). An INC tail-only arm with unchanged data arrival saves that gap minus its DONE lag. The ideal half-RTT figure corresponds to a gap of approximately one-way propagation; it is not a timing trace of Direct.

Current two-node measurements are Hybrid; existing single-node Direct data is a scale-up reference. Neither supplies the missing cross-node Direct c_j, z_d and tau_d. Record them in a fixed same-topology Direct experiment before assigning an empirical tail speedup.

## Figure and readiness corrections

The pictured NCCL HT tail is “机内写入完成汇合；向同 rail peer 发布跨轮 buffer guard（下一轮开头等待）”, not a generic receive-then-all-to-all.

For readiness, retain h_i=max_j(r_j+u_j,i) and g_i=max(r_i,h_i)+v_i, with h_i=-infinity for an empty remote-peer set. INC upload starts at r_i+delta_i under admitted capacity, while network delivery waits for all required READY and destination epoch/layout conditions.
