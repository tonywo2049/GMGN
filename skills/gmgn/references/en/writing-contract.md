---
locale: en
purpose: Define the machine fields, states, filenames, IDs, and parser surfaces shared by English and Chinese GMGN documents without prescribing document layout.
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
may use an extension `type`; project specification chains may not.

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

For a task card, `initiated` means its execution lane has been claimed, and `in-progress`
covers coding through integration. Review or verification of an isolated branch may make the
runtime candidate `accepted`, but never makes the task `closed`. `closed` requires integration
into the recorded `shared_baseline_anchor`, successful post-integration verification, and
same-batch refresh of `Task.md`, traceability, and evidence by the shared-baseline Integrator.
The card Coder stages and commits only its `write_set` in the assigned detached-HEAD or
unique-branch worktree and returns a resolvable local commit SHA as immutable
`candidate_anchor`; local commits are allowed and remote writes are not.

Integration first creates a temporary combined `candidate_anchor` from the clean current
shared baseline. Verification failure or merge/cherry-pick conflict discards or aborts that
candidate and leaves the preceding `shared_baseline_anchor` clean and unchanged. Only a
verified combined candidate plus mechanical ledger refresh may atomically advance the shared
anchor; an unverified combination is not a baseline.

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

The fixed six columns do not carry the complete execution contract. Card content keyed by the
same stable task ID also records `depends_on`, `write_set`, `conflict_domains`,
`runtime_locks`, and the semantic owner. These facts do not change the DocStar table schema.
If `workspace_mode: shared` cannot independently anchor each writer, parallel workers return
proposals/patches and one recorded writer serially applies and anchors them.

## 5. Content contract, not layout template

GMGN does not prescribe section names, order, or prose shape. The active stage skill is the
authority for what an artifact must answer and what its writer must self-check. For
WhitePaper, ROADMAP, Goal, Requirement, Design, and Task, the primary orchestrator selects the
actual writer: itself when its context makes direct authorship the clearest and least wasteful
path, or a delegated Author when bounded isolation, specialization, or parallelism creates
real value. Bind `author_ref` to that writer and keep the independent Critic separate from it.
Do not recreate a copy-ready skeleton in project or plugin references.

The only fixed body surfaces are identifiers and parser-facing tables. For `Task.md`, keep
the canonical task header from §4; surrounding headings and explanatory prose remain free.

## 6. Writing discipline

1. Read upstream, downstream, and definition locations before writing prose.
2. Give each fact one authority; every other location uses real relative links and IDs.
3. Store exploratory drafts separately from approved conclusions.
4. List affected downstream files and refresh status in the same change batch.
5. Human language never changes the semantics of ACs, tasks, links, or state.

## 7. DocStar verification

```bash
python3 docstar.py check --preset gmgn-v1 --corpus <locale-root>
python3 docstar.py dump --preset gmgn-v1 --json --corpus <locale-root>
python3 docstar.py brief M1-T1 --preset gmgn-v1 --json --corpus <locale-root>
```

When the project contains `.docstar/conventions/conventions.json`, omit
`--preset gmgn-v1`. English and Chinese mirrors should produce equivalent entities, edges,
states, and diagnostics after natural-language prose is excluded from comparison.
