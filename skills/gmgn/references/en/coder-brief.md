---
locale: en
purpose: Give a task-card implementation agent a minimal-change, failing-first, replayable brief.
upstream: [dispatch and handoff](dispatch-and-handoff.md)
downstream: [code review](code-review.md)
status: approved
type: task
nature: normative
---

# Template: coder brief

中文版本：[../zh-CN/coder-brief.md](../zh-CN/coder-brief.md)

```markdown
## Objective
Implement <task-id> against <spec-anchor> without expanding scope.

## Read first
- Task card: <Task.md pointer>
- Spec/design: <anchors>
- Real call path: <entry → changed behavior>

## Allowed changes
- <paths>

## Forbidden changes
- Do not change unrelated files, public interfaces, dependencies, or configuration unless required.
- Do not push, message, or mutate remote state.

## Implementation discipline
1. First add or confirm a failing test that discriminates an incorrect implementation.
2. Choose the first sufficient option: no implementation → reuse → stdlib → native → existing dependency → direct → least new code.
3. For a bug, find the shared root cause and sibling call paths; do not patch only the reported branch.
4. Do not remove trust-boundary validation, data protection, security, accessibility, or explicit requirements.

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
