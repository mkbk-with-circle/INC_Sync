# EP8 完成 signal 窗口：补充探针

H200 2n4/EP8 Direct, T16/T32/T96, same image and configuration as same-session T8/32/64/128 refit; three process runs and 200 active iterations per T.

| T/rank | Dispatch signal (µs) | Combine signal (µs) |
|---:|---:|---:|
| 16 | 13.98 ± 0.23 | 13.78 ± 0.18 |
| 32 | 11.15 ± 0.22 | 11.41 ± 0.55 |
| 96 | 11.12 ± 0.22 | 11.24 ± 0.92 |

| 算子 | 先前候选式 | 新 T16/T96 预测 RMSE (µs) | 最大误差 (µs) |
|:---|:---|---:|---:|
| dispatch | constant | 1.44 | 1.55 |
| dispatch | linear_log2_T | 0.69 | 0.82 |
| dispatch | linear_inverse_T | 0.97 | 1.21 |
| combine | constant | 1.29 | 1.48 |
| combine | linear_log2_T | 0.73 | 0.93 |
| combine | linear_inverse_T | 0.93 | 1.21 |

T32 是重复点，不计入上表新 T 预测误差；逐轮均值、各点预测值和来源 SHA 见 [signal_probe_20260914.json](signal_probe_20260914.json)。
