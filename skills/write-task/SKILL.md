---
name: write-task
description: "Use after Design review to create or change Task.md: milestone task decomposition, AC-to-task mapping, dependencies, orchestration status, and pointers to per-card execution contracts. Design 已过审后拆任务、维护 AC→Task 映射、依赖、宏观执行状态及执行入口；单卡验证契约与执行细节不写入 Task.md。"
---

# Task.md: milestone task index

<HARD-GATE>The complete linked Design Bundle—root `Design.md` plus every applicable module, `design/Contract.md`, split contract, and structural authority—must have passed its owning-stage acceptance and Critic necessity gates at one commit. Record `target_milestone_id`; every task belongs to that Milestone. If planning exposes changed upstream meaning or an implementation-significant unknown, stop and return the issue to `gmgn` for routing instead of deciding it in Task.</HARD-GATE>

Before writing, load the registered `gmgn` Skill through normal discovery and follow its local
writing rules. Use the Design locale for artifact prose. Keep filename `Task.md`, `type:
task`, `nature: normative`, and this parser-facing table header:

```markdown
| # | task | spec anchor | prerequisite | status | execution |
```

## Task content

- Derive Task only from the reviewed Requirement, Design, applicable Contract, and any
  implementation-relevant D-ID already linked by Design. If task planning requires changing
  upstream meaning or making a missing decision, stop and return the issue to `gmgn` for
  routing.
- Keep `Task.md` as a Milestone execution index. It answers only:
  - which independently decidable results must be delivered;
  - which applicable D-ID, AC, Design, and Contract anchors authorize each result;
  - which real prerequisites prevent a task from starting;
  - the current macro status;
  - where the execution contract is linked.
- Keep the parser-facing task header unchanged. Use stable task IDs and the task-state tokens
  defined by the writing rules. Replace current status and execution values; never append
  execution history.
- Apply this Task boundary to every row: each Task names one necessary result that can be
  executed as its own unit after its prerequisites are satisfied, has one clear pass/fail
  acceptance criterion, and cannot be split further into smaller results that each meet these
  conditions. Independently executable does not mean prerequisite-free. Task count itself is
  not a measure of simplicity or overdesign. State the criterion in `task` as one observable
  result and link its governing anchors in `spec anchor`.
- Apply the split test to every Task row: if it can be divided into two or more results that
  each meet the Task boundary, split it. Repeat until every row passes the split test.
- Keep only task boundaries supported by the current approved Design. Only when research or
  selection is itself the current Milestone result may an approved task produce that evidence.
  Task never chooses production semantics; return a missing decision to `gmgn` for routing
  before defining implementation tasks. Never create tentative, placeholder, or speculative
  task sets.
- Every in-scope AC must map to at least one task. AC coverage belongs to the task set: a task
  may cover several related ACs, one AC may require several tasks, and no individual task must
  satisfy that AC alone. If the current ACs cannot be fully mapped, the Design is not ready
  for Task planning. AC coverage does not prove that each row passes the Task boundary.
- `prerequisite` contains only real data, interface, or decision dependencies and must form
  an acyclic DAG. A dependency relationship is not a basis for Task decomposition. Whether a
  dependency exists does not determine the Task boundary. Sharing an approved Contract does
  not by itself create a dependency. Do not freeze execution waves.
- Maximize parallel execution by keeping every result that passes the Task boundary as a
  separate Task. Whether ready Tasks can run simultaneously is an orchestration decision and
  does not change their boundaries.
- Omit work that contributes to no current AC or approved Design result. This contribution
  check must not be satisfied by deleting a Task row while moving its necessary work into
  another Task. The Task boundary determines whether necessary work remains a separate row.
- Do not copy Decision, Requirement, Design, or Contract meaning into Task. Do not put verification cases,
  commands, file scopes, runtime locks, blockers, commits, candidates, review records,
  evidence, or progress narratives in `Task.md`.

## Execution link

The `execution` column stores only the current execution entry link when one exists. Do not
copy execution content or history into `Task.md`, and do not require the execution ID to equal
the Task ID.

## Writer and review loop

The primary orchestrator resolves Task boundaries and prepares one Author brief under the
registered `gmgn` Skill's shared document-candidate and dispatch rules. The independent Author
writes and revises `Task.md`, commits the fixed candidate, and waits. The primary orchestrator
checks candidate identity and prepared machine evidence, applies the Task boundary and split
test to every affected row, and applies the Critic necessity gate. It adjudicates under-
splitting or an incorrect boundary and returns an accepted in-scope repair to the same Author.
AC coverage and an acyclic dependency DAG do not substitute for this check, and Task count
alone is not a finding. A fix that expands accepted authority, objective, or write boundary
becomes a separately scoped change.

## Controlled revision

- Semantic changes to task rows, AC mappings, or dependencies require the Author loop above.
  Revise only affected content and do not reopen unrelated Tasks.
- Meaning-preserving status and execution-pointer refresh is mechanical and uses machine
  checks without an Author or Critic.

## Exit

Before acceptance, require the Author and primary orchestrator to confirm every row passes the
Task boundary and split test; every Task has an upstream anchor, only real prerequisites, and
current status/execution values; every in-scope AC is covered; the dependency graph is
acyclic; every result that passes the Task boundary remains separately visible; and no design
decision or execution detail appears in `Task.md`.
