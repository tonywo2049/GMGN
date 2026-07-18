---
locale: en
purpose: Define GMGN roles, document chains, hard gates, independent review, and closure discipline.
upstream: none
downstream: [writing contract](skills/gmgn/references/en/writing-contract.md), [dispatch and handoff](skills/gmgn/references/en/dispatch-and-handoff.md), [decision log](skills/gmgn/references/en/decision-log.md), [preflight checklist](skills/gmgn/references/en/preflight-checklist.md), [trust-surface register](skills/gmgn/references/en/trust-surface-register.md), [pre-close checklist](skills/gmgn/references/en/pre-close-checklist.md)
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
[README.md](README.md); copy-ready operating contracts belong in
[`skills/gmgn/references/en/`](skills/gmgn/references/en/).

## 0. Scope and roles

GMGN defines four required roles and one optional role.

- **Owner** decides scope, approves project-level commitments, accepts closure, and is
  the only role that may waive completion criteria. Agent-to-agent instructions do not
  constitute owner authorization.
- **Primary orchestrator** understands, decomposes, delegates, verifies, and integrates.
  It retains decisions, interface freezes, merge control, and stage gates.
- **Execution agent** receives one independently verifiable task and returns artifacts
  plus replayable evidence.
- **Critic/reviewer** tries to falsify the artifact and must be independent of its author.
- **External audit** is optional and introduces a frame from outside the working group.

Stages close against explicit criteria, not dates. Dates may be planning constraints, but
they never turn an unmet criterion into a completed one.

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
- **Task** — execution authority: cards, dependencies, status, tests, and completion proof.
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

The **process chain** is research → decision → normative document → archived exploration.
Keep revisable exploration separate from approved conclusions.

The **state chain** is task ledger → handoff → cross-track register → ROADMAP pointer.
Higher layers summarize less and point downward more.

### 2.3 Stable machine contract

Human prose may be English or Chinese. Machine-facing fields remain fixed:

```yaml
locale: en | zh-CN
purpose: <natural-language sentence>
upstream: <real Markdown links or declared none>
downstream: <real Markdown links or declared none>
status: draft | pending-approval | approved | closed
type: whitepaper | roadmap | goal | requirement | design | task | research | decision | retrospective | handoff
nature: normative | descriptive
```

Work rows use `not-started | initiated | in-progress | closed`. IDs, filenames, commands,
and task-table headers are language-independent. The full contract is in
[`writing-contract.md`](skills/gmgn/references/en/writing-contract.md).

## 3. Approval and change semantics

Approval attaches to a version anchor: commit, content hash, or equally immutable
identifier. “Approved” without the reviewed version is ambiguous.

Freezing establishes a controlled-change baseline; it does not mean immutable forever.
After approval, a change must state trigger, impact, affected downstream documents,
required signers, and the new anchor.

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

1. **scope closure** — every in-scope requirement is implemented, deferred explicitly, or
   removed by an authorized decision;
2. **evidence closure** — each criterion has a replayable test or real execution path;
3. **state closure** — task ledger, matrix, ROADMAP, decisions, and handoff are refreshed in
   the same batch.

Immediately after closure, write receiving state for the next operator. A closed milestone
without a current handoff is not operationally closed.

## 4. Six workflow laws

1. **Classify before locating.** Decide whether a new file is requirement/design/execution/
   verification and exploratory/normative before choosing its directory.
2. **Graph before prose.** Read the upstream/downstream graph and relevant definitions
   before drafting or editing.
3. **One authority per fact.** Other documents point to the authority instead of copying it.
4. **Hard gates are procedures.** Missing prerequisites route backward; apparent simplicity
   is not a bypass.
5. **Delegate independent units.** Each brief states scope, boundaries, inputs, outputs,
   verification, and required return format.
6. **Evidence before status.** A claim becomes complete only after the artifact, replayable
   evidence, and all representations agree.

Every substantial response ends with **Reflection**: weakest assumption, neglected
counterexample, and which claims were measured versus inferred.

## 5. Adversarial quality

### 5.1 Independent document critic

Use one focused falsification round after the author self-check. Findings must identify
location, evidence, impact, a normative correction, and blocking level. Scope the review
to the changed artifact plus the minimum upstream/downstream context.

Two guards prevent review from becoming another authority:

- a critic may identify a problem but may not silently expand product scope;
- conflicting findings go to the orchestrator or owner, not into an endless review loop.

### 5.2 Code review is separate

Code review examines the incremental diff, untested branches, test discrimination,
spec-anchor alignment, and unnecessary complexity. It does not replace document criticism
or runtime execution. The reviewer reports findings and does not modify the reviewed work.

Use the current platform's native read-only review surface where available. Otherwise use
an independent read-only reviewer with
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

### 5.5 Report the weakest assumption

Every approval or closure presentation explicitly names the assumption most likely to
invalidate the conclusion. This is more useful than a generic confidence statement.

## 6. Tool and automation boundaries

Automation may parse, link, count, compare, execute, and report. It must not invent product
meaning, approve scope, or infer that silence means success.

DocStar is optional and deterministic. With the GMGN convention set it can check links,
extract the G-R-D-T graph, compile a task brief, and compare English/Chinese locale trees.
Its JSON uses the stable English `eg-3` contract regardless of display language.

```bash
python3 docstar.py check --preset gmgn-v1 --corpus <corpus>
python3 docstar.py brief <task-id> --preset gmgn-v1 --json --corpus <corpus>
```

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
6. Execute one task card at a time; parallelize only dependency-free cards.
7. Review each code increment independently and replay task-level evidence.
8. Run full regression and milestone E2E.
9. Use the pre-close checklist, obtain owner acceptance, refresh every state representation,
   write Handoff, and return to `roadmap`.

Operational templates:

- [dispatch and handoff](skills/gmgn/references/en/dispatch-and-handoff.md)
- [critic brief](skills/gmgn/references/en/critic-brief.md)
- [coder brief](skills/gmgn/references/en/coder-brief.md)
- [trust-surface register](skills/gmgn/references/en/trust-surface-register.md)
- [decision log](skills/gmgn/references/en/decision-log.md)
- [preflight](skills/gmgn/references/en/preflight-checklist.md),
  [pre-merge](skills/gmgn/references/en/pre-merge-checklist.md), and
  [pre-close](skills/gmgn/references/en/pre-close-checklist.md) checklists
