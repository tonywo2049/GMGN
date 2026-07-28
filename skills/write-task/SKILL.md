---
name: write-task
description: "Use after Design review to create or change Task.md: milestone task decomposition, AC-to-task mapping, dependencies, orchestration status, and pointers to per-card execution contracts. Design 已过审后拆任务、维护 AC→Task 映射、依赖、宏观执行状态及执行入口；单卡 TDD 与执行细节不写入 Task.md。"
---

# Task.md: milestone task index

<HARD-GATE>The complete linked Design Bundle—root `Design.md` plus every applicable module, `design/Contract.md`, split contract, and structural authority—must have independent Critic plus primary-orchestrator review at one commit. Record `target_milestone_id`; every task belongs to that Milestone. If planning exposes changed upstream meaning or an implementation-significant unknown, stop and return the issue to `gmgn` for routing instead of deciding it in Task.</HARD-GATE>

Before writing, load the registered `gmgn` Skill through normal discovery and follow its local
writing contract. Use the Design locale for artifact prose. Keep filename `Task.md`, `type:
task`, `nature: normative`, and this parser-facing table header:

```markdown
| # | task | spec anchor | prerequisite | status | execution |
```

## Task content

- Derive Task only from the reviewed Requirement, Design, and applicable Contract. If task
  planning requires changing upstream meaning or making a missing design decision, stop and
  return the issue to `gmgn` for routing.
- Keep `Task.md` as a compact Milestone execution index. It answers only:
  - which independently decidable results must be delivered;
  - which AC, Design, and applicable Contract anchors authorize each result;
  - which real prerequisites prevent a task from starting;
  - the current macro status;
  - where the execution contract is linked.
- Keep the parser-facing task header unchanged. Use stable task IDs and the task-state tokens
  defined by the writing contract. Replace current status and execution values; never append
  execution history.
- Give each task exactly one approved result that can be independently accepted or failed.
  Apply the split test: if a row contains two or more approved results and each has its own
  upstream anchor and pass/fail check, split the row. Keep any real dependencies between the
  resulting tasks in `prerequisite`; a dependency is not a reason to merge them. Do not split
  by file, interface, implementation step, chronology, person, or merely to occupy capacity.
- Keep only task boundaries supported by the current approved Design. Only when research or
  selection is itself the current Milestone result may an approved task produce that evidence.
  Task never chooses production semantics; return a missing decision to `gmgn` for routing
  before defining implementation tasks. Never create tentative, placeholder, or speculative
  task sets.
- Every in-scope AC must map to at least one task. AC coverage belongs to the task set: a task
  may cover several related ACs, one AC may require several tasks, and no individual task must
  satisfy that AC alone. If the current ACs cannot be fully mapped, the Design is not ready
  for Task planning.
- `prerequisite` contains only real data, interface, or decision dependencies and must form
  an acyclic DAG. Sharing an approved Contract does not by itself create a dependency. Do not
  freeze execution waves.
- Apply the deletion test to every task. Remove a task when deleting its result leaves every
  current AC and approved Design result satisfied. Future reuse, possible hardening, and
  coordination convenience are not task owners.
- Do not copy Requirement, Design, or Contract meaning into Task. Do not put TDD cases,
  commands, file scopes, runtime locks, blockers, commits, candidates, review records,
  evidence, or progress narratives in `Task.md`.

## Execution link

The `execution` column stores only the current execution entry link when one exists. Do not
copy execution content or history into `Task.md`, and do not require the execution ID to equal
the Task ID.

## Writer and review loop

The primary session may write Task directly when it holds the clearest context, or dispatch a
fresh Author when delegation has real isolation, specialization, or parallel value. Every
delegated Author or Critic is single-use. Before creating one, prepare a role brief with the
objective, required commit references, required context, scope and prohibitions, checks, and return
format. Do not resume or repurpose a returned agent.

After the writer self-check and machine checks, commit the complete candidate locally and
dispatch one fresh independent Critic for semantic review from a brief that names the shortest
unambiguous commit reference. Collect all findings before changing the candidate.
The Critic must try splitting, deleting, and merging each affected task. Report under-splitting
when a row contains more than one result that passes the split test. Report overdesign when a
task can be deleted, or when two rows are only steps of one result and merging them loses
neither an independent acceptance boundary nor a real dependency boundary.
The primary orchestrator adjudicates them once and applies accepted fixes itself or dispatches
a fresh Author with a revision brief. It checks each resolution and runs affected machine
checks without dispatching a second Critic. A fix that expands authority or scope beyond the
accepted findings becomes a separately scoped change. Non-blocking suggestions do not reopen
an otherwise acceptable candidate. Meaning-preserving links, formatting, and status refresh
use machine checks without Critic.

## Controlled revision

- Revise only affected task rows, AC mappings, dependencies, status, and execution pointers.
  Do not reopen unrelated tasks.

## Exit

Before acceptance, confirm every task has one independently decidable result, an upstream
anchor, only real prerequisites, and current status/execution values; no task contains another
result that passes the split test; every in-scope AC is covered; the dependency graph is
acyclic; and no design decision or execution detail appears in `Task.md`. Before every
substantive return, perform a task-specific self-check and correct defects. Do not output a
fixed `Reflection` section. Disclose only unresolved material risk.
