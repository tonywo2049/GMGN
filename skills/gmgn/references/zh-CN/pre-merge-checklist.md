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

1. **集成完整性**：实际影响面是否大于文件 diff；接口、调用方、迁移和文档是否都处理？
2. **验证不降级**：是否删测、放宽断言、吞错或绕过真实路径？
3. **声明—磁盘一致**：完成状态、文件、测试输出和 git diff 是否一致？
4. **操作—形态匹配**：命令对当前路径、空集、大集、重复名和失败码如何退化？
5. **命名与数字溯源**：机制专名和关键数字能指回 Requirement/Design/Decision 吗？
6. **过度设计扫**：逐项检查 `delete | stdlib | native | empty abstraction | shrink`。

最后由 Integrator 重放相关命令，运行 `git diff --check` 与 `git status --short` 并落盘证据；
主编排者据此决定是否合并。
