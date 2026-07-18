---
locale: en
purpose: Define dispatch inputs, agent identity, runtime states, role boundaries, and return requirements for independently executed work.
upstream: [GMGN §4](../../../../GMGN.md)
downstream: [GMGN router](../../SKILL.md), [code review](code-review.md)
status: approved
type: task
nature: normative
---

# Dispatch and agent-lifecycle contract

中文版本：[../zh-CN/dispatch-and-handoff.md](../zh-CN/dispatch-and-handoff.md)

This is a content contract, not a fill-in prompt. Preserve the facts below while adapting
wording and order to the task and platform.

## Required dispatch facts

Every dispatch states:

- one independently acceptable objective and role:
  `author | coder | critic | reviewer | verifier | researcher | integrator`;
- whether to start a new agent or resume an existing identity ref;
- current runtime state, authority links, required reading, in-scope paths/behaviors, and
  explicit exclusions;
- the active stage Skill's required content and self-checks;
- workspace permission, effort when supported, remote-write prohibition, deliverables, and
  exact verification or acceptance conditions.

A dispatch for any repository operation—document node, implementation lane, or integration
queue—records and verifies the existing workspace facts `workspace_mode`, `worktree_path`, and
`branch_ref`. These facts describe the current dispatch, not an agent's permanent identity. A
document node additionally records `node_id`, `baseline_anchor`, `candidate_anchor`, and the
needed `author_ref`, `critic_ref`, or `integrator_ref`. An implementation lane records exactly
`run_id`, `card_id`, `workspace_mode`, `worktree_path`, `branch_ref`, `baseline_anchor`,
`candidate_anchor`, `write_set`, `conflict_domains`, `runtime_locks`,
`integration_queue_ref`, and `shared_baseline_anchor`, plus its own `coder_ref`,
`reviewer_ref`, and `verifier_ref`. The shared integration queue retains one
`integrator_ref`. Task planning also states `depends_on` and the semantic owner.

Every return contains artifacts or findings and replayable evidence; deviations and needed
decisions; Reflection. Before any repository-writing dispatch enters `workspace-prepared`, run
`git rev-parse --show-toplevel` and require the resolved path to equal the absolute
`worktree_path`. Also require `git rev-parse --verify "${baseline_anchor}^{commit}"` to succeed
and `git rev-parse HEAD` to equal that exact commit. If the approved authority anchor is a
content hash, map it to its existing approved repository commit and use that commit as
`baseline_anchor` before dispatch; do not add a second baseline field. If `HEAD` differs,
switch to the approved commit or rebuild the worktree, then repeat both assertions.

Before every agent return, recheck the current dispatch path. A repository-writing return must
also verify that the returned candidate is exactly identified by `candidate_anchor`; when it is
a commit, require `git rev-parse --verify "${candidate_anchor}^{commit}"` to succeed. Do not
require `HEAD` to remain at the old `baseline_anchor` after a writer has produced a candidate.
Reject a path/anchor mismatch or incomplete return without treating it as reviewed.

## Runtime states

Runtime state is separate from document `status` and task work status.

- `blocked-prerequisite`: a hard dependency or authority is missing.
- `awaiting-owner-input`: an owner ruling, initiation, approval, or acceptance is required.
- `ready-to-dispatch`: inputs, authority, dependencies, conflict domains, and locks are ready.
- `workspace-prepared`: the isolated workspace, root-path assertion, and exact
  `HEAD == baseline_anchor` commit assertion passed.
- `author-active`, `author-returned`, `author-rework`, `author-revising`: the recorded Author
  is writing, returned, repairing an incomplete return, or applying accepted findings.
- `candidate-anchored`: the exact candidate has an immutable anchor.
- `critic-active`, `critic-returned`, `critic-rechecking`: the independent Critic is reviewing,
  returned findings, or the same Critic is rechecking accepted blockers.
- `coder-active`, `coder-returned`, `coder-revising`: the lane's recorded Coder is implementing,
  returned, or revising the card.
- `reviewer-active`, `reviewer-returned`, `reviewer-rechecking`: the lane's independent
  Reviewer is reviewing, returned, or rechecking affected diff.
- `verifier-active`, `verifier-returned`: the lane's Verifier is executing or returned.
- `upstream-change-pending`: only the affected node/lane waits for a controlled authority change.
- `acceptance-ready`: required review and candidate verification have no unresolved blocker.
- `accepted`: the anchored isolated candidate may enter integration; an implementation card
  is not yet `closed`.
- `integration-queued`: the accepted card waits in the recorded integration queue.
- `integrating`: the single Integrator is applying the lane to the shared baseline.
- `integration-conflict`: integration stopped; the same Coder must resolve the conflict.
- `rebase-required`: mechanical application is not clean, dependency/specification meaning is
  invalid on the current baseline, or resolution needs Coder judgment; the same Coder updates
  the lane. A baseline advance alone does not enter this state.
- `post-integration-verifying`: the same Verifier is checking the composed shared baseline.
- `node-complete`: artifact, shared baseline, evidence, and representations agree; only now may
  an implementation card become `closed`.
- `agent-unavailable`: a recorded agent cannot be resumed; replacement rules apply.

The normal implementation tail is `accepted → integration-queued → integrating →
post-integration-verifying → node-complete`.

## Rolling ready set and workspace isolation

The orchestrator recomputes the ready set after every return, integration, conflict, or block,
then fills capacity immediately. Concurrency is the minimum of platform concurrency, ready
cards, isolated workspaces, and exclusive-resource capacity; never hard-code it. Queue order
is dependency topology and then stable `card_id`. A blocked lane and its descendants wait;
unrelated lanes continue.

For `workspace_mode: worktree`, explicitly provision an absolute `worktree_path` and use
detached `HEAD` or a unique `branch_ref`. Never attach the same branch to multiple worktrees. A
worktree isolates files and the index; it does not resolve merge, semantic, interface, or
shared-runtime-resource conflicts.

If `workspace_mode: shared` cannot independently anchor each writer, parallel agents return
proposals or patches and do not directly edit, stage, or commit; one recorded Author or Coder
applies and anchors them serially. The same authoritative document has one writer by default. Parallel document
work requires stable disjoint section/ID ownership, no shared semantics or interfaces,
independent worktrees, and a fresh Critic review of the combined candidate. Frontmatter,
tables of contents, shared tables, whole-file formatting, and the same decision, AC, or
paragraph are never parallel writer surfaces.

## Identity-preserving loops and integration ownership

Author and Critic, or Coder and Reviewer, report only through the orchestrator. Accepted
document findings return to the same `author_ref`; blockers return to the same `critic_ref`.
Card findings and `integration-conflict` or `rebase-required` return to the same `coder_ref`;
every affected diff returns to the same `reviewer_ref`; affected verification returns to the
same `verifier_ref`.

One `integrator_ref` serially owns the integration workspace, `integration_queue_ref`, shared
baseline, `Task.md`, and traceability. Integration is two-phase: from the current clean
`shared_baseline_anchor`, it creates an isolated temporary combination and mechanically applies
the accepted local-commit `candidate_anchor` without advancing the shared anchor. The
integration event/evidence retains the preceding anchor; do not add a synonymous top-level
runtime field. The same Verifier is resumed with the temporary workspace's current
`workspace_mode`, `worktree_path`, and `branch_ref`.

Only a post-integration-verified candidate plus accepted mechanical ledger refresh may
atomically advance `shared_baseline_anchor`. On merge/cherry-pick conflict or verification
failure, abort the operation or discard the temporary workspace, leave the original shared
anchor unchanged, and confirm its index/worktree clean with `git status --short` before
processing unrelated queue entries. An unverified combination is never the shared baseline.

If the platform cannot resume an agent, enter `agent-unavailable`, record why, and hand the
complete lane record to an explicit replacement. A replacement Critic/Reviewer performs a
full review; a replacement Verifier reruns the full required verification. A replacement
Integrator re-reads the queue and shared baseline and replays its mechanical checks.

## Role requirements

- **Author** writes only the assigned document or closure artifact/delta, satisfies the active
  `write-*` or `close-milestone` content contract, chooses the clearest structure, self-checks,
  and returns checks and Reflection. Run-task-only rules apply only when its dispatch says so.
- **Critic** is read-only and independent; every finding includes location, evidence, impact,
  required correction, and blocker level. It does not edit or become a second author.
- **Coder** implements exactly one approved card in its recorded workspace, stays within
  `write_set`, and stages/commits only that set on detached `HEAD` or its unique branch. It
  returns a resolvable local commit SHA as immutable `candidate_anchor`; remote writes and
  unrelated paths are forbidden.
- **Reviewer** is a general read-only reviewer for an anchored document, code, or milestone
  closure increment. When the active dispatch is a run-task card, it reviews
  `baseline_anchor..candidate_anchor` and applies the card conflict/recheck rules.
- **Verifier** independently runs the active stage's tests, real paths, negative cases, and
  gates. For a run-task card, the same `verifier_ref` receives the card workspace during
  candidate verification and the Integrator's temporary combination workspace during
  post-integration verification, validating the current dispatch path both times.
- **Integrator** performs accepted mechanical propagation for document and milestone stages.
  When the active dispatch is a run-task card, it is the shared-baseline single writer and
  follows the two-phase integration/rollback protocol above.
- **Researcher** gathers scoped evidence and labels measured facts, source-backed facts, and
  inference; recommendations do not become authority.

## Platform adapters

- **Codex:** carry these requirements in every dispatch. Record the spawned target/thread and
  send revision or recheck follow-ups to it. Plugin installation does not make bundled
  `.codex/agents` project-scoped, and subagents do not imply workspace isolation; provision
  and pass the absolute worktree explicitly.
- **Claude Code:** ordinary subagents share the primary session's current working directory and
  do not share a scheduler DAG or automatic ready set. The main session issues named `Agent`
  calls for every ready item up to the actual platform capacity before waiting, waits for any
  completion, updates the ready set, and immediately refills the freed slot. Never infer a
  concurrency number from a hard-coded environment-variable default.

  For resumable Author, Critic, Coder, Reviewer, Verifier, and Integrator work, use a custom or
  `general-purpose` agent and record its agent ID. `SendMessage` is available only when
  `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` is enabled; enabling that flag does not require
  adopting Agent Teams. When messaging is available, resume by agent ID. When it is unavailable,
  enter the existing `agent-unavailable` explicit-replacement rule; do not claim a targeted
  recheck, the same Verifier, or the same Integrator. `Explore` and `Plan` cannot carry a role
  that must be resumed. Plugin agents live in root `agents/`.

  Do not claim automatic worktree isolation. Isolation exists only when explicitly requested
  by agent frontmatter/call (`isolation: worktree`) or supplied by an isolating surface such as
  Agent View/background, Desktop, or `/batch`. Agent Teams are an experimental, optional
  scheduler: they can unlock dependencies and auto-claim tasks, but do not automatically
  create worktrees, and in-process teammates are not preserved across `/resume`. They are not
  GMGN's default correctness path. Enable them only explicitly, with every writer separately
  isolated and all file/conflict domains non-overlapping; otherwise teammates are read-only or
  return proposals. Concurrent same-file writers can overwrite each other.

  GMGN never relies on automatic merge; the recorded Integrator performs explicit integration.
  A native worktree's default base may be a fresh/origin default rather than the approved
  `baseline_anchor`, so verify the exact commit before work. If it differs, select the approved
  head, use a `WorktreeCreate` hook, or provision a manual worktree. Do not hard-code Claude
  temporary paths or branch names. Reviewer, Verifier, and Integrator use the current dispatch
  path rather than blindly creating another worktree.

If a surface lacks steering, resume, or safe workspace controls, apply the corresponding
degradation rule; do not silently weaken identity or isolation.
