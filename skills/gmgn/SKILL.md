---
name: gmgn
description: "Use first to route workflow-driven project work: new projects, product ideas, research, feature development, bug fixes, refactors, WhitePaper, ROADMAP, PRD, requirements, design, task docs, coding delegation, launch, release, acceptance, or closure. 凡要按流程推进研发、调研、功能、修 bug、重构、写白皮书/ROADMAP/PRD/需求/设计/任务、派活、上线发布、验收关账，或用户说按 GMGN/下一步做什么时使用。"
---

# GMGN router: repository state → next stage

Use this runtime method to locate the stage, then invoke the specialized skill.

## Language and contract

Infer `en` or `zh-CN` from approved project documents, then the user's language. Keep machine
tokens and IDs in English. Load the English-only layout-free
[writing contract](references/en/writing-contract.md) when writing; artifact prose may still
use the active project locale.

## Route by observable state

| State | Route |
|---|---|
| New idea; no approved WhitePaper | `brainstorm` |
| Approved WhitePaper; ROADMAP absent or changing | `roadmap` |
| Owner starts a `not-started` milestone | `write-goal` |
| Goal exists; Requirement absent or changing | `write-requirement` |
| Requirement reviewed; Design absent or changing | `write-design` |
| Design reviewed; Task absent or changing | `write-task` |
| Confirmed Task rows can run or a target-Milestone lane remains active | `run-task` |
| Every target-Milestone task is closed on one baseline but closure is not accepted | `close-milestone` |
| An immutable candidate is accepted and distribution is requested | `release` |

From `write-goal` onward, record `target_milestone_id` and the available Goal, Requirement,
Design, and Task anchors. A cross-Milestone link gives context, not execution authority. If the
owner authorizes several Milestones, keep separate execution sets and closure decisions.

## Roles and fresh-agent dispatch

Use the English-only [dispatch contract](references/en/dispatch-and-handoff.md).

The primary orchestrator keeps context, selects the stage, prepares briefs, adjudicates
findings, integrates accepted candidates, and updates shared state. It is not a delegated
agent. It may directly write WhitePaper, ROADMAP, Goal, Requirement, Design, or Task when that
uses its complete context best; otherwise it delegates a bounded Author. During long-running
work, it must not send a progress update while observable state is unchanged; update only for
material progress, a blocker, a decision request, or the final result.

Every delegated Author, Coder, Critic, Reviewer, Verifier, or Researcher is single-use. Prepare
the full role brief before creation, start with no parent or earlier-agent history, accept one
bounded return, and retire the agent. A later authoring or coding attempt, separately scoped
semantic or implementation change, or later verification uses a new brief and new agent.
Critic and Reviewer are not redispatched to recheck fixes from their completed round. Never
resume or repurpose a returned role.

Fresh identity does not require a full role set after each edit. Select roles by impact:

| Changed surface | Independent role |
|---|---|
| WhitePaper/ROADMAP/Goal/Requirement/Design/Task meaning | Critic |
| Implementation or test-code diff, including deterministic local execution | Reviewer |
| Recorded trigger from the local [assurance policy](references/en/assurance-policy.json) | Verifier after review blockers clear |
| Equivalent links, formatting, pointers, or status | Machine checks only |

The Critic/Reviewer rows above are evaluated only once, immediately before the change batch's
review round. An accepted finding fix remains part of that reviewed batch and does not
re-enter role selection.

Freeze a candidate before review. Each semantic change batch or task execution uses
`review_policy: single-pass`: at most one Critic/Reviewer round; both roles may run in that
round when both surfaces changed. Collect all active findings before changing the candidate.
The primary orchestrator adjudicates once,
batches accepted blockers, checks their resolution, and runs affected machine checks. This
bounded resolution check does not search for new findings. Do not resume or create a
Critic/Reviewer for those fixes. If a fix expands authority, scope, or behavior
beyond the accepted findings, split it into a separately scoped change. Record the reviewed
anchor, findings and rulings, exact fix delta, and post-fix checks at the final anchor.
Non-blocking suggestions do not reopen an otherwise acceptable candidate. The Reviewer runs
the prepared deterministic local checks and returns the commands and results with its code
findings. After accepted fixes, the primary orchestrator checks the fix delta and reruns
affected machine checks without another independent round.

Critic and Reviewer do not maximize finding count; a valid review may return no findings.
Report an issue only when leaving it unresolved creates concrete material harm, no accepted
effective fallback contains that harm, and a smallest sufficient correction can be stated.
Omit observations that do not change acceptance or the next action.

A fresh Verifier is exceptional, not default. Classify the final candidate from the local
assurance policy as `not-required` or `required:<trigger>`. Do not dispatch a Verifier while
accepted review blockers remain unresolved; when required, put the classification, reason,
and minimum verification plan in its brief, bind its evidence to the blocker-resolved final
candidate, and stop when the trigger is decided. A required check cannot be waived unless an
accepted fallback is itself successfully verified.

## Document nodes

The primary session or a fresh Author creates one candidate, self-checks it, and anchors it.
Every semantic change batch receives one fresh independent Critic. If blockers are accepted,
the primary session fixes them directly or uses a fresh Author, then checks each resolution
and runs affected machine checks without another Critic. The primary orchestrator performs
mechanical propagation, links, machine checks, and integration. Do not create an Integrator
agent.

## Task execution

`Task.md` is the compact Milestone index: stable task rows, AC mapping, dependencies, macro
status, and execution pointers. After the execution set is confirmed, `run-task` creates for
each selected task:

- `execution/<card_id>/Card.md` — normative execution and TDD contract, linked to `Log.md`;
- `execution/<card_id>/Log.md` — descriptive current snapshot, material decisions, and final
  evidence when closed. Its single `latest_event` pointer preserves DocStar compatibility
  without requiring a general event ledger.

Run-task continuously fills a dependency-aware ready set. Before waiting or acting as a Coder,
the primary orchestrator scans every task in the confirmed execution set, not only the current
card or active lane, and dispatches every ready, non-conflicting task that fits currently
available capacity. Compliance checks run only at a real boundary or material state change.
Concurrent writing lanes are isolated; a sole writer may use the current workspace. Freeze a
diff/content hash for a sole writer and require a complete base-to-tip diff or ordered commit
chain only for an isolated handoff. Before integration, confirm that integrated content is the
reviewed content; a changed commit SHA alone does not invalidate equivalent content.

Discovery does not expand an active Card. Keep a newly found issue in the Card only when it
blocks the Card outcome or a prepared required check, has no accepted effective fallback, and
its smallest sufficient correction stays inside existing authority without adding another
independently testable outcome. Otherwise omit it, present a materially valuable separate
candidate, or route changed authority upstream. Close the task as soon as the Card outcome,
prepared checks, accepted blockers, and any required verification are satisfied.

Accepted fixes may use another fresh Coder, but they are not sent to another Reviewer. The
primary orchestrator checks their resolution and runs affected machine checks. Dispatch a
fresh Verifier on the resulting final candidate only for the exceptional risk triggers above.
Do not repeat the same verification before and after clean mechanical integration without a
recorded risk reason.

When no implementation lane can run in parallel with useful orchestrator work, the primary
session may serve as one lane's Coder. It cannot take over an assigned lane and
cannot replace independent review or risk-triggered verification.

Agent waiting is event-driven: exhaust useful work, wait once with the longest safe interval,
and treat timeout as a liveness checkpoint rather than a polling trigger. A `list_agents`
snapshot is allowed only when a scheduling/capacity decision needs current state, a wait timed
out without an unambiguous agent state, or received lifecycle events conflict. One call serves
one decision point; do not query again until a material lifecycle event, candidate, blocker, or
scheduling condition changes. There is no periodic list interval. A long-running primary
session sends no heartbeat when state is unchanged; it reports only material progress, a
blocker, a decision request, or the final result. Telemetry is out-of-band observation and never
changes routing, readiness, acceptance, or closure.

## Controlled-change routing

Route a semantic change to the single authority that owns it:

| Authority changed | Route |
|---|---|
| WhitePaper problem, goal, scope, invariant, or interpretation | `brainstorm` revision |
| ROADMAP sequencing, Milestone allocation, dependency, or qualitative acceptance picture | `roadmap` maintenance |
| Goal objective, boundary, slice, non-goal, or acceptance-scenario mapping | `write-goal` revision |
| Requirement, constraint, parameter, or AC | `write-requirement` revision |
| Design structure, interface, data, or failure path | `write-design` revision |
| Task division, dependency, AC mapping, status, or execution pointer | `write-task` revision |

Start from the approved anchor, record the semantic delta and impact cone, and update only
affected authority, tasks, code, tests, evidence, and state. Meaning-preserving mechanical
changes use machine checks without reapproval. A closed foundation remains closed; a current
Milestone change card may revise its still-authoritative Design or Decision without reopening
the historical Milestone.

For a narrow bug or mechanical one-step change, use the controlled bypass: identify the
smallest authority and acceptance condition, implement, independently review the diff, verify
the final executable candidate when required, and refresh state in the same batch. Do not
fabricate the full document chain.

<HARD-GATE>Never skip a missing prerequisite, redefine upstream meaning downstream, execute a referenced Milestone without owner authorization, let a delegated agent self-review, expose an unverified implementation combination as the shared baseline, or push/publish/deploy without explicit authority.</HARD-GATE>

Before every substantive return, perform a task-specific self-check and correct defects. Do
not output a fixed `Reflection` section. Disclose only unresolved material risk that could
change the decision, acceptance, or downstream work.
