# LL vs DeepEP V2（core24）

## 1. 数据身份与边界

- 日期：2026-08-16。
- 机器：`node110/node111`，H100 × 8，RoCE 400G。
- 运行状态：用户提供的记录为 42/42 成功，run-id 前缀 `core24_*`。
- 目标命题：同一拓扑、消息和路由下，DeepEP V2 即使付出前置 barrier，Dispatch 仍可快于无 barrier 的 NCCL EP LL。
- 本地状态：本仓库尚未收到 `results/ledger.tsv`、`results/CORE24.md` 和 `results/{1n8,2n4,2n8}/.../core24_*` raw。本文档是对用户提供 summary 的冻结，不是本地重新解析的结果。
- 隔离项：`llvs_*` 是未授权试跑，不进入本数据集。
- 本批没有 INC 硬件、vLLM、HT、路由倾斜或 `T≥4096`，不能导出 INC 实测加速。

## 2. 实验口径

| 项 | 取值 |
|:---|:---|
| 固定配置 | `H=7168, topk=8, E=256, BF16, balanced, uniform` |
| 主拓扑 | `2n4/EP8 Hybrid`（跨机） |
| 对照拓扑 | `2n8/EP16 Hybrid`、`1n8/EP8 Direct` |
| 总延迟 | Dispatch p50（µs）；每轮先跨 rank 取 max，再跨 iteration 取 p50 |
| speedup | `LL/V2`；两者均用 trace-off |
| `T_gate` | 仅来自 trace-on 的 `pre_barrier`，不从 trace-off 总延迟中相减 |
| `gate_share` | trace-on 中 `T_gate / V2 Dispatch span` |
| NIC | 2n4/2n8 使用奇数口 `mlx5_1,3,…`（Leaf6）；1n8 使用偶数口 `mlx5_0,2,…`（Leaf5）；两机保持同奇偶 |

## 3. DeepEP V2 结果（可引用）

V2 trace-off/Kineto 的两轮数值几乎重合；下表在两轮均有时使用 r1。`T=32/1024` 只跑一轮。

| 拓扑 | T=8 | T=32 | T=128 | T=1024 | `T_gate` | `gate_share` T=8 / T=128 |
|:---|---:|---:|---:|---:|---:|:---|
| **2n4 / EP8 Hybrid** | **46.0** | **53.5** | **86.9** | **438** | **10.9** | **22% / 12%** |
| 2n8 / EP16 Hybrid | 48.2 | 56.4 | 92.6 | 491 | 10.8 | 21% / 11% |
| 1n8 / EP8 Direct | 15.0 | 21.0 | 52.8 | 336 | 4.5 | 25% / 8% |

稳定观察：V2 跨机 `T=8` 约为 46–48 µs，与既有 DeepEP 主序列一致。跨机 `T_gate≈11 µs`、单机 `T_gate≈4.5 µs`，且几乎不随 `T` 变化；因此它在小消息中占比高，在大消息中被 bulk payload 摊薄。

## 4. NCCL EP LL 对照

LL 的 `ep_bench` 编译进 CUPTI；`REQUIRE_CUPTI=0` 只关闭解析门禁，不去掉仪器化。跨机两轮可差数倍，所以表中保留两轮，不挑选某个单点当作正文代表值。用户提供的“保守 speedup”取较快 LL 那轮与 V2 相比。

| 拓扑 | T | LL r1 | LL r2 | V2 | 用户提供的保守 speedup |
|:---|---:|---:|---:|---:|---:|
| **2n4** | 8 | 57.1 | 222.8 | 46.0 | **1.24×** |
| 2n4 | 32 | 234.0 | — | 53.5 | 4.37×（仅一轮） |
| **2n4** | 128 | 289.8 | 249.3 | 86.9 | **2.85×** |
| 2n4 | 1024 | 1304 | — | 438 | 2.98×（仅一轮） |
| 2n8 | 8 | 222.3 | 63.8 | 48.2 | **1.32×** |
| 2n8 | 32 | 128.4 | — | 56.4 | 2.28×（仅一轮） |
| 2n8 | 128 | 429.7 | 416.4 | 92.6 | **4.49×** |
| 2n8 | 1024 | 5380 | — | 491 | 10.95×（LL 不可用） |
| 1n8 | 8 | 33.3 | 33.3 | 15.0 | **2.22×** |
| 1n8 | 32 | 37.8 | — | 21.0 | 1.80×（仅一轮） |
| 1n8 | 128 | 63.7 | 63.7 | 52.8 | **1.21×** |
| 1n8 | 1024 | 314 | — | 336 | **0.93×**（LL 略快） |

算术审计：表中已显示的一位小数相除时，2n4/`T=128` 为 `249.3/86.9=2.87×`，而用户提供的自动表为 2.85×。这可能来自未显示的原始精度；在 raw 未归档前，正文宜直接报告 86.9 与 249.3/289.8 µs，或写成约 2.9×，不必强调第二位小数。

### 4.1 跨机 LL 稳定性审计

| 拓扑 | T | LL 两轮范围 | `max/min` | V2 是否在两轮中都更快 |
|:---|---:|:---|---:|:---:|
| 2n4 | 8 | 57.1–222.8 | 3.90× | 是 |
| 2n4 | 128 | 249.3–289.8 | 1.16× | 是 |
| 2n8 | 8 | 63.8–222.3 | 3.48× | 是 |
| 2n8 | 128 | 416.4–429.7 | 1.03× | 是 |

因此当前最稳妥的结论是方向性的：**在所有有两轮的跨机 `T=8/128` case 中，V2 都快于 LL**。但 `T=8` 的 LL 倍数不稳定，不应从慢轮中挑选 4–5× 写进正文。

## 5. 这批数据是否有用

### 5.1 有用，且直接回答一个关键质疑

它能反驳“既然 LL 没有 pre-barrier，decode 直接用 LL 就足够”：

- 2n4/EP8、`T=8`：V2 为 46.0 µs，两轮 LL 为 57.1/222.8 µs；即使取最快 LL，V2 仍快 1.24×。
- 2n4/EP8、`T=128`：V2 为 86.9 µs，两轮 LL 为 249.3/289.8 µs；方向和幅度都更稳定。
- V2 并不是因为没有 gate 而获胜；它在跨机 case 中还付出约 10.9 µs 的 gate，却仍比 LL 快。这表明“去掉 barrier”不等于“获得更快的 EP 路径”。

结合代码路径，它支持本文选择 V2-style bulk path 作为需要保留的 baseline，而不是退回 LL 的逐流 PUT/signal/poll 结构。

### 5.2 它还能支持同步 floor 的定位

- 跨机 `T_gate≈11 µs`，单机约 4.5 µs，表明跨机第一跳显著放大固定同步成本。
- 2n4 V2 的 `gate_share` 从 `T=8` 的 22% 下降到 `T=128` 的 12%，符合“固定 gate 在小消息/decode 区间难以摊薄”的论点。
- V2 的两轮 trace-off 重合，因此 V2 数值可作为新的稳定 baseline。

### 5.3 不能单独证明的内容

1. **不能证明 INC 实测加速。** 本批没有 INC 硬件或严格 A/B。
2. **不能只根据总时延把 V2 的优势全部归因于 bulk pipeline。** 代码结构支持该解释，但 LL 缺少稳定的逐阶段时间戳，且跨机 LL 受 CUPTI/运行环境影响很大。
3. **不能把 `46.0−10.9≈35 µs` 写成实测 no-gate 结果。** 46.0 µs 来自 trace-off，10.9 µs 来自 trace-on；而且移除 barrier 后其他阶段的 overlap 和到达关系也可能改变。它只能是分析性直觉，不能作为 measurement。
4. **不能宣称 V2 在所有区间都快于 LL。** 1n8、`T=1024` 上 LL 为 314 µs，V2 为 336 µs，LL 略快。结论应限定为 scale-out 和 decode 的小到中等消息区间。

## 6. 建议的论文写法

### 正文可用版

> On two H100 nodes with EP8, DeepEP V2 Dispatch takes 46.0 µs at 8 tokens/rank, while two matched NCCL EP LL trials take 57.1 and 222.8 µs. At 128 tokens/rank, V2 takes 86.9 µs versus 249.3 and 289.8 µs for LL. V2 is faster in every matched scale-out trial despite paying a 10.9 µs pre-barrier, which accounts for 22% and 12% of its traced Dispatch span, respectively. Thus, replacing V2 with a no-barrier LL path is not a competitive substitute for eliminating V2's gate.

紧接着需要加一句边界：

> These measurements motivate preserving V2's bulk data path while removing its endpoint gate; they do not measure the proposed INC mechanism.

### 不建议写法

- 不写“LL 比 V2 慢 4.8×/10.9×”；这些数字来自 LL 慢轮或异常点。
- 不写“INC 可把 46 µs 降到 35 µs”。
- 不写“V2 在任意拓扑和消息大小下都快于 LL”。
- 不用单轮 `T=32/1024` 作为主论据。

## 7. 与旧 H100 数据的关系

- 该批 V2 与 [`KEY_NUMBERS.md`](KEY_NUMBERS.md) 的 DeepEP 主序列一致，是有价值的重复验证。
- 新 LL 结果不应直接替换 `KEY_NUMBERS.md` 中的冻结数字，因为跨机两轮方差过大，且当前 raw 尚未在本地归档。
- 论文写作时，可将该批作为“同配置 LL vs V2 的方向性对照”，而把 `KEY_NUMBERS.md` 继续作为完整消息曲线和拓扑趋势的写作入口。
