---
name: gmgn
description: "Use first to route workflow-driven project work: new projects, product ideas, research, feature development, bug fixes, refactors, WhitePaper, ROADMAP, PRD, requirements, design, task docs, coding delegation, launch, release, acceptance, or closure. 凡要按流程推进研发、调研、功能、修 bug、重构、写白皮书/ROADMAP/PRD/需求/设计/任务、派活、上线发布、验收关账，或用户说按 GMGN/下一步做什么时使用。"
---

# GMGN router: repository state → next stage

Use this skill to locate the stage, then invoke the specialized skill. The normative method is
[GMGN.md](../../GMGN.md); Chinese is [GMGN.zh-CN.md](../../GMGN.zh-CN.md).

## Language and contract

Infer `en` or `zh-CN` from approved project documents, then the user's language. Keep machine
tokens and IDs in English. Load the matching layout-free writing contract when writing:
[English](references/en/writing-contract.md) | [中文](references/zh-CN/writing-contract.md).

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

Use the locale-matched [dispatch contract](references/en/dispatch-and-handoff.md) or
[中文契约](references/zh-CN/dispatch-and-handoff.md).

The primary orchestrator keeps context, selects the stage, prepares briefs, adjudicates
findings, integrates accepted candidates, and updates shared state. It is not a delegated
agent. It may directly write WhitePaper, ROADMAP, Goal, Requirement, Design, or Task when that
uses its complete context best; otherwise it delegates a bounded Author.

Every delegated Author, Coder, Critic, Reviewer, Verifier, or Researcher is single-use. Prepare
the full role brief before creation, start with no parent or earlier-agent history, accept one
bounded return, and retire the agent. A revision, retry, recheck, or later verification uses a
new brief and new agent. Never resume or repurpose a returned role.

Fresh identity does not require a full role set after each edit. Select roles by impact:

| Changed surface | Independent role |
|---|---|
| WhitePaper/ROADMAP/Goal/Requirement/Design/Task meaning | Critic |
| Implementation or test-code diff | Reviewer |
| Executable result, environment, or package input | Verifier after review blockers clear |
| Equivalent links, formatting, pointers, or status | Machine checks only |

Freeze a candidate before review. Collect all active Critic and Reviewer findings before
changing it; the primary orchestrator adjudicates once and batches accepted blockers. A fresh
recheck role is dispatched only for affected scope. Non-blocking suggestions do not reopen an
otherwise acceptable candidate. Do not dispatch a Verifier while relevant review blockers
remain.

## Document nodes

The primary session or a fresh Author creates one candidate, self-checks it, and anchors it.
Every semantic candidate receives one fresh independent Critic. If blockers are accepted, the
primary session fixes them directly or uses a fresh Author, then a fresh Critic checks only the
affected semantic surface when the boundary is provable. The primary orchestrator performs
mechanical propagation, links, machine checks, and integration. Do not create an Integrator
agent.

## Task execution

`Task.md` is the compact Milestone index: stable task rows, AC mapping, dependencies, macro
status, and execution pointers. After the execution set is confirmed, `run-task` creates for
each selected task:

- `execution/<card_id>/Card.md` — normative execution and TDD contract, linked to `Log.md`;
- `execution/<card_id>/Log.md` — descriptive current snapshot with `latest_event`, plus
  append-only history.

Run-task continuously fills a dependency-aware ready set. Concurrent writing lanes are
isolated; a single non-colliding writer may use the verified current workspace. Each Coder
attempt is fresh. A returned candidate is anchored before a fresh Reviewer sees it.
Accepted fixes use another fresh Coder and only affected review roles. The final combination is
either a frozen sole-writer candidate already based on the unchanged shared baseline or an
isolated-lane candidate mechanically applied to a temporary workspace. One fresh Verifier
checks that final candidate when executable evidence is required. Do not repeat the same
verification before and after clean mechanical integration without a recorded risk reason.

When no implementation lane can run in parallel with useful orchestrator work, the primary
session may serve as one lane's Coder. It cannot take over an assigned lane and
cannot replace independent review or required verification.

Agent waiting is event-driven: exhaust useful work, wait once with the longest safe interval,
and treat timeout as a liveness checkpoint rather than a polling trigger. A `list_agents`
snapshot is allowed only when a scheduling/capacity decision needs current state, a wait timed
out without an unambiguous agent state, or received lifecycle events conflict. One call serves
one decision point; do not query again until a material lifecycle event, candidate, blocker, or
scheduling condition changes. There is no periodic list interval. Telemetry is out-of-band
observation and never changes routing, readiness, acceptance, or closure.

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
