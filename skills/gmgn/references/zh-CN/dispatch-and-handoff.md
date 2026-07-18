---
locale: zh-CN
purpose: 规定主编排者派发独立工作单元与验收 agent 回传的统一格式。
upstream: [GMGN §4](../../../../GMGN.zh-CN.md)
downstream: [coder brief](coder-brief.md), [critic brief](critic-brief.md), [code review](code-review.md)
status: approved
type: task
nature: normative
---

# 模板：派发与回传

English: [../en/dispatch-and-handoff.md](../en/dispatch-and-handoff.md)

## 任务书

```markdown
## Objective
<一个可独立验收的结果>

## Scope
- In: <允许改/读的路径与行为>
- Out: <明确禁区>

## Inputs
- <规格锚、文件、基线 commit、已有证据>

## Constraints
- Role: <coder | critic | reviewer | researcher>
- Effort: <low | medium | high>
- Workspace: <共享工作树 | 独立 worktree | read-only>
- Remote writes: forbidden unless explicitly authorized

## Deliverables
- <文件、finding、命令或决议>

## Verification
- <必须运行的原样命令与判据>

## Return format
1. Artifacts and evidence
2. Deviations and decisions needed
3. Reflection: weakest assumption; neglected counterexample; measured vs inferred
```

## 派发规则

- 机械查找用 low，常规实现用 medium，判断密集或高风险审查用 high；本机不支持显式档位时，用角色任务书约束。
- 输入必须自包含；不能假设 agent 读过主会话。
- 无依赖单元可并行，有共享接口的单元先冻结接缝。
- 三段回传缺一段就打回。agent 自述不是证据；主编排者抽验命令、磁盘改动和真实调用路径。
