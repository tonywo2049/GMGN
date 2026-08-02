---
locale: en
purpose: Define GMGN roles, document chains, hard gates, independent review, and closure discipline.
upstream: none
downstream: [writing rules](skills/gmgn/references/en/writing-rules.md), [dispatch contract](skills/gmgn/references/en/dispatch-and-handoff.md), [code-review contract](skills/gmgn/references/en/code-review.md)
status: approved
type: whitepaper
nature: normative
assurance_policy: gmgn-assurance-v3
---

# GMGN: a lightweight engineering method for agent collaboration

GMGN coordinates one accountable human owner, one primary AI orchestrator, and bounded task
agents. It addresses two risks:

- **representation drift** — documents, status, tests, and evidence stop matching reality;
- **shared blind spots** — a writer's own checks can preserve the same assumptions and miss
  the same defect.

The response is a small set of versioned authorities, independent checks selected by impact,
and same-batch state refresh. GMGN is not a reason to create roles, files, or gates that the
current task does not need.

## 1. Roles

- **Owner** decides scope, stage approvals, release authority, and any semantic removal or
  reassignment of a completion criterion, and reviews Milestone closure. Closure review is not
  an irrevocable acceptance decision.
- **Primary orchestrator** retains the complete session context, routes stages, conducts Owner
  dialogue, analyzes evidence, makes workflow and semantic decisions, schedules agents,
  adjudicates Critic and Reviewer findings, manages workspaces, and updates shared state.
  Outside `run-task`, it integrates accepted candidates. It may perform meaning-preserving
  mechanical edits, but it does not write upstream authority, planning, or design candidates
  and does not act as a Coder. During long-running work, it must not send a progress update
  while observable state is unchanged; update only for material progress, a blocker, a
  decision request, or the final result.
- **Commander** is the single workspace-write global-judgment role used only in `run-task`.
  One bounded Commander reads current repository state, computes ready work, supplies complete
  Runner briefs, resolves cross-Task conflicts and upstream returns, and integrates one fixed
  candidate under the existing lock and evidence gates. Only the primary orchestrator creates,
  resumes, or retires it. A Commander creates no agents and has no role variants or standing
  pool.
- **Runner** owns one accepted Task and its workspace end to end. It directly creates any
  needed Coder, Researcher, or risk-triggered Verifier, normally reviews the Coder candidate
  itself, and reports only substantive structured state or results to the primary
  orchestrator. Parallel Runners do not coordinate directly.
- **Author** independently writes and revises one bounded upstream authority, plan, design, or
  closure document candidate from a primary-orchestrator brief. Its self-check is not review
  or acceptance of its own candidate. Normal Task execution does not use an Author.
- **Coder** creates or resumes one Card/Log execution contract and implements its bounded Task
  candidate. Its tests and self-checks are evidence, not review or acceptance.
- **Critic** independently challenges a fixed normative document candidate when the primary
  orchestrator's necessity gate selects it.
- **Reviewer** independently reviews only a fixed implementation and test candidate when the
  Owner, authority, workflow, or Commander explicitly requires that role. Normal `run-task`
  review is performed by the Task's Runner.
- **Researcher** collects bounded source-by-source facts without comparing or selecting a
  solution; its caller analyzes and decides. The primary orchestrator may create it outside
  `run-task`, and a Runner may create it inside `run-task`.
- **Verifier** independently executes checks against one fixed final candidate only when the
  [assurance policy](skills/gmgn/references/en/assurance-policy.json) records a trigger.

Every delegated agent follows the
[dispatch contract](skills/gmgn/references/en/dispatch-and-handoff.md). The primary orchestrator
is not a delegated agent. Only `run-task` uses the Commander-and-Runner hub-and-spoke flow;
other stages remain in the primary session. An active Commander, Runner, Author, or Coder
keeps its identity through an interim question, child return, candidate checkpoint, or
in-scope repair while objective and write boundary remain unchanged. It retires when that
objective completes, is invalidated, is cancelled, or hard-fails. There is no Integrator role.

## 2. Authority and document chain

The normal semantic chain is:

```text
WhitePaper → Decision → ROADMAP → Goal → Requirement → Design Bundle → Task
                                                         ├─ Design.md
                                                         └─ design/ only for needed module, contract, or schema authorities
```

- WhitePaper owns the problem, goals, scope, non-goals, and invariants.
- `Decision.md` may own any accepted ruling explicitly recorded for downstream consumption,
  regardless of subject or Milestone scope. The primary orchestrator identifies candidates
  and recommends their options, scope, and downstream consequences; the human owner makes the
  ruling. Stable D-IDs identify current rulings. `DecisionLog.md` is descriptive
  accepted-change history and never downstream authority.
- ROADMAP owns outcome-based Milestone allocation, `now | next | later` horizons, relative
  priority, real cross-Milestone dependencies, necessary deliverables, result-level success
  signals, and a curated Backlog. Dependencies create only a partial order; Milestone IDs and
  display order do not. The primary orchestrator resolves allocation meaning and an Author
  writes one complete map for Owner approval. The primary orchestrator asks beforehand only
  when an irreversible blocking choice cannot be safely recommended or deferred. ROADMAP does not own an E2E path
  or detailed Close criteria.
- Goal refines one eligible `now` Milestone for exactly two purposes: provide the basis for
  Requirement and define qualitative Milestone Close criteria. It owns only the active
  boundary needed to prevent scope ambiguity, necessary Milestone-local exclusions that do
  not remove upstream obligations, ROADMAP deliverable/success-signal coverage, and the
  smallest sufficient set of qualitative Close outcomes. Result grouping is optional and
  creates no separate authority. An Author drafts the candidate after the primary
  orchestrator resolves its meaning; one Owner approval of the exact candidate both initiates
  the Milestone and approves Goal.
- Requirement translates Goal into required observable behavior, quantified parameters,
  constraints, and decidable acceptance criteria (ACs).
- `Design.md` is the root Design authority and complete R/AC mapping entry. Add architecture,
  module boundaries, and `design/<module-id>.md` only when current R/ACs need them. Add a
  Bundle index only when linked child artifacts exist. A boundary between
  independently developed modules, tasks, teams, processes, or repositories requires
  `design/Contract.md`; split contracts and structural authorities under `design/contracts/`
  and `design/schemas/` only when current correctness or independent review needs them.
  The complete linked Bundle is accepted at one Git commit.
- Design must determine or link every implementation-significant choice that could change
  another unit's data, authority, validation, error, state, recovery, security,
  compatibility, or resource behavior. If two non-communicating Coders could produce
  incompatible conforming implementations, Design is not ready. Task cannot supply the
  missing decision.
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
`DecisionLog.md`. Any stage may place a ruling in Decision. Once recorded, Decision owns its
current meaning and downstream artifacts link it while retaining only their derived content.
If later work changes a D-ID or selects a new ruling for Decision, pause only the affected
work, route the candidate through `write-decision`, and resume after the approved delta is
propagated.

One fact has one authority. Other documents link to it instead of copying it. Every review,
approval, acceptance, Milestone closure, and release binds to a Git commit or release tag.
Commit the candidate locally before independent review. Human-facing documents, briefs, logs,
and returns use the shortest unambiguous commit reference or the tag. They never use a
full-length commit object ID, diff hash, content hash, archive checksum, or artifact checksum
as a workflow anchor. If the current workspace cannot safely create the candidate commit, use
an isolated worktree. Checksums are evidence only. Editing a file never moves approval
automatically.

Documents under a project-declared archive root are historical storage, not active authority.
Delegated agents do not read, cite, or use them as context or evidence. Exclude archive roots
from briefs and generated context. If active work needs archived meaning, restore it to the
active tree through its owning authority before use.

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

For an initiated Milestone, every accepted Task row enters execution when ready without a
separate owner confirmation. The Task's Coder creates exactly two files for each new Task, or
restores them for a reopened Task, before production implementation:

- `execution/<card_id>/Card.md` — normative execution and verification contract with its completion
  criterion.
- `execution/<card_id>/Log.md` — replaceable current snapshot, material decisions, and final
  evidence summary; not a full process history.

`Task.md` links to Card without copying execution content. Detailed Card and Log rules remain
in `run-task` and the writing rules.

## 4. Review and verification

Commit and freeze the complete candidate locally before review. For a normative document
candidate, the primary orchestrator applies the Critic necessity gate in the GMGN router and
adjudicates any Critic findings. A meaning-preserving mechanical change uses machine checks
without Critic. Each semantic candidate batch has at most one Critic round.

For implementation and test candidates, the Task's Runner normally performs the independent-
writer Review under the [code-review contract](skills/gmgn/references/en/code-review.md). Create
an independent Reviewer only when explicitly required by the Owner, applicable authority,
current workflow, or Commander brief. Reviewer never reviews a document-only candidate.

Critic and Reviewer report an issue only when leaving it unresolved causes concrete material
harm, no accepted effective fallback contains that harm, and a smallest sufficient correction
can be stated. The primary orchestrator adjudicates document findings; the Runner adjudicates
in-Task implementation findings. An accepted in-scope repair returns to the same Author or
Coder while objective and write boundary remain unchanged. The adjudicating caller checks the
exact repair and reruns only affected commands without automatically dispatching another
Critic or Reviewer.

A fresh Verifier remains risk-triggered rather than automatic and runs only after relevant
review blockers clear. Failed, skipped, timed-out, or unavailable required checks are not
passes. The
[assurance policy](skills/gmgn/references/en/assurance-policy.json) defines its triggers, and
stage Skills define candidate timing and fix handling.

## 5. Task execution and integration

`run-task` owns Card/Log materialization, the dependency-aware ready set, conflict-aware
parallel dispatch, runtime tool policy, bounded writer lanes, Codex agent monitoring, direct
fixed-candidate review, verification, integration, and Task closure. On entry, the primary
orchestrator creates a Commander with the Owner instruction, repository, and observable entry
points without collecting or analyzing the ready set. The Commander reads authority and state,
computes the ready set, and returns complete briefs; the primary orchestrator mechanically
creates one Runner per selected Task without rewriting those briefs.

The Runner owns its Task and workspace, directly manages its Coder and any needed Researcher
or Verifier, normally performs Review itself, and prepares the complete candidate. Coder writes
or restores Card/Log, verification contract, tests, implementation, and related evidence;
Runner may write Review, assurance classification, Verifier result, Task state, final evidence,
and other execution-document content. Normal Task execution does not use an Author.

When a Runner reports a candidate ready, the primary orchestrator creates one Commander with
the integration brief. That Commander obtains the existing integration lock, synchronizes the
latest shared baseline, forms and identifies the final candidate, runs or verifies the bound
gates, updates the shared baseline, and releases the lock. A content-changing rebase, conflict
resolution, or Commander edit invalidates affected candidate-bound evidence and returns
through the same Runner gates. A content-preserving merge commit may reuse it. The primary
orchestrator records the Commander result mechanically and does not repeat integration or
semantic review.

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
edits authority to excuse code. The accepted closure candidate marks the reconciled Contract
commit `closed`.
Owner review is one review input; it does not make the result irrevocable or separately
authorize integration.

Milestone closure requires:

1. every ROADMAP deliverable and success signal mapped through Goal Close outcomes and
   in-scope ACs to evidence;
2. every in-scope AC completed or semantically removed/reassigned at a new authority commit;
3. replayable evidence for each retained criterion;
4. Task, Card/Log, traceability, and ROADMAP refreshed in the same batch;
5. owner review recorded against the closing commit.

If unfinished work is found later, move the Milestone from `closed` back to `initiated`, clear
its current `accepted_result`, and reopen only affected Tasks or add the missing Tasks. Keep
the old result in Git history. Check downstream Milestones for actual impact instead of
rolling them back automatically. After the missing work and invalidated checks are complete,
close the Milestone again.

Create a separate handoff only when a receiving operator needs information that has no better
existing authority. Release reuses review and verification evidence when source, semantics,
test plan, environment, and package inputs are unchanged. An unchanged deterministic packaging
recipe uses machine checks rather than an automatic Verifier; the
[assurance policy](skills/gmgn/references/en/assurance-policy.json) alone determines whether
final-candidate verification is required. Tagging, upload retries, and local installation are
not reasons to repeat Milestone closure. The shared external-operation authorization in the
dispatch contract applies across execution and release.

For a narrow bug or one-step mechanical change, identify the smallest authority and acceptance
condition. Route implementation through the smallest applicable Task and `run-task`; apply
meaning-preserving document changes mechanically, add final-candidate verification only when a
risk trigger requires it, and refresh state. Do not fabricate the full document chain.

## 7. Tools and anti-overdesign boundary

Automation may parse, link, compare, execute, and report. It cannot invent product meaning or
approval. DocStar is optional structural tooling; CodeGraph is optional navigation; exact
documents, source, diffs, tests, and runtime behavior remain evidence. Telemetry is out-of-band
observation and never changes routing, readiness, acceptance, or closure.

Solution minimality is an acceptance condition for every stage document. A retained item must
change that document's own result if removed. A possible future need, speculative reuse,
workflow narration, downstream management, or implementation convenience is not an owner.
Anything removable without weakening the document's purpose is overdesign.

The primary orchestrator applies the deletion test to affected fixed stage candidates, and a
selected Critic independently challenges it. Task division keeps its own necessity and
boundary checks under [`write-task`](skills/write-task/SKILL.md). For other candidates first
attempt deletion, reuse, native behavior, or a direct solution. Unresolved overdesign is a
material acceptance finding, not a wording, cleanup, or low-impact preference.

Choose the first sufficient option:

1. no implementation;
2. reuse existing repository behavior;
3. standard library or platform-native capability;
4. existing dependency;
5. inspect a trusted external implementation and extract or adapt only its smallest closed
   code slice;
6. direct implementation;
7. the smallest new structure.

Selecting an external project does not authorize forking or importing its whole repository or
bringing in code that the current requirement does not need.

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
