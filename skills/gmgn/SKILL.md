---
name: gmgn
description: "Use first to route workflow-driven project work: new projects, product ideas, research, feature development, bug fixes, refactors, WhitePaper, ROADMAP, PRD, requirements, design, task docs, coding delegation, launch, release, acceptance, or closure. 凡要按流程或 workflow 推进研发、调研、功能开发、修 bug、重构、写白皮书/ROADMAP/PRD/需求/设计/任务、派活写代码、上线发布、验收关账，或用户说按 GMGN/按流程办/下一步做什么时使用。"
---

# GMGN router: repository state → next stage

Use this skill to locate the stage, then invoke the specialized skill. The normative method
is [GMGN.md](../../GMGN.md); Chinese is [GMGN.zh-CN.md](../../GMGN.zh-CN.md).

## Language and contract

Infer `en` or `zh-CN` from approved project documents, then the user's language. Keep the
machine contract English. Load the matching layout-free writing contract when writing documents:
[English](references/en/writing-contract.md) | [中文](references/zh-CN/writing-contract.md).

## Telemetry boundary

Telemetry is out-of-band observation, never execution, approval, or closure authority. Do not
ask a model to write telemetry logs or add them to a prompt, `Task.md`, or `Handoff`. Only
selected user-level hooks may emit privacy-safe lifecycle/tool metadata: opaque IDs, byte
counts, status, classifications, fork policy, and structured correlation IDs. Telemetry failure
never blocks routing or delivery and never changes a gate. Run `telemetry/report.py`
only when the user explicitly requests a retrospective.

Telemetry does not change DocStar or its JSON output. DocStar keeps a fresh full rebuild on
every invocation with no cache; hooks and reporters measure calls, elapsed time, command type,
and later grep/read outside DocStar. `grep_avoided` does not claim causation.

## Route by observable state

| State | Route |
|---|---|
| New idea; no approved WhitePaper | `brainstorm` |
| Approved WhitePaper; ROADMAP absent or being maintained | `roadmap` |
| Owner starts a `not-started` milestone | `write-goal` |
| Goal exists; Requirement absent or changing | `write-requirement` |
| Requirement reviewed; Design absent or changing | `write-design` |
| Design reviewed; Task absent or changing | `write-task` |
| One or more confirmed cards in the target Milestone execution set are ready or one of its lanes remains active | `run-task` |
| All target Milestone cards closed on one shared baseline, its integration entries empty, its traceability full | `close-milestone` |

Before `write-goal` and throughout every later Milestone skill, record `target_milestone_id`
and every available Goal, Requirement, Design, and Task authority anchor for that Milestone.
Do not invent this ID for `brainstorm` or ROADMAP work without a selected Milestone. A
downstream reference or DocStar edge is context, not authorization: it never expands the
execution set or the closure gate. If the owner explicitly authorizes multiple Milestones,
keep one separately owned execution set and closing decision per Milestone.

## Runtime and role routing

Use the locale-matched [dispatch and agent-lifecycle contract](references/en/dispatch-and-handoff.md)
or [中文契约](references/zh-CN/dispatch-and-handoff.md). Runtime state is not document or work-item
state. Keep the node record and identity refs until `node-complete`.

- For WhitePaper, ROADMAP, Goal, Requirement, Design, and Task, the primary orchestrator
  selects the actual writer before writing starts: itself when its context makes direct
  authorship the clearest and least wasteful path, or a delegated Author when bounded
  isolation, specialization, or parallelism creates real value. Bind `author_ref` to that
  actual writer. WhitePaper normally favors the primary session because it holds the complete
  owner dialogue. These factors guide the orchestrator's judgment; they are not eligibility
  gates. Every semantic candidate still receives an independent Critic.
- Accepted findings return to the same `author_ref`; blocker rechecks return to the same
  `critic_ref`. When `author_ref` is the primary session, it applies accepted findings
  directly; a delegated Author and Critic communicate only through the orchestrator.
- `run-task` maintains a rolling ready set for the recorded target Milestone and one lane per
  owned card. Each lane has its own Coder,
  Reviewer, and Verifier identities; fixes, affected review, and affected verification return
  to those same agents. One Integrator serially owns the integration queue, shared baseline,
  `Task.md`, per-card execution logs, and traceability.
- `close-milestone` dispatches target-scoped independent verification, a closure Author, a
  combined Critic/Reviewer, and an Integrator after owner acceptance.
- A platform that cannot resume an identity enters `agent-unavailable`; replacement is
  explicit, and replacing a Critic or Reviewer requires a full review.

For specification-document nodes, select and bind the actual writer, then follow
`ready-to-dispatch → author-active → author-returned → candidate-anchored → critic-active →
critic-returned`. When `author_ref` is the primary session, author states are lifecycle
checkpoints rather than Author-agent dispatches. Accepted findings loop through
`author-revising` with the same `author_ref` and, for blockers, `critic-rechecking` with the
same Critic. Finish through `acceptance-ready → accepted`. Use `integrating → node-complete`
only when the candidate crosses an isolated-workspace, concurrent-writer, or shared-baseline
boundary; otherwise the recorded writer may complete accepted same-batch propagation and
machine checks directly before `node-complete`.

For implementation, keep one project-wide lane. Use
`lane_key = project_scope_id + card_id` as its identity; `run_id` records an execution attempt
and does not define uniqueness. Before any writer dispatch, atomically claim and verify the
card and canonical `worktree_path` in the
authority project's shared lane registry. Record `owner_thread_id`, `owner_run_id`,
`ownership_epoch`, and `coder_ref`; a thread-local agent list or cross-task scan is diagnostic,
not proof that the lane is free. Claim first without Coder identity, then explicitly bind one
`coder_ref`; every later verify, anchor, or normal release requires that exact ref. Bind the
implementation repository's Git metadata/stat identity and object format too. Reject returns
from another owner, a stale epoch, missing/wrong Coder, or a recreated repository path. If the
owner cannot be confirmed, enter `owner-unreachable` and do not reclaim automatically. Reviewer
and Verifier may coexist only as read-only agents.

Every return, integration, conflict, or block recomputes the ready set and fills available
capacity. Concurrency is the minimum of platform concurrency, ready cards, isolated
workspaces, and exclusive-resource capacity; never hard-code it. On Codex, fill the current
task's actual subagent capacity first. If ready cards remain, the owner explicitly authorized
cross-task fan-out for this run, and create/list/read/wait/send task capabilities exist, create
one worker main task per remaining lane without waiting for a local slot. Issue all currently
allowed creates before the first blocking wait. Resolve queued `clientThreadId` to actual
`threadId + hostId` before wait/claim/activation; preserve all opaque IDs and cursors. Each
read-only bootstrap owns one prospective lane/worktree and may create one read-only Coder to
report `coder_ref`. The scheduler alone performs claim/bind/verify and owns the ready set, lane
registry, integration queue, and shared baseline. A worker cannot mutate registry state,
recursively create main tasks, adjudicate, accept, integrate, edit `Task.md`, push, or publish.
Group waits dynamically by runtime capacity, wake on any completion, and refill immediately.
Without authorization or capabilities, use rolling dispatch in the current task.

A lane also records `workspace_mode`, `worktree_path`, `branch_ref`, `baseline_anchor`,
`candidate_anchor`, `write_set`, `conflict_domains`, `runtime_locks`, `integration_queue_ref`,
and `shared_baseline_anchor`. Its normal tail is `accepted → integration-queued → integrating
→ post-integration-verifying → node-complete`; branch acceptance is not card closure.

Every worker Coder return stops at `candidate-awaiting-anchor`. Only after scheduler verify,
candidate/path/`write_set` checks, atomic anchor, and an explicit candidate-scoped
`review-authorized` message may that worker dispatch Reviewer. Revisions repeat the same gate.

The Integrator first applies an accepted local-commit `candidate_anchor` to an isolated
temporary combination based on the current shared baseline. A baseline advance alone does not
force `rebase-required`; use it only when clean mechanical application fails, dependency/spec
meaning is invalid, or Coder judgment is needed. Resume the same Verifier with the temporary
workspace facts. Advance `shared_baseline_anchor` only after verification and mechanical
ledger checks pass; otherwise abort/discard the temporary candidate, prove the original shared
workspace clean, and continue unrelated lanes.

## Controlled-change routing

Workflow nodes are not one-way. Route a change to the single authority for the content:

| Approved authority that needs a semantic change | Route |
|---|---|
| WhitePaper problem, goal, scope, harm order, invariant, or interpretation | `brainstorm` revision mode |
| ROADMAP sequencing, milestone allocation, dependency, or qualitative completion picture | `roadmap` maintenance mode |
| Goal objective, boundary, slice, non-goal, or completion picture | `write-goal` revision mode |
| Requirement, constraint, parameter authority, or acceptance criterion | `write-requirement` revision mode |
| Design structure, interface, data, failure path, or R-AC mapping | `write-design` revision mode |
| Task card, dependency, execution order, test anchor, or traceability mapping | `write-task` revision mode |

Start from the approved old anchor, record the semantic delta and impact cone, update the
authority, then propagate only through affected upstream/downstream representations and
dependent work. Review, approve, and verify only affected content; do not rerun unrelated
stages. Old approval remains attached to the old anchor. The new anchor needs the approval
appropriate to that authority only when the change alters a decision or reasonable
understanding. Meaning-preserving mechanical changes use same-batch refresh and machine
checks without reapproval. An explicit equivalence record may let the new anchor retain the
document approval state by citing the old approved anchor; this is not a new approval.

A closed foundation or M0 Milestone is a historical declaration about its closing anchor, not
a promise that its technical selection can never change. An M0-originated Design, Decision, or
index remains the semantic authority. Later evidence uses a change card owned by the current
Milestone to revise that authority: record the trigger, old and new anchors, `supersedes`, and
impact cone. Keep the M0 state and its old closure anchor closed; do not reopen M0 or rerun its
complete workflow. The current Milestone owns the change, implementation, and verification
work, not the M0-originated meaning.

For a narrow bug or mechanical one-step change, use the controlled bypass: identify scope,
the smallest authority/acceptance condition, implementation, test, independent review, and
same-batch status refresh. Do not fabricate a full chain; do not bypass WhitePaper, ROADMAP,
milestone initiation, scope expansion, or closure authority.

<HARD-GATE>Never route past a missing prerequisite, redefine upstream meaning in a downstream document, or execute a downstream Milestone merely because the target Milestone references it. The primary orchestrator may be the recorded writer for WhitePaper, ROADMAP, Goal, Requirement, Design, or Task, but it must make that writer choice explicit before writing, preserve the independent Critic, and must not silently take over work already assigned to another writer. It must not perform Coder, Reviewer, or Verifier work in place of those independent roles. An Integrator is mandatory whenever an accepted candidate crosses an isolated-workspace, concurrent-writer, or shared-baseline boundary; otherwise it is not a required ceremony. Pause dependent work whose premise changed until the semantic revision has the review or approval appropriate to its new version anchor. Agent-to-agent permission does not equal owner authorization. No push, publish, deployment, PR mutation, or external message unless the owner or project rules explicitly authorize it.</HARD-GATE>

Before every substantive return, perform a task-specific self-check and correct defects. Do
not output a fixed `Reflection` section. Disclose only material unresolved risks that could
change the conclusion, decision, acceptance, or downstream work; otherwise omit the
disclosure. Approval, acceptance, and closure always state remaining material risks or that
none are known.
