# H100 数据边界

## 当前本地工件

- [`KEY_NUMBERS.md`](KEY_NUMBERS.md)：当前 H100 DeepEP/NCCL EP/vLLM 数字的权威写作入口。
- [`CALIB_LL_VS_V2.md`](CALIB_LL_VS_V2.md)：当前 LL vs DeepEP V2 的优先写作入口；包含 `calib_*` 三轮、五个消息点、Dispatch+Combine 汇总及引用限制。
- [`calib_ll_vs_v2_rounds.csv`](calib_ll_vs_v2_rounds.csv)：`calib_*` 用户提供表格的逐轮机器可读冻结版，不是 raw iteration 数据。
- [`CORE24_LL_VS_V2.md`](CORE24_LL_VS_V2.md) 与 [`core24_ll_vs_v2_summary.csv`](core24_ll_vs_v2_summary.csv)：较早的 `core24_*` 快速对照，保留用于历史审计；LL/V2 论文对照优先使用 `calib_*`。
- 各入口记录当前已知的配置、run-id 前缀、统计口径和完整性边界；缺失项会明确列出，不从汇总表反推。

## 重要限制

`KEY_NUMBERS.md` 说明其数字由远端 `driver/make_numbers.py` 从 `results/analysis/*.csv` 生成，但相应的完整 raw/analysis 压缩包目前没有复制进 `nsdi-同步论文/`。

`core24_*` 与 `calib_*` 目前都只收到用户提供的冻结 summary；`calib_*` 的 ledger、逐 iteration JSON、完整 run-id 和环境 metadata 尚未复制到本地。LL 虽设置 `REQUIRE_CUPTI=0`，但当前 `ep_bench` 可能仍开启 CUPTI Activity，必须在 raw JSON 中复核后才能解除该限制。

因此：

- 写 arXiv 时可直接引用 `KEY_NUMBERS.md` 中已冻结的数字；
- LL vs V2 对照只引用 `calib_*`，不引用已经归档的 `llvs_*`；
- 如果需要重画图、改变统计口径或审核单个 iteration，必须先取回完整原始结果包；
- 不应从表格反向生成伪 raw 数据，也不应在没有 raw 的情况下生成新的 p95/p99 结论。

`h100_sync_delivery/` 是离线镜像和实验代码交付物，不是 H100 实验数据包。
