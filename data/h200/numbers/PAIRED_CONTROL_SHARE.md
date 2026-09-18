# 同一case的前同步与完成signal占比

H200 2n4/EP8 DeepEP V2 Direct, H7168/topk8/E256/BF16, TC162/GDAKI3, T=[8, 32, 64, 128]. Same post-stage ABI instrumented image and exact same three runs for pre and signal at each T; 200 active iterations per run. T8/128 and intermediate T points were acquired in separate sessions.

| T/rank | 算子 | 前同步占算子 | 完成signal窗口占算子 |
|---:|:---|---:|---:|
| 8 | dispatch | (20.57 ± 0.06)%（15.09 ± 0.06 µs） | (19.33 ± 0.19)%（14.26 ± 0.16 µs） |
| 8 | combine | (19.84 ± 0.13)%（15.15 ± 0.03 µs） | (17.66 ± 0.57)%（13.49 ± 0.35 µs） |
| 32 | dispatch | (12.25 ± 0.17)%（15.35 ± 0.46 µs） | (9.50 ± 0.40)%（11.61 ± 0.30 µs） |
| 32 | combine | (12.26 ± 0.26)%（15.04 ± 0.22 µs） | (9.38 ± 0.50)%（11.32 ± 0.46 µs） |
| 64 | dispatch | (8.29 ± 0.51)%（14.90 ± 0.10 µs） | (6.31 ± 0.84)%（11.19 ± 0.84 µs） |
| 64 | combine | (8.20 ± 0.16)%（14.82 ± 0.13 µs） | (6.45 ± 0.16)%（11.57 ± 0.23 µs） |
| 128 | dispatch | (4.88 ± 0.04)%（15.05 ± 0.21 µs） | (3.79 ± 0.10)%（11.63 ± 0.38 µs） |
| 128 | combine | (5.05 ± 0.19)%（14.95 ± 0.23 µs） | (3.95 ± 0.35)%（11.61 ± 0.70 µs） |

每个T的前同步与signal数据来自同一组微基准运行和迭代，但各自独立选择时长最短rank，故百分比不能相加为单条rank时间预算。T8/128和T32/64分两次采集；T64 Dispatch signal的轮间波动较大，不据此声称绝对时长严格随T变化。signal窗口含GPU端点发起、轮询及可能的peer就绪等待。该配置与真实Qwen推理的H/E不同，不报告E2E后同步占比。
同一插桩镜像的on/off扰动见[POST_STAGES.md](POST_STAGES.md)；完整逐轮数值与来源SHA见[paired_control_share.json](paired_control_share.json)。
