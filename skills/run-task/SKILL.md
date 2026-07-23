---
name: run-task
description: "Use when one or more approved Task.md rows are confirmed: materialize per-card execution contracts, run every ready implementation task through bounded writer lanes, review code and deterministic local execution once, add separate final-candidate verification only for explicit risk triggers, integrate, and close. 已确认任务集后创建单卡 Card/Log、滚动并行开发、由 Reviewer 一轮完成代码审查与确定性本地检查，仅在风险触发时单独验证最终候选并关账。"
assurance_policy: gmgn-assurance-v1
---

# Run confirmed task cards

<HARD-GATE>Every dispatched task must exist in an independently reviewed and primary-orchestrator-accepted `Task.md`, belong to the confirmed `target_milestone_id` execution set, and have valid upstream authority. A task is ready only when its Task prerequisites are closed on the shared baseline and any declared shared-resource constraint is available. If implementation changes upstream meaning, stop only its impact cone and revise that authority.</HARD-GATE>

The primary orchestrator owns scheduling, adjudication, shared state, integration, Task status,
and per-card execution documents. It may be the Coder for one task only when no useful
implementation work can run in parallel with orchestration; it cannot replace the independent
Reviewer or any risk-triggered Verifier.

Use the English-only [dispatch contract](../gmgn/references/en/dispatch-and-handoff.md).

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
shared-resource constraint. Recompute after every material agent return, block, integration,
or resource-capacity change. Before waiting or acting as a Coder, the primary orchestrator
scans every task in the confirmed execution set, not only the current card or active lane, and
dispatches every ready, non-conflicting task that fits currently available capacity.
Concurrency is the minimum of platform capacity, ready tasks, available writer workspaces, and
any real exclusive-resource capacity; never hard-code a count. Prefer dependency topology, then stable
`card_id` order. A blocked lane does not stop unrelated lanes.

If a task still contains separable responsibilities or cannot be independently tested, pause
it and its descendants and return it to `write-task`; a Coder cannot split authority ad hoc.

## 3. Prepare every agent dispatch

Every delegated Author, Coder, Critic, Reviewer, Verifier, or Researcher is single-use. Before
creating it, prepare a complete brief containing:

- `dispatch_id`, role, one bounded objective, and return format;
- authority, immutable baseline/candidate anchors, and for a Coder the original
  `candidate_base_anchor` plus current `candidate_tip_anchor`;
- exact workspace, allowed write scope, permissions, and prohibitions;
- only the required Card/current Log context and relevant accepted findings or failures;
- checks to run and evidence required for return.

Create a new agent without parent or earlier-agent conversation history. One return ends that
agent. A later writing attempt, separately scoped semantic or implementation change, or later
verification gets a new agent and a new brief. Critic and Reviewer are not redispatched to
recheck fixes from their completed round. Fresh identity does not mean every role is dispatched
after every change.

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
A delegated isolated Coder returns the original `candidate_base_anchor` and current
`candidate_tip_anchor`. The transferable candidate is the complete
`candidate_base_anchor..candidate_tip_anchor` diff. A correction advances the tip but does not
replace the original base or become a standalone candidate. When the primary orchestrator is
the sole Coder in the verified current workspace, it may instead freeze and hash the same full
diff for review. A correction always uses a fresh delegated Coder, or a newly frozen
primary-Coder attempt, starting from the last accepted anchor.

Across the confirmed execution set, wait only after ready dispatch, primary-Coder work, integration,
state refresh, and local checks are exhausted. Use one event-driven longest-safe wait. A
timeout is a liveness checkpoint; do not turn list/status/wait into a polling loop. Use one
`list_agents` snapshot only when a scheduling/capacity decision needs current state, a wait
timed out without an unambiguous agent state, or received lifecycle events conflict. Do not
query again until a material lifecycle event, candidate, blocker, or scheduling condition
changes. No periodic list interval is configured or inferred. A long-running primary session
sends no heartbeat when state is unchanged; it reports only material progress, a blocker, a
decision request, or the final result.

## 5. Review the final useful candidate once

Before independent review, the writer completes its self-check and required machine checks.
The primary orchestrator mechanically applies the complete
`candidate_base_anchor..candidate_tip_anchor` diff, or its complete ordered commit chain, to a
temporary combination based on the current shared baseline. Never apply only the last
correction commit. A frozen single-writer candidate already based on the unchanged shared
baseline is itself the combination. Resolve an unclean application or judgment-required
conflict with a fresh Coder before freezing the immutable review candidate. Reserve that shared
baseline and integration position until the candidate integrates or is abandoned; other Coder
work may continue, but it cannot advance the reserved baseline. Once review begins, do not edit
the candidate while review roles are active merely because the orchestrator notices another
ordinary issue.

A clean mechanical application may produce a different commit SHA. A changed commit SHA alone
does not invalidate review or execution evidence; compare the relevant source and build inputs.
For task authority, compare the task definition, spec anchor, and prerequisite. Ignore Task
status, descriptive Log content, and unrelated task rows. An `execution` pointer change is
equivalent only when it resolves to the same normative Card, or when that Card's authority
anchors, completion criterion, and TDD contract are unchanged. If any relevant content changed
or equivalence cannot be proved, the existing evidence is not transferable.

Select roles by impact:

| changed surface | required independent role |
|---|---|
| specification or document meaning | fresh Critic |
| implementation diff or test code, including deterministic local execution | fresh Reviewer |
| recorded trigger from the [assurance policy](../gmgn/references/en/assurance-policy.json) | fresh Verifier, but only after review blockers clear |
| formatting, links, pointers, or equivalent mechanical state | machine checks only |

Critic and Reviewer may run together when both surfaces changed. Collect every active review
return before editing. The primary orchestrator adjudicates once, rejects scope expansion,
and batches accepted blocker fixes into one revision. Each task execution uses
`review_policy: single-pass` and has at most this one Critic/Reviewer round. The primary
orchestrator checks each resolution and runs affected machine checks; do not dispatch another
Critic or Reviewer to recheck the fixes. A fix that
expands authority, scope, or behavior beyond the accepted findings becomes a separately scoped
change. Record the reviewed anchor, complete findings and rulings, exact fix delta, and
post-fix checks at the final anchor. Non-blocking suggestions do not reopen the candidate.
Do not keep a task open to perfect a non-blocking issue when its Card outcome works and an
effective fallback keeps the remaining impact within accepted bounds.

The Reviewer also runs the prepared deterministic local targeted, negative, integration, and
project checks that fit its environment. It returns exact commands, environment, exit codes,
limitations, and side effects together with its findings. A skipped or unavailable required
Reviewer command is not a pass. If no accepted blocker changes the candidate, this execution
evidence belongs to the final candidate. After accepted fixes, the primary orchestrator checks
the exact fix delta and reruns every affected machine check without another independent round.

## 6. Add a separate Verifier only for risk triggers

Ordinary deterministic local execution belongs to the Reviewer; Coder test output remains
supporting implementation evidence. A fresh Verifier is exceptional, not default. Classify the
final candidate from the assurance policy as `not-required` or `required:<trigger>` and record
that classification in Log.

Do not dispatch a Verifier while relevant Critic or Reviewer blockers remain. When a trigger
exists, dispatch one fresh Verifier after the fixed temporary combination becomes the final
candidate. It runs only the non-transferable or explicitly independent plan and returns exact
commands, environment, exit codes, limitations, and side effects. A skipped or unavailable
required command is not a pass. The Verifier must leave every tracked file unchanged on both
pass and failure. A command that generates or refreshes oracle, evidence, or attempt files is
run beforehand by the Coder or primary orchestrator, not by the Verifier.

Do not separately verify the lane candidate and then repeat the same verification after clean
mechanical integration. An additional pre-integration Verifier is allowed only when the
integration decision itself needs independent runtime evidence, an external mutable resource
or environment makes evidence non-transferable, the baseline/test inputs changed materially,
or project policy explicitly requires dual verification. Record the reason.

If risk-triggered verification fails, record the failure in Log, create a fresh Coder for the
fix, check the resolution and affected machine checks without another Reviewer, then dispatch
a fresh Verifier because the required final-candidate evidence was invalidated. If the fix
expands authority, scope, or behavior beyond the reviewed task, route it as a separately scoped
change.

## 7. Integrate and close

Only the primary orchestrator writes the temporary combination, shared baseline, Task status,
Card/Log state, and traceability. Combination conflicts are resolved before the task's one
review round. A post-review fix uses a fresh Coder when needed, then runs affected machine
checks and any risk-triggered verification without another Reviewer.

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
