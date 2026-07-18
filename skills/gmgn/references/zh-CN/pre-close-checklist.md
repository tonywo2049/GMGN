---
locale: zh-CN
purpose: 在不可逆关账宣告前检查实体证据、信任面、正交审查、假设、不变量与状态自洽。
upstream: [GMGN §3](../../../../GMGN.zh-CN.md)
downstream: none
status: approved
type: design
nature: normative
---

# 关账前核对单

English: [../en/pre-close-checklist.md](../en/pre-close-checklist.md)

1. **实体验证覆盖**：每条关账判据是否有真实测试、启动或 E2E 路径与原样命令？
2. **信任面归零**：Design 中每个受理点的来源、校验、失败行为、owner 和负向证据是否重放？
3. **正交对抗**：是否至少有一道不共享作者框架的 critic/reviewer/外源视角？
4. **最弱假设**：哪条假设最可能推翻结论；反例是否被测或明确留债？
5. **不变量族**：顶级不变量是否逐条有正向与负向证据，而非只测 happy path？
6. **文本与状态自洽**：Task、矩阵、ROADMAP、Decision、Handoff、版本锚是否同批刷新？

任一 blocker、非零 gate finding 或未分类规范文档都阻断关账。负责人验收后才把状态改为 `closed`。
