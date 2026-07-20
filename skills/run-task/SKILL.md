---
name: run-task
description: "Use when one or more approved task cards are confirmed: continuously dispatch every ready task, feature, bug fix, refactor, test, or code change through isolated coding lanes, then integrate and close each card. 一张或多张任务卡已确认要做时滚动并行开发功能、修复缺陷/修 bug、重构、写测试/写代码、实现任务并关账；用户说开做这些卡、开始编码、把任务做完时触发。"
---

# Run ready task cards continuously

<HARD-GATE>Every dispatched card must exist in a critic-reviewed and orchestrator-reviewed `Task.md`, include the execution facts required by `write-task`, and belong to an owner/orchestrator-confirmed execution set for a recorded `target_milestone_id`. Cross-milestone references never expand this set automatically. Otherwise return to `write-task`. A card is ready only after its valid upstream dependencies are integrated into the shared baseline and its conflict domains and runtime locks are available. If implementation exposes changed upstream meaning, pause only the impact cone and route to its authority; code or Task prose must not silently redefine the specification.</HARD-GATE>

Use the document locale for status updates and the user's language for conversation. Keep
all machine tokens and IDs unchanged.

The primary orchestrator keeps the run state, per-card lanes, identity refs, adjudication,
acceptance, and merge control. It does not write implementation, repair findings, run
verification in place of a Verifier, or edit the shared ledger in place of the Integrator.

## Telemetry boundary

Telemetry is out-of-band observation, never execution, approval, or closure authority. Do not
add telemetry logs or logging requests to a lane prompt, `Task.md`, or `Handoff`; no model
manually writes telemetry logs. Selected user-level hooks may emit privacy-safe lifecycle/tool
metadata: opaque IDs, byte counts, status, classifications, fork policy, and structured
correlation IDs. The scheduler never uses telemetry for readiness, review
authorization, acceptance, integration, or card closure. Telemetry failure never blocks
delivery. Run `telemetry/report.py` only when the user explicitly requests a retrospective.

Telemetry does not change DocStar or its JSON output. Every DocStar call remains a fresh full
rebuild with no cache. Hooks and reporters measure calls, elapsed time, command type, and later
grep/read outside DocStar; `grep_avoided` does not claim causation.

## Dispatch context for every lane

The critic-reviewed `Task.md` card is the only static execution authority for a run-task lane.
The scheduler resolves that card and its spec/Design anchors, using DocStar when available,
instead of treating the parent conversation as task input. Start or resume every Coder,
Reviewer, Verifier, and Integrator without parent conversation history. On a Codex surface with
the historical schema, set `fork_turns="none"`; on a surface with the current boolean schema,
set `fork_context=false` or omit it when false is the documented default. Never use
`fork_turns="all"` or `fork_context=true` for a run-task role. Resuming a recorded identity may
retain that same agent's own history; it must not import the scheduler's transcript.

Each minimal runtime dispatch cites the exact `card_id`, Task/spec/Design authority anchors,
and authority repository or corpus, then adds only facts that do not exist until execution:
role and identity mode, runtime state, lane/workspace/anchor facts, permissions, prohibitions,
and the current return gate. It may attach the same-baseline DocStar brief as a derived index,
but does not restate the card. The dispatch is not a new `Handoff` artifact. If a required
instruction,
owner ruling, scope boundary, or acceptance condition exists only in chat, the card is not
ready; stop the affected lane and return to `write-task` rather than inheriting the transcript.

## 1. Build and continuously refill the ready set

Record one `run_id`, `target_milestone_id`, that Milestone's Goal/Requirement/Design/Task
anchors, `integration_queue_ref`, and current `shared_baseline_anchor`. Build the execution set
only from confirmed cards owned by that target Milestone's Task authority. A reference to a
downstream Milestone, its cards, documents, confirmation, implementation, or evidence is not a
dispatch instruction. If the owner explicitly authorizes multiple Milestones, create separate
execution sets and preserve each card's single owning Milestone.

For every in-set card, read its `depends_on`, spec/Design anchors, failing test, `write_set`,
`conflict_domains`, and `runtime_locks`. Use `docstar brief <card_id> --preset gmgn-v1 --json`
when available; otherwise read those sources directly. Treat DocStar IDs and edges as structural
measurements only. Validate cross-Milestone edges against ROADMAP, Goal, and the owning Task:
an already planned upstream prerequisite may gate readiness but is never executed implicitly;
a downstream reverse dependency returns to `write-task` and does not start downstream work.

Recompute the ready set after every agent return, integration, conflict, or block. Fill capacity
immediately instead of waiting for a card or wave to close. Concurrency is
`min(platform concurrency, ready cards, isolated workspaces, exclusive-resource capacity)`;
never hard-code a number. A slow or blocked lane does not stop unrelated lanes. When capacity
is lower than the ready set, choose by dependency topology and then stable `card_id` order.

On Codex, first fill the current task's actual subagent capacity. If ready cards remain, use
cross-task fan-out only when the owner explicitly authorized it for this run and the surface
provides `create_thread`, `list_threads`, `read_thread`, `wait_threads`, and
`send_message_to_thread`. For every additional lane allowed by current workspace, resource, and
task-creation capacity, issue its `create_thread` request before the scheduler's first blocking
wait. A creation-capacity rejection leaves the ready card queued; retry it after any worker or
local lane completion instead of waiting for all current work to close.

Each creation request enters `worker-create-requested` with an initial prompt that is read-only,
names exactly one card, forbids a second lane and recursive main-task creation, and requests one
independent Codex worktree. The bootstrap may create exactly one read-only Coder for that lane,
but neither may edit. It returns exact repository/worktree facts and `coder_ref`. If
`create_thread` first returns only queued `clientThreadId`, enter `worker-queued` and preserve
that opaque ID. Resolve it through non-blocking `list_threads`/`read_thread` observations to an
actual `threadId` plus `hostId`; before that resolution, do not put it in `wait_threads`, claim a
lane, or activate writing. Record `clientThreadId`, `threadId`, `hostId`, and every wait cursor
verbatim; never derive one opaque ID from another.

After the actual task/worktree and bootstrap `coder_ref` are known, move through
`worker-resolved → worker-bootstrap-returned → lane-claimed → coder-bound → worker-activated`.
The scheduler alone performs registry `claim → bind-coder → verify`, then uses
`send_message_to_thread` to activate that worker, which resumes the same Coder with the write
instruction. The originating scheduler remains the sole owner of the global ready set, lane
registry, `integration_queue_ref`, `shared_baseline_anchor`, and Integrator. A worker must not
mutate the registry, recursively create main tasks, adjudicate findings, accept a candidate,
integrate, edit shared `Task.md` or traceability, push, publish, or accept a second lane.

Only after all currently allowed creation requests have been issued may the scheduler block in
`wait_threads`. When active workers exceed one call's runtime target limit, partition them by
that observed capability rather than a method constant. If parallel waits are supported, wait
on all groups concurrently. Otherwise take a `timeoutMs: 0` snapshot of every group, then rotate
bounded short waits across groups so none starves. Wake on any completion, update global state,
and immediately refill local or worker capacity. `list_threads` and `read_thread` are collision
diagnostics, not a lock. Without the required capability or run-scoped authorization, keep
rolling within the current task; do not infer or hard-code a subagent or wait-target limit.

## 2. Provision one isolated workspace per card

Create one lane per card across the authority project. Its `lane_key` is
`project_scope_id + card_id`; `run_id` is execution provenance, not a uniqueness boundary.
Record `project_scope_id`, `lane_key`, `owner_thread_id`, `owner_run_id`, `ownership_epoch`,
`run_id`, `card_id`, `workspace_mode`, `worktree_path`, `branch_ref`, `baseline_anchor`,
`repository_identity`, `candidate_anchor`, `write_set`, `conflict_domains`, `runtime_locks`,
`integration_queue_ref`, and `shared_baseline_anchor`. Add the lane's own `coder_ref`,
`reviewer_ref`, and `verifier_ref`; retain one `integrator_ref` for the shared integration
queue.

Prefer `workspace_mode: worktree`. The orchestrator must explicitly provision the worktree
when the platform does not do so. Use detached `HEAD` or a unique `branch_ref`; never attach
the same branch to multiple worktrees. Before work starts, the agent requires
`git rev-parse --show-toplevel` to equal the absolute `worktree_path`, requires
`git rev-parse --verify "${baseline_anchor}^{commit}"` to succeed, and requires
`git rev-parse HEAD` to equal that exact commit. Map a content-hash authority anchor to its
existing approved repository commit as `baseline_anchor` before dispatch. If `HEAD` differs,
switch to the approved commit or rebuild the worktree and recheck. Enter `workspace-prepared`
only after both path and baseline checks pass. On return, recheck the current path and verify
the returned commit through `candidate_anchor`; do not require `HEAD` to remain at the old
`baseline_anchor`.

Before any Coder receives write permission, run `scripts/lane_registry.py` against the
authority project's coordination root. That root owns the registry and may be a different Git
repository from the implementation `worktree_path`. The helper stores JSON runtime state behind
`refs/gmgn/lane-registry` in the authority repository's Git common metadata; linked worktrees
and Codex tasks therefore share it, while normal branch commits, status, and pushes do not.
Its `claim`, `bind-coder`, `status`, `verify`, `anchor`, `release`, and `cancel-unbound`
operations use Git `update-ref` compare-and-swap and stable English JSON keys. `claim` never
accepts `coder_ref`; bind it only with the separate `bind-coder` operation. An unbound claim may
be cancelled only with `cancel-unbound`; normal `release` is reserved for a bound lane and
requires its exact `coder_ref`.

The global dispatch gate is: provision and validate the worktree; inspect cross-task state for
diagnostics; atomically `claim` the `card_id` and canonical `worktree_path`; bind the one
`coder_ref`; then `verify` the exact `owner_thread_id`, `owner_run_id`, `ownership_epoch`,
`coder_ref`, and path before activation. Reject a claim if either the card or canonical path has
another active writer. Thread-local agent absence and a clear cross-task scan never prove
vacancy. If the registered owner cannot be confirmed, enter `owner-unreachable` and stop this
lane; do not expire, steal, or recreate it automatically. A released lane keeps its tombstone,
and its next claim increments `ownership_epoch`.

At claim, bind the implementation repository identity as well as the path: canonical Git
common-dir and git-dir paths, both directories' local stat identities, and Git object format.
Every `bind-coder`, `verify`, `anchor`, `release`, or `cancel-unbound` recomputes and matches that
identity and confirms the original `baseline_anchor` still exists. Deleting the path and
recreating another clone at the same absolute name is a mismatch even when that clone contains
the same baseline commit.

A worktree isolates files and the Git index. It does not resolve merge conflicts, semantic or
interface conflicts, or shared runtime resources. With `workspace_mode: shared`, agents must
not stage or commit concurrently. If that workspace cannot give each writer an independent
immutable anchor, parallel agents return proposals or patches only; one recorded Coder or
Author applies them serially, stages only the assigned `write_set`, and creates the anchor. If
neither isolation nor proposal-only delegation is safe, keep the conflicting lane out of the
ready set.

## 3. Run each card lane independently

At `workspace-prepared`, dispatch a new Coder for exactly that approved card and retain its
`coder_ref`. Require allowed paths, failing-first discrimination, the first sufficient
implementation, real-call-path evidence, and no edits to shared `Task.md`, traceability, or
the shared baseline. At `coder-returned`, reject incomplete or out-of-scope work to the same
Coder. Otherwise the Coder stages and commits only this card's `write_set` in its assigned
worktree on detached `HEAD` or its unique `branch_ref`, without any remote write. The return
includes a parseable local commit SHA as immutable `candidate_anchor`. The worker enters
`candidate-awaiting-anchor`, stops, and returns the scheduler its exact path, candidate, and
`write_set` evidence; it must not dispatch Reviewer yet. The scheduler re-runs registry
`verify` with the exact bound `coder_ref`, confirms repository/path identity, resolves the
candidate commit, and checks that its diff contains only the card `write_set`. A return from
another owner, a stale `ownership_epoch`, a missing/wrong `coder_ref`, a changed repository, or
a different path is rejected before review or integration. Uncommitted files, a symbolic
branch name, or a commit containing unrelated paths is not a candidate anchor.

Only the scheduler may run the atomic registry `anchor`. After it succeeds, enter
`candidate-anchored`, then send an explicit `review-authorized` message tied to that exact
`candidate_anchor` and `ownership_epoch`. A worker may dispatch one independent read-only
Reviewer and retain `reviewer_ref` only after receiving that authorization. Review the exact
`baseline_anchor..candidate_anchor` card diff. Accepted findings return to the same Coder in
`coder-revising`; blocker fixes return to the same Reviewer in `reviewer-rechecking`. Every
revised candidate repeats `candidate-awaiting-anchor → candidate-anchored → review-authorized`;
authorization for an older candidate cannot authorize review of the new one. A native surface
without resumable identity repeats the full card review.

Reviewer and Verifier may coexist with the lane only as read-only agents at its recorded
anchor. They do not claim writer ownership, change `coder_ref`, or make a second worktree into
a second writer lane.

After review blockers clear, dispatch one independent Verifier as `verifier-active` and
retain `verifier_ref`. For candidate verification, the dispatch gives that Verifier the card
lane's current `workspace_mode`, `worktree_path`, and `branch_ref`.
The Verifier runs the targeted test, relevant integration/startup/E2E and negative paths,
plus project gates at `candidate_anchor`, returning exact commands, environment, exit codes,
and limitations as `verifier-returned`. A skipped or unavailable command is not a pass. Failure returns to the same
Coder, then the affected diff returns to the same Reviewer and verification to the same
Verifier. With no blocker, the orchestrator may mark the branch candidate `accepted`; it is
not `closed` and must not update the shared ledger.

## 4. Serialize integration, then close the card

Move an accepted lane through `accepted → integration-queued → integrating →
post-integration-verifying → node-complete`. The same Integrator is the only writer for the
integration workspace, shared baseline, `Task.md`, and traceability. It processes eligible
queue entries by dependency topology and then stable `card_id`; a conflicted entry is skipped
while unrelated eligible entries continue.

Integration is two-phase. Starting from the current clean `shared_baseline_anchor`, the
Integrator creates an isolated temporary combination workspace and mechanically applies the
accepted lane there without advancing the shared anchor. The integration dispatch includes
the current `workspace_mode`, absolute `worktree_path`, and `branch_ref`; its
`candidate_anchor` is the temporary combined commit. Preserve the preceding anchor in the
integration event and evidence rather than adding another top-level runtime field.

An advanced shared baseline does not by itself require a rebase. First try the mechanical
application in the temporary combination workspace. Use `integration-conflict` for a failed
merge/cherry-pick attempt. Enter `rebase-required` and resume the same Coder only when the lane
cannot apply cleanly, its dependency or specification meaning is invalid on the current
baseline, or resolution requires Coder judgment. Unrelated accepted lanes remain eligible.
Every resulting changed diff returns to the same Reviewer and affected candidate verification
to the same Verifier before requeueing.

For post-integration verification, resume the same `verifier_ref` but dispatch the temporary
combination workspace's current `workspace_mode`, current `worktree_path`, and current
`branch_ref`; agent
identity is preserved while the verified path changes. The Verifier enters
`post-integration-verifying` at its `candidate_anchor` and runs the card's affected tests plus
required interaction and project gates. The temporary combined commit is not yet the shared
baseline.

If merge/cherry-pick conflicts or post-integration verification fails, abort the Git operation
or discard the temporary combination workspace and leave the original
`shared_baseline_anchor` unchanged. Record the failed `candidate_anchor` and preceding anchor
in event/evidence, confirm the original shared-baseline index and worktree are clean with
`git status --short`, then skip the failed entry and process unrelated eligible queue items.
A verification failure returns to the same Coder, affected diff to the same Reviewer, and
verification to the same Verifier.

Only after post-integration verification passes does the Integrator refresh `Task.md`,
traceability, evidence pointers, and upstream state in that isolated candidate. Re-read all
of `Task.md` and scan stale assertions:
`not-started`, `pending`, `not created`, `not run`, `awaiting confirmation`, plus
`待执行`, `未创建`, `未运行`, `待确认`, old output, and stale risk or uncertainty statements. Mechanically refresh
them or explain why they remain true. Run `git diff --check`, link checks, and
`git status --short`; prepare or create the local integration commit under repository policy.
After these checks, atomically advance `shared_baseline_anchor` to the verified combined
candidate. Never expose an unverified temporary combination as the shared baseline.

Only now set the card work status to `closed` and the lane to `node-complete`. Update
`shared_baseline_anchor`, release its locks, delete no worktree until the integrated anchor and
evidence are recorded, then call the registry `release` operation with the exact owner and
epoch so the tombstone remains while writer ownership and path occupancy are freed. Immediately
recompute and refill the ready set. Do not push unless explicitly authorized.

## Upstream change during execution

When implementation evidence contradicts an approved premise:

1. Stop only the affected lane and its dependency descendants at the current anchor; record
   the observation, old authority anchor, proposed semantic delta, and impact cone. Continue
   unrelated lanes and refill their capacity.
2. Route WhitePaper to `brainstorm`, ROADMAP to `roadmap`, Goal to `write-goal`, Requirement
   or R-AC meaning to `write-requirement`, Design intent to `write-design`, and Task execution
   authority to `write-task`.
3. Resume only after the changed authority has the review or approval required for its new
   anchor. Resume the same `coder_ref`; update only affected downstream documents, cards,
   code, tests, evidence, and state. Mark an invalidated branch `rebase-required`, return its
   affected diff to the same `reviewer_ref`, and verification to the same `verifier_ref`; do not restart unrelated work.
   If an agent is unavailable, enter `agent-unavailable` and
   perform an explicit replacement handoff; a replacement Reviewer repeats the full review
   and a replacement Verifier repeats the full required verification.
4. For a meaning-preserving mechanical change, refresh affected representations in the same
   batch and run machine checks without reapproval.

## Exit

Remain in `run-task` while any confirmed target-Milestone card can become ready, any lane owned
by that Milestone is active, or one of its integration queue entries is pending. When all cards
owned by `target_milestone_id` are `closed` on one `shared_baseline_anchor`, that Milestone's
queue entries are empty, none of its lanes is active, `rebase-required`, or
`integration-conflict`, and its traceability is full, **REQUIRED next skill:
`close-milestone`**. Downstream execution sets and lanes have separate lifecycle decisions.

Before every substantive return, perform a task-specific self-check and correct defects. Do
not output a fixed `Reflection` section. Disclose only material unresolved risks that could
change the conclusion, decision, acceptance, or downstream work; otherwise omit the
disclosure. Approval, acceptance, and closure always state remaining material risks or that
none are known.
