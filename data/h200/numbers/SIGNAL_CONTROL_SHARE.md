# 后同步完成signal窗口占比

H200 two-node EP8 DeepEP V2 Direct, H7168 topk8 E256 BF16, uniform/balanced, GDAKI3 TC162, T8/128, dedicated ABI tracing image; not full-model E2E.

选取每次迭代signal发起至全部预期signal被观察到时长最短的rank，并以该rank同轮trace-on算子时间为分母；每格200次有效迭代、三轮。百分比为逐迭代配对比例的均值再跨轮平均。

| T/rank | 算子 | signal窗口占算子 | 窗口时长 | signal占宽post包络 |
|---:|:---|---:|---:|---:|
| 8 | combine | 17.66% ± 0.57 pp | 13.49 ± 0.35 µs | 28.46% |
| 8 | dispatch | 19.33% ± 0.19 pp | 14.26 ± 0.16 µs | 27.21% |
| 128 | combine | 3.95% ± 0.35 pp | 11.61 ± 0.70 µs | 4.43% |
| 128 | dispatch | 3.79% ± 0.10 pp | 11.63 ± 0.38 µs | 4.12% |

这个窗口是后同步中的完成协调观测，不包括首signal之前的宽数据收尾包络；它仍可能等待其他rank就绪。各时长与对应算子均取自同轮trace-on。
该数据来自微基准H7168/E256，不能直接除以Qwen真实推理的GPU step时长。插桩与采样扰动见[POST_STAGES.md](POST_STAGES.md)。
逐轮值、两端审查来源与SHA见[signal_control_share.json](signal_control_share.json)。
