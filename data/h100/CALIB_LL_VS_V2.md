# NCCL EP LL vs DeepEP V2（`calib_*`）

## 1. 数据身份与引用边界

- 本地接收日期：2026-08-17；用户提供冻结摘要的 SHA-256 为 `3fc9bd1fc5f6cf04d2c081d83446f3cf232df17a79696cdfee8ec3e33e0109f9`。
- **论文只引用 `calib_*`。** 2026-08-16 的 `llvs_*` 未授权试跑已在远端归档，不得作为论文数字。
- 本地目前只有用户提供的汇总表，没有 `calib_*` 的逐 iteration JSON、ledger、完整 run-id、机器环境留档或远端 archive。因此本文件冻结已给出的统计量，不能据此重算百分位。
- LL 使用 `REQUIRE_CUPTI=0`，但用户特别注明当前 `ep_bench` 仍可能开启 CUPTI Activity；DeepEP 使用 `TRACE_ENABLED=0`。在逐 run JSON 证明两边 instrumentation 对称之前，LL/V2 倍数需要保留这一限制。
- 本批没有 INC 硬件，不能声称 INC 实测加速。

## 2. 统计口径

| 项 | 口径 |
|:---|:---|
| 工作点 | `T/rank=8,16,32,64,128`；具体 `H/topk/E/dtype/routing` 未在本次摘要中重述，引用时需与远端 metadata 交叉确认 |
| 拓扑 | `1n8/EP8 Direct`、`2n4/EP8 Hybrid`、`2n8/EP16 Hybrid` |
| 百分位 | 每次迭代先跨 rank 取最大值，再对迭代取 p50/p95；不报告 p99 |
| EP 通信延迟 | `L_EP = Dispatch + Combine`，同一 `RUN_ID` 轮次配对 |
| speedup | `(LL Dispatch p50 + LL Combine p50) / (V2 Dispatch p50 + V2 Combine p50)` |
| 详细逐轮表 | [`calib_ll_vs_v2_rounds.csv`](calib_ll_vs_v2_rounds.csv) |

`L_EP` 是一次 MoE 层中两次 EP 通信的算术合计，不是完整模型端到端延迟，也不是 trace-on 的同步占比。

## 3. 三轮汇总（`L_EP` p50，µs）

### 3.1 2n8/EP16 Hybrid

| T/rank | LL median | LL min–max | V2 median | V2 min–max | Speedup median | Speedup min–max |
|--:|--:|--:|--:|--:|--:|--:|
| 8 | 195.0 | 138.5–291.0 | 127.3 | 127.3–127.8 | 1.53× | 1.08–2.29× |
| 16 | 320.6 | 218.2–338.3 | 133.3 | 133.2–133.4 | 2.40× | 1.64–2.54× |
| 32 | 323.7 | 265.5–334.3 | 157.9 | 157.6–157.9 | 2.05× | 1.68–2.12× |
| 64 | 496.0 | 340.6–498.6 | 200.9 | 200.8–200.9 | 2.47× | 1.70–2.48× |
| 128 | 561.3 | 469.8–593.7 | 306.8 | 306.5–306.8 | 1.83× | 1.53–1.94× |

### 3.2 2n4/EP8 Hybrid

| T/rank | LL median | LL min–max | V2 median | V2 min–max | Speedup median | Speedup min–max |
|--:|--:|--:|--:|--:|--:|--:|
| 8 | 132.1 | 112.4–141.3 | 117.2 | 117.2–117.2 | 1.13× | 0.96–1.21× |
| 16 | 137.5 | 136.6–224.4 | 123.8 | 123.4–123.8 | 1.11× | 1.11–1.81× |
| 32 | 361.8 | 180.6–364.2 | 143.1 | 142.9–143.2 | 2.53× | 1.26–2.54× |
| 64 | 432.0 | 359.1–449.2 | 182.1 | 182.0–182.1 | 2.37× | 1.97–2.47× |
| 128 | 484.2 | 417.5–578.6 | 265.0 | 265.0–265.1 | 1.83× | 1.58–2.18× |

### 3.3 1n8/EP8 Direct

| T/rank | LL median | LL min–max | V2 median | V2 min–max | Speedup median | Speedup min–max |
|--:|--:|--:|--:|--:|--:|--:|
| 8 | 63.6 | 63.0–77.9 | 28.1 | 28.0–28.1 | 2.26× | 2.24–2.78× |
| 16 | 69.1 | 68.2–69.5 | 31.8 | 31.8–31.9 | 2.16× | 2.14–2.19× |
| 32 | 77.7 | 77.4–77.8 | 39.8 | 39.8–39.9 | 1.95× | 1.95–1.95× |
| 64 | 98.6 | 96.8–98.7 | 59.2 | 59.1–59.4 | 1.67× | 1.63–1.67× |
| 128 | 146.0 | 143.2–156.9 | 95.7 | 95.6–95.7 | 1.53× | 1.50–1.64× |

## 4. 是否有用

### 4.1 直接回应“无 barrier 的 LL 足以替代 V2”

这批数据支持的不是“LL 很慢”，而是更窄且更可靠的命题：**去掉独立 barrier 并不会自动得到更快的 EP 路径，因此本文应保留 V2 的 bulk/Hybrid 数据面，再处理其 payload 前 gate。**

- `2n8/EP16 Hybrid`：五个点的三轮中位 speedup 为 1.53–2.47×，而且每一轮 V2 的 `L_EP` 都快于 LL，适合作为完整 Dispatch+Combine 的正文证据。
- `2n4/EP8 Hybrid`：`T/rank≥16` 的每轮 `L_EP` 均是 V2 更快；`T=8` 仅能说三轮中位 V2 快 1.13×，其中一轮 LL 以 112.4 µs 略快于 V2 的 117.2 µs，不能写成“所有 scale-out 轮次都更快”。
- `1n8/EP8 Direct`：五个点每轮均是 V2 更快，但它没有真正的 scale-out leg，只能证明 LL 不是普遍优越的无 barrier 替代方案，不能作为 INC 必要性的主证据。

### 4.2 对本文最直接的是 Dispatch-only 结果

本文的主机制首先处理 Dispatch。`2n4/T=8` 的三轮 LL Dispatch 为 59.9–76.7 µs，V2 稳定为 46.2 µs；`T=128` 的 LL 为 181.6–283.8 µs，V2 为 87.5–87.7 µs。即便不借助 Combine，V2 Dispatch 在这两个代表点的每轮仍更快。与旧 `core24` 相比，这组 `calib_*` 有三轮和 p95，论文应优先采用它。

### 4.3 稳定性本身也是结果，但不能过度解释

V2 在所有拓扑和工作点的三轮 p50 几乎重合；LL 尤其在跨机上有明显 run-to-run 离散，个别 p95 很大，例如 `2n8/T=128/r1` 的 `L_EP` p95 达 2935.1 µs。它说明当前 LL 对照不稳定，但在 CUPTI Activity 尚未彻底关闭和 raw 尚未归档前，不能把该长尾直接归因为 LL 协议本身。

## 5. 论文使用建议

正文可以采用两层证据：

1. **完整 EP 路径**：用 `2n8` 三轮中位表说明 V2 在五个 decode 点仍快 1.53–2.47×；
2. **目标 Dispatch 路径**：用 `2n4/T=8` 的 46.2 µs 对 59.9–76.7 µs，说明在首次 scale-out、最小消息点，V2 的 bulk Dispatch 即使保留前同步也不逊于 LL。

随后必须限定：

> These calibrated measurements motivate preserving V2's bulk/Hybrid data path instead of falling back to a no-barrier LL path. They do not measure the proposed INC mechanism.

本批 `TRACE_ENABLED=0`，没有测 `T_gate`。若同时引用约 11 µs 的 Hybrid gate，必须明确它来自另一组 trace-on 数据，不能写成 `calib_*` 自身的分解结果，也不能从 V2 trace-off 总时延中直接相减。

## 6. 尚缺的归档项

正式冻结论文数字前仍应取回：

- `calib_*` 的 ledger、逐轮 run-id 和逐 iteration JSON；
- LL JSON 中 CUPTI Activity 是否实际启用的字段；
- 两端完整环境 metadata，以及与旧数据相同的 `H/topk/E/dtype/routing/NIC` 证明；
- `L_EP p95` 是逐 iteration 配对后取 p95，还是两个独立 p95 相加的生成逻辑。

在这些工件到齐前，当前表足以支持方向性论证和论文草稿，但不适合重新计算百分位或把 LL 长尾包装成新的系统结论。
