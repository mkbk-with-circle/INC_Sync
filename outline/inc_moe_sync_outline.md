# Overlapping MoE Pre-Barriers with Data Transfer Using In-Network Computing

> 主线：rank 本地就绪后先上传，INC 同时收集 READY 并暂存早到数据；接收条件满足后转发，把等待其他 rank 就绪的时间用于搬运数据。

## 1. Introduction — 引言

- **问题**：小 batch 缩短 token 传输，但 pre-barrier 仍需等待同一组 rank，开销难以摊薄。
- **观测**：H200 跨机 EP8 Direct 的 pre-barrier 约 15 µs，小 batch 时约占算子 20%；真实跨机 decode 中约占 GPU step 的 15%–17%。
- **思想**：将“开始上传”和“允许写入目标 buffer”分开。INC 汇总 READY 的同时接收数据，就绪后转发。
- **贡献**：pre-barrier 开销测量、提前上传协议，以及完整通信操作的时延分析。

## 2. Background and Motivation — 背景与动机

### 2.1 Expert-Parallel Communication

介绍 Dispatch → expert compute → Combine。路由决定 token 的目标，计数和布局元数据决定接收后的组织方式。READY 表示本轮通信所需资源可用。

典型发送前协调方式：NCCL EP HT 先汇总路由；DeepEP V2 Direct 先执行 pre-barrier，再并行处理计数与数据；NCCL EP LL 向预留槽位写入并使用细粒度信号。

### 2.2 Pre-Barriers in DeepEP V2 Direct

Direct Dispatch/Combine 在 token 发送前等待参与 rank 就绪并完成本地同步。预分配 buffer 使地址可知，但目标 buffer 本轮是否允许覆盖仍需确认。

固定 EP8，T/rank 从 8 增至 128 时，pre-barrier 约保持 15 µs，占比从约 20% 降至约 5%。这说明小 batch 下提前上传的机会值得研究。

### 2.3 Opportunities for In-Network Computing

INC 可在转发时维护哪些 rank 已就绪，并暂存早到 token。所有相关通信经过 INC 时，可将上传与 READY 汇总并行组织。

**Key Insight**：本地数据就绪后即可上传到网络暂存区，目标写入仍等待所需就绪条件。这样 pre-barrier 的等待过程可以与部分数据传输重叠。

## 3. Design — 设计

### 3.1 Overview and Assumptions

![前同步与提前上传](figures/prebarrier-overview.png)

INC 为每轮维护 READY bitmap 和有上限的数据队列。generation 标识一次 Dispatch/Combine，epoch 区分接收 buffer 的不同轮使用。相关参与者及数据路径需纳入相同的就绪判定范围。

接收 buffer 在初始化时按 symmetric memory 分配、注册，布局和访问映射一次性建立。token 路由和标识决定目标及写入偏移，不依赖全局计数。READY 确认本地输入可用，且目标 buffer 已结束上一轮使用。

### 3.2 Early Upload and Readiness Aggregation

rank 发布 READY 后开始上传，不等其他 rank 的 READY 返回。READY 携带 rank、generation、epoch；路由随 token 传输，必要计数和元数据按原通信流程处理，不把完整 count vector 作为 READY 的前置条件。

INC 忽略重复和旧轮次消息。所需 READY 未收齐时暂存 DATA；就绪且目标可写后，按路由转发缓存和新到 token。Dispatch 接收后按 expert 整理；Combine 将 expert outputs 送回 token owner 完成合并。

### 3.3 Buffer Management and Backpressure

接收 buffer 的最后一次读取完成后才可复用，下一轮 READY 确认这一点。发送 buffer 保留到发送硬件读完。INC 在队列排空且所有 rank 进入下一轮后回收旧轮 READY 状态。

PFC 在缓存溢出前暂停 DATA，并预留 headroom 接纳暂停生效前的在途数据。READY 与必要控制元数据有独立优先级和预留资源，避免暂停 DATA 时阻塞就绪消息。

## 4. Latency Analysis — 时延分析

### 4.1 Operation Latency

建模一次完整 Dispatch/Combine，从输入本地可用到所有 rank 完成。借鉴 [Swift](https://doi.org/10.1145/3387514.3406591) 区分处理与网络时延。

参考条件：rank 同时就绪、无明显拥塞，INC 维持基线数据转发速率。L 为单向传播和固定转发时延，S 为整次通信在瓶颈速率下传输全部 payload 的时间；H 为关键路径上未重叠的处理时间，C 为后续交付确认和本地收尾。

- 基线：T_base = H_base + L + (S + L) + C。
- INC：T_INC = H_INC + (S + L) + C。

### 4.2 How Early Upload Creates Overlap

![就绪等待与上传重叠](figures/prebarrier-timing.png)

基线先完成 READY 的端点间传播，再启动数据；INC 让 READY 与后续 DATA 一起向网络节点前进，条件满足后继续转发。因此参考收益为 **L + H_base − H_INC**。只有未被额外处理和排队抵消的提前量，才会缩短操作完成时间。

### 4.3 Unequal Readiness and Backpressure

rank 到达不一致时，早到数据可在 INC 等待；真正收益取决于晚到 rank、出口排队和 PFC。完整操作以最后一个 rank 完成为准，某个目标提前收到数据不必然等于全局操作加速。

## 5. Evaluation — 实验评估

### 5.1 Experimental Setup and Methodology

- 两台 H200，各八卡；机内 NVSwitch，机间八轨 400GbE RoCE。Direct、GDAKI3、TC162。
- 微基准：H=7168、topk=8、E=256、BF16、balanced/uniform。每点三轮独立进程，每轮 200 次有效迭代。
- 每次选 pre-barrier 最短的 rank，除以同 rank 同轮 trace-on 算子时间；先逐迭代计算，再对三轮均值取平均。误差为轮间标准差。
- 推理使用同 rank 的 pre-barrier 累计时间与 GPU step 配对，再跨 rank 和三个 client 窗口平均。

### 5.2 Pre-Barrier Cost

H200 跨机 EP8 Direct：

| T/rank | Dispatch pre-barrier 占比 | Combine pre-barrier 占比 |
|---:|---:|---:|
| 8 | (20.57 ± 0.06)% | (19.84 ± 0.13)% |
| 32 | (12.25 ± 0.17)% | (12.26 ± 0.26)% |
| 64 | (8.29 ± 0.51)% | (8.20 ± 0.16)% |
| 128 | (4.88 ± 0.04)% | (5.05 ± 0.19)% |

四档绝对时长均约 15 µs；算子占比随 T 增大而下降。来源：[配对数值](../data/h200/numbers/PAIRED_CONTROL_SHARE.md)；[主图源码](../figures/entry-cost.tex)。

### 5.3 Dependence on EP Size

各固定 EP 配置的常数估计使用全部所列 token 档，每档三轮：

| EP 卡数 | T/rank | Dispatch (µs) | Combine (µs) | 各档均值最大偏差 (µs) |
|---:|:---|---:|---:|---:|
| 4 | 8/32/96/128 | 11.65 | 11.54 | 0.06 |
| 8 | 8/32/64/96/128 | 14.96 | 14.94 | 0.16 |
| 16 | 8/32/96/128 | 18.36 | 18.28 | 0.09 |

固定 EP 时，pre-barrier 对 T 近似恒定。EP4/8/16 同时改变每机卡数、目标分布和网络并发，数值体现这些配置的综合变化。EP8 T=64 来自后续不同插桩批次。来源：[拟合数值](../data/h200/numbers/PRE_MIN_FITS_T64.md)。

### 5.4 Pre-Barriers in MoE Inference

Qwen3-30B-A3B，BF16、TP1/EP8 Direct，输入/输出各 128 token；实际路由，比较单机 1n8 和跨机 2n4：

| 拓扑 | 并发 | 实测 token/rank | D+C pre-barrier 占 GPU step |
|:---|---:|---:|---:|
| 单机 1n8 | 64 | 8 | 9.33% |
| 跨机 2n4 | 64 | 8 | 16.72% |
| 单机 1n8 | 128 | 16 | 7.94% |
| 跨机 2n4 | 128 | 16 | 15.19% |

每个采样 step 含 48 次 Dispatch 与 48 次 Combine；三个 client 窗口使用同一 server 实例。占比分母为 GPU step。来源：[推理数值](../data/h200/numbers/E2E.md)、[分项](../data/h200/numbers/outline_shares.json)；[主图源码](../figures/inference-share.tex)。

## 6. Related Work — 相关工作

### 6.1 EP Communication

[DeepEP](https://github.com/deepseek-ai/DeepEP) 与 [NCCL EP](https://arxiv.org/abs/2603.13606) 提供 EP 数据路径与不同发送前协调方式。[SwiftEP](https://www.usenix.org/conference/nsdi26/presentation/li-xingyi)、[Perseus](https://arxiv.org/abs/2605.00686)、[UBEP](https://arxiv.org/abs/2607.06202) 改进数据移动和传输过程中的协调。本文用网络暂存重叠发送前的就绪等待。

### 6.2 In-Network Computation

[SHARP](https://developer.nvidia.com/blog/advancing-performance-with-nvidia-sharp-in-network-computing)、[SwitchML](https://www.usenix.org/conference/nsdi21/presentation/sapio) 展示网内归约与状态管理；[DySHARP](https://arxiv.org/abs/2605.05607)、[MultiWrite](https://arxiv.org/abs/2605.22428) 将网络处理用于 MoE 数据交换。本文利用临时状态和缓存改变 pre-barrier 与上传的先后关系。

### 6.3 Synchronization and Delay Analysis

[EPIC](https://arxiv.org/abs/2605.18683) 的 INC 协议和资源抽象、[GPU-Initiated Networking](https://arxiv.org/abs/2511.15076) 的端点原语为实现提供基础。[Swift](https://doi.org/10.1145/3387514.3406591) 提供处理/网络时延分解思路，[FabricPerf](https://github.com/open-neutrino/fabricperf) 强调明确的计时边界。

## 7. Conclusion — 结论

小 batch 下 pre-barrier 开销显著。INC 允许本地就绪的 rank 在等待期间提前上传，并在接收条件满足后转发。收益取决于暂存空间、就绪时间差和转发速率。
