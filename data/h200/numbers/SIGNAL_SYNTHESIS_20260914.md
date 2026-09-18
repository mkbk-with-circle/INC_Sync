# H200 跨机 EP8 完成 signal 窗口：复测结论

配置：DeepEP V2 Direct，2n4/EP8，H=7168、topk=8、E=256、BF16，GDAKI3/TC162。使用同一专用 post-stage ABI 镜像。主复测在同一实验中覆盖 T/rank=8/32/64/128；后续探针覆盖 16/32/96。每档三次独立进程、每次 200 个有效迭代，双端所有 off/on 实验臂完成，traced 时间戳顺序审查通过。原始 trace 留远端，本地只保存压缩数值与来源校验。

| T/rank | Dispatch signal (µs) | Combine signal (µs) | 说明 |
|---:|---:|---:|:---|
| 8 | 13.97 ± 0.04 | 13.56 ± 0.24 | 主复测 |
| 16 | 13.98 ± 0.23 | 13.78 ± 0.18 | 新横坐标探针 |
| 32 | 12.20 ± 1.15 / 11.15 ± 0.22 | 11.98 ± 2.13 / 11.41 ± 0.55 | 主复测 / 再测；慢轮次均保留 |
| 64 | 11.81 ± 0.42 | 11.76 ± 0.29 | 主复测 |
| 96 | 11.12 ± 0.22 | 11.24 ± 0.92 | 新横坐标探针 |
| 128 | 11.73 ± 0.07 | 11.88 ± 0.18 | 主复测 |

数值是每轮 200 次迭代中分别选择最短 signal 时长的 rank 后，三轮均值的平均值 ± 轮间标准差。T32 两批六轮合计为 Dispatch **11.67 ± 0.94 µs**、Combine **11.70 ± 1.43 µs**。主复测第三轮的 Dispatch/Combine 为 13.51/14.44 µs，显著高于前两轮；同档再测回到约 11–11.5 µs。该轮通过了时间戳审查，未因“不好看”而删除。

同批主复测的 signal 窗口占算子比例在 T8 为 Dispatch/Combine 19.00%/17.78%，T128 为 3.79%/4.08%；比例下降主要反映算子随 T 变长，不等于 signal 的绝对时长按比例下降。T32 的占比轮间波动较大，逐轮值见来源 JSON。

**拟合判断。** 仅用主复测四档拟合的 `a+b/T` 曾给出很小的档均值残差，但在新的 T16/T96 上，Dispatch/Combine 预测 RMSE 分别为 0.97/0.93 µs；T16 单点均低估约 1.21 µs。因此不能把 `1/T` 当作已验证规律。现在更稳妥的描述是：本配置下 T≤16 约为 Dispatch/Combine 13.97/13.67 µs，T≥32 各档约为 11.58/11.64 µs（T32 两批先合并，再让各 T 等权）。这只是两个**观测区间**，不是已定位的 T=32 协议分支；尚未测 T=17–31。

**代码与可能解释。** Direct 的 [Dispatch](../../../moe_sync_experiments/third_party/DeepEP.official/deep_ep/include/deep_ep/impls/dispatch.cuh) 和 [Combine](../../../moe_sync_experiments/third_party/DeepEP.official/deep_ep/include/deep_ep/impls/combine.cuh) 都在数据循环后调用尾部 `gpu_barrier`；它先等 TMA 写入与本地 grid 汇合，再 flush GIN QP、做可见性 fence，最后由 SM0 对固定的 EP rank 集合各发一条 signal 并轮询相应 signal 槽（[comm.cuh](../../../moe_sync_experiments/third_party/DeepEP.official/deep_ep/include/deep_ep/common/comm.cuh)，第 219–279、143–185 行）。[私有插桩](../../../moe_sync_experiments/platforms/h200/repro/collect/install_h200_post_stages.py)把窄窗口定在 signal 发起前至所有预期 signal 观察完成，**不含前面的 flush**。固定 EP8 时，这段代码的 signal 数量不随 `T` 变化；较小 `T` 下额外约 2 µs 与 rank 到达/peer 就绪等待相容，但也可能涉及端点调度或瞬时网络排队。现有时间戳不能将这些因素拆开，因此这只是解释假设，不是已证实的 T=32 路径切换或传输时延公式。

完成 signal 窗口包含 GPU 端点发起/轮询及可能的 peer 就绪等待，不是纯网络 RTT，也不是 INC 保证可节省的时间。上述结论仅适用此 EP8 配置，不可外推卡数或作为论文中的通用后同步时延公式。

来源：[同批四档与候选式](SIGNAL_REFIT_20260914.md)、[T16/T32/T96 探针与新点预测误差](SIGNAL_PROBE_20260914.md)；逐轮值、来源 SHA 见相应 JSON。
