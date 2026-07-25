---
name: roadmap
description: "Use after owner approval of the WhitePaper to create or maintain the project roadmap, milestones, explicit deliverables, priority, dependency order, at least one end-to-end acceptance scenario per Milestone, closure backfill, or Backlog allocation. 白皮书已批后规划里程碑、明确产出、依赖及每个 Milestone 至少一个端到端验收场景。"
---

# ROADMAP: single sequencing authority

<HARD-GATE>An approved, commit-bound WhitePaper must exist; otherwise return to `brainstorm`. If ROADMAP work exposes a WhitePaper premise that must change, use `brainstorm` revision mode instead of redefining it here. ROADMAP must not contain R-AC IDs, quantitative requirement metrics, or executable test cases. It precedes Milestone requirements, so acceptance pictures stay qualitative.</HARD-GATE>

## Language and contract

Before writing, load the registered `gmgn` Skill through normal discovery and follow its local
writing contract. Use the active locale for artifact prose. Use `ROADMAP.md`, `type: roadmap`,
`nature: normative`, and `status: draft` until approved.

## Create

- Restate only the WhitePaper boundary and invariants needed for sequencing.
- Define ordered Milestones with one qualitative objective, explicit **Milestone
  deliverables**, one **Milestone acceptance picture**, dependencies, and work state
  `not-started`.
- Every Milestone names its concrete deliverables. A deliverable may be a named artifact such
  as a document or report, or one or more named qualitative end-to-end scenarios for product,
  infrastructure, or operational work. Include only deliverables owned by that Milestone. The
  acceptance picture must cover every deliverable.
- Every Milestone acceptance picture names at least one high-level end-to-end scenario that
  traverses the full outcome owned by that Milestone. Add more only for independently
  decidable main paths, permission boundaries, or failure/recovery outcomes.
  Each scenario has a stable Markdown anchor and states the starting situation, actor or
  system action, observable outcome, and any decision-relevant failure or recovery outcome.
- Every acceptance scenario must be independently decidable from work owned by that Milestone.
  An infrastructure Milestone may use a real input → processing → persistence/recovery →
  observable output path; a research-only Milestone may use question → method → result →
  decision evidence. Do not fabricate a user-interface E2E.
- If no full owned path can be stated, the Milestone is not independently acceptable: merge it
  with the consumer that makes its outcome observable or revise its boundary.
- Do not prescribe a test framework, command, test file, fixture, selector, or exact numeric
  threshold in ROADMAP. Requirement refines scenarios into ACs; Design and Card own executable
  verification details.
- Sequence strong dependencies from earlier Milestones to later consumers. A downstream
  implementation, confirmation, document, or evidence item must not be an earlier Milestone's
  acceptance condition.
- Maintain one Backlog for possible future work that is not yet allocated to a Milestone.
- Do not pre-create empty G-R-D-T files for unstarted milestones.

## Maintain

- Closure backfill updates the Milestone state and links each acceptance-scenario anchor to its
  closing evidence, plus any Handoff that exists.
- New ideas enter the Backlog, then are assigned to a Milestone before becoming requirements.
- Record a downstream-only confirmation as a non-blocking Handoff when a receiving
  Milestone/owner exists. Otherwise keep it in the Backlog. Record the question, trigger,
  possible impact, and any safe default assumption. Closure of the producing Milestone does
  not wait for the consumer to resolve it.
- For existing pre-GMGN inventory, have the recorded writer capture each legacy ID, source,
  summary, target milestone/requirement or pending decision, rationale, and allocation state.
  Reconcile source total = allocated + explicitly rejected + pending, then archive the
  migration record. Do not create this layer for new work.

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
  qualitative acceptance pictures, or Backlog placement. Do not reopen unaffected Milestones.
- A later Milestone may supersede a technical selection originating in a closed foundation or
  M0 Milestone. The M0-originated Design, Decision, or index remains semantic authority. Keep
  the historical Milestone and old closure commit closed; record the current Milestone's
  change card, trigger, old commit, new commit, `supersedes`, and impact cone instead of
  reopening or
  rerunning M0. That current card owns change, implementation, and verification work.
- A change that alters a decision or reasonable understanding receives independent criticism
  and owner approval at a new commit. Old approval remains attached to the old commit.
- Meaning-preserving mechanical changes use same-batch link and status refresh plus
  machine checks without reapproval.
- Propagate the approved delta only to affected Goal, Requirement, Design, Task, execution,
  test, evidence, and state representations; review and verify that impact cone only.

## Exit

For creation or a semantic revision, run the fresh-agent writer/Critic loop using the
English-only dispatch contract, present remaining material risks or that none are known,
obtain owner approval bound to the candidate commit, and integrate only when required by workspace
topology. Before approval, confirm every Milestone has at least one full-owned-outcome
end-to-end scenario. A mechanical maintenance batch needs machine checks but no
new approval. When the owner explicitly starts a target Milestone, **REQUIRED next skill:
`write-goal`**. After a revision, return to the stage that raised it and continue only the
affected path.

Before every substantive return, perform a task-specific self-check and correct defects. Do
not output a fixed `Reflection` section. Disclose only material unresolved risks that could
change the conclusion, decision, acceptance, or downstream work; otherwise omit the
disclosure. Approval, acceptance, and closure always state remaining material risks or that
none are known.
