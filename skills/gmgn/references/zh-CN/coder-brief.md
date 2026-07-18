---
locale: zh-CN
purpose: 给逐卡实现 agent 一份最小改动、失败先行、可重放验证的任务书。
upstream: [派发与回传](dispatch-and-handoff.md)
downstream: [代码审查](code-review.md)
status: approved
type: task
nature: normative
---

# 模板：Coder 任务书

English: [../en/coder-brief.md](../en/coder-brief.md)

```markdown
## Objective
实现 <task-id>，满足 <spec-anchor>，不扩大范围。

## Read first
- Task card: <Task.md pointer>
- Spec/design: <anchors>
- Real call path: <entry → changed behavior>

## Allowed changes
- <paths>

## Forbidden changes
- 不改无关文件、公共接口、依赖或配置，除非任务明确要求。
- 不 push、不发消息、不改远端状态。

## Implementation discipline
1. 先写或确认一个能区分错误实现的 failing test。
2. 按 no implementation → reuse → stdlib → native → existing dependency → direct → least new code 选首个足够方案。
3. Bug 修复找共享根因和同类调用路径，不只补题面分支。
4. 不删除信任边界校验、数据保护、安全、无障碍或明确需求。

## Verification
- <targeted test>
- <startup/E2E or real-path command>
- git diff --check
- git status --short

## Return
1. Artifacts and evidence: files, exact commands, result summary
2. Deviations and decisions needed
3. Reflection: weakest assumption; neglected counterexample; measured vs inferred
```
