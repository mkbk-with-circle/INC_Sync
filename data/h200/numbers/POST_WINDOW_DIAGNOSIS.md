# 高post占比的计时边界问题

结论：原post记录是最早warp进入尾部barrier到最后warp返回的时间包络，包含同时仍在进行的数据工作、TMA等待、GIN flush和完成协调。它可以覆盖绝大部分通信算子时间，但不能解释为纯控制同步开销。将这一包络直接称为“后同步占比”，以及将其与pre合计作为可优化同步占比，均不适合论文正文。

## 直接证据

定位到rank-min统计中两项比例之和最高的样本：`h200_cross_tc162_small_2n8_t128_r3`，Dispatch，有效迭代索引114（从0开始）。pre最小值来自rank10，post最小值来自rank15，合计98.0778%。

同一GPU内相对于各自kernel entry的时间，单位µs：

| 记录事件 | rank10 | rank15 |
|:---|---:|---:|
| pre开始 | 0.384 | 0.320 |
| pre结束 | 19.616 | 19.680 |
| post开始 | 19.968 | 20.000 |
| 首个远端payload发起标记 | 21.664 | 21.728 |
| 最后数据warp离开发送循环标记 | 54.240 | 52.640 |
| notify/layout工作结束标记 | 97.536 | 105.120 |
| post结束 | 456.992 | 452.800 |
| kernel退出 | 457.280 | 453.088 |
| 同轮CUPTI算子span（含epilogue） | 465.889 | 460.672 |

post开始早于首个远端payload发起，说明它不可能是“全部数据完成之后才开始的纯同步阶段”。数据warp离开发送循环只表示工作已提交，异步写出可能仍未完成；不能把52.640µs解释为目标数据已可见。

源码中每个warp以`dispatch_warp_idx * num_sms + sm_idx`为token起点；没有分到token的warp可以直接跳过数据循环。所有warp随后都写post-begin，导出取其中最小值。因此空闲/提前结束的warp会把post包络起点提前，其他warp和传输引擎仍可能在做数据工作。改变跨rank的min/max无法修正rank内部这个边界。

## 分段数据的交叉证据

另一个已完成的EP8、T128 Dispatch三轮实验，选择post最短rank。相对于post开始，平均记录时刻为：TMA等待结束60.284µs，初次grid汇合结束61.679µs，GIN flush/fence结束265.171µs，首signal发起266.893µs，预期signal全部观察完成282.275µs，post结束282.446µs。

这些是同rank内的进度时间戳，进一步表明大量时间位于signal交换之前，尤其与数据完成等待有关。signal窗口约15.382µs，不能把整个282.446µs归入控制signal开销。此处来自独立的细分采样配置，不拿它替换EP16那个单迭代的未知signal窗口。

## 口径处理

- 原始post数值保留，改作“数据收尾/barrier调用包络”诊断；不截断、不归一化、不因数值高而删样本。
- 微基准正文先使用已定义的rank-min前同步观测时长及对应算子占比。
- 真实推理中原约50%的并集也含这一post包络，不能称为纯同步占比；正文重点使用前同步占比。
- 若报告控制尾部协调，应明确采用signal发起到预期signal观察完成的窗口，并继续标明其中可能包含peer就绪差和轮询。
- 已从两端保留的微基准细分记录按rank-min计算该窄窗口占同期trace-on算子的比例；结果见[SIGNAL_CONTROL_SHARE.md](SIGNAL_CONTROL_SHARE.md)，不把它直接当作真实模型step占比。
- 前一次超过100%的表还存在独立选择phase最大rank、分母不同的问题；这一统计呈现错误与此次post语义问题是两件事。低于100%只是算术检查，不足以证明指标含义正确。

源码位置：`moe_sync_experiments/third_party/DeepEP.official/deep_ep/include/deep_ep/impls/dispatch.cuh`的数据循环与post插桩；`common/comm.cuh`的TMA/grid/GIN flush/signal顺序。原trace仍在gpu3的borrow结果目录，未下载原始trace。
