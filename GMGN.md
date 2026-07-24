---
locale: en
purpose: Define GMGN roles, document chains, hard gates, independent review, and closure discipline.
upstream: none
downstream: [writing contract](skills/gmgn/references/en/writing-contract.md), [dispatch contract](skills/gmgn/references/en/dispatch-and-handoff.md), [preflight checklist](skills/gmgn/references/en/preflight-checklist.md), [pre-merge checklist](skills/gmgn/references/en/pre-merge-checklist.md), [pre-close checklist](skills/gmgn/references/en/pre-close-checklist.md)
status: approved
type: whitepaper
nature: normative
assurance_policy: gmgn-assurance-v1
---

# GMGN: a lightweight engineering method for agent collaboration

GMGN coordinates one accountable human owner, one primary AI orchestrator, and short-lived
task agents. It addresses two risks:

- **representation drift** — documents, status, tests, and evidence stop matching reality;
- **shared blind spots** — a writer and reviewer inherit the same assumptions and miss the
  same defect.

The response is a small set of versioned authorities, independent checks selected by impact,
and same-batch state refresh. GMGN is not a reason to create roles, files, or gates that the
current task does not need.

## 1. Roles

- **Owner** decides scope, approvals, acceptance, release authority, and any semantic removal
  or reassignment of a completion criterion.
- **Primary orchestrator** retains the complete session context, routes stages, prepares
  briefs, adjudicates findings, integrates accepted work, and updates shared state. It may
  directly write WhitePaper, ROADMAP, Goal, Requirement, Design, and Task when that is the
  clearest use of context. It may act as one Coder only when no implementation lane can run
  in parallel with useful orchestration work. During long-running work, it must not send a
  progress update while observable state is unchanged; update only for material progress, a
  blocker, a decision request, or the final result.
- **Author** writes one delegated document candidate.
- **Coder** implements one bounded Card attempt.
- **Critic** independently challenges document meaning.
- **Reviewer** independently reviews implementation or test-code diffs and runs the prepared
  deterministic local checks against that frozen candidate.
- **Verifier** independently executes checks against one fixed final candidate only when the
  [assurance policy](skills/gmgn/references/en/assurance-policy.json) records a trigger.

Every delegated agent is single-use. Prepare its complete brief before creation, give it one
bounded objective, accept one return, and retire it. A later authoring or coding attempt,
separately scoped semantic or implementation change, or later verification uses a new agent
and new brief without parent or earlier-agent conversation history. Critic and Reviewer are
not redispatched to recheck fixes from their completed round. The primary orchestrator is not
a delegated agent and remains the integration owner; there is no Integrator-agent role.

## 2. Authority and document chain

The normal semantic chain is:

```text
WhitePaper → ROADMAP → Goal → Requirement → Design → Task
```

- WhitePaper owns the problem, goals, scope, non-goals, and invariants.
- ROADMAP owns Milestone order, priority, cross-Milestone dependency, and each Milestone's
  qualitative acceptance picture.
- Goal owns one initiated Milestone's objective, boundary, slices, and the mapping from the
  ROADMAP acceptance picture into active scope.
- Requirement owns requirements, constraints, and acceptance criteria (ACs).
- Design owns the implementation structure, interfaces, data, and failure paths.
- Task owns task division, AC mapping, dependencies, macro status, and execution pointers.

One fact has one authority. Other documents link to it instead of copying it. Approval binds
to an immutable version anchor; editing a file never moves approval automatically.

Human prose may be English or Chinese. Machine fields, IDs, status tokens, and Task headers
remain stable. The complete structural contract is in the
[writing contract](skills/gmgn/references/en/writing-contract.md).

## 3. Compact Task and per-card execution

`Task.md` is a Milestone index, not an execution diary:

```markdown
| # | task | spec anchor | prerequisite | status | execution |
```

It also contains the AC-to-task mapping and Milestone-level execution pointers. It does not
contain TDD cases, commands, write sets, locks, blockers, candidate anchors, review rounds,
verification evidence, or progress history.

Within the approved Design, Task decomposition targets useful independent execution. Give each
task one primary responsibility and an independently decidable result; minimize unnecessary
dependencies, shared writes, and runtime conflicts so work with no real dependency can run in
parallel. Optimize useful parallelism, not task count. Do not invent empty wrapper tasks, fake
interfaces, or new design decisions merely to create concurrency, and stop when coordination
cost exceeds the isolation benefit.

After the owner confirms the execution set, `run-task` creates exactly two files per selected
task before Coder dispatch:

- `execution/<card_id>/Card.md` — normative stable execution/TDD contract. It links to the
  exact Task/Requirement/Design authority and exposes `execution_log: [Log.md](Log.md)`.
- `execution/<card_id>/Log.md` — descriptive execution record with a replaceable current
  snapshot, material decisions only, and one final evidence summary when closed.

Create Card first, then Log, then publish the Task execution link to Card in the same checked
candidate. Do not create separate State, Verification, per-role Handoff, or project-wide
execution-log files unless an independent project requirement needs one.
For DocStar compatibility, the snapshot keeps one `latest_event` pointer: it targets
`#current` while active and `#final-evidence` when closed. This pointer does not create an
event ledger or require generated event IDs.

## 4. Review and verification

Freeze a candidate before independent checks. Select roles by what changed:

| Changed surface | Independent check |
|---|---|
| WhitePaper/ROADMAP/Goal/Requirement/Design/Task meaning | fresh Critic |
| implementation or test-code diff, including deterministic local execution | fresh Reviewer |
| recorded trigger from the assurance policy | fresh Verifier after review clears |
| equivalent links, formatting, pointers, or status | machine checks only |

The Critic/Reviewer rows above are evaluated only once, immediately before the change batch's
review round. An accepted finding fix remains part of that reviewed batch and does not
re-enter role selection.

Each semantic change batch or task execution uses `review_policy: single-pass`: at most one
independent Critic/Reviewer round. When both surfaces changed, both roles may run in that same
round. Collect every finding before editing. The primary orchestrator adjudicates once,
batches accepted blocker fixes,
checks each resolution against the finding, and runs the affected machine checks. This bounded
resolution check does not search for new findings. Do not resume or create a Critic/Reviewer
for those fixes. A fix that expands authority, scope, or behavior
beyond the accepted findings becomes a separately scoped change rather than a review recheck.
The final anchor records the reviewed anchor, complete findings and rulings, exact fix delta,
and post-fix checks. Non-blocking suggestions do not reopen an otherwise acceptable candidate.

Critic and Reviewer do not maximize finding count; a valid review may return no findings.
Before reporting an issue, they consider its concrete material harm if left unresolved,
whether an effective fallback already keeps the impact within accepted bounds, and the
smallest sufficient correction. Omit preference-only, speculative, low-impact, or adequately
contained issues when they do not change acceptance or the next action. Verifier applies the
same materiality boundary to incidental observations, runs only the checks needed to decide
its recorded trigger, and stops when that decision is established. It cannot waive a failed,
skipped, timed-out, or unavailable required check unless an accepted fallback is itself the
required and successfully verified path.

The Reviewer runs the prepared deterministic local checks as part of its single return and
reports exact commands, environment, exit codes, limitations, and side effects. After accepted
findings are fixed, the primary orchestrator checks the exact fix delta and reruns affected
machine checks; this does not trigger another independent review or verification round. The
Reviewer and Verifier only check evidence: on both pass and failure, every tracked file must
remain unchanged. Evidence generation or refresh belongs to the Coder or primary orchestrator
before the independent check.

A fresh Verifier is exceptional, not default. Classify the final candidate against the
assurance policy as `not-required` or `required:<trigger>`. Do not dispatch a Verifier while
relevant review blockers remain. When required, run it once against the blocker-resolved final
candidate and bind its evidence there. Verification is an evidence activity, not a mandatory
agent stage.

## 5. Task execution and integration

`run-task` continuously fills a dependency-aware ready set. A task is ready when its
prerequisites are integrated and any declared shared-resource constraint is available.
Concurrency is determined by real capacity; GMGN defines no fixed agent count or wave barrier.
Before waiting or acting as a Coder, the primary orchestrator scans every task in the confirmed
execution set, not only the current card or active lane, and dispatches every ready,
non-conflicting task that fits currently available capacity.

Compliance checks are triggered by a real boundary or material state change, not merely by
starting a task. Before the first write, confirm the Card scope, preservation of existing user
changes, and one writer per workspace. Concurrent writers use isolated worktrees or equivalent
workspaces; a single writer may use the current workspace. Require workspace/base anchors and
a transferable commit range only when concurrent work or candidate handoff makes them
necessary. When CodeGraph indexing is authorized and the CLI is available, initialize it once
in each isolated workspace before source discovery; initialization failure falls back to
targeted source reads and never blocks the task. Every query targets the exact assigned
workspace. Use its usable index first for source location and code relationships, and treat
returned source as already read. Read files directly only when the index is absent, stale,
unsupported, changed after the query, or insufficient for the decision. Freeze the simplest
exact identity before review: a diff or content hash for a sole writer, and the complete
base-to-tip diff or ordered commit chain for an isolated handoff.
Recheck a fact only after an event or command that could have changed it. Before integration,
confirm that the content being integrated is the reviewed content; a changed commit SHA alone
does not invalidate equivalent content. Do not repeat unchanged checks or create evidence only
to prove that a compliance check ran.

Discovery does not expand a task. Once a Card is active, its outcome, completion criterion,
and authority boundary stay fixed. A newly found issue belongs to that Card only when leaving
it unresolved prevents the Card outcome or a prepared required check, no accepted effective
fallback contains the impact, and the smallest sufficient correction fits the existing
authority without adding another independently testable outcome. Otherwise omit a low-value
issue, present a materially valuable separate candidate to the primary orchestrator, or route
an authority change upstream; do not keep the current Card open. Close the task as soon as its
Card outcome works, prepared required checks pass, accepted blockers are resolved, and any
required verification passes.

The primary orchestrator owns Task/Card/Log runtime state, the integration queue, and the
shared baseline. It applies the complete transferable candidate, resolves judgment-required
conflicts before review, and integrates only content covered by required review and
risk-triggered evidence.

Wait only after dispatch, local checks, integration, and state refresh are exhausted. Use one
event-driven longest-safe wait. A timeout is a liveness checkpoint, not a reason to start a
list/status/wait polling loop. Use one `list_agents` snapshot only when a scheduling/capacity
decision needs current state, a wait timed out without an unambiguous agent state, or received
lifecycle events conflict. One call serves one decision point; do not query again until a
material lifecycle event, candidate, blocker, or scheduling condition changes. There is no
periodic list interval; a wait timeout configures only that wait call.

## 6. Change, closure, and release

When evidence contradicts approved meaning, route the semantic change to its owning authority
and pause only its impact cone. Record old and new anchors and propagate only affected tasks,
code, tests, evidence, and state. Mechanical changes need machine checks, not semantic
reapproval.

Milestone closure requires:

1. every ROADMAP acceptance scenario traced through Goal slices and in-scope ACs to evidence;
2. every in-scope AC completed or semantically removed/reassigned at a new authority anchor;
3. replayable evidence for each retained criterion;
4. Task, Card/Log, traceability, and ROADMAP refreshed in the same batch;
5. owner acceptance bound to the closing anchor.

Create a separate handoff only when a receiving operator needs information that has no better
existing authority. Release reuses review and verification evidence when source, semantics,
test plan, environment, and package inputs are unchanged. An unchanged deterministic packaging
recipe uses machine checks rather than an automatic Verifier; installation, startup,
non-machine-checkable artifacts, or another recorded risk may still require one. Tagging,
upload retries, and local installation are not reasons to repeat Milestone closure.

For a narrow bug or one-step mechanical change, identify the smallest authority and acceptance
condition, implement it, independently review the diff and deterministic local behavior, add
separate final-candidate verification only when a risk trigger requires it, and refresh state.
Do not fabricate the full document chain.

## 7. Tools and anti-overdesign boundary

Automation may parse, link, compare, execute, and report. It cannot invent product meaning or
approval. DocStar is optional structural tooling; CodeGraph is optional navigation; exact
documents, source, diffs, tests, and runtime behavior remain evidence. Telemetry is out-of-band
observation and never changes routing, readiness, acceptance, or closure.

Choose the first sufficient option:

1. no implementation;
2. reuse existing repository behavior;
3. standard library or platform-native capability;
4. existing dependency;
5. direct implementation;
6. the smallest new structure.

Do not add roles, state machines, identity history, configuration, wrappers, or documents
without a current requirement. Preserve trust-boundary validation, security, accessibility,
and data-loss protection; simplicity is not permission to remove required safeguards.

Completion does not require every non-critical issue to be perfected. When the accepted main
path works and an effective fallback keeps a remaining non-blocking issue within acceptable
bounds, stop fixing that issue. A task is complete when its Card contract is satisfied, not
when every nearby issue discovered during the work has been resolved.

Before every substantive return, self-check the active contract and correct in-scope defects.
Do not output a fixed `Reflection` section. Report only unresolved material risk that could
change a decision, acceptance, or downstream work.

Operational detail lives in the stage Skills and these shared contracts:

- [dispatch](skills/gmgn/references/en/dispatch-and-handoff.md)
- [writing](skills/gmgn/references/en/writing-contract.md)
- [code review](skills/gmgn/references/en/code-review.md)
- [preflight](skills/gmgn/references/en/preflight-checklist.md)
- [pre-merge](skills/gmgn/references/en/pre-merge-checklist.md)
- [pre-close](skills/gmgn/references/en/pre-close-checklist.md)
