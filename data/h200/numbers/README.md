# H200 实验数值汇总

更新：2026-09-13。本目录仅保存数值、配置及来源校验信息，不保存原始trace、模型或完整归档。

**计时口径更正：[post包络诊断](POST_WINDOW_DIAGNOSIS.md)。** 原post会从早到warp进入barrier开始，可能早于首个payload发起，覆盖数据工作与完成等待。此前把它和pre合计称为同步占比的表述已撤回；数学上小于100%并不能证明它是纯同步开销。正文现在采用[rank-min前同步数据](MIN_STATISTICS.md)，post与原E2E约50%的并集只保留作含数据完成等待的区间诊断。旧独立phase-max占比表不再用于正文。

前同步与完成 signal **窄窗口**已在跨机 EP8 的 T8/32/64/128 四档分别按同一运行、同一迭代配对统计，优先见[同一 case 前后窗口](PAIRED_CONTROL_SHARE.md)。T32/64 为后续同配置补测，不与 T8/128 混称同一采集时段。该比例不能代入真实 Qwen step；本次端到端记录没有窄窗口的逐层标记。早期仅统计 signal 的版本见[后同步完成协调窗口](SIGNAL_CONTROL_SHARE.md)。

**优先阅读：[关键数据与实验配置总览](KEY_DATA_AND_CONFIG.md)**。该文件集中列出关键数值、各组配置、公式、误差与使用边界；结构化配置见[EXPERIMENT_CONFIG.json](EXPERIMENT_CONFIG.json)。

| 表格 | 内容 | 当前覆盖 |
|:---|:---|:---|
| [单机数值](SINGLE_NODE.md) | Dispatch/Combine总时延、前同步、后同步 | 2/4/8卡，T8–8192共11档，每点3轮 |
| [跨机数值](CROSS_NODE.md) | TC162下相同指标；诊断数据单列 | 4/8/16卡，T8/32/128训练及T96独立验证均齐 |
| [跨机拟合](CROSS_FITS.md) | 前同步常数、后同步小batch线性式 | 固定模型，T96验证最大相对误差4.39%；不外推任意rank |
| [前同步全点拟合](PRE_MIN_FITS_T64.md) | rank-min 前同步常数；EP8 纳入后补 T64，所有规模纳入 T96 | outline §2.3 使用；各档均值最大偏差 0.16 µs |
| [后同步细分](POST_STAGES.md) | 首signal前、signal交换/观察、之后 | 跨机8卡，T8/128，各3轮，独立采样扰动对照 |
| [后同步完成signal占比](SIGNAL_CONTROL_SHARE.md) | 窄 signal 窗口占同期算子，按rank-min统计 | 跨机8卡，T8/128，各3轮；不是E2E占比 |
| [同一case前后窗口](PAIRED_CONTROL_SHARE.md) | 同一运行、同一迭代的前同步及窄signal窗口，分别按rank-min统计 | 跨机8卡，T8/32/64/128，各3轮；outline §1.2使用 |
| [完成signal复测结论](SIGNAL_SYNTHESIS_20260914.md) | 同批四档复测、T16/T32/T96探针与拟合判断 | 跨机EP8，每档3轮；原始trace留远端 |
| [端到端数值](E2E.md) | 请求TPOT/TTFT与真实GPU step同步区间占比 | 单机8卡decode；跨机4/8/16卡decode与prefill，均3窗口 |
| [Outline 占比数值与口径](outline_shares.json) | 微基准同rank算子占比、单机/跨机E2E分项、post内部比例 | 与outline中的百分比表对应，保留逐轮值和来源SHA |

JSON文件保留逐轮均值、标准差、p50/p95/p99等已采统计，供后续拟合，不需要重新读取原始trace：

- [单机逐轮与汇总](single_node.json)
- [跨机逐轮与汇总](cross_node.json)
- [端到端逐轮与汇总](e2e.json)
- `sources/numeric-20260913-complete-node{0,1}.json.gz`：最新完整数值向量与远端路径/校验信息，用于复核双端合并，非原始trace；先前不完整数值快照保留但不重复计入。

## 有效性与统计口径

- 微基准：每轮200个有效迭代，逐迭代跨rank取最大持续时间；主表为三轮均值的平均值±轮间样本标准差。p95等尾部数值留在JSON，未删除慢样本。
- Outline当前§1.2占比：每个迭代分别选前同步、窄signal窗口时长**最短**的rank，以各自被选rank同期trace-on算子时间作分母，再平均。两阶段可能选择不同rank，不能相加；也不使用trace-off分母。旧`outline_shares.json`及宽post比例保留作历史诊断，不能与当前§1.2口径混用。
- 跨机数值已分别核对两端完整性、Direct标记、形状和迭代数量，再逐迭代合并；不对未校准的跨GPU绝对时间戳作差。
- 总时延来自trace-off，前/后同步来自trace-on。post仍含数据排空、本地汇合，不能全部当作纯同步或INC收益。新增细分已单列，按每个迭代post最长rank的同rank分段，保持可加性；signal区间仍含端点发起/轮询与peer就绪差，不是裸网络RTT。
- 细分T128 Combine的signal区间轮间标准差约7.77µs（均值42.29µs），不声称所有分段同样稳定；on/off负差值保留，不解释为负采样开销。单机细分冒烟的采样扰动约12%–15%，仅用于辅助定位。
- 训练EP4/T128/第3轮、验证EP4/T96/第1轮与EP16/T96/第1、2轮均采用retry1整对；原中断或受干扰样本排除，不按快慢挑选。
- TC0跨机旧数据仅作历史QoS诊断，不混入本目录TC162主表。T1024的SM默认/16对照在跨机表的诊断章节单独保留。
- 端到端GPU step占比不是HTTP请求wallclock占比，也不是INC可省比例。三次客户端窗口不等同三次独立服务重启。

## 其他已有数值

- [独立单机验证与误差](../20260912/gpu3/results/holdout-validation-all.json)
- [H3584形状对照](../20260912/gpu3/results/shape-h3584-summary.json)
- [现有单机拟合：2卡](../20260912/gpu3/results/ep2-token-model-exploratory.json)、[4卡](../20260912/gpu3/results/ep4-token-model-exploratory.json)、[8卡](../20260912/gpu3/results/ep8-token-model-exploratory.json)
- [旧QoS诊断及边界](../20260912/QOS_ANOMALY_REVIEW.md)

原始记录留在gpu2/gpu3各自`/export/home/yinjinrun.montyyin/.borrow/yuanmingyu/inc-sync-h200-20260912/results/`。已生成的完整归档也留在远端`exports/local-20260913a/`，不再下载。
