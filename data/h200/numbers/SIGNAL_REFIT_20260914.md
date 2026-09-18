# EP8 后同步窄窗口：同批复测

H200 2n4/EP8 DeepEP V2 Direct, TC162/GDAKI3, H7168/topk8/E256/BF16. T8/32/64/128 acquired in one new campaign; 3 separate process runs per T and 200 active iterations per run.

| T/rank | Dispatch signal (µs) | Combine signal (µs) | Dispatch pre (µs) | Combine pre (µs) |
|---:|---:|---:|---:|---:|
| 8 | 13.97 ± 0.04 | 13.56 ± 0.24 | 15.18 ± 0.14 | 15.15 ± 0.10 |
| 32 | 12.20 ± 1.15 | 11.98 ± 2.13 | 15.15 ± 0.21 | 15.11 ± 0.20 |
| 64 | 11.81 ± 0.42 | 11.76 ± 0.29 | 15.15 ± 0.08 | 15.02 ± 0.05 |
| 128 | 11.73 ± 0.07 | 11.88 ± 0.18 | 15.12 ± 0.27 | 15.03 ± 0.15 |

每格为三次进程运行均值 ± 轮间标准差；每次 200 个有效迭代。同批复测消除了此前 T8/128 与 T32/64 分时段采集这一差别，但 signal 窗口仍含端点操作和 peer 就绪差。

| T/rank | Dispatch 旧→新 (µs) | Combine 旧→新 (µs) |
|---:|:---|:---|
| 8 | 14.26→13.97 (-0.29) | 13.49→13.56 (+0.07) |
| 32 | 11.61→12.20 (+0.59) | 11.32→11.98 (+0.66) |
| 64 | 11.19→11.81 (+0.62) | 11.57→11.76 (+0.19) |
| 128 | 11.63→11.73 (+0.11) | 11.61→11.88 (+0.26) |

| 算子 | 候选描述式 | 四档拟合 RMSE (µs) | 留一档预测 RMSE (µs) |
|:---|:---|---:|---:|
| dispatch | constant | 0.91 | 1.21 |
| dispatch | linear_log2_T | 0.29 | 0.84 |
| dispatch | linear_inverse_T | 0.03 | 0.09 |
| combine | constant | 0.74 | 0.98 |
| combine | linear_log2_T | 0.33 | 0.95 |
| combine | linear_inverse_T | 0.10 | 0.56 |

留一档预测只检验四个已测 T 之间的稳健性；四档不足以确立通用函数，更不能外推 EP 卡数。逐轮数值、每档占比与来源 SHA 见 [signal_refit_20260914.json](signal_refit_20260914.json)。
