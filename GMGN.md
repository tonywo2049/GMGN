---
locale: en
purpose: Define GMGN roles, document chains, hard gates, independent review, and closure discipline.
upstream: none
downstream: [writing contract](skills/gmgn/references/en/writing-contract.md), [dispatch contract](skills/gmgn/references/en/dispatch-and-handoff.md), [preflight checklist](skills/gmgn/references/en/preflight-checklist.md), [pre-merge checklist](skills/gmgn/references/en/pre-merge-checklist.md), [pre-close checklist](skills/gmgn/references/en/pre-close-checklist.md)
status: approved
type: whitepaper
nature: normative
---

# GMGN: a lightweight engineering method for agent collaboration

中文版本：[GMGN.zh-CN.md](GMGN.zh-CN.md)

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
  in parallel with useful orchestration work.
- **Author** writes one delegated document candidate.
- **Coder** implements one bounded Card attempt.
- **Critic** independently challenges document meaning.
- **Reviewer** independently reviews implementation or test-code diffs.
- **Verifier** independently executes the required checks against one fixed candidate.

Every delegated agent is single-use. Prepare its complete brief before creation, give it one
bounded objective, accept one return, and retire it. A revision, retry, recheck, or later
verification uses a new agent and new brief without parent or earlier-agent conversation
history. The primary orchestrator is not a delegated agent and remains the integration owner;
there is no Integrator-agent role.

## 2. Authority and document chain

The normal semantic chain is:

```text
WhitePaper → ROADMAP → Goal → Requirement → Design → Task
```

- WhitePaper owns the problem, goals, scope, non-goals, and invariants.
- ROADMAP owns Milestone order, priority, and cross-Milestone dependency.
- Goal owns one initiated Milestone's objective and boundary.
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

After the owner confirms the execution set, `run-task` creates exactly two files per selected
task before Coder dispatch:

- `execution/<card_id>/Card.md` — normative stable execution/TDD contract. It links to the
  exact Task/Requirement/Design authority and exposes `execution_log: [Log.md](Log.md)`.
- `execution/<card_id>/Log.md` — descriptive current snapshot plus append-only events. Its
  snapshot exposes `latest_event` as a link to the current event anchor in that file.

Create Card first, then Log, then publish the Task execution link to Card in the same checked
candidate. Do not create separate State, Verification, per-role Handoff, or project-wide
execution-log files unless an independent project requirement needs one.

## 4. Review and verification

Freeze a candidate before independent checks. Select roles by what changed:

| Changed surface | Independent check |
|---|---|
| WhitePaper/ROADMAP/Goal/Requirement/Design/Task meaning | fresh Critic |
| implementation or test-code diff | fresh Reviewer |
| executable result, environment, or package input | fresh Verifier after review clears |
| equivalent links, formatting, pointers, or status | machine checks only |

Critic and Reviewer findings are collected before any edit. The primary orchestrator
adjudicates once and batches accepted blocker fixes. Recheck only changed scope when the new
brief proves the boundary; do not dispatch unchanged roles. Non-blocking suggestions do not
reopen an otherwise acceptable candidate.

Do not dispatch a Verifier while relevant review blockers remain. By default, first create the
final temporary combined candidate, then use one fresh Verifier there. Do not repeat the same
verification at lane and integration boundaries. A second boundary needs a recorded reason,
such as non-transferable environment evidence, changed baseline/test inputs, an integration
decision that itself needs runtime proof, or an explicit project policy.

A simple mechanical or documentation-only change may need no Verifier. Verification exists to
independently establish executable evidence, not to complete a role checklist.

## 5. Task execution and integration

`run-task` continuously fills a dependency-aware ready set. A task is ready when its
prerequisites are integrated and any declared shared-resource constraint is available.
Concurrency is determined by real capacity; GMGN defines no fixed agent count or wave barrier.

Concurrent writers use isolated worktrees or equivalent workspaces. A single writer may use a
verified current workspace when no other writer can collide with it. One task has one writer
at a time. The Coder writes only the allowed scope in its prepared brief and returns an
immutable local candidate. The primary orchestrator owns Task/Card/Log runtime state, the
integration queue, and the shared baseline.

After review clears, the primary orchestrator mechanically applies an isolated-lane candidate
to a temporary combination. A frozen sole-writer candidate already based on the unchanged
shared baseline is itself the final combination and needs no copy. A clean application needs
no Coder. A conflict or judgment-required resolution uses a fresh Coder and returns through
only the affected review and verification gates. An unverified executable combination never
becomes the shared baseline.

Wait only after dispatch, local checks, integration, and state refresh are exhausted. Use one
event-driven longest-safe wait. A timeout is a liveness checkpoint, not a reason to start a
list/status/wait polling loop.

## 6. Change, closure, and release

When evidence contradicts approved meaning, route the semantic change to its owning authority
and pause only its impact cone. Record old and new anchors and propagate only affected tasks,
code, tests, evidence, and state. Mechanical changes need machine checks, not semantic
reapproval.

Milestone closure requires:

1. every in-scope AC completed or semantically removed/reassigned at a new authority anchor;
2. replayable evidence for each retained criterion;
3. Task, Card/Log, traceability, and ROADMAP refreshed in the same batch;
4. owner acceptance bound to the closing anchor.

Create a separate handoff only when a receiving operator needs information that has no better
existing authority. Release reuses review and verification evidence when source, semantics,
test plan, environment, and package inputs are unchanged. Tagging, upload retries, and local
installation are not reasons to repeat Milestone closure.

For a narrow bug or one-step mechanical change, identify the smallest authority and acceptance
condition, implement it, independently review the diff, verify executable behavior only when
needed, and refresh state. Do not fabricate the full document chain.

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
