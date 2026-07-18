---
name: run-task
description: "Use when one or more approved task cards are confirmed: continuously dispatch every ready task, feature, bug fix, refactor, test, or code change through isolated coding lanes, then integrate and close each card. 一张或多张任务卡已确认要做时滚动并行开发功能、修复缺陷/修 bug、重构、写测试/写代码、实现任务并关账；用户说开做这些卡、开始编码、把任务做完时触发。"
---

# Run ready task cards continuously

<HARD-GATE>Every dispatched card must exist in a critic-reviewed and orchestrator-reviewed `Task.md`, include the execution facts required by `write-task`, and belong to an owner/orchestrator-confirmed execution set. Otherwise return to `write-task`. A card is ready only after its dependencies are integrated into the shared baseline and its conflict domains and runtime locks are available. If implementation exposes changed upstream meaning, pause only the impact cone and route to its authority; code or Task prose must not silently redefine the specification.</HARD-GATE>

Use the document locale for status updates and the user's language for conversation. Keep
all machine tokens and IDs unchanged.

The primary orchestrator keeps the run state, per-card lanes, identity refs, adjudication,
acceptance, and merge control. It does not write implementation, repair findings, run
verification in place of a Verifier, or edit the shared ledger in place of the Integrator.

## 1. Build and continuously refill the ready set

Record one `run_id`, `integration_queue_ref`, and current `shared_baseline_anchor`. For every
confirmed card, read its `depends_on`, spec/Design anchors, failing test, `write_set`,
`conflict_domains`, and `runtime_locks`. Use `docstar brief <card_id> --preset gmgn-v1 --json`
when available; otherwise read those sources directly.

Recompute the ready set after every agent return, integration, conflict, or block. Fill capacity
immediately instead of waiting for a card or wave to close. Concurrency is
`min(platform concurrency, ready cards, isolated workspaces, exclusive-resource capacity)`;
never hard-code a number. A slow or blocked lane does not stop unrelated lanes. When capacity
is lower than the ready set, choose by dependency topology and then stable `card_id` order.

## 2. Provision one isolated workspace per card

Create one lane per `card_id` and record only these workspace/integration facts:
`run_id`, `card_id`, `workspace_mode`, `worktree_path`, `branch_ref`, `baseline_anchor`,
`candidate_anchor`, `write_set`, `conflict_domains`, `runtime_locks`,
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
includes a parseable local commit SHA as immutable `candidate_anchor`; verify it resolves as a
commit before entering `candidate-anchored`. Uncommitted files, a symbolic branch name, or a
commit containing unrelated paths is not a candidate anchor.

Dispatch one independent read-only Reviewer for that lane and retain `reviewer_ref`. Review
the exact `baseline_anchor..candidate_anchor` card diff. Accepted findings return to the same
Coder in `coder-revising`; blocker fixes return to the same Reviewer in
`reviewer-rechecking`. A native surface without resumable identity repeats the full card
review.

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
`待执行`, `未创建`, `未运行`, `待确认`, old output, and old Reflection. Mechanically refresh
them or explain why they remain true. Run `git diff --check`, link checks, and
`git status --short`; prepare or create the local integration commit under repository policy.
After these checks, atomically advance `shared_baseline_anchor` to the verified combined
candidate. Never expose an unverified temporary combination as the shared baseline.

Only now set the card work status to `closed` and the lane to `node-complete`. Update
`shared_baseline_anchor`, release its locks, delete no worktree until the integrated anchor and
evidence are recorded, then immediately recompute and refill the ready set. Do not push unless
explicitly authorized.

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

Remain in `run-task` while any confirmed card can become ready, any lane is active, or the
integration queue is non-empty. When all cards are `closed` on one `shared_baseline_anchor`,
the queue is empty, no lane is active, `rebase-required`, or `integration-conflict`, and
traceability is full, **REQUIRED next skill: `close-milestone`**.

End every substantive response with **Reflection**: weakest assumption; neglected
counterexample; measured versus inferred.
