---
name: write-task
description: "Use after Design review to create or change Task.md: milestone task decomposition, AC-to-task mapping, dependencies, orchestration status, and pointers to per-card execution contracts. Design 已过审后拆任务、维护 AC→Task 映射、依赖与宏观执行状态；单卡 TDD 与执行细节在 run-task 创建的 execution 文档中维护。"
---

# Task.md: milestone task index

<HARD-GATE>`Design.md` must exist and have independent Critic plus primary-orchestrator review. Record `target_milestone_id`; every task belongs to that Milestone. If planning exposes changed upstream meaning, revise its WhitePaper, ROADMAP, Goal, Requirement, or Design authority instead of redefining it in Task.</HARD-GATE>

Before writing, load the registered `gmgn` Skill through normal discovery and follow its local
writing contract. Use the Design locale for artifact prose. Keep filename `Task.md`, `type:
task`, `nature: normative`, and this parser-facing table header:

```markdown
| # | task | spec anchor | prerequisite | status | execution |
```

## What Task.md owns

`Task.md` is a compact Milestone index. It owns only:

- stable task IDs and one-line independently decidable outcomes;
- Requirement AC and Design anchors;
- the task dependency DAG;
- current macro status;
- the per-card execution pointer, initially `none`;
- the target Milestone execution set, shared-baseline pointer, integration-queue pointer, and
  an AC → task traceability table.

Do not put TDD cases, commands, allowed paths, write sets, locks, candidate anchors, blockers,
review rounds, verification evidence, or progress narratives in `Task.md`. Those facts belong
to the per-card execution documents created by `run-task`. Updating Task status or its
execution link replaces the old value; it never appends history.

## Decompose work

Within the approved Design, optimize decomposition for useful independent execution. Give each
task one primary responsibility and one independently decidable, testable result. Minimize
unnecessary task dependencies, shared writes, and runtime conflicts so work with no real
dependency can run in parallel. The objective is useful parallelism, not more task cards. Never
invent empty wrappers, fake interfaces, or new design decisions merely to increase concurrency.

- Split at an independent proof boundary, not by file count, chronology, or a final product
  qualification. One task has one primary semantic owner and one independently decidable
  result; one AC may map to several tasks.
- Separate independently verifiable interface/schema enablement, implementation,
  cross-module integration, real-environment or E2E qualification, production eligibility,
  and Milestone closure.
- An intermediate task may integrate only while unfinished product paths remain unreachable,
  disabled, or fail-closed, with that containment proved by its later Card TDD contract.
- Continue splitting when a task still combines separable responsibilities, unrelated
  failure causes, independent modules, or qualification with implementation.
- Stop when a smaller unit would not have an independently testable result, would leave
  required responsibility without an owner, or would add more coordination cost than
  isolation benefit.
- Define each outcome so satisfying it closes the task. Do not make cleanup, adjacent defects,
  future hardening, or repository-wide completeness part of a task unless the approved AC
  requires them.
- `prerequisite` forms an acyclic DAG. Add only real data, interface, or authority
  dependencies. Order interface/schema work before consumers; do not serialize independent
  work for convenience.
- An external hard prerequisite may point only to an already planned upstream Milestone and
  never authorizes executing it. A current or upstream Milestone must not depend on downstream
  implementation or evidence.
- Keep an explicit `| AC | task |` mapping and cover every in-scope AC. A task may appear in
  several rows and an AC may map to several tasks.

Before return, check that every task is independently decidable, the DAG is acyclic, no
reverse Milestone dependency exists, and every in-scope AC maps to at least one task. Do not
freeze waves; `run-task` derives the rolling ready set.

## Per-card execution contract

After the owner confirms the Task execution set, `run-task` materializes exactly two files for
each selected task before any Coder dispatch:

1. `execution/<card_id>/Card.md` — normative stable execution contract: Task/AC/Design
   anchors, outcome, completion criterion, the TDD contract, and an `execution_log` link to
   its sibling `Log.md`. Add scope exclusions or an allowed path/write set only when they
   materially bound a delegated writer. Add conflict domains or runtime locks only for a real
   shared-resource collision. Link the Task row instead of copying its dependency DAG.
2. `execution/<card_id>/Log.md` — descriptive current runtime snapshot, material decisions
   only, and one final evidence summary when closed. Routine dispatch, waiting, unchanged
   status, and successful intermediate checks do not become Log entries. Its `latest_event`
   field is only a DocStar compatibility pointer to `#current` or `#final-evidence`, not a
   general event ledger.

The TDD contract belongs in `Card.md`, not Task. It identifies the test case or test location,
the wrong behavior it must expose in RED, expected GREEN behavior, the replay command or
executable path, and the final verification/evidence destination. Do not create separate
`Verification.md`, `State.md`, handoff, or per-role brief files unless the project has an
independent requirement for them.

`Card.md` may refine implementation mechanics but cannot add scope, dependencies, acceptance
meaning, or design decisions absent from approved authority. If materialization reveals such a
gap, stop that task and return to the owning authority. After a Card becomes active, discovery
does not expand it; another independently testable outcome requires a separately accepted task.

## Writer and review loop

The primary session may write Task directly when it holds the clearest context, or dispatch a
fresh Author when delegation has real isolation, specialization, or parallel value. Every
delegated Author or Critic is single-use. Before creating one, prepare a role brief with the
objective, immutable anchors, required context, scope and prohibitions, checks, and return
format. Do not resume or repurpose a returned agent.

After the writer self-check and machine checks, freeze one candidate and dispatch one fresh
independent Critic for semantic review. Collect all findings before changing the candidate.
The primary orchestrator adjudicates them once and applies accepted fixes itself or dispatches
a fresh Author with a revision brief. It checks each resolution and runs affected machine
checks without dispatching a second Critic. A fix that expands authority or scope beyond the
accepted findings becomes a separately scoped change. Non-blocking suggestions do not reopen
an otherwise acceptable candidate. Meaning-preserving links, formatting, and status refresh
use machine checks without Critic.

## Controlled revision and legacy migration

- Revise only affected task rows, AC mappings, dependencies, and execution pointers. Pause
  active tasks whose authority changed; do not reopen unrelated tasks.
- When migrating an oversized legacy `Task.md`, anchor the old version when possible, retain
  only the current macro projection, and link historical detail rather than copying it.
- Existing per-card execution history may be summarized into the new `Log.md` only when its
  ownership and evidence are unambiguous. Preserve material decisions and final acceptance
  evidence; otherwise keep the legacy anchor and state the limitation. Never invent event
  order, commands, or acceptance evidence.
- Existing projects may keep their old layout until a controlled migration. New or revised
  cards use the two-file execution layout.

## Exit

After Task semantic review, primary-orchestrator acceptance, and owner confirmation of the
target execution set, use **REQUIRED next skill: `run-task`**. Before every substantive return,
perform a task-specific self-check and correct defects. Do not output a fixed `Reflection`
section. Disclose only unresolved material risk.
