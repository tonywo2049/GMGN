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

Before direct or delegated writing, Critic, Reviewer, or Verifier work, exclude every
project-declared archive root from reads, briefs, generated context, authority, and evidence.
Never cite archived documents. Restore needed meaning to the active tree through its owning
authority before use.

## Route by observable state

| State | Route |
|---|---|
| New idea; no approved WhitePaper | `brainstorm` |
| Approved WhitePaper; ROADMAP absent or changing | `roadmap` |
| Owner starts a `not-started` milestone | `write-goal` |
| Goal exists; Requirement absent or changing | `write-requirement` |
| Requirement reviewed; Design-stage candidate absent or changing | `write-design` |
| Design-stage candidate reviewed; Task absent or changing | `write-task` |
| Confirmed Task rows can run or a target-Milestone lane remains active | `run-task` |
| Every target-Milestone task is closed on one baseline but closure is not accepted | `close-milestone` |
| An immutable candidate is accepted and distribution is requested | `release` |

From `write-goal` onward, record `target_milestone_id` and the available Goal, Requirement,
Design, applicable interface-Contract, and Task anchors. A cross-Milestone link gives context,
not execution authority. If the owner authorizes several Milestones, keep separate execution
sets and closure decisions.

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

Commit the complete candidate locally before review. Each semantic change batch or task execution uses
`review_policy: single-pass`: at most one Critic/Reviewer round; both roles may run in that
round when both surfaces changed. Collect all active findings before changing the candidate.
The primary orchestrator adjudicates once,
batches accepted blockers, checks their resolution, and runs affected machine checks. This
bounded resolution check does not search for new findings. Do not resume or create a
Critic/Reviewer for those fixes. If a fix expands authority, scope, or behavior
beyond the accepted findings, split it into a separately scoped change. Record the reviewed
commit, findings and rulings, exact fix delta, and post-fix checks at the final accepted commit.
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

## Minimality gates

Requirement, Design, and Task writers keep the least structure that satisfies the current Goal
and R/ACs. Each retained R/AC, design element, dependency, configuration item, and task must
name the current upstream outcome that would fail if it were removed. Their fresh Critic
attempts deletion, reuse, native behavior, or a direct solution and treats avoidable complexity
as a material acceptance finding because it propagates downstream. A possible future need is
not an owner.

`Design.md` is always the Design-stage authority. A current boundary between independently
developed modules, tasks, or teams requires a separate `Contract.md`; otherwise keep the
interface in Design. The contract is mandatory at such a boundary, while the separate file is
conditional on the boundary existing. When present, Design and Contract form one reviewed
bundle at one Git commit. Design acceptance makes it the shared implementation
baseline, not the final frozen contract. `close-milestone` freezes the implementation-matching
Contract as `closed`. Do not invent a parallel API-version workflow unless a current
compatibility requirement needs coexisting versions.

Code minimality uses the separately installed
[Ponytail](https://github.com/DietrichGebert/ponytail) plugin. Every run-task Coder brief
requires `ponytail:ponytail` at `full`. A run-task Reviewer brief requires
`ponytail:ponytail-review` when its candidate contains implementation or test-code changes. The
role loads the named Skill through normal discovery before writing or accepting that code.
Missing Ponytail blocks that code task. Ponytail review stays inside the single Reviewer round
and supplements rather than replaces correctness, regression, safety, data, acceptance, and
deterministic local execution.

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
Concurrent writing lanes are isolated; a sole writer may use the current workspace. Commit
the complete candidate locally before review and identify it with the shortest unambiguous
commit reference. An isolated handoff also returns the complete base-to-candidate commit
range. Before integration, confirm through Git that integrated content matches the reviewed
commit; a different integration commit is acceptable only when the reviewed source, build
inputs, and normative content are unchanged. Full-length commit object IDs, diff/content
hashes, and checksums are not workflow anchors.

Discovery does not expand an active Card. Keep a newly found issue in the Card only when it
blocks the Card outcome or a prepared required check, has no accepted effective fallback, and
its smallest sufficient correction stays inside existing authority without adding another
independently testable outcome. Otherwise omit it, present a materially valuable separate
candidate, or route changed authority upstream. Close the task as soon as the Card outcome,
prepared checks, accepted blockers, and any required verification are satisfied.

All Coder lanes use the same current approved Design Bundle commit. A Coder cannot edit shared
interface authority; when implementation evidence contradicts it, the Coder returns the
evidence, smallest proposed delta, and affected tasks. The primary orchestrator keeps
unaffected lanes running, classifies a meaning-preserving clarification for same-batch machine
checks, and routes a semantic Design/Contract change through `write-design` for one new bundle
commit and its required Critic round.

Accepted fixes may use another fresh Coder, but they are not sent to another Reviewer. The
primary orchestrator checks their resolution and runs affected machine checks. Dispatch a
fresh Verifier on the resulting final candidate only for the exceptional risk triggers above.
Do not repeat the same verification before and after clean mechanical integration without a
recorded risk reason.

When no implementation lane can run in parallel with useful orchestrator work, the primary
session may serve as one lane's Coder. It cannot take over an assigned lane and
cannot replace independent review or risk-triggered verification.

Agent waiting is event-driven. After useful work is exhausted, wait for agent events.
Every Codex `wait_agent` call uses `agent_wait_timeout_ms = 3600000` (1 hour). Routine
progress-update cadence never shortens it. A timeout has no workflow meaning. If an agent is
known to remain `running`, immediately re-arm the same one-hour wait without inserting
`list_agents`, another status query, or a user update between unchanged timeouts. A timeout
alone is not a `list_agents` trigger. Use one
`list_agents` snapshot only when a real scheduling/capacity decision cannot be made from
received lifecycle events or those events conflict; do not query again until a material
lifecycle event or scheduling condition changes.

The primary orchestrator must not interrupt, terminate, or kill an agent merely because it has
not returned content, is silent or slow, or crossed one or more wait timeouts. Stop it only on
explicit user cancellation or concrete evidence that it has hard-failed, its scope is invalid,
or continuing is unsafe. While observable state is unchanged, do not report a wait timeout,
silence, absence of content, agent count, or `running` status. Report only material progress, a
blocker, a decision request, or the final result. Telemetry is out-of-band observation and
never changes routing, readiness, acceptance, or closure.

## Controlled-change routing

Route a semantic change to the single authority that owns it:

| Authority changed | Route |
|---|---|
| WhitePaper problem, goal, scope, invariant, or interpretation | `brainstorm` revision |
| ROADMAP sequencing, Milestone allocation, deliverable, dependency, qualitative acceptance picture, Backlog placement, or Handoff placement | `roadmap` maintenance |
| Goal objective, boundary, non-goal, result-based slice, or ROADMAP deliverable/acceptance-scenario mapping | `write-goal` revision |
| Requirement behavior, quantified parameter, constraint, or decidable AC | `write-requirement` revision |
| Design structure, implementation-specific parameter or decision, cross-task interface contract, data, or failure path | `write-design` revision |
| Task division, dependency, AC mapping, status, or execution pointer | `write-task` revision |

Start from the approved commit, record the semantic delta and impact cone, and update only
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
