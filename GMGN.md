---
locale: en
purpose: Define GMGN roles, document chains, hard gates, independent review, and closure discipline.
upstream: none
downstream: [writing contract](skills/gmgn/references/en/writing-contract.md), [dispatch and handoff](skills/gmgn/references/en/dispatch-and-handoff.md), [preflight checklist](skills/gmgn/references/en/preflight-checklist.md), [pre-merge checklist](skills/gmgn/references/en/pre-merge-checklist.md), [pre-close checklist](skills/gmgn/references/en/pre-close-checklist.md)
status: approved
type: whitepaper
nature: normative
---

# GMGN: an engineering method for agent collaboration

GMGN is designed for one accountable human owner, one primary AI orchestrator, and
several task-focused agents. It applies to document-heavy product work and to software
implementation. Its central claim is simple: use structure and timed procedures to
counter two risks created by high-speed agent output.

中文版本：[GMGN.zh-CN.md](GMGN.zh-CN.md)

This file is the normative method. Installation and quick use belong in
[README.md](README.md); shared machine/dispatch contracts and checklists belong in
[`skills/gmgn/references/en/`](skills/gmgn/references/en/).

## 0. Scope and roles

GMGN defines six execution-separated roles and one optional audit role.

- **Owner** decides scope, approves project-level commitments, accepts closure, and is the only
  role that may authorize removing or reassigning a completion criterion through a controlled
  semantic change. A bare waiver does not close an AC. Agent-to-agent instructions do not
  constitute owner authorization.
- **Primary orchestrator** understands, decomposes, maintains the rolling ready set,
  dispatches, adjudicates, accepts, and gates. It retains decisions, interface freezes,
  merge control, and stage transitions. For WhitePaper, ROADMAP, Goal, Requirement, Design,
  and Task, it may write or revise the artifact directly when its context makes that the
  clearest and least wasteful path, or delegate a bounded writing unit to an Author when that
  produces a real isolation, specialization, or parallelism benefit. These are judgment
  inputs, not eligibility gates; the primary orchestrator owns the writer choice. It also
  applies accepted mechanical propagation, serializes shared-baseline writes, and refreshes
  `Task.md`, per-card execution logs, and traceability. When no implementation lane can
  currently run in parallel with useful orchestrator work, it may explicitly bind itself as
  one lane's Coder before writing; it never takes over a lane already assigned to another
  Coder or replaces independent review or verification.
- **Author** is an optional delegated writer. It creates or revises one document artifact
  against a content contract, chooses the document structure, and self-checks before return.
  A document stage does not require an Author-agent dispatch when the primary orchestrator is
  the recorded writer.
- **Coder** implements one approved task card and returns code, tests, and replayable evidence.
  This is normally a delegated agent, but may be the primary session under the explicit
  no-parallelism rule.
- **Critic/reviewer** tries to falsify an anchored artifact and must be independent of its
  actual writer/Coder. It reports findings and never edits the reviewed work.
- **Verifier** independently executes tests, gates, and real product paths at an anchored
  candidate without changing product meaning or source code.
- **External audit** is optional and introduces a frame from outside the working group.

Stages close against explicit criteria, not dates. Dates may be planning constraints, but
they never turn an unmet criterion into a completed one.

### 0.1 Node runtime lifecycle and agent identity

Runtime state is separate from document approval state and work-item state. Each active node
records `node_id`, `state`, `baseline_anchor`, `candidate_anchor`, and the relevant
`author_ref`, `critic_ref`, `coder_ref`, `reviewer_ref`, or `verifier_ref`.

A specification-document node first records its actual writer in `author_ref`: either the
primary session or a delegated Author agent. It then follows `ready-to-dispatch →
workspace-prepared → author-active → author-returned → candidate-anchored → critic-active →
critic-returned`. An incomplete return uses `author-rework` with that same writer. Accepted
findings use `author-revising` with the same writer; blocker resolution uses
`critic-rechecking` with the same independent Critic. Upstream correction uses
`upstream-change-pending` while preserving the current writer.

Successful review enters `acceptance-ready → accepted`. The primary orchestrator applies any
accepted mechanical propagation, links, state, and commit material; when a candidate crosses
an isolated-workspace, concurrent-writer, or shared-baseline boundary, continue through
`integrating → node-complete`. If the primary already owns the canonical workspace, the node
may move from `accepted` to `node-complete` after the same-batch propagation and machine checks
pass. WhitePaper normally favors the primary session because it retains the
complete Brainstorm dialogue, but the same writer-selection rule applies to all six
specification documents. The Critic always remains independent of the actual writer.

Implementation keeps one independent lane per card across the whole authority project, not
per conversation. Its `lane_key` is the combination of `project_scope_id` and `card_id`;
`run_id` records an execution attempt and does not define lane uniqueness. Each lane records
`project_scope_id`, `lane_key`, `owner_thread_id`, `owner_run_id`, `ownership_epoch`, `run_id`,
`card_id`, `workspace_mode`, `worktree_path`, `branch_ref`, `baseline_anchor`,
`candidate_anchor`, `write_set`, `conflict_domains`, `runtime_locks`, `integration_queue_ref`,
and `shared_baseline_anchor`, plus its own `coder_ref`, `reviewer_ref`, and `verifier_ref`.
The primary orchestrator that owns `owner_thread_id` and `owner_run_id` also owns the shared
integration queue. Bind `coder_ref` to the actual writer before implementation. Use the
primary session only when no implementation lane can currently run in parallel with useful
orchestrator work; record that reason, keep the lane isolated, and preserve independent
Reviewer and Verifier identities.

The normal card path is `ready-to-dispatch → workspace-prepared → coder-active →
coder-returned → candidate-awaiting-anchor → candidate-anchored → review-authorized →
reviewer-active → reviewer-returned → verifier-active → verifier-returned → acceptance-ready →
accepted → integration-queued → integrating → post-integration-verifying → node-complete`.
`accepted` means only that the isolated card
candidate may enter the integration queue. A card becomes `closed` only after the primary
orchestrator integrates it into `shared_baseline_anchor`, post-integration verification
passes, and the primary refreshes `Task.md` and traceability.

The primary orchestrator is the hub: a delegated Author and Critic, or Coder and Reviewer, do
not communicate directly. Within one lane the same Coder repairs findings and
`integration-conflict`, the same Reviewer rechecks affected diffs, and the same Verifier
reruns affected verification. A shared-baseline advance first receives a mechanical
application attempt in an isolated temporary combination; use `rebase-required` only when it
cannot apply cleanly, dependency/specification meaning became invalid, or Coder judgment is
required. An upstream semantic change uses `upstream-change-pending` only for its impact cone.
Any return, integration, conflict, or block immediately recomputes the ready set and fills
available capacity; unrelated lanes continue.

If a platform cannot resume the recorded agent, enter `agent-unavailable` and record why.
Replacement is explicit and receives the complete node record. Replacing a Critic/Reviewer
requires a full review; a new agent cannot claim the old agent's targeted recheck. The complete
state meanings and dispatch requirements are in
[`dispatch-and-handoff.md`](skills/gmgn/references/en/dispatch-and-handoff.md).

### 0.2 Parallel workspaces and ownership

Concurrency is the minimum of platform concurrency, ready cards, isolated workspaces, and
exclusive-resource capacity; no fixed number belongs in this method. A ready card has every
dependency integrated into the shared baseline and no incompatible `conflict_domains` or
`runtime_locks`. Scheduling is continuous: a wave is an observable snapshot, never a barrier
that waits for the slowest card.

The authority project's shared lane registry is the machine source of truth across Codex main
tasks and worktrees. An atomic compare-and-swap claim must succeed before any Coder can write.
At most one active writer may own a `card_id`, and one canonical `worktree_path` may belong to
at most one active writer lane. Cross-task thread scans are useful collision diagnostics but
cannot replace the atomic claim. A return from a different `owner_thread_id` or stale
`ownership_epoch`, or without the exact bound `coder_ref`, cannot enter review or integration.
Claim records the worktree's Git metadata/stat identity and object format; every later machine
operation must match it and prove the original baseline commit still exists. If ownership cannot be confirmed, mark
`owner-unreachable`; never infer vacancy or reclaim automatically. Reviewer and Verifier may
coexist as read-only agents against the recorded anchor, but neither becomes a second writer.

On Codex, first fill the current task's actual subagent capacity. If ready cards remain and the
owner explicitly authorized cross-task fan-out for this run, a scheduler with create/list/read/
wait/send task capabilities issues every currently allowed worker-main-task creation before its
first blocking wait. A queued `clientThreadId` is not an active target: resolve it to actual
`threadId + hostId` and exact worktree facts before waiting on it, claiming its lane, or
activating writes. Each read-only bootstrap owns exactly one prospective lane and one
independent Codex worktree, and may create one read-only Coder to report `coder_ref`. The
scheduler performs `claim → bind-coder → verify`, then activates that same Coder through the
worker. It remains the only owner of the global ready set, lane registry, integration queue,
and shared baseline. Workers cannot mutate the registry, create more main tasks, adjudicate,
accept, integrate, edit `Task.md`, push, or publish. Dynamically group waits by runtime tool
capacity. Use the longest platform-safe blocking wait after useful local work is exhausted;
a timeout is only a liveness checkpoint and never triggers an automatic list/read/wait loop.
Workers push material lifecycle events instead of periodic heartbeats. Within the current task,
one event-driven `wait_agent` covers any live agent; do not chain `list_agents`, status/worktree
probes, and another wait after timeout. Send one targeted status request only after a
task-derived liveness threshold is crossed. Refill immediately on any material update. Without
the capabilities or run-scoped authorization, keep rolling within the current task; never
hard-code a platform slot, wait-target count, or polling interval.

Each parallel writing lane uses an explicitly provisioned worktree at an absolute
`worktree_path`, with either detached `HEAD` or a unique `branch_ref`; the same branch must not
be attached to multiple worktrees. Before writing, require `git rev-parse --show-toplevel` to
equal the recorded absolute `worktree_path`, require `baseline_anchor` to resolve as a commit,
and require `git rev-parse HEAD` to equal it. Map a content-hash authority anchor to its existing
approved repository commit first; switch or rebuild and recheck on mismatch. At return, recheck
the path and verify `candidate_anchor`, not the old baseline. A worktree isolates files and the index. It does not resolve Git merge
conflicts, semantic conflicts, interface conflicts, or shared runtime resources.

The Coder stages and commits only its card's `write_set` in that assigned worktree and returns
a resolvable local commit SHA as immutable `candidate_anchor`. Local candidate commits are
allowed; remote writes are not. When `workspace_mode: shared` cannot independently anchor each
writer, parallel agents return proposals or patches instead of editing directly; one recorded
writer serially applies, stages, commits, and anchors them.

A worker stops at `candidate-awaiting-anchor` after every initial or revised Coder return. The
scheduler verifies lane/repository identity, path, candidate commit, and `write_set`, then
atomically anchors it. Only an explicit `review-authorized` message for that exact candidate and
epoch lets the worker dispatch Reviewer; old authorization never carries to a revision.

Integration is two-phase. From the clean current `shared_baseline_anchor`, the primary
orchestrator mechanically applies an accepted lane in an isolated temporary combination
workspace. The same Verifier keeps its identity but receives that temporary workspace's current
`workspace_mode`, `worktree_path`, and `branch_ref`. Only a verified combined candidate plus
its mechanical ledger refresh may atomically advance the shared anchor. On merge/cherry-pick
conflict or verification failure, abort the operation or discard the temporary workspace,
leave the original shared anchor unchanged, confirm its index/worktree are clean, and continue
unrelated queue entries. An unverified combination is never the shared baseline.

One authoritative document version has one writer by default. Controlled parallel authoring
is allowed only for stable, disjoint section or ID ownership with no shared meaning or
interface, independent worktrees, and a combined candidate that receives a fresh Critic
review. Frontmatter, tables of contents, shared tables, whole-file formatting, and the same
decision, AC, or paragraph are single-writer surfaces.

## 1. Two primary risks

### 1.1 Representation–reality drift

Representations are status fields, indexes, matrices, ledgers, and hashes. Reality is the
actual code, document, deployed behavior, or executed product path. If synchronization is
optional or delayed, representations drift from reality.

Typical failures include stale status, outdated hashes, full coverage matrices for paths
that never execute, and ledgers that lag behind merged work. GMGN counters this with
version anchors, same-batch status refresh, real execution paths, and machine-checkable
links.

### 1.2 Shared-frame blind spots

An author and reviewers using the same assumptions can all miss the same error. Three
properties are independent:

- internal consistency on paper;
- robustness in realistic scenarios;
- feasibility and correctness in the running implementation.

Review must therefore vary its frame: independent document criticism, implementation
review, execution evidence, and external input where risk justifies it.

## 2. Documents and chains

### 2.1 Document types

Each document answers one question and has one lifecycle.

- **WhitePaper / Goal** — why the work exists, harm ordering, top-level invariants.
- **ROADMAP** — qualitative sequencing, milestone goals, and unallocated TODOs.
- **Requirement** — what a milestone must satisfy; numbered, decidable acceptance criteria.
- **Design** — how structures and interfaces satisfy requirements.
- **Task** — normative current execution snapshot: cards, dependencies, current status,
  tests, blockers, and completion proof. It replaces superseded state instead of retaining
  detailed progress history.
- **Execution log** — descriptive, append-only per-card history under
  `execution/<card_id>.md`; it records attempts, transitions, review and verification rounds,
  commands, results, conflicts, and superseded anchors without becoming execution authority.
- **Research** — revisable exploration; archive it after conclusions enter the spec chain.
- **Decision** — append-only decisions, conditions, rationale, and propagation targets.
- **Handoff** — concise receiving state: baseline, current status, remaining work, pointers.
- **Retrospective** — conclusions after an event or milestone.
- **Checklists/registers** — timed prompts and cross-cutting facts, not duplicate specs.

### 2.2 Three chains

The **specification chain** is:

```text
Goal.md → Requirement.md → Design.md → Task.md → code/tests → AC traceability
```

`Requirement.md` is the single requirement authority for its milestone. Every task card
binds a spec anchor, a failing-first test, and a completion criterion. Uncovered ACs are
unimplemented work.

Task decomposition follows independent proof boundaries. A card has one primary semantic owner
and one independently decidable completion result. Separate independently verifiable
implementation, integration, real-environment or E2E qualification, production eligibility,
and closure instead of using the final qualification to justify one large implementation card.
Intermediate cards may integrate only while unfinished product paths remain unreachable,
disabled, or fail-closed and that containment is proved. Stop splitting when a smaller unit
would no longer be independently verifiable or would create empty wrapper work. The complete
authoring and review rules are in `skills/write-task/SKILL.md`.

The **process chain** is research → decision → normative document → archived exploration.
Keep revisable exploration separate from approved conclusions.

The **state chain** is per-card execution log → current Task snapshot → handoff → cross-track
register → ROADMAP pointer. Normal dispatch reads the Task card; resume, failure, conflict,
audit, and closure start from its anchored `latest_event` and follow the `execution_log` only
when history is needed; neither path ingests the whole file by default. Higher
layers summarize less and point downward more.

### 2.3 Stable machine contract

Human prose may be English or Chinese. Machine-facing fields remain fixed:

```yaml
locale: en | zh-CN
purpose: <natural-language sentence>
upstream: <real Markdown links or declared none>
downstream: <real Markdown links or declared none>
status: draft | pending-approval | approved | closed
type: whitepaper | roadmap | goal | requirement | design | task | execution-log | research | decision | retrospective | handoff
nature: normative | descriptive
```

Work rows use `not-started | initiated | in-progress | closed`. IDs, filenames, commands,
and task-table headers are language-independent. The full contract is in
[`writing-contract.md`](skills/gmgn/references/en/writing-contract.md).

### 2.4 Milestone ownership and closure boundary

Every Milestone-scoped run, from `write-goal` through `close-milestone`, records one
`target_milestone_id` and that Milestone's G-R-D-T authority anchors. `brainstorm` and ROADMAP
work without a selected Milestone do not invent this ID. Each card has exactly one owning
Milestone. Its execution set contains only cards in that Milestone's Task authority which the
owner or orchestrator confirmed. A cross-Milestone reference does not authorize work and never
expands the set automatically. If several Milestones are explicitly authorized, they retain
separate execution sets, state, and closing decisions.

`depends_on` may link cards inside one Milestone. An external hard prerequisite may point only
to an already planned upstream Milestone and may gate readiness without authorizing its
execution. A current or upstream Milestone must not depend on downstream implementation,
confirmation, document completion, or evidence. If a technical-selection or architecture
feasibility proof is required to satisfy the current Milestone, create a current-Milestone
spike or verification card. If the responsibility belongs downstream, create a non-blocking
TODO/Handoff with receiving Milestone/owner, question, trigger, possible impact, and a default
assumption where useful. Repair a reverse dependency through controlled `write-task` and any
affected authority before dispatch; do not start the downstream work to satisfy the bad edge.

Milestone closure is scoped to the target: its own cards, ACs, evidence, lanes, locks,
integration entries, and closing anchor. Downstream work or documents that have not started,
downstream active lanes, and downstream confirmations or TODOs do not block closure unless
they show that the target still has an undecided or unproved in-scope criterion. A shared
resource conflict may delay a mechanical integration or state refresh, but it does not change
semantic closure eligibility.

A foundation or M0 closure preserves the technical selection and architecture that were
accepted at its historical closing anchor. It does not make those choices immutable. Later
Milestone evidence may trigger a controlled revision of an M0-originated Design, Decision, or
index, which remains the semantic authority: record the trigger, old anchor, new anchor,
`supersedes`, and impact cone, while the old approval and closure remain attached to the old
anchor. Do not reopen M0 or rerun its complete workflow. The current Milestone owns the change,
implementation, and verification cards, not the M0-originated meaning; only the impact cone is
reviewed, propagated, and tested.

## 3. Approval and change semantics

Approval attaches to a version anchor: commit, content hash, or equally immutable
identifier. “Approved” without the reviewed version is ambiguous.

Freezing establishes a controlled-change baseline; it does not mean immutable forever.
After approval, a change must state trigger, impact, affected downstream documents,
required signers, and the new anchor.

When adopting a repository whose historical anchors cannot be recovered, never guess commits
or infer approval from current status. Record the current reviewed clean commit as an adoption
baseline and state that it proves only the imported present state. Known closed historical work
stays closed rather than being reopened to manufacture evidence. Active work without usable
anchors starts again from that baseline and receives full review and verification before its
next acceptance. Unanchored pre-adoption evidence is descriptive only and cannot authorize a
release.

### 3.1 Place changes by authority; review them by impact

Workflow nodes are not one-way. When current work exposes an upstream defect or changed
premise, return to the document that is the single authority for that content. Record the
trigger, old anchor, proposed delta, impact cone, required reviewers or approvers, and new
anchor. Do not redefine upstream meaning in a downstream document.

After the authority changes, propagate the result through affected upstream and downstream
links, mappings, status representations, tasks, tests, and evidence. Re-review, re-approve,
and re-verify only the impact cone. Returning to an authority does not restart the complete
workflow, and unaffected work may continue.

An old approval remains attached to the old version anchor; it never moves implicitly to an
edited file. A new version needs the approval appropriate to that authority only when the
change can alter a decision or a reasonable reader's understanding, including scope,
obligation, acceptance meaning, design intent, or execution authority. A file-content change
does not by itself require approval. Mechanical renames, moves, links, formatting, hashes, or
mirrored status updates that preserve meaning need only same-batch refresh and machine checks.
After an explicit equivalence record and successful checks, the new anchor may retain the
document's approval state by citing the old approved anchor; this is not a new approval. When
meaning is uncertain, classify the change as semantic.

Closure has three disciplines:

1. **scope closure** — every in-scope requirement is completed with evidence, or is first
   removed or reassigned by a controlled semantic change at a new authority anchor with
   Requirement, Task, and matrix synchronized; a `deferred` label or TODO alone never waives
   an AC that remains in target scope;
2. **evidence closure** — each criterion has a replayable test or real execution path;
3. **state closure** — current Task snapshot, matrix, ROADMAP, decisions, and handoff are refreshed in
   the same batch.

Immediately after closure, write receiving state for the next operator. A closed milestone
without a current handoff is not operationally closed.

### 3.2 Reuse accepted evidence for release

Acceptance and release are separate events. Acceptance decides whether an immutable candidate
is fit; release distributes it. Bind review and verification evidence to the accepted anchor,
their checked scope, required test plan, execution environment, and packaging inputs. One
unchanged semantic candidate receives one closure verification and combined review. A later
tag, upload, authentication retry, or installation consumes that evidence rather than
recreating it.

When the release anchor equals the accepted anchor, reuse the accepted review, regression,
E2E, structural, and closure evidence. When it differs only by an explicitly allowed
meaning-preserving release delta, record both anchors, `semantic_delta: none`, the exact
`allowed_diff`, and `approval_inherited_from`; prove that diff mechanically and rerun only the
affected version, artifact, or installation checks. A release retry with unchanged inputs
does not invalidate any evidence.

If source behavior, specification meaning, acceptance, scope, design intent, execution
authority, required test plan, target environment, or packaging inputs change, invalidate
only the evidence that depends on that input. Route semantic impact back to its authority;
rerun artifact or environment checks when only those inputs changed. Full regression, E2E,
combined review, DocStar, and closure authoring are not publication rituals and must not be
repeated without an invalidated dependency. External publication or deployment still needs
separate owner authorization.

## 4. Six workflow laws

1. **Classify before locating.** Decide whether a new file is requirement/design/execution/
   verification and exploratory/normative before choosing its directory.
2. **Graph before prose.** Read the upstream/downstream graph and relevant definitions
   before drafting or editing.
3. **One authority per fact.** Other documents point to the authority instead of copying it.
4. **Hard gates are procedures.** Missing prerequisites route backward; apparent simplicity
   is not a bypass.
5. **Delegate only when delegation creates value.** For specification documents, the
   orchestrator selects itself or an Author as the actual writer from context completeness,
   task size, isolation, specialization, and parallelism benefit; delegation is not a
   correctness gate. Each actual dispatch states node identity, scope, boundaries, inputs,
   content contract, outputs, verification, agent identity, and return format. The same
   recorded writer handles in-node corrections. During implementation, the reviewed `Task.md`
   card is the only static execution authority: Coder, Reviewer, and Verifier
   receive a minimal runtime dispatch and no parent conversation history. That dispatch cites
   the card and current lane facts; it is not a per-agent Handoff. Detailed history stays in
   the card's descriptive execution log and cannot introduce scope, gates, or completion
   meaning. The orchestrator continuously
   dispatches every ready card owned by the target Milestone into an isolated lane and keeps
   shared-baseline integration serial.
6. **Evidence before status.** A claim becomes complete only after the artifact, replayable
   evidence, and all representations agree.

Before every substantive return, the primary orchestrator and every agent check the work
against the active stage contract, available evidence, and the task's most likely failure
modes, then correct every in-scope defect they find. The self-check is an action, not a report:
its process is not emitted, and three fixed questions are neither required nor exhaustive.

Do not output a fixed `Reflection` section. Disclose only unresolved assumptions,
counterevidence, inference, limitations, or risks that could materially change the conclusion,
an owner decision, acceptance, or downstream work. Use the form clearest for the task and omit
the disclosure when no such item remains; never invent uncertainty to fill a template.
Approval, acceptance, and closure presentations always state the remaining material risks—or
that none are known. For each reported risk, give its impact, evidence strength, and cheapest
next falsification step. When none is known, cite the evidence supporting that statement and
do not invent a hypothetical concern or test merely to fill fields.

## 5. Adversarial quality

### 5.1 Independent document critic

Use one focused falsification round after the author self-check. Findings must identify
location, evidence, impact, a normative correction, and blocking level. Scope the review
to the changed artifact plus the minimum upstream/downstream context.

Accepted findings return to the same recorded writer, whether that is the primary session or
a delegated Author. Blocking fixes return to the same Critic for targeted recheck; a
replacement Critic repeats the full review. This preserves accountability without turning
recheck into another independent full round.

Two guards prevent review from becoming another authority:

- a critic may identify a problem but may not silently expand product scope;
- conflicting findings go to the orchestrator or owner, not into an endless review loop.

### 5.2 Code review is separate

Code review examines the incremental diff, untested branches, test discrimination,
spec-anchor alignment, and unnecessary complexity. It does not replace document criticism
or runtime execution. The reviewer reports findings and does not modify the reviewed work.

Use the current platform's native read-only review surface where available. A native surface
that does not expose a resumable reviewer identity performs a full review on every invocation;
it cannot satisfy a targeted same-Reviewer recheck. Otherwise use an independent read-only reviewer with
[`code-review.md`](skills/gmgn/references/en/code-review.md).

### 5.3 Orthogonal evidence

A strong close combines different evidence sources: structural checks, targeted tests,
full regression, real startup/E2E, independent review, and negative-path evidence. Repeating
the same check with another agent is not an independent source.

### 5.4 External input and incident generalization

External advice enters as evidence, not authority. Record it, reproduce relevant claims,
decide whether to adopt, then propagate the decision through the normal chain.

After an incident, fix the local defect and generalize the lesson into the narrowest
reusable location: test, checklist question, convention, or design rule. Do not create a
new framework when one line in an existing authority is sufficient.

### 5.5 Report residual risk at decisions and closure

Apply the §4 disclosure rule unconditionally at approval, acceptance, and closure. Present the
remaining material risk, its impact, the evidence strength, and the cheapest next falsification
step. If none is known, say so and cite the evidence supporting closure without manufacturing
a hypothetical concern.

## 6. Tool and automation boundaries

Automation may parse, link, count, compare, execute, and report. It must not invent product
meaning, approve scope, or infer that silence means success.

### 6.1 Telemetry is out-of-band observation

Telemetry is out-of-band observation, never execution, approval, or closure authority. Do not
write telemetry logs into a prompt, `Task.md`, or `Handoff`. No model manually writes telemetry
logs. Selected user-level hooks may emit privacy-safe lifecycle/tool metadata: opaque IDs,
byte counts, status, classifications, fork policy, and structured correlation IDs. Telemetry
failure never blocks delivery or changes a workflow gate. Run
`telemetry/report.py` only when the user explicitly requests a retrospective; its output is
evidence for that retrospective, not a state transition.

For agent waits, retain only normalized outcome and correlation metadata, never message text.
The retrospective reports update/timeout/state-change counts, consecutive-timeout and wait-storm
signals, and actual cumulative-token deltas associated with model reactivation after a wait.
Merge wait observations per `tool_use_id`: prefer a structured hook outcome and use session JSONL
only for uncovered calls. Do not count a linked hook and session call twice. Leave a legacy
unstructured rejection without reliable failure status as `unknown`; never infer an error from
argument/error message wording.
When the platform omits native turn/call linkage, label the association
`session_sequence_delta` with matched/eligible coverage; never present it as exact native
attribution.

External observation does not change DocStar or its JSON output. DocStar keeps a fresh full
rebuild on every invocation, with no cache. Hooks and reporters measure outside DocStar: call
count, elapsed time, command type, and subsequent grep/read activity. `grep_avoided` does not
claim causation.

DocStar is optional and deterministic. With the GMGN convention set it can check links,
extract the G-R-D-T graph, compile a task brief, and compare English/Chinese locale trees.
Its JSON uses the stable English `eg-3` contract regardless of display language. These IDs,
edges, briefs, checks, and verification results are structural measurements. They do not decide
Milestone ownership, dependency legality, execution authorization, or closure eligibility, and
DocStar `classification_complete` does not establish GMGN semantic scope classification.
GMGN must validate a cross-Milestone edge against ROADMAP, Goal, and the owning Task before
using it as a gate. Record every finding, its evidence, and exactly one classification:
`target-scoped | candidate-introduced-or-polluted | external-pre-existing`. The first two block
target closure. The last is recorded as debt only when evidence proves both its external scope
and pre-existing anchor. If that proof is missing, scope classification is incomplete and
closure is blocked.

```bash
python3 docstar.py check --preset gmgn-v1 --corpus <corpus>
python3 docstar.py brief <task-id> --baseline <baseline-anchor> --preset gmgn-v1 --json --corpus <corpus>
```

When commit-bound `brief` is available, run-task uses it as the required starting evidence
bundle and verifies that `context_manifest.corpus_revision` is the resolved baseline commit.
The bundle reduces repeated discovery; it is not a reading restriction. An agent may follow
omitted/boundary pointers, issue narrower DocStar queries, or read exact source ranges whenever
the bundle is insufficient, conflicting, or does not cover code and runtime evidence.

CodeGraph remains a separate optional code-navigation layer. In an indexed repository, the
Coder queries it at the baseline, the Reviewer independently queries it at the candidate, and
the Verifier uses it only when a failure or coverage question requires call-path navigation.
If index-to-commit identity is not proven, CodeGraph is only a locator. Exact checked-out
source, Git diff, tests, and real execution remain evidence. GMGN requires no CodeGraph engine
or storage changes.

When DocStar is absent, perform equivalent file/link/table checks with repository-native
commands. Never claim a gate ran when the tool was unavailable.

## 7. Anti-overdesign boundary

Choose the first sufficient option in this order:

1. no implementation;
2. reuse an existing repository implementation;
3. standard library;
4. platform-native capability;
5. existing dependency;
6. direct implementation;
7. the least new code or structure.

Do not add abstractions, configuration, dependencies, wrappers, or files without a current
requirement. Complexity review uses five labels only: delete, standard library, native,
empty abstraction, and shrink. Never trade away trust-boundary validation, data-loss
protection, security, accessibility, hardware calibration, or explicit requirements merely
to reduce code.

## 8. Start-from-zero checklist

1. Identify the owner and the active locale.
2. Run `brainstorm`; approve a version-anchored WhitePaper.
3. Build and approve the qualitative ROADMAP.
4. Initiate one milestone and create `Goal.md`.
5. Write `Requirement.md`, `Design.md`, and `Task.md` in order, with an independent critic
   and orchestrator review at each transition.
6. Record the target Milestone and its G-R-D-T anchors, then continuously execute every ready
   card it owns, one isolated Coder/Reviewer/Verifier lane per card; serialize only valid
   dependencies, incompatible conflict domains or runtime locks, and integration into the
   shared baseline.
7. Review each code increment independently and replay task-level evidence.
8. Run the regression and E2E required by the target Milestone.
9. Use the target-scoped pre-close checklist, obtain owner acceptance, refresh its state
   representations, write Handoff (including non-blocking downstream TODOs), and return to
   `roadmap`.

Operational contracts and checklists:

- [dispatch and handoff](skills/gmgn/references/en/dispatch-and-handoff.md)
- [writing contract](skills/gmgn/references/en/writing-contract.md), which fixes machine
  fields and parser surfaces but does not prescribe document layout
- [preflight](skills/gmgn/references/en/preflight-checklist.md),
  [pre-merge](skills/gmgn/references/en/pre-merge-checklist.md), and
  [pre-close](skills/gmgn/references/en/pre-close-checklist.md) checklists
