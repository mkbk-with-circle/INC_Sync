# 跨机前后同步经验模型（min phase duration）

Two-node H200 Direct, GDAKI3/TC162, H7168/topk8/E256/BF16, default resource settings. T8–128 only; ranks are categorical, not a universal rank-scaling formula.

前同步 a；后同步 a+bT。时间单位µs，T为token/rank。每个卡数单独拟合，不外推任意rank或节点数。

| EP卡数 | 算子 | 区间 | a | b | T96预测 | T96实测 | 相对误差 |
|---:|:---|:---|---:|---:|---:|---:|---:|
| 4 | dispatch | pre | 11.6380 | 0.00000 | 11.638 | 11.696 | 0.50% |
| 4 | dispatch | post | 40.8674 | 0.54640 | 93.322 | 91.764 | 1.70% |
| 4 | combine | pre | 11.5363 | 0.00000 | 11.536 | 11.541 | 0.04% |
| 4 | combine | post | 33.3652 | 0.61281 | 92.195 | 91.966 | 0.25% |
| 8 | dispatch | pre | 15.0117 | 0.00000 | 15.012 | 14.869 | 0.96% |
| 8 | dispatch | post | 36.9958 | 1.90049 | 219.443 | 223.554 | 1.84% |
| 8 | combine | pre | 14.9885 | 0.00000 | 14.988 | 14.916 | 0.48% |
| 8 | combine | post | 31.1421 | 1.84636 | 208.393 | 201.681 | 3.33% |
| 16 | dispatch | pre | 18.3928 | 0.00000 | 18.393 | 18.279 | 0.62% |
| 16 | dispatch | post | 37.7766 | 2.73126 | 299.978 | 313.755 | 4.39% |
| 16 | combine | pre | 18.3001 | 0.00000 | 18.300 | 18.227 | 0.40% |
| 16 | combine | post | 31.9676 | 2.42431 | 264.701 | 265.713 | 0.38% |

仅用T8/32/128三轮训练；T96独立验证，不因验证误差修改模型。post包括数据收尾和本地汇合，不可当作纯同步signal成本。完整来源及误差见[cross_min_fits.json](cross_min_fits.json)。
