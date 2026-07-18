---
name: write-task
description: "Use after Design review to create or change Task.md: implementation/development plan, steps, tasks/subtasks, task cards, work items, TODOs, dependencies, traceability, and rolling ledger. Design 已过审后拆任务/拆卡/排任务、实施计划/开发计划、任务卡/工作项/待办/TODO，并建立 Task.md 滚动台账。"
---

# Task.md: execution authority

<HARD-GATE>`Design.md` must exist and have independent-critic plus primary-orchestrator review. Otherwise return to `write-design`.</HARD-GATE>

## Language and contract

Use the Design locale and the matching
[English](../gmgn/references/en/writing-contract.md) or
[中文](../gmgn/references/zh-CN/writing-contract.md) Task template. Keep filename `Task.md`,
`type: task`, `nature: normative`, and these exact headers:

```markdown
| # | task | spec anchor | prerequisite | failing test | status |
```

## Split work

- Each card is the smallest independently reviewable and verifiable unit.
- Every card has a stable ID, R-AC spec anchor, explicit prerequisites, failing-first test,
  completion criterion, allowed paths, and work state `not-started`.
- Order interface/schema changes before consumers. Parallelize only dependency-free cards.
- Maintain an AC → task → test → evidence traceability matrix; every in-scope AC is covered.
- Do not use task prose to redefine Requirement or Design.

If DocStar is available, run `brief <task-id> --preset gmgn-v1 --json` on a representative
card; otherwise inspect all fixed table columns manually.

## Exit

Reconcile the full matrix and three anchors per card. Run one independent critic with
`critic-brief.md`, resolve findings, obtain primary-orchestrator review, commit, and after a
card is explicitly confirmed **REQUIRED next skill: `run-task`**.

End every substantive response with **Reflection**: weakest assumption; neglected
counterexample; measured versus inferred.
