---
name: write-goal
description: "Use when an approved ROADMAP exists and the owner explicitly starts or initiates a not-started milestone, phase, or version; refine that Milestone into Requirement input and qualitative Close criteria in Goal.md. Also use for a controlled semantic revision of an existing Goal authority. ROADMAP 已批且负责人点名启动 Milestone 时，用 Goal.md 细化目标，作为 Requirement 依据和 Milestone Close 标准；也用于既有 Goal 的受控语义修订。"
---

# Initiate a milestone and write Goal.md

<HARD-GATE>Creation mode requires an approved ROADMAP commit, a `not-started` milestone row, and explicit owner initiation. Revision mode requires an existing initiated Goal and its approved ROADMAP commit, but does not require re-initiation. If a prerequisite is missing or the changed meaning belongs to WhitePaper or ROADMAP, stop and return the issue to `gmgn` for routing. Work on an uninitiated milestone is out of scope.</HARD-GATE>

## Language and contract

Before writing, load the registered `gmgn` Skill through normal discovery and follow its local
writing contract. Use the ROADMAP locale unless the owner changes it explicitly. Keep filename
`Goal.md`, `type: goal`, and `nature: normative`.

## Goal content

- Derive Goal only from the approved ROADMAP Milestone and its WhitePaper authority.
  Later documents, implementation, or evidence may expose a needed revision but cannot
  silently redefine Goal.
- Include only content that either gives Requirement a necessary basis or decides whether the
  Milestone can Close. Delete anything that serves neither purpose.
- State the refined Milestone result, active boundary, and non-goals. Split it into
  independently meaningful result slices, not teams, components, files, or work steps.
- Cover every ROADMAP deliverable with one or more result slices and a qualitative observable
  Close outcome. Every slice must contribute to a deliverable or Close outcome.
- When ROADMAP has a core E2E anchor, carry it into the applicable slices and add only the
  qualitative main, permission, failure, or recovery outcomes needed to judge Close. A
  Milestone without a ROADMAP core E2E has no E2E content.
- Resolve every Goal-owned ambiguity into the result, boundary, slices, or Close outcomes
  before accepting Goal. Keep exact numeric criteria, technical design, task division,
  execution, and evidence out of Goal.
- Do not include a document map, known gaps, downstream propagation or gates, next-stage
  instructions, component or interface design, code structure, test cases, commands, results,
  task status, research history, candidate comparisons, or closure history.

## One change batch

The recorded writer performs one semantic batch:

1. Change the ROADMAP row from `not-started` to `initiated` and record the owner authorization.
2. Create the milestone directory and `Goal.md` as its single entry document, following
   `Goal content`. The writer chooses the section structure.
3. Add reciprocal ROADMAP ↔ Goal links and return one committed candidate.

This batch changes only the ROADMAP initiation state/link and Goal.

## Writer and critic loop

Record the ROADMAP commit and owner initiation. The primary session may write directly, or it
prepares a complete brief and creates one fresh Author when the bounded
handoff creates real value. The writer self-checks before return; a delegated Author ends on
return, so later correction uses the primary session or a fresh Author with a new brief.
Commit the complete candidate locally and dispatch one fresh independent Critic from a
prepared brief that names the shortest unambiguous commit reference. Collect all
findings before editing, adjudicate once, and batch accepted blocker fixes. The primary
orchestrator checks each resolution without dispatching a second Critic, then reviews the
committed candidate, applies accepted mechanical links and state, and runs machine checks.

## Controlled revision

1. Start from the old Goal commit and record the trigger, semantic delta, affected slices and
   Close outcomes, plus the proposed new commit.
2. Return WhitePaper- or ROADMAP-owned changes to `gmgn` for routing; do not patch that
   meaning into Goal.
3. Revise only Goal-owned results, boundaries, non-goals, result slices, ROADMAP
   deliverable/core-E2E mappings, or qualitative Close outcomes. Preserve unaffected content.
4. If the delta changes a decision or reasonable understanding, run the independent critic
   and primary-orchestrator review against the affected content and bind it to a new commit.
   Old review remains attached to the old commit.
Meaning-preserving mechanical changes use same-batch link and status refresh plus
machine checks without reapproval.

## Exit

Require the recorded writer to confirm:

- the refined result, boundary, and non-goals are complete;
- every ROADMAP deliverable maps to slices and qualitative Close outcomes, every optional core
  E2E maps when present, and every slice contributes to a deliverable or Goal Close outcome;
- every Goal-owned ambiguity is resolved into accepted Goal content;
- deleting any retained item would remove necessary Requirement input or change the Close
  decision;
- no document map, downstream rule, component, interface, exact criterion, test, task,
  execution, evidence, or history leaks into Goal; and
- an invalid mapping returns to `gmgn` for routing instead of changing upstream meaning in
  Goal.

For creation or a semantic revision, run the fresh-agent writer/Critic loop using the
English-only dispatch contract, obtain primary-orchestrator review, and integrate only when
required by workspace topology.

Before every substantive return, perform a task-specific self-check and correct defects. Do
not output a fixed `Reflection` section. Disclose only material unresolved risks that could
change the conclusion, decision, acceptance, or downstream work; otherwise omit the
disclosure. Approval, acceptance, and closure always state remaining material risks or that
none are known.
