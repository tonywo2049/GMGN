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
- `type`: `whitepaper | roadmap | goal | requirement | design | task | task-card |
  execution-log | research | decision | retrospective | handoff`
- `nature`: `normative | descriptive`

Use `upstream: none` for a root and `downstream: none` until the downstream file exists.
Replace `none` with a real relative link in the same checked batch that creates the file.
Normative content owns meaning; descriptive content records observations and never creates
scope or approval.

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
on the shared baseline. Independent verification is required only when executable behavior,
environment, or package input needs it.

Approval and acceptance bind an immutable commit, content hash, or equivalent version anchor.
Editing a file does not move that decision. WhitePaper and ROADMAP need owner approval;
Goal, Requirement, Design, and Task need independent Critic review plus primary-orchestrator
acceptance; Milestone closure needs owner acceptance.

Each semantic change batch receives at most one Critic round. When accepted findings are fixed
after that review, the final accepted anchor records the reviewed anchor, complete findings and
rulings, exact fix delta, and post-fix machine checks. The fixes are not sent to a second
Critic.

## 3. Controlled changes

Change only the authority that owns the meaning:

| authority | route |
|---|---|
| WhitePaper | `brainstorm` revision |
| ROADMAP | `roadmap` maintenance |
| Goal | `write-goal` revision |
| Requirement or AC | `write-requirement` revision |
| Design | `write-design` revision |
| Task | `write-task` revision |

A semantic change can alter scope, obligation, acceptance meaning, design intent, or execution
authority. It gets the review or approval appropriate to that authority at a new anchor. A
mechanical change preserves meaning, such as formatting, links, mirrored status, or generated
metadata; it needs affected machine checks, not automatic semantic reapproval.

Propagate only the impact cone. Record the trigger, old anchor, classification, exact delta,
affected IDs/files/tests/evidence, required review, and new anchor in the owning authority or
an existing linked decision record. Do not add an empty change-log section or copy the record
into every affected document.

## 4. Stable names and Task surface

- Project: `WhitePaper.md`, `ROADMAP.md`
- Milestone: `Goal.md`, `Requirement.md`, `Design.md`, `Task.md`
- Card: `execution/<card_id>/Card.md`
- Runtime record: `execution/<card_id>/Log.md`
- Milestones: `M1`, `M2`, ...
- Requirements: `R1`, `R2`, ...
- ACs: `R1-AC1`, `R1-AC2`, ...
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
commands, write sets, locks, blockers, candidate anchors, evidence, or progress history.
Replace current values; do not append execution narrative.

## 5. Card and Log

After the owner confirms the execution set, `run-task` creates exactly two files per selected
task before Coder dispatch:

- `Card.md` is normative. Its frontmatter uses `type: task-card`, links upstream to the exact
  Task row and downstream to `Log.md`. Its minimum stable contract is outcome, Requirement and
  Design anchors, completion criterion, TDD contract, and
  `execution_log: [Log.md](Log.md)`.
- `Log.md` is descriptive. Its frontmatter uses `type: execution-log` and links upstream to
  Card. It contains a replaceable current snapshot and append-only events. The snapshot has
  `latest_event: [<event_id>](#<event_id>)`; each event has a stable ID, result, and evidence
  needed to replay or understand the decision.

Add scope exclusions or an allowed path/write set when they materially bound a delegated
writer. Add conflict domains or runtime locks only when a real shared-resource collision
exists. Task remains the dependency authority; Card links to the Task row instead of copying
its prerequisite DAG.

Create Card first, Log second, then publish the Task execution link in the same checked
candidate. Correct history with a later event rather than rewriting an old one. Do not create
a project-wide execution log or separate Verification, State, per-role brief, or Handoff file
without an independent need.

Card may refine implementation mechanics but cannot add scope, dependency, acceptance
meaning, or design decisions absent from approved authority. Log never owns normative meaning.

## 6. Content, not a template

GMGN does not prescribe section names, order, or prose shape beyond the parser-facing fields
above. The stage Skill defines what an artifact must answer and self-check. The primary
orchestrator writes specification documents directly when its context makes that clearest;
delegate a fresh Author only when bounded isolation, specialization, or parallelism has real
value. Keep the independent Critic separate from the writer.
