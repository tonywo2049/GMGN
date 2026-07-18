---
locale: en
purpose: Define the scope, seven falsification dimensions, and finding format for an independent document critic.
upstream: [dispatch and handoff](dispatch-and-handoff.md)
downstream: [GMGN router](../../SKILL.md)
status: approved
type: task
nature: normative
---

# Template: independent critic brief

中文版本：[../zh-CN/critic-brief.md](../zh-CN/critic-brief.md)

```markdown
## Objective
Run one independent falsification review of <artifact + version anchor>. Report findings; do not edit files.

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

The critic may not expand scope and may not start endless rounds over non-blocking
preferences. Conflicting findings go to the orchestrator or owner.
