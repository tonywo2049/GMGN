---
name: run-task
description: "Use when one or more approved Task.md rows are confirmed: materialize per-card execution contracts, run every ready implementation task through bounded writer lanes, review affected diffs, verify the final candidate once by default, integrate, and close. 已确认任务集后创建单卡 Card/Log、滚动并行开发、按影响复审、默认只验证最终候选一次并关账。"
---

# Run confirmed task cards

<HARD-GATE>Every dispatched task must exist in an independently reviewed and primary-orchestrator-accepted `Task.md`, belong to the confirmed `target_milestone_id` execution set, and have valid upstream authority. A task is ready only when its Task prerequisites are closed on the shared baseline and any declared shared-resource constraint is available. If implementation changes upstream meaning, stop only its impact cone and revise that authority.</HARD-GATE>

The primary orchestrator owns scheduling, adjudication, shared state, integration, Task status,
and per-card execution documents. It may be the Coder for one task only when no useful
implementation work can run in parallel with orchestration; independent review and required
verification remain separate.

Use the locale-matched [dispatch contract](../gmgn/references/en/dispatch-and-handoff.md) or
[中文契约](../gmgn/references/zh-CN/dispatch-and-handoff.md).

## 1. Materialize execution documents

Before the first Coder dispatch, the primary orchestrator creates exactly two files for each
confirmed task selected for this run:

1. `execution/<card_id>/Card.md` first. It is normative and contains the stable task execution
   contract: exact Task/Requirement/Design anchors, outcome, completion criterion, TDD
   contract, and `execution_log: [Log.md](Log.md)`. Add scope exclusions or an allowed
   path/write set only when they materially bound a delegated writer. Add conflict domains or
   runtime locks only for a real shared-resource collision. Do not copy the Task dependency
   DAG into Card.
2. `execution/<card_id>/Log.md` second. It is descriptive and contains a replaceable current
   snapshot—status, blocker, workspace, latest candidate, current evidence, and a
   `latest_event` link to the current event anchor in that file—then append-only events with
   stable IDs and evidence links.
3. After both files resolve, replace the Task row's `execution: none` with a real link to
   `Card.md` and set its macro status to `prepared`. Do this in the same checked candidate so
   no published Task pointer dangles.

The TDD contract states the RED test or test location, the wrong behavior it discriminates,
expected GREEN behavior, replay command or executable path, and final verification/evidence
destination. It is an implementation refinement of approved authority, not permission to add
scope. An unresolved semantic gap returns to `write-task`, `write-design`, or the appropriate
upstream skill.

Do not create `Verification.md`, `State.md`, a per-role Handoff, or one project-wide execution
log. On retries, start from the current snapshot and latest relevant event in `Log.md`; do not
read the full history unless the unresolved issue requires it.

Run diff, link, and repository-required document checks before advancing the shared baseline
with this preparation candidate.

## 2. Build and refill the ready set

Read the compact Task rows for the confirmed execution set and the selected tasks' Card current
contracts. A ready task has every prerequisite integrated and no collision with a declared
shared-resource constraint. Recompute after every material agent return, block, or integration.
Concurrency is the minimum of platform capacity, ready tasks, available writer workspaces, and
any real exclusive-resource capacity; never hard-code a count. Prefer dependency topology, then stable
`card_id` order. A blocked lane does not stop unrelated lanes.

If a task still contains separable responsibilities or cannot be independently tested, pause
it and its descendants and return it to `write-task`; a Coder cannot split authority ad hoc.

## 3. Prepare every agent dispatch

Every delegated Author, Coder, Critic, Reviewer, Verifier, or Researcher is single-use. Before
creating it, prepare a complete brief containing:

- `dispatch_id`, role, one bounded objective, and return format;
- authority and immutable baseline/candidate anchors;
- exact workspace, allowed write scope, permissions, and prohibitions;
- only the required Card/current Log context and relevant accepted findings or failures;
- checks to run and evidence required for return.

Create a new agent without parent or earlier-agent conversation history. One return ends that
agent. Any revision, retry, recheck, or later verification gets a new agent and a new brief.
Fresh identity does not mean every role is dispatched after every change.

Use a commit-bound DocStar brief when available and verified against the exact baseline; treat
it as an index, not authority. Use CodeGraph as a locator only when its index matches or can be
confirmed against the checked-out source.

## 4. Protect one writer boundary per task

Use one worktree or equivalently isolated workspace for each concurrent writing lane. A single
writer may use the verified current workspace when no other writer can collide with it and
existing user changes are preserved. Record only the boundary facts needed for this run: task,
owner, workspace, baseline, candidate, and allowed write scope; add conflict domains or locks
only when they exist. Reject stale ownership, wrong workspace, unrelated paths, or an
unresolvable candidate before review or integration.

A Coder writes only the prepared brief's allowed scope and any Card `write_set`, never shared
`Task.md`, Card/Log runtime state, the integration queue, or remote state. It first establishes
a discriminating RED test, implements the smallest sufficient change, and runs the Card checks.
A delegated isolated Coder returns one local candidate commit. When the primary orchestrator is
the sole Coder in the verified current workspace, it may instead freeze and hash the exact diff
for review. A correction always uses a fresh delegated Coder, or a newly frozen primary-Coder
attempt, starting from the last accepted anchor.

Within the current task, wait only after ready dispatch, primary-Coder work, integration,
state refresh, and local checks are exhausted. Use one event-driven longest-safe wait. A
timeout is a liveness checkpoint; do not turn list/status/wait into a polling loop.

## 5. Review a frozen candidate

Before independent review, the writer completes its self-check, required machine checks, and
immutable candidate anchor. Once review begins, freeze that candidate. Do not edit it while
review roles are active merely because the orchestrator notices another ordinary issue.

Select roles by impact:

| changed surface | required independent role |
|---|---|
| specification or document meaning | fresh Critic |
| implementation diff or test code | fresh Reviewer |
| executable behavior, test result, environment, or package input | fresh Verifier, but only after review blockers clear |
| formatting, links, pointers, or equivalent mechanical state | machine checks only |

Critic and Reviewer may run together when both surfaces changed. Collect every active review
return before editing. The primary orchestrator adjudicates once, rejects scope expansion,
and batches accepted blocker fixes into one revision. A fresh replacement role checks only
its affected scope when the brief proves the boundary; otherwise it checks the full applicable
surface. Do not dispatch an unchanged role. Non-blocking suggestions do not reopen the
candidate.

## 6. Verify once at the final useful boundary

Do not dispatch a Verifier while relevant Critic or Reviewer blockers remain. Coder test output
is implementation evidence; it is not independent verification.

For an isolated lane, the primary orchestrator mechanically applies the review-cleared
candidate to a temporary workspace based on the current shared baseline. A frozen single-writer
candidate already based on the unchanged shared baseline is itself the final combination and
does not need another copy. Then dispatch one fresh Verifier when executable evidence is
required. The Verifier runs the Card's targeted,
negative, integration/startup/E2E, and project gates that are actually required, and returns
commands, environment, exit codes, limitations, and side effects. A skipped or unavailable
required command is not a pass.

Do not separately verify the lane candidate and then repeat the same verification after clean
mechanical integration. An additional pre-integration Verifier is allowed only when the
integration decision itself needs independent runtime evidence, an external mutable resource
or environment makes evidence non-transferable, the baseline/test inputs changed materially,
or project policy explicitly requires dual verification. Record the reason.

If review finds a blocker, no Verifier is dispatched. If verification fails, record the
failure in Log, create a fresh Coder for the fix, review only the changed implementation scope
with a fresh Reviewer, and dispatch the next fresh Verifier only after review clears again.

## 7. Integrate and close

Only the primary orchestrator writes the temporary combination, shared baseline, Task status,
Card/Log state, and traceability. A clean mechanical application needs no Coder. A conflict or
judgment-required resolution creates a fresh Coder and returns the resulting diff through the
affected review and verification gates.

After the final candidate clears required review and any required verification:

- append the successful event and evidence to `Log.md` and set its current snapshot to closed;
- keep `Card.md` unchanged as the stable contract;
- set only the Task row's macro `status` to `closed` and keep its `execution` link;
- refresh affected AC traceability and shared-baseline/integration-queue pointers;
- run diff, links, repository checks, and then atomically advance the shared baseline.

Detailed blockers, anchors, commands, evidence, and event history stay in Log and are never
copied back into Task. Release the lane only after the integrated anchor and closure evidence
are durable. Do not push unless explicitly authorized.

## Upstream change and exit

When evidence contradicts approved authority, pause only the affected task and descendants,
record the observation in Log, and route the semantic change to its owner. Resume with fresh
agents only after the new authority anchor has the required review or approval.

Remain in `run-task` while a confirmed task can become ready or a lane/integration entry is
active. When every target-Milestone task is closed on one shared baseline and AC traceability
is full, use **REQUIRED next skill: `close-milestone`**. Before every substantive return,
perform a task-specific self-check and correct defects. Do not output a fixed `Reflection`
section; disclose only unresolved material risk.
