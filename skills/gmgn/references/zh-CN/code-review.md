---
locale: zh-CN
purpose: 统一 Codex、Claude Code 与只读 reviewer 的增量代码审查范围和 finding 格式。
upstream: [派发与回传](dispatch-and-handoff.md)
downstream: [pre-merge checklist](pre-merge-checklist.md)
status: approved
type: task
nature: normative
---

# 代码审查契约：原生入口与统一补查

English: [../en/code-review.md](../en/code-review.md)

## 1. 选择入口

- Codex Desktop：`/review`。
- Codex CLI：`codex review --uncommitted`、`--commit <sha>` 或 `--base <branch>`；范围 flag 与自定义 prompt 不混用。
- Claude Code：独立只读 reviewer；只有用户已授权操作 GitHub PR 时才用 `/code-review`。
- 原生入口不可用：派 read-only reviewer，不取消审查。

## 2. 审查面

1. 本卡增量 diff 是否满足规格锚。
2. 哪些输出、错误路径、无基线分支和同类调用路径未被断言。
3. 新增测试能否在实现错误时失败；变异只在隔离副本做。
4. 是否削弱边界校验、安全、数据保护、性能或无障碍。
5. 五类复杂度：`delete | stdlib | native | empty abstraction | shrink`。

只报 finding，不修改被审工作树。每条写 `location · evidence · impact · normative fix · priority`。
结束后运行 `git status --short`，把审查生成的缓存或副产物显式列出。
