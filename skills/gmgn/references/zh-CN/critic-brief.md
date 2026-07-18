---
locale: zh-CN
purpose: 规定独立文档 critic 的单轮证伪范围、七个维度和 finding 格式。
upstream: [派发与回传](dispatch-and-handoff.md)
downstream: [GMGN 路由](../../SKILL.md)
status: approved
type: task
nature: normative
---

# 模板：独立 Critic 任务书

English: [../en/critic-brief.md](../en/critic-brief.md)

```markdown
## Objective
对 <artifact + version anchor> 做一次独立证伪审查，只报 finding，不改文件。

## Scope
- Changed artifact: <path>
- Required context: <minimum upstream/downstream links>
- Out of scope: new product scope and implementation work

## Seven dimensions
1. factual correctness
2. completeness against upstream scope
3. internal consistency
4. upstream/downstream consistency
5. decidability and verification path
6. normative/descriptive contamination
7. overdesign or duplicate authority

## Finding format
- Location: <file:line or section>
- Evidence: <text, command, or contradiction>
- Impact: <what fails>
- Normative correction: <specific required change>
- Blocking: <blocker | non-blocker>

## Return
1. Findings, or explicit no-findings with coverage
2. Conflicts requiring orchestrator/owner decision
3. Reflection: weakest assumption; neglected counterexample; measured vs inferred
```

Critic 不能自行扩大范围，也不能用第二轮无限追逐非阻塞偏好。冲突 finding 交主编排者或负责人裁决。
