---
locale: en
purpose: Define the common format for delegating independent work units and accepting agent handoffs.
upstream: [GMGN §4](../../../../GMGN.md)
downstream: [coder brief](coder-brief.md), [critic brief](critic-brief.md), [code review](code-review.md)
status: approved
type: task
nature: normative
---

# Template: dispatch and handoff

中文版本：[../zh-CN/dispatch-and-handoff.md](../zh-CN/dispatch-and-handoff.md)

## Brief

```markdown
## Objective
<one independently acceptable outcome>

## Scope
- In: <paths and behaviors that may be read or changed>
- Out: <explicit boundaries>

## Inputs
- <spec anchors, files, baseline commit, existing evidence>

## Constraints
- Role: <coder | critic | reviewer | researcher>
- Effort: <low | medium | high>
- Workspace: <shared worktree | isolated worktree | read-only>
- Remote writes: forbidden unless explicitly authorized

## Deliverables
- <files, findings, commands, or decisions>

## Verification
- <exact commands and acceptance conditions>

## Return format
1. Artifacts and evidence
2. Deviations and decisions needed
3. Reflection: weakest assumption; neglected counterexample; measured vs inferred
```

## Dispatch rules

- Use low effort for mechanical lookup, medium for routine implementation, and high for
  judgment-heavy or high-risk review. When the platform cannot set effort, constrain the
  role through the brief.
- Inputs are self-contained; never assume the agent has read the parent conversation.
- Parallelize dependency-free units. Freeze shared interfaces before parallel work begins.
- Reject a return that omits any of the three sections. Agent claims are not evidence;
  replay commands and inspect disk changes and the real call path proportionally to risk.
