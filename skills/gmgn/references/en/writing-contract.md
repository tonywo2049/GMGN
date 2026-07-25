---
locale: en
purpose: Define the stable machine fields, states, filenames, IDs, and parser surfaces shared by English and Chinese GMGN documents.
upstream: [GMGN methodology](../../../../GMGN.md)
downstream: [GMGN router](../../SKILL.md)
status: approved
type: design
nature: normative
---

# GMGN writing contract

## 1. Language and frontmatter

Select `en` or `zh-CN` from the existing project and the user's request. Prose uses that
language; machine fields, enums, filenames, IDs, commands, and Task headers below do not. A
project artifact chain normally uses one active locale. If a project independently requires
translated artifact chains, keep them in separate locale roots so duplicate IDs are not
scanned as one corpus.

Every GMGN-managed document starts with these seven keys:

```yaml
---
locale: en
purpose: <one sentence explaining what this document answers>
upstream: [<upstream name>](<relative path>)
downstream: [<downstream name>](<relative path>)
status: draft
type: requirement
nature: normative
---
```

- `locale`: `en | zh-CN`
- `status`: `draft | pending-approval | approved | closed`
- `type`: `whitepaper | roadmap | goal | requirement | design | contract | task | task-card |
  execution-log | research | decision | retrospective | handoff`
- `nature`: `normative | descriptive`

Use `upstream: none` for a root and `downstream: none` until the downstream file exists.
Replace `none` with a real relative link in the same checked batch that creates the file.
Normative content owns meaning; descriptive content records observations and never creates
scope or approval.

Documents under a project-declared archive root are historical storage only. Writers do not
read, cite, or use them as authority, context, or evidence. Restore needed meaning to the
active tree through its owning authority before use.

## 2. States and anchors

Normative document state is:

```text
draft → pending-approval → approved → closed
```

Task work state is:

```text
not-started → prepared → active | blocked → closed
```

`prepared` means Card and Log exist. `blocked` is only the Task-level macro signal; Log owns
the reason. `closed` means the accepted implementation and required evidence are integrated
on the shared baseline. The Reviewer normally supplies deterministic local execution evidence.
Any `required:<trigger>` Verifier evidence must be bound to the blocker-resolved final
candidate.

For an interface `Contract.md`, `approved` means the current shared working baseline that all
affected Coder lanes must follow. Coding evidence may replace it through a controlled
`write-design` revision at a new approved commit. `closed` means Milestone closure has
reconciled the contract with provider and consumer implementations plus evidence and the owner
has accepted that final frozen commit.

<HARD-GATE>In a Git-backed GMGN project, every review, approval, acceptance, Milestone
closure, and release anchor is a Git commit or release tag. Commit the candidate locally
before independent review. In human-facing documents, briefs, logs, and returns, use the
shortest unambiguous commit reference or the tag; never use a full-length commit object ID,
diff hash, content hash, archive checksum, or artifact checksum as a workflow anchor. If the
current workspace cannot safely create the candidate commit, use an isolated worktree.
Checksums are evidence only.</HARD-GATE>

Editing a file does not move a decision. WhitePaper and ROADMAP need owner approval; Goal,
Requirement, the whole Design-stage candidate, and Task need independent Critic review plus
primary-orchestrator acceptance; Milestone closure needs owner acceptance.

Each semantic change batch receives at most one Critic round. When accepted findings are fixed
after that review, the final accepted commit records the reviewed commit, complete findings
and rulings, exact fix delta, and post-fix machine checks. The fixes are not sent to a second
Critic.

## 3. Controlled changes

Change only the authority that owns the meaning:

| authority | route |
|---|---|
| WhitePaper | `brainstorm` revision |
| ROADMAP | `roadmap` maintenance |
| Goal | `write-goal` revision |
| Requirement or AC | `write-requirement` revision |
| Design or cross-task interface contract | `write-design` revision |
| Task | `write-task` revision |

A semantic change can alter scope, obligation, acceptance meaning, design intent, or execution
authority. It gets the review or approval appropriate to that authority at a new commit. A
mechanical change preserves meaning, such as formatting, links, mirrored status, or generated
metadata; it needs affected machine checks, not automatic semantic reapproval.

Propagate only the impact cone. Record the trigger, old commit, classification, exact delta,
affected IDs/files/tests/evidence, required review, and new commit in the owning authority or
an existing linked decision record. Do not add an empty change-log section or copy the record
into every affected document.

## 4. Stable names and Task surface

- Project: `WhitePaper.md`, `ROADMAP.md`
- Milestone: `Goal.md`, `Requirement.md`, `Design.md`, optional `Contract.md`, `Task.md`
- Card: `execution/<card_id>/Card.md`
- Runtime record: `execution/<card_id>/Log.md`
- Milestones: `M1`, `M2`, ...
- Requirements: `R1`, `R2`, ...
- ACs: `R1-AC1`, `R1-AC2`, ...
- Cross-task contracts: `C1`, `C2`, ...
- Tasks: `M1-T1`, `M1-T2`, ...; a single-Milestone corpus may use `T1`

Never renumber an ID after downstream references exist. Keep a tombstone or decision pointer
when removing one.

The parser-facing Task header is fixed:

```markdown
| # | task | spec anchor | prerequisite | status | execution |
|---|---|---|---|---|---|
| **M1-T1** | <independently decidable result> | R1-AC1 | none | not-started | none |
```

Chinese documents use the same header. Keep a separate `| AC | task |` mapping. Task owns task
division, spec anchors, the dependency DAG, macro status, execution pointers, and the few
Milestone-level pointers needed to schedule and integrate. It does not contain TDD cases,
commands, write sets, locks, blockers, candidate commit references, evidence, or progress history.
Replace current values; do not append execution narrative.

## 5. Design Bundle and interface contracts

`Design.md` is always the Design-stage architecture authority. When current work crosses
independently developed module, task, or team boundaries, one normative `Contract.md` is
required so those implementations use the same interface authority. Keep an interface owned
by one implementation unit in `Design.md`; never create an empty contract artifact. The
contract is mandatory at a cross-unit boundary; only the separate file is conditional on that
boundary existing.

When present, `Contract.md` and `Design.md` form one Design Bundle accepted at the same Git
commit. `Contract.md` owns stable Contract IDs, provider/consumer boundaries,
input/output semantics, invariants, observable failures, and only the compatibility or caller
obligations required by current R/ACs and the real call path. Link code-native interfaces,
OpenAPI, Protobuf, JSON Schema, event schemas, commands, or file formats instead of duplicating
them in Markdown. The contract does not imply HTTP or a network service.

Task division remains many-to-many with Contract IDs. Split tasks at independently provable
outcomes, not API count: one Contract ID may anchor provider, consumer, and integration tasks,
and one cohesive task may implement several Contract IDs. The `spec anchor` cell links the
applicable AC, Design decision/module, and Contract IDs or bundle anchor without copying their
meaning.

The accepted Design Bundle is identified by its Git commit. Add formal API versions only when
a current external or coexisting-version compatibility requirement needs them; do not create
a parallel `v1`/`v2` workflow. Design acceptance makes this an approved implementation
baseline. `close-milestone` alone marks the final implementation-matching Contract commit
`closed`.

## 6. Card and Log

After the owner confirms the execution set, `run-task` creates exactly two files per selected
task before Coder dispatch:

- `Card.md` is normative. Its frontmatter uses `type: task-card`, links upstream to the exact
  Task row and downstream to `Log.md`. Its minimum stable contract is outcome, Requirement and
  Design plus applicable interface-Contract anchors, completion criterion, TDD contract, and
  `execution_log: [Log.md](Log.md)`.
- `Log.md` is descriptive. Its frontmatter uses `type: execution-log` and links upstream to
  Card. It contains a replaceable current snapshot, material decisions, and one final evidence
  summary when closed. The snapshot contains status, current candidate when one exists, next
  action, and only an active blocker or material workspace fact. It also contains
  `latest_event: [Current](#current)` while active and points that field to
  `[Final Evidence](#final-evidence)` when closed, solely for DocStar compatibility. Append a
  decision only for a blocker or failed required check, accepted fallback, review finding and
  ruling, accepted fix, or another fact that changes acceptance or the next action. Routine
  dispatch, waiting, unchanged status, and successful intermediate checks are not Log entries.
  The compatibility pointer does not require generated event IDs; a decision needs a stable ID
  only when another artifact links to it.

Final evidence identifies the accepted candidate commit and integrated commit, records the
discriminating RED and final GREEN commands/results, gives the independent review result and
any accepted finding/fix, and records the verification classification plus required evidence
when applicable. Omit optional fields that do not exist instead of writing placeholder values.

Add scope exclusions or an allowed path/write set when they materially bound a delegated
writer. Add conflict domains or runtime locks only when a real shared-resource collision
exists. Task remains the dependency authority; Card links to the Task row instead of copying
its prerequisite DAG.

Create Card first, Log second, then publish the Task execution link in the same checked
candidate. Correct a material decision with a later decision rather than rewriting it. Do not
create a project-wide execution log or separate Verification, State, per-role brief, or Handoff
file without an independent need.

Card may refine implementation mechanics but cannot add scope, dependency, acceptance
meaning, design decisions, or cross-task interface semantics absent from approved authority.
Log never owns normative meaning. When coding evidence challenges an interface contract, Log
records only the evidence, smallest proposed delta, and affected tasks. The Coder does not edit
the shared Design Bundle or create a separate change-request document.

## 7. Content, not a template

GMGN does not prescribe section names, order, or prose shape beyond the parser-facing fields
above. The stage Skill defines what an artifact must answer and self-check. The primary
orchestrator writes specification documents directly when its context makes that clearest;
delegate a fresh Author only when bounded isolation, specialization, or parallelism has real
value. Keep the independent Critic separate from the writer.
