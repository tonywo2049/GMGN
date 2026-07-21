---
name: close-milestone
description: "Use when every target-milestone card is closed and its traceability is full to perform required or target-required full regression/E2E, combined review, milestone/stage/version closure, launch readiness, or ROADMAP backfill. 目标 Milestone 自有任务卡已关账且追踪完整后，用于阶段/版本收尾、关账验收、所需回归/E2E、准备上线或 ROADMAP 回填；普通单卡收尾不触发。"
---

# Close a milestone

<HARD-GATE>Every hard gate is scoped to the recorded `target_milestone_id`: every card owned by that Milestone must be `closed` on the same `shared_baseline_anchor`; the target Milestone integration queue must be empty; no lane owned by it may be active, `rebase-required`, or `integration-conflict`; every target-Milestone AC must have a task, test, and evidence row; and every executed card must link its own closed descriptive execution log. At the closing shared-baseline anchor, its `latest_event` must resolve inside that log to the final closure event; that event records the verified combined candidate and preceding shared anchor, and its evidence/current pointers match the Task card. Downstream work, lanes, documents, confirmations, TODOs, or evidence gaps do not block unless they prove that this target Milestone still has an undecided or unproved in-scope criterion. Otherwise return to `run-task` or revise an invalid reverse dependency through `write-task`. If closure review exposes a changed in-scope premise, withhold closure and route to its authority. Closure is an owner-accepted, version-anchored declaration; do not infer it from green unit tests.</HARD-GATE>

## Establish evidence first

The primary orchestrator records `target_milestone_id` plus its Goal/Requirement/Design/Task
anchors, proves that Milestone's integration entries are empty, reconciles every lane it owns
to the same `shared_baseline_anchor`, verifies that every executed card has a real
`execution_log` link to its own closed descriptive log and a resolvable `latest_event` aligned
with the card's current closure evidence, records that value as the closing anchor, and dispatches an
independent Verifier as
`verifier-active`; it does not run closure evidence in place of that agent. The Verifier must:

- receive and verify the current dispatch's `workspace_mode`, absolute `worktree_path`, and
  `branch_ref`; these workspace facts are not permanently bound to its identity;

- run the complete regression required by the target Milestone at the closing revision;
- run target-milestone startup/E2E through the real product path, including required negative
  and recovery cases;
- record exact commands, environment, revision, exit codes, result summaries, and limitations;
- return as `verifier-returned` without changing source code or product meaning.

After evidence returns, dispatch a closure Author and retain `author_ref`. The Author prepares
the anchored closure candidate: scope reconciliation, evidence map, known debt, remaining
material risks or an explicit none-known statement, proposed Handoff, and proposed state
changes. Each reported risk includes its impact, evidence strength, and cheapest next
falsification step; a none-known statement cites supporting closure evidence. The Author
chooses the document structure and must not mark anything closed before owner acceptance.

## Three closure disciplines

1. Scope: every target-Milestone AC is completed with evidence, or is first removed or
   reassigned by a controlled semantic change at a new authority anchor with Requirement,
   Task, and matrix synchronized. A `deferred` label, TODO, or Handoff alone never waives an AC
   that remains in target scope; downstream-only items may be non-blocking only after that
   ownership check.
2. Evidence: every target-Milestone closure criterion has a replayable real verification path.
3. State: the target Task, matrix, ROADMAP row, Decision, version anchors, and Handoff refresh
   together. `Task.md` remains a current snapshot: closed cards retain closure evidence and
   per-card log pointers, while superseded execution narratives remain only in those logs.
4. Integration: no accepted branch owned by the target Milestone remains outside the shared
   baseline and no lane or lock it owns remains active. An unrelated resource conflict may
   delay a mechanical integration or state-refresh action, but it does not alter semantic
   closure eligibility.

## Author and combined-review loop

At `author-returned`, reject incomplete or premature state changes to the same Author as
`author-rework`; otherwise create `candidate-anchored`. Dispatch an independent combined
Critic/Reviewer across Requirement, Design, Task, code, evidence, and the closure candidate;
retain its identity ref. At return, the orchestrator adjudicates findings, resumes the same
closure Author in `author-revising`, and sends blocker fixes to the same Critic/Reviewer for
targeted recheck. Replacing that reviewer requires a full combined review. Enter
`acceptance-ready` only when verification and combined review have no unresolved blocker.

## Upstream change during closure

If closing evidence reveals that approved WhitePaper, ROADMAP, Goal, Requirement, Design, or
Task meaning must change, record the old anchor, semantic delta, and impact cone, then use the
router's controlled-change route. First decide whether the finding changes a target-Milestone
criterion. A downstream implementation or confirmation question becomes a non-blocking TODO or
Handoff with receiving Milestone/owner, question, trigger, possible impact or default
assumption; it does not withhold target closure. Pause or revise only affected criteria, cards,
documents, tests, and evidence. After the new authority anchor receives its required review or approval,
rerun affected verification plus any full-regression or E2E gate independently required for
closure, then resume the same closure Author. Do not repeat unrelated authoring stages. Meaning-preserving mechanical changes need
same-batch refresh and machine checks without reapproval.

## Machine checks and checklist

Have the Verifier run `check --preset gmgn-v1 --json` and relevant gates when DocStar is
available. DocStar IDs, edges, `brief`, `check`, and `verify` are structural measurements; they
do not decide Milestone ownership, dependency legality, or closure eligibility. Verify
DocStar `classification_complete` as a structural result, but do not treat it as proof that
GMGN semantic scope classification is complete. Record every finding with evidence and exactly
one GMGN classification: `target-scoped | candidate-introduced-or-polluted |
external-pre-existing`. A non-zero gate finding in either of the first two classes blocks. Use
`external-pre-existing` as debt only when evidence proves both that it is outside the target
scope and that it predates the closing candidate. If evidence cannot prove
`external-pre-existing`, scope classification is incomplete and closure is blocked. A tool
execution failure or unparseable result also blocks because measurement did not complete. When
DocStar is absent, run equivalent repository link/table checks and disclose that substitution. The closure Author completes the locale-matched
`pre-close-checklist.md` against the Verifier's evidence; the combined reviewer challenges it.

## Presentation and close

Present scope, evidence, known debt, remaining material risks—or that none are known—and the
version anchor to the owner. Only after explicit acceptance, set state to `accepted` and dispatch an Integrator:

- set the target Milestone and its normative chain to `closed` where appropriate;
- create/update Handoff with `type: handoff`, `nature: descriptive`, one-line state,
  baseline, completed work, non-blocking downstream TODOs, risks, authority pointers, and next
  command;
- if DocStar uses a project classification mapping, reuse a registered type/token;
- refresh ROADMAP, Task, matrix, Decision, version anchors, execution-log links, and evidence
  pointers in the same batch; reject a project-wide or Milestone-wide combined execution log,
  then prepare or create the topic commit under repository policy.

The orchestrator checks disk and evidence, then marks `node-complete`. Do not push, publish,
deploy, or release unless separately authorized.

Closure evidence is reusable and remains bound to this immutable closing anchor. A later tag,
package, upload, deployment handoff, authentication retry, or local installation must not
redispatch the closure Author, combined Critic/Reviewer, or closure Verifier merely because it
is a release operation. Route an authorized release through `release`; that skill validates
the artifact delta and regenerates only evidence whose inputs changed.

## Exit

Update the target ROADMAP row with closure evidence and the receiving state. Downstream
Milestones retain their own states and closure gates. If the owner authorizes distribution,
**REQUIRED next skill: `release`**. Otherwise use **REQUIRED next skill: `roadmap`** for
maintenance or the next milestone.

Before every substantive return, perform a task-specific self-check and correct defects. Do
not output a fixed `Reflection` section. Disclose only material unresolved risks that could
change the conclusion, decision, acceptance, or downstream work; otherwise omit the
disclosure. Approval, acceptance, and closure always state remaining material risks or that
none are known.
