---
locale: en
purpose: Define the machine fields, states, filenames, IDs, headers, and templates shared by English and Chinese GMGN documents.
upstream: [GMGN methodology](../../../../GMGN.md)
downstream: [GMGN router](../../SKILL.md)
status: approved
type: design
nature: normative
---

# GMGN writing contract

中文版本：[../zh-CN/writing-contract.md](../zh-CN/writing-contract.md)

## 1. One workflow, two human languages

Select `en` or `zh-CN` from the existing project and the user's request. Headings and
prose use that language. The machine fields, enums, filenames, IDs, commands, and task
headers below are never translated. Do not maintain separate skills.

One specification chain normally has one active locale. If translated mirrors are
required, place them in separate locale roots and validate each root separately. Scanning
two trees with the same IDs as one DocStar corpus creates duplicate definitions.

## 2. Frontmatter

Every normative document starts with:

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

Fixed keys: `locale | purpose | upstream | downstream | status | type | nature`.

- `locale`: `en | zh-CN`
- `status`: `draft | pending-approval | approved | closed`
- `type`: `whitepaper | roadmap | goal | requirement | design | task | research | decision | retrospective | handoff`
- `nature`: `normative | descriptive`

`normative` means downstream work depends on the document and changes must propagate.
`descriptive` records facts or process and does not establish a gate. Repository guides
and template sources may use an extension `type`; project specification chains may not.

Use `upstream: none` for a chain root and `downstream: none` until the downstream file
exists; replace it with a real link in the same batch that creates the file. Do not disguise
plain text as a link.

## 3. Do not mix the two state machines

Document approval state:

```text
draft → pending-approval → approved → closed
```

Milestone, slice, and task work state:

```text
not-started → initiated → in-progress → closed
```

The owner approves WhitePaper and ROADMAP. The primary orchestrator reviews Goal,
Requirement, Design, and Task after an independent critic. The owner accepts milestone
closure. Every approval binds a commit, content hash, or equivalent version anchor.

### 3.1 Controlled changes after approval

Workflow nodes are not one-way. If downstream work exposes an upstream defect or changed
premise, return to the document that is the single authority for that meaning:

| Meaning owned by | Revision route |
|---|---|
| WhitePaper | `brainstorm` revision mode |
| ROADMAP | `roadmap` maintenance mode |
| Goal | `write-goal` revision mode |
| Requirement or R-AC | `write-requirement` revision mode |
| Design | `write-design` revision mode |
| Task | `write-task` revision mode |

A **semantic change** can alter a decision or a reasonable reader's understanding of scope,
obligation, acceptance meaning, design intent, or execution authority. It receives the review
or approval appropriate to that authority at a new version anchor. The old approval remains
attached to the old anchor; it never moves implicitly to the edited file.

A **mechanical change** preserves meaning: for example, a rename, move, link, formatting,
hash, or mirrored status update. File-content change alone does not require reapproval.
Refresh every affected representation in the same batch and run machine checks. If the
checks pass and the change record explicitly establishes semantic equivalence, the new anchor
may retain the document's approval state by citing the old approved anchor; this is not a new
approval. If the classification is uncertain, treat the change as semantic.

After either kind, propagate only through the impact cone: affected upstream/downstream
links, IDs, mappings, documents, tasks, tests, evidence, and state. Review, approve, and
verify only affected content. Returning to an authority does not rerun unrelated stages.

For a semantic revision, add or update a change record in the authority or its linked decision
log. A mechanical batch may keep one batch-level equivalence record; do not edit every
affected document solely to add history. Do not add an empty record to a newly created
document:

| item | required content |
|---|---|
| trigger | why the approved baseline is insufficient |
| old anchor | the version to which existing approval still applies |
| classification | `semantic` or `mechanical`, with rationale |
| authority and delta | the single authority and exact meaning changed |
| impact cone | affected IDs, documents, work, tests, evidence, and state |
| review or approval | who must review or approve this version, or why none is needed |
| new anchor and checks | the resulting version plus propagation and verification evidence |

## 4. Stable names and identifiers

- Project level: `WhitePaper.md`, `ROADMAP.md`
- Milestone level: `Goal.md`, `Requirement.md`, `Design.md`, `Task.md`
- Milestones: `M1`, `M2`, ...
- Requirements: `R1`, `R2`, ...
- Acceptance criteria: `R1-AC1`, `R1-AC2`, ...
- Tasks: `M1-T1`, `M1-T2`, ...; a single-milestone local corpus may use `T1`

Never renumber an ID after downstream references exist. Keep a tombstone or decision
pointer when removing one.

Task-table headers are fixed English tokens:

```markdown
| # | task | spec anchor | prerequisite | failing test | status |
|---|---|---|---|---|---|
| **M1-T1** | <task> | R1-AC1 | none | `test_name` | not-started |
```

This is the shared GMGN/DocStar parsing surface. Chinese documents use the same headers.

## 5. G-R-D-T templates

### Goal.md

```markdown
---
locale: en
purpose: Define M1 objectives, boundaries, slices, and completion picture.
upstream: [ROADMAP](../../ROADMAP.md)
downstream: [Requirement](Requirement.md)
status: draft
type: goal
nature: normative
---

# M1 Goal

## Objective
## Boundary
## Work slices
## Non-goals
## Qualitative completion picture
## Known gaps
```

### Requirement.md

```markdown
---
locale: en
purpose: Define the single M1 requirement authority and decidable acceptance criteria.
upstream: [Goal](Goal.md)
downstream: [Design](Design.md)
status: draft
type: requirement
nature: normative
---

# M1 Requirement

## Functional requirements
- **R1** — <what must hold, without prescribing implementation>
  - **R1-AC1** — GIVEN <precondition> WHEN <action> THEN <observable result>

## Non-functional requirements
## Parameters and constraints
## Non-goals
## Traceability
```

### Design.md

```markdown
---
locale: en
purpose: Map M1 requirements to implementation structures, interfaces, data, and verification paths.
upstream: [Requirement](Requirement.md)
downstream: [Task](Task.md)
status: draft
type: design
nature: normative
---

# M1 Design

## Constraints and current state
## System structure
## Interfaces and data
## Failure paths and rollback
## Requirement mapping
| requirement | design location | verification |
|---|---|---|
| R1-AC1 | §2.1 | <test or E2E path> |
## Rejected alternatives
```

### Task.md

```markdown
---
locale: en
purpose: Define M1 task cards, dependencies, tests, and rolling status.
upstream: [Design](Design.md)
downstream: none
status: draft
type: task
nature: normative
---

# M1 Task

## Tasks
| # | task | spec anchor | prerequisite | failing test | status |
|---|---|---|---|---|---|
| **M1-T1** | <smallest verifiable work unit> | R1-AC1 | none | `test_r1_ac1` | not-started |

## Traceability matrix
| acceptance criterion | task | test | evidence |
|---|---|---|---|
| R1-AC1 | M1-T1 | `test_r1_ac1` | <command and result pointer> |

## Rolling record
```

## 6. Minimum content for other types

| type | Must answer |
|---|---|
| `whitepaper` | problem, goals, non-goals, users/scenarios, harm ordering, invariants, validation direction |
| `roadmap` | qualitative milestone goals and completion pictures, dependencies, state, unallocated TODOs |
| `research` | question, evidence, options, counterexamples, inference boundary, recommendation; normally `descriptive` |
| `decision` | ID, trigger, ruling, rationale, conditions, propagation list, version anchor |
| `retrospective` | event, root cause, missed signals, generalized test/rule/checklist question |
| `handoff` | one-line state, baseline, completed, remaining, risks, next command, authority pointers; `descriptive` |

## 7. Writing discipline

1. Read upstream, downstream, and definition locations before writing prose.
2. Give each fact one authority; every other location uses real relative links and IDs.
3. Store exploratory drafts separately from approved conclusions.
4. List affected downstream files and refresh status in the same change batch.
5. Human language never changes the semantics of ACs, tasks, links, or state.

## 8. DocStar verification

```bash
python3 docstar.py check --preset gmgn-v1 --corpus <locale-root>
python3 docstar.py dump --preset gmgn-v1 --json --corpus <locale-root>
python3 docstar.py brief M1-T1 --preset gmgn-v1 --json --corpus <locale-root>
```

When the project contains `.docstar/conventions/conventions.json`, omit
`--preset gmgn-v1`. English and Chinese mirrors should produce equivalent entities, edges,
states, and diagnostics after natural-language prose is excluded from comparison.
