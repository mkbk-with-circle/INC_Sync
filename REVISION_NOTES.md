# 前同步稿修订

- 分支：`codex/pre-barrier-focus`。
- 修改前检查点：`47facf6`，包含当时本地最新章节和 `manuscript.pdf`。
- 当前稿件：标题、摘要、设计、模型、图表及 outline 统一到 READY 汇总与提前上传。
- READY 不再要求完整 count vector；路由和计数元数据按数据路径处理。
- 使用现有 pre-barrier 数据；原始数值文件未删改，无新增实验。新增
  `e2e_prebarrier_expanded.json`，从已有逐 rank GPU-step 汇总重算 serving 对照。
- 旧机制图、尾部数据和审计记录可在原目录与 Git 历史中查阅。
- 当前审阅 PDF：`manuscript.pdf`；outline：`outline/inc_moe_sync_outline.pdf`。
- 本轮只做本地提交，不推送远程。
