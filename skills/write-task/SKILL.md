---
name: write-task
description: "Use after Design review to create or change Task.md: implementation/development plan, steps, tasks/subtasks, task cards, work items, TODOs, dependencies, traceability, current execution snapshot, and linked per-card execution logs. Design 已过审后拆任务/拆卡/排任务、实施计划/开发计划、任务卡/工作项/待办/TODO，并建立 Task.md 当前执行快照与单卡执行日志关联。"
---

# Task.md: execution authority

<HARD-GATE>`Design.md` must exist and have independent-critic plus primary-orchestrator review. Record `target_milestone_id`; every card must be owned by that Milestone's Task authority. Otherwise return to `write-design`. If task planning exposes changed upstream meaning, route to the WhitePaper, ROADMAP, Goal, Requirement, or Design authority instead of redefining it in Task.</HARD-GATE>

## Language and contract

Use the Design locale and the matching layout-free
[English](../gmgn/references/en/writing-contract.md) or
[中文](../gmgn/references/zh-CN/writing-contract.md) contract. Keep filename `Task.md`,
`type: task`, `nature: normative`, and these exact headers:

```markdown
| # | task | spec anchor | prerequisite | failing test | status |
```

## Writer content and self-check

- Split the Design into cards; the recorded writer chooses the surrounding document structure
  while preserving the fixed parser-facing table header. Give each card a stable Markdown
  anchor keyed by its existing task ID for its log's exact upstream link.
- Each card is the smallest independently reviewable and verifiable unit.
- Every card has a stable ID, R-AC spec anchor, explicit `depends_on`, failing-first test,
  completion criterion, allowed paths, `write_set`, `conflict_domains`, `runtime_locks`, a
  semantic owner, exactly one owning Milestone, work state `not-started`,
  `execution_log: none`, and `latest_event: none`. Keep the six parser-facing columns unchanged; record the additional
  execution facts in card content keyed by the same stable ID.
- `depends_on` forms an acyclic DAG. It may name cards in the same Milestone; an external hard
  prerequisite may only point to an already planned upstream Milestone as established by the
  ROADMAP dependency relationship, not by Milestone ID or numeric order, and never authorizes
  executing that external card. A current or upstream Milestone must not depend on downstream
  implementation, confirmation, evidence, or document completion. Such a reverse dependency
  returns to `write-task` revision mode, and to an upstream authority when its meaning is wrong,
  before any downstream work starts.
- If the target Milestone must itself prove technical-selection or architecture feasibility,
  create a spike or verification card owned by that target Milestone. If responsibility belongs
  downstream, record a non-blocking TODO or Handoff with receiving Milestone/owner, question,
  trigger, possible impact or default assumption; do not turn it into the target's prerequisite.
- A card becomes ready only when every valid predecessor is `node-complete` on the current
  shared baseline. Order interface/schema changes before their consumers, but do not add
  artificial ordering between independent cards.
- `write_set` names intended files and, where useful, stable sections or symbols.
  `conflict_domains` names shared semantic/interface/schema/migration/generated-artifact
  surfaces; `runtime_locks` names exclusive databases, ports, hardware, accounts, or other
  mutable resources. File overlap alone is not proof of safety or conflict.
- Maintain an AC → task → test → evidence traceability matrix; every in-scope AC is covered.
- Do not use task prose to redefine Requirement or Design.

Before return, the recorded writer checks that every target-Milestone AC has at least one card,
test, and evidence destination; every card has all required facts; prerequisites form no cycle;
and no reverse dependency points to a downstream Milestone. Cards eligible together have
compatible `conflict_domains`, `runtime_locks`, and semantic ownership. The writer does not
freeze waves in `Task.md`; the orchestrator derives a rolling ready set from the current shared
baseline.

## Current snapshot and per-card execution history

- Keep `Task.md` as the normative current execution snapshot. It contains only the facts
  needed for current scope, readiness, ownership, status, blockers, latest anchors, current
  evidence, and closure; replace superseded state rather than appending progress narratives.
- On the first durable execution event for a card, create `execution/<card_id>.md` with
  all seven fixed frontmatter keys: Task locale; a purpose naming the card; `upstream` as a
  real relative link to the exact Task card anchor; `downstream: none`; `status: draft`;
  `type: execution-log`; and `nature: descriptive`. Then replace the card's
  `execution_log: none` and `latest_event: none` with real relative links in the same
  state-refresh batch.
- Append durable status transitions, attempts, candidate and baseline anchors, review and
  verification rounds, commands, results, limitations, integration conflicts, corrections,
  and superseded states to that card's log. Give each event a stable `event_id`, a
  `previous_event` link or `none`, and evidence links; update the Task card's `latest_event`
  pointer in the same batch. Do not rewrite old event bodies; append a correction. Fixed
  frontmatter and current pointers may be mechanically refreshed.
- Keep one log per stable `card_id`. Never accumulate all cards into one project-wide or
  Milestone-wide execution log.
- The execution log is descriptive and on-demand. It never defines current scope,
  dependencies, acceptance, status, or closure. Promote any discovered semantic change to
  its normative authority through the controlled revision route before affected work resumes.
- A single-card operator resolves the exact card, its directly gating rows, affected AC rows,
  and target-Milestone shared-baseline/integration-queue pointers. Do not ingest all of
  `Task.md`, unrelated closed cards, or the whole execution log by default; start from
  `latest_event` and follow only the unresolved cycle's links.
- A closed card remains in the canonical Task table with its closure result, current evidence,
  and execution-log pointer. Remove its superseded narrative from `Task.md`; do not remove its
  stable ID or traceability.

## Writer and critic loop

At `ready-to-dispatch`, record the Design anchor, select the actual writer, and bind
`author_ref`. The primary session may write directly, or an Author may be delegated with the
content and self-check above when the bounded handoff creates real value. At `author-returned`,
send incomplete or out-of-scope work to the same recorded writer as `author-rework`; otherwise
enter `candidate-anchored` and dispatch an independent Critic. At `critic-returned`, adjudicate
findings, resume the same recorded writer in `author-revising`, and send blocker fixes to the
same Critic in `critic-rechecking`. With no blocker, the primary orchestrator reviews the
candidate. The primary orchestrator applies accepted mechanical traceability, links, state,
and commit material, including across an integration boundary, and runs machine checks. Finish at
`node-complete`.

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
5. Propagate only to affected implementation, tests, evidence, per-card execution logs, and state
   representations; review and verify that impact cone only.

Meaning-preserving mechanical changes use same-batch link, hash, task reference, and status
refresh plus machine checks without reapproval.

## Legacy Task migration

When an existing `Task.md` already mixes current authority with accumulated history:

1. Bind `legacy_task_anchor` to the pre-migration commit, content hash, or equivalent immutable
   version before editing. It remains the source for history that cannot be assigned safely.
2. Reconstruct only the current normative projection: canonical rows, current dependencies,
   status, blocker, anchors, evidence, traceability, and log pointers. If current meaning is
   uncertain, treat the migration as a semantic revision and use the normal Critic loop.
3. For each previously executed card, create its per-card log and append one
   `legacy-migration` event that cites `legacy_task_anchor` and exact source locations. Copy or
   summarize only facts that are unambiguously owned by that `card_id`; do not invent event
   order, timestamps, evidence, or outcomes. Use the same seven-key frontmatter and exact
   Task-card upstream link as a new log.
4. Preserve unassignable old batch or project narrative only through `legacy_task_anchor`.
   Keep a single compact pointer in the migrated Task or Handoff; do not copy it into a new
   project-wide or Milestone-wide live log, and do not use it as current authority.
5. Cut over Task, per-card links, current traceability, and migration record in one checked
   batch. Verify the new current projection against the old anchor and keep unrelated cards
   unchanged.

If DocStar is available, run `brief <task-id> --preset gmgn-v1 --json` on a representative
card; otherwise inspect all fixed table columns manually. DocStar reports structural IDs and
edges; it does not decide Milestone ownership, dependency legality, or closure eligibility.

## Exit

Require the recorded writer to reconcile the affected matrix and three anchors per changed
card. For creation or a semantic revision, run the identity-preserving writer/Critic loop
using the locale-matched dispatch contract, obtain primary-orchestrator review, and integrate
only when required by workspace topology. After a target-Milestone execution set is explicitly
confirmed, use **REQUIRED next skill: `run-task`** to dispatch every ready owned card and keep
refilling capacity. A revision returns to the stage that raised it and continues through the
affected path only.

Before every substantive return, perform a task-specific self-check and correct defects. Do
not output a fixed `Reflection` section. Disclose only material unresolved risks that could
change the conclusion, decision, acceptance, or downstream work; otherwise omit the
disclosure. Approval, acceptance, and closure always state remaining material risks or that
none are known.
