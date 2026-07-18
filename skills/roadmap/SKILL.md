---
name: roadmap
description: "Use after owner approval of the WhitePaper to create or maintain the project roadmap, product roadmap, milestones, phases, release/version plan, priority, dependency order, closure backfill, or TODO allocation. 白皮书已批后排路线图/产品路线图/里程碑规划/版本规划/发布规划、优先级；也用于 ROADMAP 关账回填、新想法登记分配、依赖调整和里程碑重排。"
---

# ROADMAP: single sequencing authority

<HARD-GATE>An approved, version-anchored WhitePaper must exist; otherwise return to `brainstorm`. If ROADMAP work exposes a WhitePaper premise that must change, use `brainstorm` revision mode instead of redefining it here. ROADMAP must not contain R-AC IDs or quantitative requirement metrics. It precedes milestone requirements, so goals and completion pictures stay qualitative.</HARD-GATE>

## Language and contract

Use the active locale and the matching
[English](../gmgn/references/en/writing-contract.md) or
[中文](../gmgn/references/zh-CN/writing-contract.md) template. Use `ROADMAP.md`,
`type: roadmap`, `nature: normative`, and `status: draft` until approved.

## Create

- Restate only the WhitePaper boundary and invariants needed for sequencing.
- Define ordered milestones with one qualitative objective, qualitative completion picture,
  dependencies, and work state `not-started`.
- Maintain one TODO list for ideas not yet allocated to a milestone.
- Do not pre-create empty G-R-D-T files for unstarted milestones.

## Maintain

- Closure backfill updates the milestone state and links the closure/Handoff evidence.
- New ideas enter TODO, then are assigned to a milestone before becoming requirements.
- Existing pre-GMGN inventory may use the one-time locale-matched `allocation-ledger.md`;
  it is not a permanent planning layer.

## Controlled revision

- Start from the approved old anchor. Record the trigger, semantic delta, affected milestone
  rows and documents, required reviewer or approver, and proposed new anchor.
- If the changed meaning belongs to the WhitePaper, initiate `brainstorm` revision mode and
  resume ROADMAP maintenance only after the required new upstream approval.
- Revise only ROADMAP-owned sequencing, milestone allocation, dependencies, qualitative
  completion pictures, or TODO placement. Do not reopen unaffected milestones.
- A change that alters a decision or reasonable understanding receives independent criticism
  and owner approval at a new anchor. Old approval remains attached to the old anchor.
- Meaning-preserving mechanical changes use same-batch link, hash, and status refresh plus
  machine checks without reapproval.
- Propagate the approved delta only to affected Goal, Requirement, Design, Task, execution,
  test, evidence, and state representations; review and verify that impact cone only.

## Exit

For creation or a semantic revision, run one independent critic using the locale-matched
`critic-brief.md`, resolve findings, present the weakest assumption, obtain owner approval
with a version anchor, and commit. A mechanical maintenance batch needs machine checks but no
new approval. When the owner explicitly starts a milestone, **REQUIRED next skill:
`write-goal`**. After a revision, return to the stage that raised it and continue only the
affected path.

End every substantive response with **Reflection**: weakest assumption; neglected
counterexample; measured versus inferred.
