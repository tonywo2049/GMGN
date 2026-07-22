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
  `author | coder | critic | reviewer | verifier | researcher`;
- whether to start a new agent or resume an existing identity ref;
- current runtime state, authority links, required reading, in-scope paths/behaviors, and
  explicit exclusions;
- the active stage Skill's required content and self-checks;
- workspace permission, effort when supported, remote-write prohibition, deliverables, and
  exact verification or acceptance conditions.

For `run-task`, the critic-reviewed `Task.md` card is the only static execution authority.
An exact card and authority anchor satisfies the static part of this contract; do not copy the
card into another prompt or document. The minimal dispatch adds only the current role and
identity mode, authority repository or corpus pointer, runtime state, lane/workspace/anchor
facts, permissions, prohibitions, and return gate. A verified same-baseline DocStar brief
accompanies those pointers as a derived index when available; otherwise the dispatch records
the degradation and targeted-read pointers. This dispatch is not a per-agent `Handoff`; GMGN Handoff is
the receiving-state artifact used after closure or at a session boundary that does not cross
active owner-bound lanes.

For a run-task lane, resolve the immutable baseline commit and, when supported, produce the
brief with `--baseline <baseline_anchor>`. Check that its manifest SHA equals that resolved
commit before dispatch. The brief is a starting evidence bundle; it does not prohibit targeted
source reads. A recipient may follow `omitted`/`boundary_pointers`, issue narrower DocStar
queries, or read exact files and line ranges when required evidence is missing or conflicting.
Record a missing/failed DocStar command as a degradation and use direct targeted reads.
A revision Coder receives that authority brief plus only the current card snapshot, anchored
candidate, accepted findings, latest relevant event, replayable failure evidence, and return
gate. These are required facts, not a mandatory prompt or checkpoint template.

CodeGraph is a locator for code relationships, not evidence authority. When `.codegraph/`
exists, the Coder uses it at the checked-out expected head, the Reviewer independently uses it at the candidate,
and the Verifier uses it only after a failure or unresolved coverage question. If index-to-commit
identity is not proven, confirm every result in the checked-out source, Git diff, and tests.

Start every run-task Coder attempt without parent or earlier-Coder conversation history. Start
or resume Reviewer and Verifier identities without parent conversation history. Where the
historical Codex schema is exposed, set `fork_turns="none"`; where the
boolean schema is exposed, set `fork_context=false` or omit it when false is the documented
default. Do not use `fork_turns="all"` or `fork_context=true` for these roles. A resumed
Reviewer or Verifier may retain its own history, but never imports the scheduler transcript. A
Coder revision always starts fresh. If required execution meaning exists only in chat, the card is not ready: stop the
affected lane and return to `write-task` so the authority is reviewed and anchored.

Detailed execution history is not part of the normal initial read set. Follow the card's
`execution_log` link only for a revision attempt, retry, failure, conflict, replacement, audit, or closure,
starting from its anchored `latest_event`; extract that event and follow only links needed for
the unresolved cycle instead of ingesting the whole descriptive log. For single-card work,
resolve only the exact card, directly gating rows, affected AC rows, and current shared-baseline
and integration-queue pointers rather than all of `Task.md`. Meaning found only in the log must
be promoted to the correct normative authority before affected work continues.

A repository operation—document node, implementation lane, or primary-orchestrator
integration—records and verifies the existing workspace facts `workspace_mode`, `worktree_path`, and
`branch_ref`. These facts describe the current repository operation, not an agent's permanent identity. A
document node additionally records `node_id`, `baseline_anchor`, `candidate_anchor`, and the
needed `author_ref` or `critic_ref`. An implementation lane records exactly
`project_scope_id`, `lane_key`, `owner_thread_id`, `owner_run_id`, `ownership_epoch`, `run_id`,
`card_id`, `workspace_mode`, `worktree_path`, `branch_ref`, `baseline_anchor`,
`repository_identity`, `coder_epoch`, `candidate_anchor`, `candidate_coder_epoch`, `write_set`, `conflict_domains`, `runtime_locks`,
`integration_queue_ref`, and `shared_baseline_anchor`, plus its own `coder_ref`,
`reviewer_ref`, and `verifier_ref`. The primary orchestrator identified by `owner_thread_id`
and `owner_run_id` owns the shared integration queue. Task planning also states `depends_on`
and the semantic owner.
`owner_thread_id` is the main task that owns the writer lane, `owner_run_id` is the scheduler
run holding the claim, and `coder_ref` plus `coder_epoch` identify the lane's current Coder
attempt: normally a delegated
Coder, or the primary session under the no-parallelism rule. These identities are not
interchangeable. `run_id` remains execution provenance and is not a uniqueness key. Bind the
first Coder before writing. Later attempts use atomic `rotate-coder`; never silently take over a
lane already bound to another one.

For WhitePaper, ROADMAP, Goal, Requirement, Design, and Task, record the writer choice before
writing begins. `author_ref` identifies either the primary session or a delegated Author
agent. Prefer direct primary authorship when its context makes that the clearest and least
wasteful path; delegate only when bounded isolation, specialization, or parallelism creates
real value. An `author_ref` bound to the primary session is a lifecycle identity, not an
Author-agent dispatch. The Critic remains independent of whichever writer was selected.

Before returning, every agent checks its work against the active stage contract, available
evidence, and task-specific failure modes, then corrects every in-scope defect it finds. The
self-check process is not a return artifact and does not use a fixed `Reflection` section.
Every return contains artifacts or findings and replayable evidence; deviations and needed
decisions; and only material unresolved risks that could change the conclusion, decision,
acceptance, or downstream work. Omit that disclosure when no such risk remains; approval,
acceptance, and closure candidates instead always state remaining material risks or that none
are known. Before any repository-writing dispatch enters `workspace-prepared`, derive
`expected_head_anchor`: use `baseline_anchor` for an initial attempt and the current
`candidate_anchor` for a revision. Run `git rev-parse --show-toplevel` and require the resolved
path to equal the absolute `worktree_path`. Also require
`git rev-parse --verify "${baseline_anchor}^{commit}"` and
`git rev-parse --verify "${expected_head_anchor}^{commit}"` to succeed, and require
`git rev-parse HEAD` to equal the expected-head commit. If the approved authority anchor is a
content hash, map it to its existing approved repository commit and use that commit as
`baseline_anchor` before dispatch; do not add a second baseline field. If `HEAD` differs,
switch to the expected commit or rebuild the worktree, then repeat the assertions.

Before every agent return, recheck the current dispatch path. A repository-writing return must
also verify that the returned candidate is exactly identified by `candidate_anchor`; when it is
a commit, require `git rev-parse --verify "${candidate_anchor}^{commit}"` to succeed. Do not
require `HEAD` to remain at the old `baseline_anchor` after a writer has produced a candidate.
Reject a path/anchor mismatch or incomplete return without treating it as reviewed.

## Runtime states

Runtime state is separate from document `status` and task work status.

- `blocked-prerequisite`: a hard dependency or authority is missing.
- `awaiting-owner-input`: an owner ruling, initiation, approval, or acceptance is required.
- `ready-to-dispatch`: inputs, authority, dependencies, conflict domains, and locks are ready;
  for a specification document, the actual writer can now be selected and bound.
- `workspace-prepared`: the assigned workspace and root-path assertion passed, and `HEAD`
  equals the derived `expected_head_anchor`: `baseline_anchor` initially or the current
  `candidate_anchor` for a revision.
- `author-active`, `author-returned`, `author-rework`, `author-revising`: the recorded writer
  is writing, returned or reached its self-check checkpoint, repairing an incomplete
  candidate, or applying accepted findings. The recorded writer may be the primary session or
  a delegated Author agent.
- `candidate-anchored`: the exact candidate has an immutable anchor.
- `critic-active`, `critic-returned`, `critic-rechecking`: the independent Critic is reviewing,
  returned findings, or the same Critic is rechecking accepted blockers.
- `coder-active`, `coder-returned`, `coder-revising`: the lane's current Coder attempt is
  implementing, returned, or revising the card. A revision uses a fresh Coder generation.
- `candidate-awaiting-anchor`: a Coder returned an initial or revised candidate, but the
  scheduler has not yet completed identity/diff checks and atomic anchor; Reviewer is forbidden.
- `review-authorized`: the scheduler anchored the exact candidate and explicitly authorized
  review for that candidate, ownership epoch, and Coder epoch.
- `reviewer-active`, `reviewer-returned`, `reviewer-rechecking`: the lane's independent
  Reviewer is reviewing, returned, or rechecking affected diff.
- `verifier-active`, `verifier-returned`: the lane's Verifier is executing or returned.
- `upstream-change-pending`: only the affected node/lane waits for a controlled authority change.
- `acceptance-ready`: required review and candidate verification have no unresolved blocker.
- `accepted`: the anchored candidate passed adjudication or owner approval. A document
  candidate crosses an integration boundary only when its workspace topology requires it; an
  implementation card enters the integration queue and is not yet `closed`.
- `integration-queued`: the accepted card waits in the recorded integration queue.
- `integrating`: the primary orchestrator is applying a candidate across an isolated-workspace,
  concurrent-writer, or shared-baseline boundary.
- `integration-conflict`: integration stopped; a fresh Coder attempt resolves the conflict from
  the anchored candidate.
- `rebase-required`: mechanical application is not clean, dependency/specification meaning is
  invalid on the current baseline, or resolution needs Coder judgment; a fresh Coder attempt
  updates the lane. A baseline advance alone does not enter this state.
- `post-integration-verifying`: the same Verifier is checking the composed shared baseline.
- `node-complete`: artifact, shared baseline, evidence, and representations agree; only now may
  an implementation card become `closed`, and completed role threads are retired.
- `agent-unavailable`: a recorded agent cannot be resumed; replacement rules apply.
- `owner-unreachable`: an active writer lane's registered owner cannot be confirmed; no new
  writer may claim, reuse, expire, or steal the lane automatically.
- `worker-create-requested`, `worker-queued`, `worker-resolved`, `worker-bootstrap-returned`,
  `lane-claimed`, `coder-bound`, `worker-activated`: Codex cross-main-task startup states; a
  queued client ID is not an active worker target.

The normal implementation tail is `accepted → integration-queued → integrating →
post-integration-verifying → node-complete`.

## Rolling ready set and workspace isolation

The orchestrator recomputes the ready set after every return, integration, conflict, or block,
then fills capacity immediately. Concurrency is the minimum of platform concurrency, ready
cards, isolated workspaces, and exclusive-resource capacity; never hard-code it. Queue order
is dependency topology and then stable `card_id`. A blocked lane and its descendants wait;
unrelated lanes continue.

Implementation lane identity is project-wide across main tasks: `lane_key` is
`project_scope_id + card_id`, while `run_id` is only execution provenance. Before any Coder may
write, the scheduler must atomically claim both the card and canonical `worktree_path` in the
authority project's shared lane registry, then verify `owner_thread_id`, `owner_run_id`,
`ownership_epoch`, `coder_ref`, `coder_epoch`, and path. At most one active writer owns a card
or canonical path. `claim` has no Coder identity; `bind-coder` explicitly binds the first one,
and `rotate-coder` atomically binds a fresh attempt from the current anchored candidate. Every
verify, anchor, rotation, and normal release requires the exact bound `coder_ref` and
`coder_epoch`. Only `cancel-unbound` may cancel a claim before binding. Cross-task scans are
collision diagnostics, not a lock. Reject stale-owner, stale-epoch, missing/wrong-Coder,
stale-Coder-generation, or recreated-repository returns before review or integration.
Reviewer and Verifier may coexist only as read-only agents against the recorded anchor.

The claim also records canonical Git common-dir and git-dir paths, both directories' local stat
identities, and object format as `repository_identity`. Every bind, verify, anchor, release, or
unbound cancellation recomputes that identity and confirms the original `baseline_anchor`
still exists. Replacing the same absolute path with another clone is not the same repository,
even if it contains that baseline commit.

For `workspace_mode: worktree`, explicitly provision an absolute `worktree_path` and use
detached `HEAD` or a unique `branch_ref`. Never attach the same branch to multiple worktrees. A
worktree isolates files and the index; it does not resolve merge, semantic, interface, or
shared-runtime-resource conflicts.

If `workspace_mode: shared` cannot independently anchor each writer, parallel agents return
proposals or patches and do not directly edit, stage, or commit; one recorded writer applies
and anchors them serially. The same authoritative document has one writer by default.
Parallel document work requires stable disjoint section/ID ownership, no shared semantics or
interfaces, independent worktrees, and a fresh Critic review of the combined candidate.
Frontmatter, tables of contents, shared tables, whole-file formatting, and the same decision,
AC, or paragraph are never parallel writer surfaces.

## Identity-preserving loops and integration ownership

A delegated Author and Critic, or Coder and Reviewer, report only through the orchestrator.
Accepted document findings return to the same `author_ref`; when that ref is the primary
session, it applies them directly without an Author-agent handoff. Blockers return to the
same `critic_ref`.
Card findings and implementation failures start a fresh Coder attempt from the anchored
candidate. Every affected diff returns to the same `reviewer_ref`; affected verification
returns to the same `verifier_ref`. The same Critic remains bound for targeted blocker recheck;
replacing a Critic or Reviewer requires a full review.

Every initial or revised worker candidate stops at `candidate-awaiting-anchor` and returns to
the scheduler. The worker cannot mutate the registry or dispatch Reviewer. The scheduler
verifies the bound lane/repository/path, current `coder_ref` and `coder_epoch`, candidate
commit, and `write_set`, performs atomic anchor, records `candidate_coder_epoch`, retires that
Coder thread, and then sends candidate-and-epoch-scoped `review-authorized`. Only then may the
worker dispatch Reviewer. A revision first creates a fresh read-only Coder, then the scheduler
atomically rotates and activates it after checking `HEAD == candidate_anchor`. Revision
invalidates the preceding authorization and repeats the gate.

For specification documents, the primary orchestrator performs accepted same-batch propagation,
machine checks, and commit control, including when the candidate crosses an isolated-workspace,
concurrent-writer, or shared-baseline boundary. For implementation, the primary orchestrator
serially owns the integration workspace, `integration_queue_ref`, shared baseline, `Task.md`,
per-card execution logs, and traceability. Implementation integration is two-phase: from the
current clean `shared_baseline_anchor`, it creates an isolated temporary combination and
mechanically applies
the accepted local-commit `candidate_anchor` without advancing the shared anchor. The
integration event/evidence retains the preceding anchor; do not add a synonymous top-level
runtime field. The same Verifier is resumed with the temporary workspace's current
`workspace_mode`, `worktree_path`, and `branch_ref`.

Only a post-integration-verified candidate plus accepted mechanical ledger refresh may
atomically advance `shared_baseline_anchor`. On merge/cherry-pick conflict or verification
failure, abort the operation or discard the temporary workspace, restore the preceding shared
anchor, and confirm its index/worktree clean with `git status --short`. The failed implementation
candidate never advances it. From that clean anchor, the primary orchestrator may create and mechanically
check a separate state-only candidate containing the durable event in
`execution/<card_id>.md` and the replaced current blocker, status, anchors, evidence, and
`latest_event` in `Task.md`; that descriptive-only
commit may then advance the shared anchor. It never copies detailed history into Task or
combines cards into one log. An unverified implementation combination is never the shared baseline.

After successful post-integration verification, the verified combined candidate itself must
append the final event, close the log metadata, compact and close the Task card, and refresh
affected traceability and evidence. Only that exact candidate may advance the shared anchor;
the runtime lane becomes `node-complete` afterward and its completed role threads are retired.

If the platform cannot resume an agent, enter `agent-unavailable`, record why, and hand the
complete lane record to an explicit replacement. A replacement Critic/Reviewer performs a
full review; a replacement Verifier reruns the full required verification. An active lane must
not change `owner_thread_id` or `owner_run_id`: if its originating primary session cannot be
resumed, enter `owner-unreachable`; a new session must not reconstruct ownership, impersonate
the old IDs, anchor, integrate, or release that lane. Main-session handoff is allowed only
after every lane owned by that session reaches `node-complete` and is released.

## Role requirements

- **Author** is used only when writing was delegated. It writes the assigned document or
  closure artifact/delta, satisfies the active `brainstorm`, `write-*`, or `close-milestone`
  content contract, chooses the clearest structure, self-checks, and returns checks plus any
  material unresolved risk. Run-task-only rules apply only when its dispatch says so.
- **Critic** is read-only and independent; every finding includes location, evidence, impact,
  required correction, and blocker level. It does not edit or become a second author.
- **Coder** implements exactly one immutable candidate attempt for one approved card in its
  recorded workspace, stays within `write_set`, and stages/commits only that set on detached
  `HEAD` or its unique branch. It returns a resolvable local commit SHA as immutable
  `candidate_anchor`; remote writes and unrelated paths are forbidden. Its thread retires after
  that candidate is anchored. Any later revision starts a fresh Coder with the authority brief
  and current-cycle delta, never earlier-Coder conversation history. The primary session may
  hold this identity for one lane only when no implementation lane can currently run in
  parallel with useful orchestrator work; that does not waive isolation, anchoring, independent
  review, or independent verification.
- **Reviewer** is a general read-only reviewer for an anchored document, code, or milestone
  closure increment. When the active dispatch is a run-task card, it reviews
  `baseline_anchor..candidate_anchor` only after exact `review-authorized`, and applies the card
  conflict/recheck rules.
- **Verifier** independently runs the active stage's tests, real paths, negative cases, and
  gates. For a run-task card, the same `verifier_ref` receives the card workspace during
  candidate verification and the primary orchestrator's temporary combination workspace during
  post-integration verification, validating the current dispatch path both times.
- **Researcher** gathers scoped evidence and labels measured facts, source-backed facts, and
  inference; recommendations do not become authority.

## Platform adapters

- **Codex:** carry these requirements in every dispatch. Record the spawned target/thread and
  send revision or recheck follow-ups to it. Plugin installation does not make bundled
  `.codex/agents` project-scoped, and subagents do not imply workspace isolation; provision
  and pass the absolute worktree explicitly.

  Fill the current task's actual subagent capacity first. If ready cards remain, create worker
  main tasks only when the owner explicitly authorized cross-task fan-out for this run and
  `create_thread`, `list_threads`, `read_thread`, `wait_threads`, and
  `send_message_to_thread` are available. Issue every currently allowed creation request before
  the first blocking wait. A creation-capacity rejection leaves the lane ready for refill after
  any completion.

  Each initial worker prompt is read-only, names exactly one card/worktree, forbids recursive
  main-task creation, and may create one read-only Coder. It returns exact worktree/repository
  facts and `coder_ref`. Preserve opaque `clientThreadId`, `threadId`, `hostId`, and wait cursor
  values verbatim. When creation first returns only queued `clientThreadId`, resolve it through
  non-blocking task observations to actual `threadId + hostId`; before resolution, never put it
  in `wait_threads`, claim its lane, or activate it. Once resolved and bootstrapped, the scheduler
  performs `claim → bind-coder → verify`, then sends activation for that fresh Coder. A later
  revision bootstraps another read-only Coder and waits for scheduler `rotate-coder` before
  writing.

  The originating scheduler is the sole global ready-set, lane-registry, integration-queue,
  and shared-baseline owner. Workers cannot mutate the registry, recursively create
  main tasks, adjudicate, accept, integrate, edit shared `Task.md` or traceability, push, or
  publish. When workers exceed one `wait_threads` call's runtime target limit, group them by the
  observed capability. Wait on groups concurrently when supported; otherwise take one
  `timeoutMs: 0` snapshot when grouping changes, select one group, and block once with the
  longest platform-safe wait. On timeout, record the next group for the next external
  reactivation and yield; the current activation must not call another wait or list/read tasks.
  A timeout is a liveness checkpoint, never an in-turn rotation signal. Wake on a material update and refill
  immediately. Workers may show progress in their own thread, but send the scheduler only
  blockers, required approvals/rulings, candidates, review, verification, and completion—not
  progress or periodic heartbeats. Without capability or run-scoped authorization, degrade to rolling
  dispatch in the current task. Never encode a current/default subagent count, wait-target
  count, or polling interval as a method constant.

  For current-task agents, use one event-driven `wait_agent` covering any live agent only after
  ready dispatch, primary-Coder work, integration, state refresh, and local checks are
  exhausted. Use the longest platform-safe wait allowed by the surface's user-update and
  liveness limits. After a timeout, resume useful local work or yield; never automatically
  chain `list_agents`, status/worktree probes, and another `wait_agent`. Send one targeted
  status request only after a task-derived liveness threshold is crossed.
- **Claude Code:** ordinary subagents share the primary session's current working directory and
  do not share a scheduler DAG or automatic ready set. The main session issues named `Agent`
  calls for every ready item up to the actual platform capacity before waiting, waits for any
  completion, updates the ready set, and immediately refills the freed slot. Never infer a
  concurrency number from a hard-coded environment-variable default.

  Whenever Author, Critic, Coder, Reviewer, or Verifier work is delegated to a
  resumable agent, use a custom or `general-purpose` agent and record its agent ID. A primary
  session recorded as a document writer is not an Author-agent dispatch. `SendMessage` is
  available only when
  `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` is enabled; enabling that flag does not require
  adopting Agent Teams. When messaging is available, resume by agent ID. When it is unavailable,
  enter the existing `agent-unavailable` explicit-replacement rule; do not claim a targeted
  recheck or the same Verifier. `Explore` and `Plan` cannot carry a role
  that must be resumed. Plugin agents live in root `agents/`.

  Do not claim automatic worktree isolation. Isolation exists only when explicitly requested
  by agent frontmatter/call (`isolation: worktree`) or supplied by an isolating surface such as
  Agent View/background, Desktop, or `/batch`. Agent Teams are an experimental, optional
  scheduler: they can unlock dependencies and auto-claim tasks, but do not automatically
  create worktrees, and in-process teammates are not preserved across `/resume`. They are not
  GMGN's default correctness path. Enable them only explicitly, with every writer separately
  isolated and all file/conflict domains non-overlapping; otherwise teammates are read-only or
  return proposals. Concurrent same-file writers can overwrite each other.

  GMGN never relies on automatic merge. The primary orchestrator explicitly integrates every
  candidate that crosses an integration boundary; implementation candidates always do so.
  A native worktree's default base may be a fresh/origin default rather than the approved
  `baseline_anchor`, so verify the exact commit before work. If it differs, select the approved
  head, use a `WorktreeCreate` hook, or provision a manual worktree. Do not hard-code Claude
  temporary paths or branch names. Reviewer and Verifier use the current dispatch path rather
  than blindly creating another worktree.

If a surface lacks steering, resume, or safe workspace controls, apply the corresponding
degradation rule; do not silently weaken identity or isolation.
