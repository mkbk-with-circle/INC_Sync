# Overlapping MoE Synchronization with Data Transfer through In-Network Coordination

> **核心 idea**：INC 在数据上传期间汇总 READY，并在目标尾包后追加 DONE，将同步与数据传输重叠。

## 1. 当前问题：小 batch 下，两端的同步往返难以摊薄

- **前同步**：本地数据已就绪，仍需等 EP 组的 READY，才能开始发送。
- **后同步**：发送收尾、flush 和本地汇合后，端点再发起完成 signal 交换。
- **小 batch 的影响**：payload 变少，固定协调成本不会等比例下降。
- **研究对象**：存在 EP 组入口与尾部协调的 DeepEP V2 跨机 Direct Dispatch/Combine，不将这一路径的同步行为推广到所有 EP 实现。

### 1.1 场景定位

**Deepep-v2里的:跨机 Direct Dispatch / Combine**：入口 barrier，以及发送完成／本地汇合后的全 EP 尾部协调

### 1.2 已有数据：证明问题的重要性

每次迭代取前同步**耗时最短的 rank**，除以该 rank 当次的算子时长，得到前同步占比。

**H200 跨机 EP8 Direct，H=7168、topk=8、E=256、BF16、TC162/GDAKI3；T=32/64 是同配置的后续补测。误差为三轮间标准差：**


| T/rank | Dispatch 前同步 | Combine 前同步 |
| ------ | -------------- | -------------- |
| 8      | **(20.57 ± 0.06)%** | **(19.84 ± 0.13)%** |
| 32     | **(12.25 ± 0.17)%** | **(12.26 ± 0.26)%** |
| 64     | **(8.29 ± 0.51)%** | **(8.20 ± 0.16)%** |
| 128    | **(4.88 ± 0.04)%** | **(5.05 ± 0.19)%** |


先逐迭代计算占比，再对三轮均值取平均。**四档的前同步均约 15 µs，占算子的比例随 T 增大而下降。**

**真实模型中的位置。** Qwen3-30B-A3B，BF16，固定 EP8、Direct、decode 输入/输出各 128 token，比较单机与跨机：


| 拓扑     | 并发  | 实测 token/rank | D+C 前同步占 GPU step |
| ------ | --- | ------------- | ----------------- |
| 单机 1n8 | 64  | 8             | 9.33%             |
| 跨机 2n4 | 64  | 8             | 16.72%            |
| 单机 1n8 | 128 | 16            | 7.94%             |
| 跨机 2n4 | 128 | 16            | 15.19%            |


在相同 EP 规模和并发下，跨机的前同步占比约 **15%–17%**，高于单机的约 **8%–9%**。



### 2.1 借鉴 Swift：把端点与网络时延分开

![基于 Swift 重绘的端点与网络时延分解](figs_outline/swift-delay-redrawn.png)

依据 [Swift，SIGCOMM’20，Fig. 2 / §3.1–§3.3](https://doi.org/10.1145/3387514.3406591) 重新绘制，保留原时间戳和分解公式。


| 迁移到 EP | 具体内容                     |
| ------ | ------------------------ |
| 发送端    | READY／DATA 发起、flush、局部汇合 |
| fabric | 传播、序列化、排队、INC 暂存与处理      |
| 接收端    | 数据可见、signal 观察、本地消费条件    |


本文借用时延分解方法；**实测 gate 含端点成本，不能直接等同于半个网络 RTT。**

### 2.2 一般情况：各 rank 独立就绪，INC 重叠两端协调

![基线与 INC 的收益时序对照：上排一般情况，下排理想特例](figs_outline/inc-benefits-redrawn.png)


| 收益      | 基线                             | INC                                 | 省在哪里                        |
| ------- | ------------------------------ | ----------------------------------- | --------------------------- |
| **前同步** | sender 等其他 rank READY 后才上传     | 本 rank 就绪即上传；INC 暂存早到数据，READY 收齐后放行 | 其他 rank 的准备和信号传播期间，上行传输已在进行 |
| **后同步** | sender 收尾／汇合后再产生全 EP 完成 signal | INC 根据预期数量识别目标尾部，紧随最后 DATA 产生 DONE  | 目标通知不再串行等待 sender 返回完成协调路径  |


**一般到达时序。** 各 rank 可以在不同时间就绪：

- 基线上传：同时满足**自己就绪**与**所需 peer READY 到齐**。
- INC 上传：自己就绪、发出 READY，且网络暂存已获准。
- INC 放行：相关 READY 收齐，目标本轮可写，出口可服务。
- 慢 rank 与出口瓶颈仍然存在；缓存覆盖率不等于算子加速比。

**实际收益按同一关键路径核算：**

```text
净收益 = 前侧被重叠的等待 + 后侧减少的暴露等待 − 新增开销
```

**后同步信号窗口。** H200 跨机 EP8 Direct，测量从完成 signal 发起到所需 signal 全部观察；每档三轮、每轮 200 次有效迭代，T=32 合并两批共六轮。表中为绝对时长（µs，均值 ± 轮间标准差）：

| T/rank | Dispatch | Combine |
|---:|---:|---:|
| 8 | 13.97 ± 0.04 | 13.56 ± 0.24 |
| 16 | 13.98 ± 0.23 | 13.78 ± 0.18 |
| 32 | 11.67 ± 0.94 | 11.70 ± 1.43 |
| 64 | 11.81 ± 0.42 | 11.76 ± 0.29 |
| 96 | 11.12 ± 0.22 | 11.24 ± 0.92 |
| 128 | 11.73 ± 0.07 | 11.88 ± 0.18 |

T≤16 约为 14 µs，已测的 T≥32 约为 11–12 µs，但 T=32 波动较大，不能据此认定存在协议切换。窗口仍含端点轮询和 peer 就绪等待，不等于 INC 可全部消除的时间；[完整逐轮数据与代码分析](../data/h200/numbers/SIGNAL_SYNTHESIS_20260914.md)。

**同时开始是理想特例。** 若路径对称、DATA 服务能力不变，且两侧各暴露一次单向控制传播：

```text
L = RTT_fabric / 2
前侧 ≈ L，后侧 ≈ L；净收益 ≈ RTT_fabric − 新增开销
```

这个特例解释“两次半 RTT”的来源；真实 Direct 用实际时间戳判断暴露了多少。

### 2.3 数据分析：前同步随 token 数近似不变

令 `T` 为 token/rank，`P` 为 EP 卡数。固定 `P`、H/topk/E 与链路配置时，跨机 Direct 的 rank-min 前同步在小 batch 区间近似为常数。


| EP 卡数 | 拟合 T/rank | Dispatch `a` (µs) | Combine `a` (µs) | 各档均值最大偏差 (µs) |
| ----- | ----------- | ----------------- | ---------------- | -------------------- |
| 4     | 8/32/96/128 | 11.65             | 11.54            | 0.06                 |
| 8     | 8/32/64/96/128 | 14.96          | 14.94            | 0.16                 |
| 16    | 8/32/96/128 | 18.36            | 18.28            | 0.09                 |


本区间内所有可用 T 档均参与常数拟合，每档三轮；EP8 的 T=64 来自后续同配置、不同插桩批次补测。结果只说明**各固定 EP 配置下，前同步对 T 近似恒定**，不推断任意卡数的规律；
后同步暂不拟合：§2.2 的窄完成 signal 数据只覆盖 EP8，原宽 post 又包含数据传输。详见 [拟合记录](../data/h200/numbers/PRE_MIN_FITS_T64.md)与[计时边界诊断](../data/h200/numbers/POST_WINDOW_DIAGNOSIS.md)。

## 3. INC 设计

![INC 就绪汇总、数据暂存与有序尾通知流程](figs_outline/inc-coordination-flow.png)

[可编辑矢量图](figs_outline/inc-coordination-flow.svg)

- **保留状态**：本轮标识、READY 集合、目标预期数量、写出进度。
- **Dispatch**：转发 activation，可结合已有 multicast。
- **Combine**：复用 Dispatch 建立的 contributor 集合，完成网内归约后写回结果。
- **贡献边界**：同步与传输的时序重叠；multicast/reduction 的带宽机制沿用已有工作。



## 4. 场景限定条件



### 4.1 四个成立条件

1. **资源与轮次**：使用合法的本轮 staging；消费结束后才可复用，每个 DATA 必须写到本轮合法的 staging buffer。即使 INC 已经发了 DONE，buffer 也不能立即给下一轮复用，因为目标 GPU 的后继算子可能还在读取它。
2. **有序可见，即Fence**：目标观察到 DONE，必须意味着其覆盖的数据已对 GPU 可见。
3. **流量必须都经过INC**：INC 只判断受管流量；如果有其他bypass路径，那么管理复杂度会显著上升，因此场景仅限于流量均经过INC的；
  - 关于“机内”/“机外”的问题： 感觉主要是是否保序，机外一般是保序的，机内一般不保序，因此需要做Fence（需要确保后同步的Done在到达的时候，所有数据都需要传输完毕）；并且机外的同步占比一般更高一些？
4. **容量与进展**：暂存有上限，压力沿同路背压；READY 等控制消息不能被等待中的 DATA 堵死。



### 4.2 当前已有证据


| 证据                          | 支撑的结论                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------- |
| Direct 内核与 GDAKI 源码         | 前后协调阶段确实存在                                                                              |
| H200 跨机 Direct，小 batch 三轮对照 | rank-min：T=8 时前同步约占对应 rank 算子 17%–21%；各固定 EP 配置下，T=8–128 各档均值离常数拟合最多 0.16 µs                    |
| H200 Direct 尾部细分            | 原宽 post 覆盖数据工作和排空；独立 signal 发起/观察窗口在 EP8、T=8 时约占对应算子 18%–19%，T=128 时约 4%，含端点和 peer 就绪成本 |
| Qwen3-30B-A3B 跨机推理          | EP8、decode 并发 64/128 时，前同步本身占被选 GPU step 约 16.72%/15.19%；前后并集合计还包括含数据收尾的 post           |
| Swift 分解与本文模型               | 解释重叠和尾通知的收益条件                                                                           |


路径判定依据：[Direct Dispatch](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaac82068020353dce2c302e38153c0bfaa/deep_ep/include/deep_ep/impls/dispatch.cuh#L397-L403)、[Direct Combine](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaac82068020353dce2c302e38153c0bfaa/deep_ep/include/deep_ep/impls/combine.cuh#L239-L242) 与 [GIN 保序语义](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/api/device_gin.html)；完整核对见 [路径记录](arxiv/data/TAIL_PATH_AUDIT.md)。

## 5. Related Work



### 5.1 EP 通信、同步与重叠


| 工作                                                                          | 核心做法                                                                           | 与本文的关系／区别                                                                                                          |
| --------------------------------------------------------------------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| [DeepEP](https://github.com/deepseek-ai/DeepEP)                             | 为 MoE Dispatch/Combine 提供低时延、高吞吐、Direct 与 Hybrid 路径                            | 是本文主要基线与场景来源；本文不替换其数据路径，而是尝试把特定路径中暴露的 READY 和完成协调移入网络并与 DATA 重叠                                                    |
| [NCCL EP](https://arxiv.org/abs/2603.13606)                                 | LL 面向小 batch，采用直接 RDMA+NVLink mesh 和双缓冲；HT 面向大 batch，采用机内汇聚后的分层传输              | 展示两类端点数据路径；本文只在其确有暴露同步依赖时比较，不声称所有 LL/HT 路径都存在双 barrier                                                             |
| [SwiftEP](https://www.usenix.org/conference/nsdi26/presentation/li-xingyi)  | 通过 buffer fusion、TMA offload 和传输优化减少拷贝与 GPU 开销                                 | 优化 DATA 如何搬运；本文研究 DATA 何时可上传、何时可安全宣布目标完成，两者可以叠加                                                                    |
| [UEP](https://www.usenix.org/conference/osdi26/presentation/mao-ziming-uep) | 以 GPU--CPU 控制通道和 CPU proxy 提供跨硬件的 EP 通信与顺序语义                                   | 关注可移植传输及端点代理；本文把动态 READY 汇总和目标完成判定放在网络会合点                                                                          |
| [Perseus](https://arxiv.org/abs/2605.00686)                                 | 将每个 tile 的 PUT 与 completion signal 解耦，并用 NIC fence flag 保序，减少 proxy/NIC 流水线串行化 | 优化的是**已启动 RDMA 传输内部**的 PUT/fence/signal 顺序开销；不汇总跨 rank READY，也不以 INC 暂存早到 DATA 或产生逐目标 DONE                         |
| [UBEP](https://arxiv.org/abs/2607.06202)                                    | 在 CM384 上分解 BSP Dispatch 流水，以点对点信号和 Data-as-Flag 替代其中的 SyncAll 与显式 barrier     | 优化的是**EP 数据传输流水内部**的阶段同步和到达验证；它依赖预分区接收地址及 UB Fabric 的 512 B 原子 load/store，不提供本文的网内 READY 汇总、暂存放行和 fabric 侧逐目标 DONE |




### 5.2 MoE 与动态 INC 数据面


| 工作                                             | 核心做法                                                                       | 与本文的关系／区别                                                          |
| ---------------------------------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| [DySHARP](https://arxiv.org/abs/2605.05607)    | 用动态 in-switch addressing、multicast/reduction 与 token-centric fusion 加速 MoE | 提供可复用的 INC 数据面；本文不把 multicast/reduction 的带宽收益作为贡献，而关注这些动作前后的同步关键路径 |
| [MultiWrite](https://arxiv.org/abs/2605.22428) | 用 multicast 写语义消除 many-to-many 通信中的重复上行                                    | 减少 Dispatch 流量；不负责动态 READY 汇总、暂存放行或目标完成判定                          |




### 5.3 网内集合通信与同步卸载


| 工作                                                                                                                                                           | 核心做法                               | 与本文的关系／区别                                                    |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------- | ------------------------------------------------------------ |
| [SHARP](https://doi.org/10.1109/COMHPC.2016.006) / [SHARPv3](https://developer.nvidia.com/blog/advancing-performance-with-nvidia-sharp-in-network-computing) | 将 reduction、broadcast 等集合通信操作卸载到网络 | 面向已建立的集合操作；本文处理 MoE 中随路由变化的就绪集合、目标流量计划与完成条件                  |
| [SwitchML](https://www.usenix.org/conference/nsdi21/presentation/sapio)                                                                                      | 端网协同实现交换机内模型梯度聚合                   | 提供 reduction 状态管理先例；其规整 dense aggregation 不包含本文的未同步上传和逐目标尾通知 |
| [EPIC](https://arxiv.org/abs/2605.18683)                                                                                                                     | 为以太网 INC 提供可编程协议与资源抽象              | 可作为本文机制的潜在承载平台；本文贡献是 MoE 专用的事件语义和时序，而非通用 INC 架构              |
| [GPU-Initiated Networking](https://arxiv.org/abs/2511.15076)                                                                                                 | 向 GPU 提供 PUT、signal、fence 等设备侧网络原语 | 是基线路径的传输构件和保序基础；它不自行聚合跨 rank READY 或判断每个目标的动态完成条件            |




### 5.4 时延模型、观测与背压


| 工作                                                        | 核心做法                  | 与本文的关系／区别                                                 |
| --------------------------------------------------------- | --------------------- | --------------------------------------------------------- |
| [Swift](https://doi.org/10.1145/3387514.3406591)          | 以端点与 fabric 时间戳分解网络时延 | 本文借用其分解方式建立统一模型；不重新提出拥塞控制算法                               |
| [FabricPerf](https://github.com/open-neutrino/fabricperf) | 细粒度观测 GPU scale-up 通信 | 为事件与关键路径测量提供方法参考；本文还需单独测量跨机 Direct 的 READY、DATA 与 DONE 事件 |
| [IEEE 802.1Qbb PFC](https://1.ieee802.org/dcb/802-1qbb/)  | 在链路压力下暂停无损优先级流量       | 可保护暂存主路径，但不能替代容量准入、轮次隔离、控制消息进展或端到端可见性语义                   |


**本文的位置。** 尾随 DATA 的 signal、网内 multicast/reduction 和设备侧 barrier 都已有先例。本文要新增并验证的是它们在跨机 EP 同步中的组合与放置：rank 就绪后无需等待全组 release 即上传，网络以有界暂存吸收早到 DATA；会合点汇总动态预期流量，并在每个目标的最后 DATA 之后产生有序 DONE。核心基线是 DeepEP/NCCL EP 的具体路径；DySHARP 用于划清 INC 数据面边界，Perseus 与 UBEP 用于区分已有的传输内部保序和阶段同步优化。
