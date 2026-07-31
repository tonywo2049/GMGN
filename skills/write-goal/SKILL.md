---
name: write-goal
description: "Use when an approved ROADMAP has an eligible `now`, `not-started` Milestone that needs one combined initiation and Goal approval, or for a controlled revision of an approved Goal. Define only the active boundary and qualitative Close outcomes in Goal.md as Requirement input. ROADMAP 已批且存在可启动的 `now` Milestone 时，形成 Goal 候选并用一次批准同时完成启动与 Goal 批准；也用于受控修订已批准 Goal。"
---

# Initiate a milestone and write Goal.md

<HARD-GATE>Creation mode requires the current approved Decision and ROADMAP commits, a Milestone with `horizon: now` and `state: not-started`, and every declared prerequisite Milestone at `state: closed` with an `accepted_result`. Prepare the Goal and proposed initiation as one candidate; do not require a separate initiation authorization. Revision mode requires the current approved Goal plus its approved Decision and ROADMAP commits. If a prerequisite is missing or the changed meaning belongs to WhitePaper, Decision, or ROADMAP, stop and return the issue to `gmgn` for routing.</HARD-GATE>

## Language and writing rules

Before writing, load the registered `gmgn` Skill through normal discovery and follow its local
writing rules. Use the ROADMAP locale unless the owner changes it explicitly. Keep filename
`Goal.md`, `type: goal`, and `nature: normative`.

## Working rhythm

Read the approved WhitePaper, current Decision, and target ROADMAP Milestone, then form the
complete Goal candidate directly. Do not run a routine discovery or question checklist. Ask
the owner only when two or more interpretations remain consistent with upstream authority and
the answer would change the active Milestone boundary or whether it can Close. Combine related
blocking ambiguity into the smallest useful question, recommend one option, and state the real
alternative and its effect on Requirement scope or Close.

Do not ask about facts already decided upstream, document shape, mechanical mapping, product
behavior, parameters, architecture, tests, or tasks. Leave Requirement-owned detail for
Requirement. If an unresolved ruling needed by the current Goal crosses Milestones or
constrains a shared project object, return it to `gmgn` for Decision routing instead of
writing or deciding it in Goal. If no blocking Goal-owned ambiguity remains, write the
candidate without intermediate questions.

## Goal content

- Derive Goal only from the approved ROADMAP Milestone and its WhitePaper and applicable
  Decision authority.
  Later documents, implementation, or evidence may expose a needed revision but cannot
  silently redefine Goal.
- Include only content that either gives Requirement a necessary basis or decides whether the
  Milestone can Close. Delete anything that serves neither purpose.
- Link the ROADMAP outcome, deliverables, success signal, and applicable D-IDs instead of
  copying or redefining them. State the active boundary only when it prevents a plausible
  scope misunderstanding. Add a Milestone-local exclusion only when necessary; it cannot
  remove a ROADMAP obligation or contradict upstream authority.
- Define the smallest set of qualitative Close outcomes whose combined truth is sufficient to
  Close the Milestone. They must cover every ROADMAP deliverable and success signal, and each
  Close outcome must name its upstream source. Do not require result slices. A complex Goal
  may group related Close outcomes for readability, but the grouping creates no separate
  authority or R/AC mapping.
- A Close outcome states what result must exist at Milestone Close. Requirement owns actors,
  scenarios, observable behavior, constraints, parameters, and decidable ACs. Missing
  Requirement-owned detail does not make Goal incomplete.
- Link any ROADMAP-owned numeric target without copying, refining, or supplying its measurement
  rule. Keep behavioral thresholds, technical design, task division, execution, and evidence
  out of Goal.
- Do not include a document map, known gaps, downstream propagation or gates, next-stage
  instructions, component or interface design, code structure, test cases, commands, results,
  task status, research history, candidate comparisons, or closure history.

## One change batch

The recorded writer performs one semantic batch:

1. On first creation, propose the ROADMAP row change from `not-started` to `initiated`.
2. Create or revise the milestone directory's single entry document, `Goal.md`, with
   `status: pending-approval`, following `Goal content`. The writer chooses the section
   structure.
3. Ensure reciprocal ROADMAP ↔ Goal links and return one committed candidate.

This candidate changes only the ROADMAP initiation state/link and Goal and has no shared-
baseline effect before approval.

## Writer and review-selection loop

Record the Decision and ROADMAP commits, then process one complete Goal candidate through the
registered `gmgn` Skill's shared document-candidate and dispatch rules. The primary
orchestrator also checks the proposed ROADMAP state and reciprocal links.

With no unresolved blocker, present the exact committed Goal candidate and remaining material
risks—or that none are known—for one owner approval. That approval both authorizes the
Milestone state change and approves Goal meaning. Then move Goal to `status: approved`, apply
the mechanical reciprocal-link record, and integrate the candidate without another semantic
review.

## Controlled revision

1. Start from the old approved Goal commit and record the trigger, semantic delta, affected
   boundary or Close outcomes, plus the proposed new commit.
2. Return WhitePaper-, Decision-, or ROADMAP-owned changes to `gmgn` for routing; do not patch
   that meaning into Goal.
3. Revise only the active boundary, necessary Milestone-local exclusions, ROADMAP
   deliverable/success-signal coverage, or qualitative Close outcomes. Preserve unaffected
   content. Leave behavior, constraints, parameters, and AC choices to Requirement.
4. If the delta changes a decision or reasonable understanding, apply the Critic necessity
   gate, run any required independent criticism and primary-orchestrator review against the
   affected content, and bind it to a new commit. Old review remains attached to the old
   commit.
Meaning-preserving mechanical changes use same-batch link and status refresh plus
machine checks without reapproval.

## Exit

Require the recorded writer to confirm:

- every applicable D-ID remains linked and unmodified;
- every ROADMAP deliverable and success signal is covered by qualitative Close outcomes, and
  every Close outcome has an upstream source;
- any retained boundary or Milestone-local exclusion prevents a real scope ambiguity without
  removing an upstream obligation;
- no grouping is treated as separate authority or translated independently into R/AC;
- every blocking Goal-owned ambiguity is resolved, while Requirement-owned detail remains for
  Requirement;
- deleting any retained item would remove necessary Requirement input or change the Close
  decision;
- no document map, downstream rule, component, interface, newly invented target, behavioral
  criterion, test, task, execution, evidence, or history leaks into Goal; and
- an invalid mapping returns to `gmgn` for routing instead of changing upstream meaning in
  Goal.

For creation or a semantic revision, run the writer/review-selection loop using the
English-only dispatch contract, obtain primary-orchestrator review, and integrate only when
required by workspace topology.
