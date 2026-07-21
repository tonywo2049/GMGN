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

审查前和回传前都运行 `git rev-parse --show-toplevel`，解析结果必须等于本 lane 的绝对
`worktree_path`，且该路径取当前派发。审查本地 commit SHA 锁定的不可变
`baseline_anchor..candidate_anchor`，不能以当前恰好打开的
uncommitted diff 代替。

1. 本卡增量 diff 是否满足规格锚、`write_set`、`conflict_domains` 与 `runtime_locks`。
2. 哪些输出、错误路径、无基线分支和同类调用路径未被断言。
3. 新增测试能否在实现错误时失败；变异只在隔离副本做。
4. 是否削弱边界校验、安全、数据保护、性能或无障碍。
5. 五类复杂度：`delete | stdlib | native | empty abstraction | shrink`。

存在 `.codegraph/` 时，在候选 worktree 中独立查询 CodeGraph，检查改动符号、调用者和同类路径。
索引不能证明与候选 commit 一致时，只用于定位。finding 必须引用精确 Git diff 或已检出源码；测试
与真实运行才是行为证据。任务 brief 或图不够用时，允许直接定向读取文件。

只报 finding，不修改被审工作树。每条写 `location · evidence · impact · normative fix · priority`。
结束后运行 `git status --short`，把审查生成的缓存或副产物显式列出。

`shared_baseline_anchor` 前移时，先在隔离临时组合上尝试机械应用；前移本身不强制 review 或
`rebase-required`。只有应用不干净、依赖/规格语义失效，或 Coder 判断改变 lane 时，所有受影响
diff 才回同一 Reviewer。定向复核只适用于原已采纳 blocker；集成 diff 变化时审全部变化 hunk。
集成后验证仍由 Verifier 负责。
