---
name: close-milestone
description: "Use when every target-milestone task is closed and traceability is full to reconcile scope, run any still-required milestone regression/E2E, independently review the closure candidate, obtain owner acceptance, and backfill ROADMAP plus any needed receiver handoff. 目标 Milestone 自有任务全部关账后做范围核对、仍必需的回归/E2E、关账审查与负责人验收。"
---

# Close a milestone

<HARD-GATE>Every task owned by `target_milestone_id` must be `closed` on one `shared_baseline_anchor`; its integration queue and active lanes must be empty; every in-scope AC must map to a task and evidence; and every executed task must link `execution/<card_id>/Card.md` plus a closed `Log.md` current snapshot and final event. Downstream work does not block unless it proves an in-scope criterion remains undecided or unproved. Otherwise return to `run-task` or revise the owning authority.</HARD-GATE>

## Reconcile the closing anchor

The primary orchestrator records the Goal/Requirement/Design/Task anchors and checks:

- all target tasks and their execution pointers;
- Card completion contracts against Log current evidence;
- AC → task → test → evidence coverage;
- no target lane, lock, accepted candidate, or queue entry remains outside the shared baseline;
- known debt and material risk are classified without silently waiving an AC.

Task remains a compact macro index. Detailed commands, anchors, blockers, and event history
stay in each card's Log.

## Reuse evidence before rerunning it

Do not dispatch a Verifier merely because closure started. Reuse verification evidence when it
is bound to the exact closing anchor and already covers the Milestone's required regression,
real path, negative/recovery cases, environment, and limitations.

If any required closure evidence is missing, stale, environment-specific, or explicitly
mandated at Milestone scope, prepare a complete brief and create one fresh Verifier. It runs
only the missing or invalidated plan and returns exact commands, environment, revision, exit
codes, results, limitations, and side effects. A skipped or unavailable required command is not
a pass. The single return ends that Verifier.

## Closure candidate and review

The primary session normally writes the closure candidate because it owns the complete
Milestone state. Delegate only when a bounded Author handoff has real value; prepare its full
brief before creating that fresh single-use Author.

The candidate contains scope reconciliation, evidence map, controlled debt, remaining
material risks or a supported none-known statement, proposed state changes, and a Handoff plan
only when a receiving operator lacks an existing authority for needed information. It does not
mark the Milestone closed before owner acceptance.

Freeze the candidate after writer self-check and machine checks. Prepare one brief and create a
fresh independent combined Critic/Reviewer for Requirement–Design–Task–Card/Log–code–evidence
consistency and closure meaning. Collect the full review before editing. The primary
orchestrator adjudicates once and batches accepted blockers; later semantic/diff recheck uses a
fresh agent only for affected scope. Non-blocking suggestions do not reopen closure. Enter
Present the candidate for owner acceptance only when required evidence and review have no blocker.

## Structural checks

Use DocStar `check`/`verify` when available and classify introduced findings. DocStar measures
links, entities, and structure; it does not decide scope ownership or semantic closure. A tool
failure, unparseable result, or target-scoped unresolved finding blocks. When DocStar is absent,
run equivalent repository link/table checks and record the substitution.

## Owner acceptance and integration

Present scope, evidence, debt, risks, and immutable closing anchor. Only explicit owner
acceptance authorizes the primary orchestrator to:

- close the target Milestone and its appropriate normative chain;
- create/update Handoff only when a receiver needs one, using the accepted anchor, acceptance
  reference, applicable evidence, environment, risks, authority pointers, and next command;
- refresh ROADMAP, Task macro states, AC traceability, execution links, and version anchors;
- run final diff/link/repository checks and create the local closure commit under project policy.

Do not create an Integrator agent. Do not push, publish, deploy, or release without separate
authorization. `release` reuses exact-anchor acceptance, review, and verification evidence and
regenerates only evidence invalidated by changed packaging or environment inputs.

## Exit

If distribution is authorized, use **REQUIRED next skill: `release`**. Otherwise return to
`roadmap` maintenance or the next Milestone. Before every substantive return, perform a
task-specific self-check and correct defects. Do not output a fixed `Reflection` section;
disclose only unresolved material risk.
