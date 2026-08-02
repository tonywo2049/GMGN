---
name: close-milestone
description: "Use when every target-milestone task is closed and traceability is full to reconcile scope, run any still-required milestone regression/E2E, independently review the closure candidate, record owner review, and backfill ROADMAP plus any needed receiver handoff. 目标 Milestone 自有任务全部关账后做范围核对、仍必需的回归/E2E、独立关账审查与负责人复核。"
---

# Close a milestone

<HARD-GATE>The target ROADMAP Milestone must currently have `state: initiated` and `accepted_result: none`. Every task owned by `target_milestone_id` must be `closed` on one `shared_baseline_anchor`, whose value is the shortest unambiguous commit reference; its integration queue and active lanes must be empty; every ROADMAP deliverable and success signal must map through Goal Close outcomes and in-scope ACs to sufficient evidence; and every executed task must link `execution/<card_id>/Card.md` plus a closed `Log.md` current snapshot and final evidence. A required product, integration, regression, recovery, or E2E path still needs evidence when Goal or Requirement makes it part of Close. Downstream work does not block unless it proves an in-scope criterion remains undecided or unproved. Otherwise return to the owning stage before closure.</HARD-GATE>

## Reconcile the closing commit

The primary orchestrator records the exact Goal/Requirement/Design/applicable Contract/Task
commits and machine state. The assigned Adjudicator checks:

- all target tasks and their execution pointers;
- Card completion contracts against Log current evidence;
- ROADMAP deliverable and success signal → Goal Close outcome → AC → sufficient
  evidence coverage; Task, test, and E2E are included only when applicable to that evidence;
- every ROADMAP deliverable against its accepted result;
- every retained Contract ID against its provider implementation, every in-scope consumer,
  conformance/integration evidence, structural authority, and observable failure behavior;
- no target lane, lock, accepted candidate, or queue entry remains outside the shared baseline;
- known debt and material risk are classified without silently waiving an AC.

The Design-stage `design/Contract.md`, its split contracts, and structural authorities were
one approved working baseline. If closure finds a semantic contract/implementation mismatch,
return only that impact cone to `write-design`, obtain the new reviewed Bundle commit, refresh
affected tasks and evidence, and then restart closure. Closure cannot silently rewrite the
contract to match code.

Task remains a macro index. Material decisions and final commands, anchors, review, and
required evidence stay in each card's Log.

## Reuse evidence before rerunning it

Do not dispatch a Verifier merely because closure started. Reuse the active Adjudicator review
bound to the closing commit, post-fix machine checks, and any risk-triggered verification when
they already cover every ROADMAP deliverable, Goal Close outcome, the Milestone's required
E2E, regression, or integration paths, relevant negative/recovery outcomes, environment, and
limitations.

The primary orchestrator runs any missing or stale deterministic local checks from the closure
check plan and forwards exact evidence without interpretation. Apply `not-required` or
`required:<trigger>` mechanically when the current assurance policy and recorded facts make
the classification explicit; the Adjudicator resolves only judgment-dependent trigger
applicability. The primary orchestrator creates one fresh Verifier only for
`required:<trigger>` from the classification, reason, and minimum verification plan. It
returns exact commands, environment, revision, exit codes, results, limitations, and side
effects. A skipped or unavailable required command is not a pass. The Verifier's interim
questions follow the dispatch contract.

## Closure candidate and review

The Adjudicator prepares one closure Author brief from the exact Milestone state. The Author
writes and revises the closure candidate under the shared dispatch contract; the primary
orchestrator does not draft it.

The candidate contains deliverable, success-signal, and Goal Close-outcome reconciliation,
evidence map, controlled debt, remaining material risks or a supported none-known statement,
proposed state changes, the proposed closing Contract commit when applicable, and a Handoff
plan only when a receiving operator lacks an existing authority for needed information.
Prepare the actual Milestone, Contract, ROADMAP, Task, traceability, and Handoff state in an
isolated closure commit; it has no effect on the shared baseline before closure review.

Process the candidate through the registered `gmgn` Skill's shared dispatch rules. The primary
orchestrator fixes candidate identity and runs the closure plan's deterministic checks. The
same active Adjudicator directly reviews the complete fixed closure candidate: its document
meaning and every applicable implementation/test diff. If both surfaces exist, it handles
them as one continuous case under the owning stage and code-review contracts, not as two role
dispatches. It accepts or sends the minimum in-scope finding to the same closure Author. The
Author commits a new complete candidate, the primary orchestrator reruns only affected checks,
and the same Adjudicator inspects the exact fix delta. A fix that expands authority, scope, or
closure meaning becomes a separately scoped change.

## Structural checks

Before committing the review candidate and the blocker-resolved final candidate, use DocStar
`check`/`verify` when available and classify introduced findings. DocStar measures
links, entities, and structure; it does not decide scope ownership or semantic closure. A tool
failure, unparseable result, or target-scoped unresolved finding blocks. When DocStar is absent,
run equivalent repository link/table checks and record the substitution.

## Owner review and integration

When required evidence exists and no accepted review blocker remains, the Adjudicator presents
scope, evidence, debt, risks, and the shortest unambiguous closing-commit reference through the
primary orchestrator's exact relay. Owner review is one closure review input, not irrevocable
authority or separate integration authorization. Resolve its material findings through the
same active Adjudicator and closure Author case. When required evidence exists and that
Adjudicator has accepted the complete candidate, the primary orchestrator integrates the exact
closing commit.
That commit already contains:

- the target Milestone and its appropriate normative chain marked closed;
- the reconciled implementation-matching Contract marked `closed`;
- a Handoff only when a receiver needs one, using the closing commit, applicable evidence,
  environment, risks, authority pointers, and next command;
- ROADMAP `state: closed` plus one canonical `accepted_result` link supplied by this closure,
  refreshed Task macro states, AC traceability, execution links, and commit references;
- the final diff/link/repository check results.

Integrate that exact commit without creating post-review closure content. If it cannot be
integrated without changing closure content, stop and prepare a new committed closure
candidate and rerun only affected machine checks and Adjudicator review.

Do not create an Integrator agent. External operations require the shared authorization from
the dispatch contract. `release` reuses commit-bound review and verification evidence and
regenerates only evidence invalidated by changed packaging or environment inputs.

## Exit

If the shared authorization includes distribution, use **REQUIRED next skill: `release`**.
Otherwise return to `roadmap` maintenance or the next Milestone.
