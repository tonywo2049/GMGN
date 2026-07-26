---
locale: en
purpose: Define the stable machine fields, states, paths, IDs, links, and parser surfaces shared by English and Chinese GMGN artifacts.
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

For `design/Contract.md`, `approved` means the current shared working baseline that all
affected Coder lanes must follow. `closed` means Milestone closure has reconciled the contract
with provider and consumer implementations plus evidence and the owner has accepted that
final frozen commit.

<HARD-GATE>In a Git-backed GMGN project, every review, approval, acceptance, Milestone
closure, and release anchor is a Git commit or release tag. Commit the candidate locally
before independent review. In human-facing documents, briefs, logs, and returns, use the
shortest unambiguous commit reference or the tag; never use a full-length commit object ID,
diff hash, content hash, archive checksum, or artifact checksum as a workflow anchor. If the
current workspace cannot safely create the candidate commit, use an isolated worktree.
Checksums are evidence only.</HARD-GATE>

Editing a file does not move its state; the owning stage Skill defines approval and closure.

## 3. Authority links

Each meaning has one normative owner. Other artifacts link that owner instead of copying its
fields, schema, mapping, decision, or status history. Use real relative links for `upstream`,
`downstream`, Bundle indexes, R/AC anchors, Contract IDs, execution pointers, and evidence
pointers. A root owns the complete mapping; a child links only its applicable entries.

When meaning changes, use the owning stage Skill and update only the affected link graph at one
new commit. Formatting, equivalent links, mirrored status, and generated metadata are
mechanical only while they preserve the owner's meaning.

## 4. Stable names and Task surface

- Project: `WhitePaper.md`, `ROADMAP.md`
- Milestone: `Goal.md`, `Requirement.md`, `Design.md`, optional `design/`, `Task.md`
- Design module: `design/<module-id>.md`
- Cross-unit catalog: `design/Contract.md`
- Split interface: `design/contracts/<contract-id>.md`
- Structural authority: `design/schemas/<schema-or-compilable-interface>`
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

## 5. Design Bundle links

`Design.md` always owns the global architecture, Bundle index, and complete R/AC mapping.
Every child under `design/` links back to it. When current work crosses an independently
developed boundary, `design/Contract.md` is required and links each stable Contract ID to its
provider, consumers, applicable module documents, and single structural authority. A small
contract may live in the catalog; larger contracts may be split under `design/contracts/`.
Exact schemas and compilable interfaces live under `design/schemas/` or an explicitly linked
code location and are not copied into Markdown.

The linked files form one Design Bundle accepted at the same Git commit. The `spec anchor`
cell may link applicable AC, module, Contract ID, and schema without copying their meaning.
The stage Skills own Design completeness, interface semantics, task division, controlled
revision, and final Contract closure.

## 6. Execution pointers

`Card.md` uses `type: task-card`, links its exact Task row and `Log.md`, and exposes
`execution_log: [Log.md](Log.md)`. `Log.md` uses `type: execution-log`, links its Card, and
exposes `latest_event: [Current](#current)` while active and
`latest_event: [Final Evidence](#final-evidence)` when closed. Task owns dependencies and
macro status; Card owns the stable execution contract; Log is descriptive evidence. The
stage Skills own their content and lifecycle.

## 7. Content, not a template

GMGN does not prescribe section names, order, or prose shape beyond the parser-facing fields
above. The stage Skill defines what an artifact must answer and self-check. The primary
orchestrator writes specification documents directly when its context makes that clearest;
delegate a fresh Author only when bounded isolation, specialization, or parallelism has real
value. Keep the independent Critic separate from the writer.
