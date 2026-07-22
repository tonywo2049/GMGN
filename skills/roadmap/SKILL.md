---
name: roadmap
description: "Use after owner approval of the WhitePaper to create or maintain the project roadmap, product roadmap, milestones, phases, release/version plan, priority, dependency order, closure backfill, or TODO allocation. 白皮书已批后排路线图/产品路线图/里程碑规划/版本规划/发布规划、优先级；也用于 ROADMAP 关账回填、新想法登记分配、依赖调整和里程碑重排。"
---

# ROADMAP: single sequencing authority

<HARD-GATE>An approved, version-anchored WhitePaper must exist; otherwise return to `brainstorm`. If ROADMAP work exposes a WhitePaper premise that must change, use `brainstorm` revision mode instead of redefining it here. ROADMAP must not contain R-AC IDs or quantitative requirement metrics. It precedes milestone requirements, so goals and completion pictures stay qualitative.</HARD-GATE>

## Language and contract

Use the active locale and the matching layout-free
[English](../gmgn/references/en/writing-contract.md) or
[中文](../gmgn/references/zh-CN/writing-contract.md) contract. Use `ROADMAP.md`,
`type: roadmap`, `nature: normative`, and `status: draft` until approved.

## Create

- Restate only the WhitePaper boundary and invariants needed for sequencing.
- Define ordered milestones with one qualitative objective, qualitative completion picture,
  dependencies, and work state `not-started`.
- Make each completion picture independently decidable from work owned by that Milestone.
  Sequence strong dependencies from earlier Milestones to later consumers; a downstream
  implementation, confirmation, document, or evidence item must not be an earlier Milestone's
  completion criterion.
- Maintain one TODO list for ideas not yet allocated to a milestone.
- Do not pre-create empty G-R-D-T files for unstarted milestones.

## Maintain

- Closure backfill updates the milestone state, closure evidence, and any Handoff that exists.
- New ideas enter TODO, then are assigned to a milestone before becoming requirements.
- Record downstream-only confirmations as a non-blocking TODO or Handoff with receiving
  Milestone/owner, question, trigger, possible impact, and any safe default assumption. Closure
  of the producing Milestone does not wait for the consumer to resolve it.
- For existing pre-GMGN inventory, have the recorded writer capture each legacy ID, source,
  summary, target milestone/requirement or pending decision, rationale, and allocation state.
  Reconcile source total = allocated + explicitly rejected + pending, then archive the
  migration record. Do not create this layer for new work.

## Writer and critic loop

1. Record the WhitePaper anchor and mode. The primary session may write directly, or it may
   prepare a complete brief and create one fresh Author when the bounded handoff creates real
   value.
2. The writer self-checks before return. A delegated Author ends after that return; missing
   inputs or later revision use the primary session or a fresh Author with a new brief.
3. Freeze the candidate and dispatch one fresh independent Critic from a prepared brief.
   Collect all findings before editing, adjudicate once, and batch accepted blocker fixes. A
   semantic recheck uses a fresh Critic only for affected scope; unchanged roles are not sent.
4. With no blocker, owner approval binds the candidate anchor. The primary orchestrator applies
   accepted mechanical reciprocal links, state, and evidence pointers, then runs machine checks.

Closure backfill and other meaning-preserving maintenance skip semantic criticism. The primary
session applies the mechanical batch directly, including across an integration boundary. Run
machine checks and preserve the existing approval through an
equivalence record. Any semantic ambiguity returns to the full writer/Critic loop.

## Controlled revision

- Start from the approved old anchor. Record the trigger, semantic delta, affected milestone
  rows and documents, required reviewer or approver, and proposed new anchor.
- If the changed meaning belongs to the WhitePaper, initiate `brainstorm` revision mode and
  resume ROADMAP maintenance only after the required new upstream approval.
- Revise only ROADMAP-owned sequencing, milestone allocation, dependencies, qualitative
  completion pictures, or TODO placement. Do not reopen unaffected milestones.
- A later Milestone may supersede a technical selection originating in a closed foundation or
  M0 Milestone. The M0-originated Design, Decision, or index remains semantic authority. Keep
  the historical Milestone and old closure anchor closed; record the current Milestone's change
  card, trigger, old anchor, new anchor, `supersedes`, and impact cone instead of reopening or
  rerunning M0. That current card owns change, implementation, and verification work.
- A change that alters a decision or reasonable understanding receives independent criticism
  and owner approval at a new anchor. Old approval remains attached to the old anchor.
- Meaning-preserving mechanical changes use same-batch link, hash, and status refresh plus
  machine checks without reapproval.
- Propagate the approved delta only to affected Goal, Requirement, Design, Task, execution,
  test, evidence, and state representations; review and verify that impact cone only.

## Exit

For creation or a semantic revision, run the fresh-agent writer/Critic loop using the
locale-matched dispatch contract, present remaining material risks or that none are known,
obtain owner approval with a version anchor, and integrate only when required by workspace
topology. A mechanical maintenance batch needs machine checks but no
new approval. When the owner explicitly starts a target Milestone, **REQUIRED next skill:
`write-goal`**. After a revision, return to the stage that raised it and continue only the
affected path.

Before every substantive return, perform a task-specific self-check and correct defects. Do
not output a fixed `Reflection` section. Disclose only material unresolved risks that could
change the conclusion, decision, acceptance, or downstream work; otherwise omit the
disclosure. Approval, acceptance, and closure always state remaining material risks or that
none are known.
