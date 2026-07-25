---
name: close-milestone
description: "Use when every target-milestone task is closed and traceability is full to reconcile scope, run any still-required milestone regression/E2E, independently review the closure candidate, obtain owner acceptance, and backfill ROADMAP plus any needed receiver handoff. 目标 Milestone 自有任务全部关账后做范围核对、仍必需的回归/E2E、关账审查与负责人验收。"
---

# Close a milestone

<HARD-GATE>The target Milestone must have at least one ROADMAP end-to-end acceptance scenario covering its full owned outcome. Every task owned by `target_milestone_id` must be `closed` on one `shared_baseline_anchor`, whose value is the shortest unambiguous commit reference; its integration queue and active lanes must be empty; every in-scope AC and ROADMAP scenario must map to evidence; and every executed task must link `execution/<card_id>/Card.md` plus a closed `Log.md` current snapshot and final evidence. Downstream work does not block unless it proves an in-scope criterion remains undecided or unproved. Otherwise return to `run-task` or revise the owning authority.</HARD-GATE>

## Reconcile the closing commit

The primary orchestrator records the Goal/Requirement/Design/applicable Contract/Task commits
and checks:

- all target tasks and their execution pointers;
- Card completion contracts against Log current evidence;
- ROADMAP acceptance scenario → Goal slice → AC → task → test → evidence coverage;
- every ROADMAP deliverable against its accepted result and required canonical pointer;
- every retained Contract ID against its provider implementation, every in-scope consumer,
  conformance/integration evidence, and observable failure behavior;
- no target lane, lock, accepted candidate, or queue entry remains outside the shared baseline;
- known debt and material risk are classified without silently waiving an AC.

The Design-stage Contract was an approved working baseline. If closure finds a semantic
contract/implementation mismatch, return only that impact cone to `write-design`, obtain the
new reviewed working commit, refresh affected tasks and evidence, and then restart closure.
Closure cannot silently rewrite the contract to match code.

Task remains a compact macro index. Material decisions and final commands, anchors, review, and
required evidence stay in each card's Log.

## Reuse evidence before rerunning it

Do not dispatch a Verifier merely because closure started. Reuse Reviewer execution, post-fix
machine checks, and any risk-triggered verification when they are bound to the exact closing
commit and already cover every ROADMAP acceptance scenario, the Milestone's required
regression, real end-to-end or integration path, relevant negative/recovery outcomes,
environment, and limitations.

Put missing or stale deterministic local checks in the closure Reviewer's prepared plan.
Classify remaining final-candidate evidence as `not-required` or `required:<trigger>` using the
current assurance policy loaded through the registered `gmgn` Skill. Create one fresh Verifier
only for `required:<trigger>` and put the classification, reason, and minimum verification
plan in its brief. It returns exact commands, environment, revision, exit codes, results,
limitations, and side effects. A skipped or unavailable required command is not a pass. The
single return ends that Verifier.

## Closure candidate and review

The primary session normally writes the closure candidate because it owns the complete
Milestone state. Delegate only when a bounded Author handoff has real value; prepare its full
brief before creating that fresh single-use Author.

The candidate contains deliverable and acceptance-picture reconciliation, evidence map,
controlled debt, remaining material risks or a supported none-known statement, proposed state
changes, the proposed final Contract commit when applicable, and a Handoff plan only when a
receiving operator lacks an existing authority for needed information. Prepare the actual
Milestone, Contract, ROADMAP, Task, traceability, and Handoff state in an isolated closure
commit; it has no effect on the shared baseline before owner acceptance.

Commit the complete candidate locally after writer self-check and machine checks. Prepare one
brief naming its shortest unambiguous commit reference and create a fresh independent combined
Critic/Reviewer for Requirement–Design–Task–Card/Log–code–evidence
consistency, closure meaning, and any missing deterministic local checks. Collect the full
review before editing. The primary
orchestrator adjudicates once, batches accepted blockers, checks each resolution, and runs
affected machine checks without dispatching another Critic or Reviewer. A fix that expands
authority, scope, or closure meaning becomes a separately scoped change. Non-blocking
suggestions do not reopen closure. After accepted fixes, commit the blocker-resolved final
closure candidate and run affected machine checks. Present that exact closing commit for owner
acceptance only when required evidence exists and no accepted review blocker remains
unresolved.

## Structural checks

Before committing the review candidate and the blocker-resolved final candidate, use DocStar
`check`/`verify` when available and classify introduced findings. DocStar measures
links, entities, and structure; it does not decide scope ownership or semantic closure. A tool
failure, unparseable result, or target-scoped unresolved finding blocks. When DocStar is absent,
run equivalent repository link/table checks and record the substitution.

## Owner acceptance and integration

Present scope, evidence, debt, risks, and the shortest unambiguous closing-commit reference.
Owner acceptance binds to that exact commit. Only explicit acceptance authorizes integrating
it into the shared baseline. That commit already contains:

- the target Milestone and its appropriate normative chain marked closed;
- the reconciled implementation-matching Contract marked `closed`; this is the final frozen
  Contract for that Milestone;
- a Handoff only when a receiver needs one, using the closing commit, applicable evidence,
  environment, risks, authority pointers, and next command;
- refreshed ROADMAP deliverable pointers and acceptance-scenario links to accepted evidence,
  Task macro states, AC traceability, execution links, and commit references;
- the final diff/link/repository check results.

Integrate that exact commit without creating post-acceptance closure content. If it cannot be
integrated without changing closure content, stop and prepare a new committed closure
candidate instead of transferring the old acceptance.

Do not create an Integrator agent. Do not push, publish, deploy, or release without separate
authorization. `release` reuses commit-bound acceptance, review, and verification evidence and
regenerates only evidence invalidated by changed packaging or environment inputs.

## Exit

If distribution is authorized, use **REQUIRED next skill: `release`**. Otherwise return to
`roadmap` maintenance or the next Milestone. Before every substantive return, perform a
task-specific self-check and correct defects. Do not output a fixed `Reflection` section;
disclose only unresolved material risk.
