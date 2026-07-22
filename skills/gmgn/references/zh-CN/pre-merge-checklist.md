---
locale: zh-CN
purpose: 在共享基线集成前检查候选身份、审查、验证、状态和复杂度。
upstream: [GMGN](../../../../GMGN.zh-CN.md), [代码审查](code-review.md)
downstream: none
status: approved
type: design
nature: normative
---

# 合并前核对单

English: [../en/pre-merge-checklist.md](../en/pre-merge-checklist.md)

1. **候选身份**：已审候选是否能从预期基线、工作区、任务和预先声明的写入边界精确解析？
2. **影响范围**：接口、调用方、迁移、文档和交互任务是否都在范围内？
3. **审查屏障**：是否先收齐全部活动 Critic/Reviewer finding 并清除 blocker，再派 Verifier？
4. **最终组合**：它是已应用到当前共享基线的隔离 lane 候选，还是已经基于未变共享基线的单 writer
   冻结候选？
5. **验证边界**：需要可执行证据时，是否只派一个新 Verifier 检查最终组合？存在第二边界时，
   是否记录风险理由？
6. **验证不降级**：是否删测、放宽断言、吞错或绕过真实路径？
7. **Task/Card/Log 分离**：Task 是否只保留宏观信息，Card 是否为稳定执行/TDD 权威，Log 是否保存
   当前快照和历史？
8. **失败隔离**：冲突或失败后，前一共享基线是否仍 clean，失败是否只记录在 Log 而不扩张 Task？
9. **过度设计**：能否删除、改用标准/原生能力，或缩小结构？

在临时组合运行 `git diff --check`、`git status --short` 等仓库检查。只有审查清零，且在需要时独立
验证通过的组合才能推进共享基线；Task/Card/Log 与追踪关系必须在该候选中同批刷新。
