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

1. **目标边界**：是否记录 `target_milestone_id`、其 Goal/Requirement/Design/Task 锚、
   自有任务卡、closing anchor 与目标范围 finding 集？跨 Milestone 引用是否错误扩张了
   执行或关账范围？
2. **实体验证覆盖**：目标 Milestone 的每条关账判据是否有真实测试、启动或 E2E 路径与
   原样命令？
3. **信任面归零**：目标 Design 中每个受理点的来源、校验、失败行为、owner 和负向证据
   是否重放？
4. **正交对抗**：是否至少有一道不共享作者框架的 critic/reviewer/外源视角？
5. **最弱假设**：哪条假设最可能推翻结论；反例是否被测或明确留债？
6. **不变量族**：目标范围内的不变量是否逐条有正向与负向证据，而非只测 happy path？
7. **文本与状态自洽**：目标 Task、矩阵、ROADMAP 行、Decision、Handoff、版本锚是否同批刷新？
8. **集成收敛**：目标 Milestone 的集成队列条目是否为空，是否不存在它拥有的 active、
   `rebase-required`、`integration-conflict` lane 或未释放锁，其所有任务卡是否关在同一个
   `shared_baseline_anchor`？
9. **下游留债**：仅属下游的问题是否已写成非阻塞 TODO/Handoff，并包含接收 Milestone/owner、
   触发条件、可能影响与必要时的默认假设？
10. **结构测量边界**：DocStar finding 是否按目标或 closing candidate 定界；无关下游和既存
    外部 finding 是否只登记为债务？

目标范围内未解决的 blocker、gate finding，或 closing candidate 新增的结构污染会阻断关账；
仅属下游的 TODO 与无关既存 finding 不阻断。负责人验收后才把目标状态改为 `closed`。
