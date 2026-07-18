---
name: write-task
description: "Use after Design review to create or change Task.md: implementation/development plan, steps, tasks/subtasks, task cards, work items, TODOs, dependencies, traceability, and rolling ledger. Design 已过审后拆任务/拆卡/排任务、实施计划/开发计划、任务卡/工作项/待办/TODO，并建立 Task.md 滚动台账。"
---

# Task.md: execution authority

<HARD-GATE>`Design.md` must exist and have independent-critic plus primary-orchestrator review. Otherwise return to `write-design`. If task planning exposes changed upstream meaning, route to the WhitePaper, ROADMAP, Goal, Requirement, or Design authority instead of redefining it in Task.</HARD-GATE>

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

## Controlled revision

1. Classify the authority before editing. Route WhitePaper to `brainstorm`, ROADMAP to
   `roadmap`, Goal to `write-goal`, Requirement or R-AC meaning to `write-requirement`, and
   design intent to `write-design`. Resume after any required new upstream review or approval.
2. For Task-owned meaning, start from the old anchor and record the trigger, semantic delta,
   affected cards, dependencies, tests, mappings, evidence, and proposed new anchor.
3. Revise only affected cards and traceability rows. Pause active cards whose premise changed;
   do not re-split or reopen unrelated work.
4. A delta that changes execution authority or reasonable understanding receives independent
   criticism and primary-orchestrator review at a new anchor. Old review remains attached to
   the old anchor.
5. Propagate only to affected implementation, tests, evidence, rolling records, and state
   representations; review and verify that impact cone only.

Meaning-preserving mechanical changes use same-batch link, hash, task reference, and status
refresh plus machine checks without reapproval.

If DocStar is available, run `brief <task-id> --preset gmgn-v1 --json` on a representative
card; otherwise inspect all fixed table columns manually.

## Exit

Reconcile the affected matrix and three anchors per changed card. For creation or a semantic
revision, run one independent critic with `critic-brief.md`, resolve findings, obtain
primary-orchestrator review, and commit. After a new card is explicitly confirmed, use
**REQUIRED next skill: `run-task`**. A revision returns to the stage that raised it and
continues through the affected path only.

End every substantive response with **Reflection**: weakest assumption; neglected
counterexample; measured versus inferred.
