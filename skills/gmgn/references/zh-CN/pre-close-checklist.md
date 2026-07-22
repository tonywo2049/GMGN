---
locale: zh-CN
purpose: 在 Milestone 关账前检查范围、证据、状态、风险与验收。
upstream: [GMGN](../../../../GMGN.zh-CN.md)
downstream: none
status: approved
type: design
nature: normative
---

# 关账前核对单

English: [../en/pre-close-checklist.md](../en/pre-close-checklist.md)

1. **边界**：目标 Milestone 及其 Goal/Requirement/Design/Task 锚是否固定；跨 Milestone 引用是否
   错误扩大范围？
2. **判据**：每条范围内 AC 是否已完成，或已在新权威锚完成语义删除/转移？
3. **证据**：每条保留判据是否有可重放命令或真实执行路径，并覆盖相关负向行为？
4. **独立检查**：所需 Critic/Reviewer blocker 是否清零；需要时，最终可执行验证是否仍有效？
5. **状态**：Task 宏观状态、Card 契约、已关闭 Log 快照/latest event、追踪关系、ROADMAP 和关账锚
   是否一致？
6. **集成**：目标任务是否关闭在同一共享基线；是否没有遗留的自有集成项或锁？
7. **Finding 与风险**：实质结构 finding 是否已归为目标 blocker 或证明为外部既有债务；剩余风险
   是否如实说明且未编造？
8. **验收**：负责人验收是否绑定精确关账锚？

未解决目标 blocker 或未分类的实质 finding 阻断关账。只有接手者需要且现有权威没有合适落点时，
才单独创建 Handoff。
