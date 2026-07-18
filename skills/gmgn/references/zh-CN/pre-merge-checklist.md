---
locale: zh-CN
purpose: 在并行产出进入共享基线前检查集成、验证强度、声明真实性、工具退化和复杂度。
upstream: [GMGN §7](../../../../GMGN.zh-CN.md), [代码审查](code-review.md)
downstream: none
status: approved
type: design
nature: normative
---

# 合并前核对单

English: [../en/pre-merge-checklist.md](../en/pre-merge-checklist.md)

1. **工作区溯源**：`run_id`、`card_id`、`worktree_path`、`branch_ref`、`baseline_anchor`、
   `candidate_anchor` 是否锁定同一条已审 lane；开工与回传根核验是否通过；候选是否为只含本卡
   `write_set` 的可解析本地 commit？
2. **两阶段基线安全**：是否先从干净的当前 `shared_baseline_anchor` 创建隔离临时组合并应用候选，
   且不推进共享锚？基线前移本身不得触发 `rebase-required`；是否只有应用不干净、依赖/规格语义
   失效或需要 Coder 判断时才使用该状态？
3. **集成完整性**：实际影响面是否大于文件 diff；接口、调用方、迁移、文档和交互 lane 是否都处理？
4. **验证不降级**：是否删测、放宽断言、吞错或绕过真实路径？
5. **声明—磁盘一致**：完成状态、文件、测试输出和 git diff 是否一致；分支 `accepted` 是否仍与
   `closed` 明确分开？
6. **操作—形态匹配**：命令对当前路径、空集、大集、重复名和失败码如何退化？
7. **命名、数字与所有权溯源**：机制专名、关键数字、semantic owner、`conflict_domains` 和
   `runtime_locks` 能否指回权威？
8. **过度设计扫**：逐项检查 `delete | stdlib | native | empty abstraction | shrink`。

同一 Integrator 在临时组合运行 `git diff --check`、`git status --short` 等机械检查。同一 lane 的
Verifier 收到当前派发的 `workspace_mode`、`worktree_path`、`branch_ref`，在该临时组合运行受影响
交互与项目门禁。冲突/失败时中止或丢弃临时候选并证明原共享工作区 clean。只有验证通过的候选
加台账刷新才能原子推进 `shared_baseline_anchor` 并进入 `node-complete`/`closed`；未验证组合不得
成为共享基线。
