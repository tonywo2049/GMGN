---
name: roadmap
description: "Use after owner approval of the WhitePaper to create or maintain the project roadmap, milestones, explicit deliverables, priority, dependency order, concise acceptance summaries, optional core E2E paths, closure backfill, or Backlog allocation. 白皮书已批后规划里程碑、明确产出、依赖、简要验收摘要及按需核心 E2E。"
---

# ROADMAP: single sequencing authority

<HARD-GATE>An approved, commit-bound WhitePaper must exist; otherwise return to `brainstorm`. If ROADMAP work exposes a WhitePaper premise that must change, use `brainstorm` revision mode instead of redefining it here. ROADMAP stays at project-sequencing level and must not contain detailed Milestone closure conditions, R-AC IDs, quantitative requirement metrics, technical design, task breakdown, or executable test cases.</HARD-GATE>

## Language and contract

Before writing, load the registered `gmgn` Skill through normal discovery and follow its local
writing contract. Use the active locale for artifact prose. Use `ROADMAP.md`, `type: roadmap`,
`nature: normative`, and `status: draft` until approved.

## Create

- Restate only the WhitePaper boundary and invariants needed for sequencing.
- Define ordered Milestones with one qualitative objective, explicit **Milestone
  deliverables**, one concise qualitative acceptance summary, dependencies, and work state
  `not-started`.
- Derive each deliverable from the approved WhitePaper and that Milestone's expected outcome;
  later artifacts or evidence cannot silently redefine it.
- Name what will exist at the end, not how well it must perform. Choose only the concrete
  objects appropriate to the Milestone: a specification, repository state, release, running
  network or environment, tool, report, ledger, or a realized product/operational E2E when that
  path itself is the final result. The acceptance summary states what counts as the stage
  result without expanding every close condition. Keep evidence out of planning rows; closure
  backfill links the accepted result.
- Write a core E2E only when the realized product or operational path is itself a Milestone
  deliverable. Otherwise omit E2E content; never invent one for a specification, research,
  report, infrastructure component, or other artifact merely to satisfy the workflow.
- When applicable, write the core E2E under a stable Markdown anchor as the shortest complete
  path from its start through key actions to an observable result. The Milestone row links to
  that anchor. Do not expand permission branches, failure/recovery paths, exact parameters, or
  test details in ROADMAP.
- When a deliverable such as a complete
  specification already contains its functions, E2E, failure, and recovery definitions, list
  that artifact once instead of repeating its contained paths as deliverables.
- Use a candidate name during planning, and point an internal-code deliverable to its
  repository when known. Refine the name at Milestone start or closure when the owned outcome
  is unchanged; otherwise use controlled revision. In a shared table cell, number deliverables
  consecutively and put one item on each line.
- Do not prescribe a test framework, command, test file, fixture, selector, exact numeric
  threshold, technical solution, task, execution instruction, or evidence record in ROADMAP.
- Sequence strong dependencies from earlier Milestones to later consumers. A later
  implementation, confirmation, document, or evidence item must not be an earlier Milestone's
  acceptance condition.
- Maintain one Backlog for possible future work that is not yet allocated to a Milestone.

## Maintain

- Closure backfill updates the Milestone state and replaces candidate deliverable identities
  with canonical pointers:
  internal code uses `repository@<accepted-commit>`; an external distribution uses its release
  tag and release page; a network or environment uses its applicable stable identity and
  access pointers, such as an ID, identity or genesis hash, manifest, and endpoints; and a
  document, report, or tool links directly to the accepted artifact. Omit pointers that do not
  apply. When a core E2E anchor exists, link it to accepted evidence.
- New ideas remain in the Backlog until allocated to a Milestone.

## Writer and critic loop

1. Record the WhitePaper commit and mode. The primary session may write directly, or it may
   prepare a complete brief and create one fresh Author when the bounded handoff creates real
   value.
2. The writer self-checks before return. A delegated Author ends after that return; missing
   inputs or later revision use the primary session or a fresh Author with a new brief.
3. Commit the complete candidate locally and dispatch one fresh independent Critic from a
   prepared brief that names the shortest unambiguous commit reference. Collect all findings
   before editing, adjudicate once, and batch accepted blocker fixes.
   Check each resolution and run affected machine checks; do not dispatch a second Critic to
   recheck this round's fixes.
4. With no blocker, owner approval binds the candidate commit. The primary orchestrator applies
   accepted mechanical reciprocal links, state, and evidence pointers, then runs machine checks.

Closure backfill and other meaning-preserving maintenance skip semantic criticism. The primary
session applies the mechanical batch directly, including across an integration boundary. Run
machine checks and preserve the existing approval through an
equivalence record. Any semantic ambiguity returns to the full writer/Critic loop.

## Controlled revision

- Start from the approved old commit. Record the trigger, semantic delta, affected milestone
  rows and documents, required reviewer or approver, and proposed new commit.
- If the changed meaning belongs to the WhitePaper, initiate `brainstorm` revision mode and
  resume ROADMAP maintenance only after the required new upstream approval.
- Revise only ROADMAP-owned sequencing, Milestone allocation, deliverables, dependencies,
  concise qualitative acceptance summaries, optional core E2E paths, or Backlog placement.
  Do not reopen unaffected Milestones.
- A change that alters a decision or reasonable understanding receives independent criticism
  and owner approval at a new commit. Old approval remains attached to the old commit.
- Meaning-preserving mechanical changes use same-batch link and status refresh plus
  machine checks without reapproval.

## Exit

For creation or a semantic revision, run the fresh-agent writer/Critic loop using the
English-only dispatch contract, present remaining material risks or that none are known,
obtain owner approval bound to the candidate commit, and integrate only when required by workspace
topology. Before approval, confirm every Milestone has concrete deliverables and a concise
qualitative acceptance summary; a core E2E appears only
when that path is itself a deliverable, and no E2E is fabricated for other Milestones. A
mechanical maintenance batch needs machine checks but no new approval.

Before every substantive return, perform a task-specific self-check and correct defects. Do
not output a fixed `Reflection` section. Disclose only material unresolved risks that could
change the conclusion, decision, acceptance, or downstream work; otherwise omit the
disclosure. Approval, acceptance, and closure always state remaining material risks or that
none are known.
