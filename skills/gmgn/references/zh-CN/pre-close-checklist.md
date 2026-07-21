---
locale: zh-CN
purpose: 在不可逆关账宣告前检查实体证据、信任面、正交审查、剩余风险、不变量与状态自洽。
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
5. **剩余风险**：还有什么未解决风险可能改变关账结论；其影响、证据强度和最便宜的下一步证伪动作是什么？
   没有已知风险时是否直接写明，而非编造一条？
6. **不变量族**：目标范围内的不变量是否逐条有正向与负向证据，而非只测 happy path？
7. **文本与状态自洽**：目标 Task、矩阵、ROADMAP 行、Decision、Handoff、版本锚是否同批刷新？
   每张已执行任务卡是否链接各自已关闭的描述性执行日志，Task 是否只保留当前状态与关账证据？
   在关账共享锚上，`latest_event` 是否可解析到该日志的最终关账事件？该事件是否记录验证过的组合
   候选与前一共享锚，且证据/当前指针是否与 Task 卡一致？
8. **集成收敛**：目标 Milestone 的集成队列条目是否为空，是否不存在它拥有的 active、
   `rebase-required`、`integration-conflict` lane 或未释放锁，其所有任务卡是否关在同一个
   `shared_baseline_anchor`？
9. **下游留债**：仅属下游的问题是否已写成非阻塞 TODO/Handoff，并包含接收 Milestone/owner、
   触发条件、可能影响与必要时的默认假设？仍在目标范围内的 AC 是否被错误标成 `deferred`，
   而没有完成，或没有先在新权威锚完成受控删除/重新分配并同步 Requirement、Task 与矩阵？
10. **结构测量边界**：每条 DocStar finding 是否连同证据归入且只归入
    `target-scoped | candidate-introduced-or-polluted | external-pre-existing`？是否只有在
    同时证明目标范围外与早于 closing candidate 时才使用 `external-pre-existing`？不能证明时，
    是否标记 scope classification incomplete 并阻断，而不是留债？DocStar
    `classification_complete` 本身不能回答这些问题。

未解决的目标 blocker、`target-scoped` finding、`candidate-introduced-or-polluted` finding，或
未完成的 scope classification 都阻断关账；有证据的 `external-pre-existing` finding 不阻断。
负责人验收后才把目标状态改为 `closed`。
