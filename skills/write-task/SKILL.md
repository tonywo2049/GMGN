---
name: write-task
description: "Use after Design review to create or change Task.md: implementation/development plan, steps, tasks/subtasks, task cards, work items, TODOs, dependencies, traceability, and rolling ledger. Design 已过审后拆任务/拆卡/排任务、实施计划/开发计划、任务卡/工作项/待办/TODO，并建立 Task.md 滚动台账。"
---

# Task.md: execution authority

<HARD-GATE>`Design.md` must exist and have independent-critic plus primary-orchestrator review. Otherwise return to `write-design`. If task planning exposes changed upstream meaning, route to the WhitePaper, ROADMAP, Goal, Requirement, or Design authority instead of redefining it in Task.</HARD-GATE>

## Language and contract

Use the Design locale and the matching layout-free
[English](../gmgn/references/en/writing-contract.md) or
[中文](../gmgn/references/zh-CN/writing-contract.md) contract. Keep filename `Task.md`,
`type: task`, `nature: normative`, and these exact headers:

```markdown
| # | task | spec anchor | prerequisite | failing test | status |
```

## Author content and self-check

- Dispatch an Author to split the Design into cards; the Author chooses the surrounding
  document structure while preserving the fixed parser-facing table header.
- Each card is the smallest independently reviewable and verifiable unit.
- Every card has a stable ID, R-AC spec anchor, explicit `depends_on`, failing-first test,
  completion criterion, allowed paths, `write_set`, `conflict_domains`, `runtime_locks`, a
  semantic owner, and work state `not-started`. Keep the six parser-facing columns unchanged;
  record the additional execution facts in card content keyed by the same stable ID.
- `depends_on` forms an acyclic DAG. A card becomes ready only when every predecessor is
  `node-complete` on the current shared baseline. Order interface/schema changes before their
  consumers, but do not add artificial ordering between independent cards.
- `write_set` names intended files and, where useful, stable sections or symbols.
  `conflict_domains` names shared semantic/interface/schema/migration/generated-artifact
  surfaces; `runtime_locks` names exclusive databases, ports, hardware, accounts, or other
  mutable resources. File overlap alone is not proof of safety or conflict.
- Maintain an AC → task → test → evidence traceability matrix; every in-scope AC is covered.
- Do not use task prose to redefine Requirement or Design.

Before return, the Author checks that every in-scope AC has at least one card, test, and
evidence destination; every card has all required facts; prerequisites form no cycle; and
cards eligible together have compatible `conflict_domains`, `runtime_locks`, and semantic
ownership. The Author does not freeze waves in `Task.md`; the orchestrator derives a
rolling ready set from the current shared baseline.

## Author and critic loop

At `ready-to-dispatch`, record the Design anchor and dispatch one Author with the content and
self-check above; retain `author_ref`. The orchestrator does not split or edit cards. At
`author-returned`, send incomplete or out-of-scope work to the same Author as `author-rework`;
otherwise enter `candidate-anchored` and dispatch an independent Critic. At `critic-returned`,
adjudicate findings, resume the same Author in `author-revising`, and send blocker fixes to
the same Critic in `critic-rechecking`. With no blocker, the primary orchestrator reviews the
candidate and dispatches an Integrator for accepted mechanical traceability, links, state,
and commit material. Finish at `node-complete`.

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

Require the Author to reconcile the affected matrix and three anchors per changed card. For
creation or a semantic revision, run the identity-preserving Author/Critic loop using the
locale-matched dispatch contract, obtain primary-orchestrator review, and integrate. After a
card or execution set is explicitly confirmed, use **REQUIRED next skill: `run-task`** to
dispatch every ready card and keep refilling capacity. A revision returns to the stage that
raised it and continues through the affected path only.

End every substantive response with **Reflection**: weakest assumption; neglected
counterexample; measured versus inferred.
