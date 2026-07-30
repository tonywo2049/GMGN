---
locale: en
purpose: Define GMGN roles, document chains, hard gates, independent review, and closure discipline.
upstream: none
downstream: [writing rules](skills/gmgn/references/en/writing-rules.md), [dispatch contract](skills/gmgn/references/en/dispatch-and-handoff.md), [code-review contract](skills/gmgn/references/en/code-review.md)
status: approved
type: whitepaper
nature: normative
assurance_policy: gmgn-assurance-v2
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
  directly write WhitePaper, Decision, ROADMAP, Goal, Requirement, Design, and Task when that
  is the clearest use of context. It may act as one Coder only when no implementation lane can run
  in parallel with useful orchestration work. During long-running work, it must not send a
  progress update while observable state is unchanged; update only for material progress, a
  blocker, a decision request, or the final result.
- **Author** writes one delegated document candidate.
- **Coder** implements one bounded Card attempt.
- **Critic** independently challenges document meaning.
- **Reviewer** independently reviews implementation or test-code diffs and runs the prepared
  deterministic local checks against that candidate commit.
- **Verifier** independently executes checks against one fixed final candidate only when the
  [assurance policy](skills/gmgn/references/en/assurance-policy.json) records a trigger.

Every delegated agent is single-use under the
[dispatch contract](skills/gmgn/references/en/dispatch-and-handoff.md). The primary
orchestrator is not a delegated agent and remains the integration owner; there is no
Integrator-agent role.

## 2. Authority and document chain

The normal semantic chain is:

```text
WhitePaper → Decision → ROADMAP → Goal → Requirement → Design Bundle → Task
                                                         ├─ Design.md
                                                         └─ design/ only for needed module, contract, or schema authorities
```

- WhitePaper owns the problem, goals, scope, non-goals, and invariants.
- `Decision.md` owns the complete current set of accepted project-level product, business,
  protocol, and architecture rulings that constrain multiple Milestones and are not already
  owned by another stage. The primary orchestrator identifies candidates and recommends the
  jurisdiction and options; the human owner decides both. Stable D-IDs identify current
  rulings. `DecisionLog.md` is descriptive accepted-change history and never downstream
  authority.
- ROADMAP owns outcome-based Milestone allocation, `now | next | later` horizons, relative
  priority, real cross-Milestone dependencies, necessary deliverables, result-level success
  signals, and a curated Backlog. Dependencies create only a partial order; Milestone IDs and
  display order do not. The primary orchestrator proposes the map, then asks the human owner
  one material allocation question at a time before writing the candidate. ROADMAP does not
  own an E2E path or detailed Close criteria.
- Goal refines one initiated Milestone for exactly two purposes: provide the basis for
  Requirement and define qualitative Milestone Close criteria. It owns only the active
  boundary needed to prevent scope ambiguity, necessary Milestone-local exclusions that do
  not remove upstream obligations, ROADMAP deliverable/success-signal coverage, and the
  smallest sufficient set of qualitative Close outcomes. Result grouping is optional and
  creates no separate authority. The primary orchestrator normally drafts directly; owner
  initiation is not Goal approval, so the exact candidate receives one final owner
  confirmation before Requirement may use it.
- Requirement translates Goal into required observable behavior, quantified parameters,
  constraints, and decidable acceptance criteria (ACs).
- `Design.md` is the root Design authority and complete R/AC mapping entry. Add architecture,
  module boundaries, and `design/<module-id>.md` only when current R/ACs need them. Add a
  Bundle index only when linked child artifacts exist. A boundary between
  independently developed modules, tasks, teams, processes, or repositories requires
  `design/Contract.md`; split contracts and structural authorities under `design/contracts/`
  and `design/schemas/` only when current correctness or independent review needs them.
  The complete linked Bundle is accepted at one Git commit.
- Design must determine every implementation-significant choice that could change another
  unit's data, authority, validation, error, state, recovery, security, compatibility, or
  resource behavior. If two non-communicating Coders could produce incompatible conforming
  implementations, Design is not ready. Task cannot supply the missing decision.
- Every applicable cross-unit boundary closes its authoritative producer, derivation,
  consumer validation entries, success/errors, and state effects. Exact compatibility-
  significant structure has one machine-readable or compilable authority; Markdown links it
  and owns only semantics that structure cannot express.
- Task owns task division, AC mapping, dependencies, macro status, and execution pointers.

Each stage document contains only facts needed for its own purpose. Stage documents do not
contain document maps without real children, downstream propagation rules, downstream gates,
or next-stage instructions. The GMGN router owns cross-stage routing and impact propagation.

An approved `Decision.md` is required before ROADMAP even when no additional ruling beyond
WhitePaper is currently needed. Later stages read applicable current D-IDs, not
`DecisionLog.md`. If later work exposes a missing or changed cross-Milestone ruling, pause
only the affected work, route the candidate through `write-decision`, and resume after the
approved delta is propagated.

One fact has one authority. Other documents link to it instead of copying it. Every review,
approval, acceptance, Milestone closure, and release binds to a Git commit or release tag.
Commit the candidate locally before independent review. Human-facing documents, briefs, logs,
and returns use the shortest unambiguous commit reference or the tag. They never use a
full-length commit object ID, diff hash, content hash, archive checksum, or artifact checksum
as a workflow anchor. If the current workspace cannot safely create the candidate commit, use
an isolated worktree. Checksums are evidence only. Editing a file never moves approval
automatically.

Documents under a project-declared archive root are historical storage, not active authority.
Writers, Critics, Reviewers, and Verifiers do not read, cite, or use them as context or
evidence. Exclude archive roots from briefs and generated context. If active work needs
archived meaning, restore it to the active tree through its owning authority before use.

Human prose may be English or Chinese. Machine fields, IDs, status tokens, and Task headers
remain stable. The complete structural rules are in
[writing rules](skills/gmgn/references/en/writing-rules.md).

## 3. Task index and per-card execution

`Task.md` is a Milestone index, not an execution diary:

```markdown
| # | task | spec anchor | prerequisite | status | execution |
```

It also contains the AC-to-task mapping and Milestone-level execution pointers. It does not
contain verification cases, commands, write sets, locks, blockers, candidate commit
references, review rounds, verification evidence, or progress history.

[`write-task`](skills/write-task/SKILL.md) solely owns the per-row Task boundary, dependency
semantics, AC mapping, and granularity check; Task count itself is not a measure of simplicity
or overdesign.

After the owner confirms the execution set, `run-task` creates exactly two files per selected
task before Coder dispatch:

- `execution/<card_id>/Card.md` — normative execution and verification contract with its completion
  criterion.
- `execution/<card_id>/Log.md` — replaceable current snapshot, material decisions, and final
  evidence summary; not a full process history.

`Task.md` links to Card without copying execution content. Detailed Card and Log rules remain
in `run-task` and the writing rules.

## 4. Review and verification

Commit the complete candidate locally before independent checks. Document meaning passes the
Critic necessity gate defined by the [GMGN router](skills/gmgn/SKILL.md). For implementation,
`run-task` owns the at-most-two-round dispatch schedule and the
[code-review contract](skills/gmgn/references/en/code-review.md) owns each Review surface.
There is no third Review round.

A fresh Verifier remains risk-triggered rather than automatic. Failed, skipped, timed-out, or
unavailable required checks are not passes. The
[assurance policy](skills/gmgn/references/en/assurance-policy.json) defines role triggers,
and stage Skills define when Review and verification are dispatched.

## 5. Task execution and integration

`run-task` owns Card/Log materialization, the dependency-aware ready set, conflict-aware
parallel dispatch, runtime tool policy, bounded writer lanes, Codex agent monitoring, full and
delta Review dispatch, verification, integration, and Task closure. The primary orchestrator
retains runtime state, the integration queue, and the shared baseline.

All Coder lanes use the same approved Design Bundle commit and must not invent or edit shared
interface authority. Evidence that contradicts Design or Contract returns upstream through
the owning stage while unaffected work continues. Discovery does not expand a Card.

A Task closes only after the reviewed content is integrated into the shared baseline and every
project-declared required check has passed against that exact integrated candidate. Skipped,
unavailable, or unauthorized checks do not count as passes. Detailed execution rules are
defined only by [`run-task`](skills/run-task/SKILL.md).

## 6. Change, closure, and release

When evidence contradicts approved meaning, route the semantic change to its owning authority
and pause only its impact cone. A Decision change replaces current meaning in `Decision.md`
and appends only its accepted change event to `DecisionLog.md`. Record old and new commits
and propagate only affected authorities, tasks, code, tests, evidence, and state. Mechanical
changes need machine checks, not semantic reapproval.

Milestone closure proves every ROADMAP deliverable and every Goal Close outcome through
in-scope ACs and sufficient evidence. When an end-to-end result matters, Goal and Requirement
own the outcome and observable behavior; verification may use E2E evidence without putting
the path in ROADMAP.

Closure also reconciles every retained Contract ID with provider and consumer code plus
conformance/integration evidence. A semantic mismatch returns to `write-design`; closure never
edits authority to excuse code. Owner acceptance marks the reconciled Contract commit
`closed`, which is the Milestone's final frozen contract. Later Milestones create controlled
new commits rather than rewriting that history.

Milestone closure requires:

1. every ROADMAP deliverable and success signal mapped through Goal Close outcomes and
   in-scope ACs to evidence;
2. every in-scope AC completed or semantically removed/reassigned at a new authority commit;
3. replayable evidence for each retained criterion;
4. Task, Card/Log, traceability, and ROADMAP refreshed in the same batch;
5. owner acceptance bound to the closing commit.

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

Solution minimality is an acceptance condition for every stage document. A retained item must
change that document's own result if removed. A possible future need, speculative reuse,
workflow narration, downstream management, or implementation convenience is not an owner.
Anything removable without weakening the document's purpose is overdesign.

When dispatched, the independent Critic applies the deletion test to affected stage candidates
except Task division, whose necessity and boundary checks are owned by
[`write-task`](skills/write-task/SKILL.md). For other candidates it first attempts deletion,
reuse, native behavior, or a direct solution. Unresolved overdesign is a material acceptance
finding, not a wording, cleanup, or low-impact preference.

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
The same deletion test applies to `design/Contract.md`: it is required for a current
independently developed boundary and omitted when one implementation unit owns the interface.
Never create an empty contract, module document, schema directory, or duplicate a code-native
schema in prose.

Code minimality is delegated to the registered
[Ponytail](https://github.com/DietrichGebert/ponytail) plugin. `run-task` is the sole authority
for when Ponytail, CodeGraph, and DocStar are used during task execution; their rules are not
copied into this core method.

Completion does not require every non-critical issue to be perfected. When the accepted main
path works and an effective fallback keeps a remaining non-blocking issue within acceptable
bounds, stop fixing that issue. A task is complete when its Card contract is satisfied, not
when every nearby issue discovered during the work has been resolved.

Operational detail lives in the stage Skills and these shared rules and contracts:

- [dispatch](skills/gmgn/references/en/dispatch-and-handoff.md)
- [writing rules](skills/gmgn/references/en/writing-rules.md)
- [code review](skills/gmgn/references/en/code-review.md)
