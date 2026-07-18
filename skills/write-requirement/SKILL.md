---
name: write-requirement
description: "Use after milestone initiation and Goal.md to analyze, clarify, create, or change functional/non-functional requirements, PRD/product requirements, requirement pool, user stories, acceptance criteria, or ACs in Requirement.md. Milestone 已立项后写/补需求分析、PRD/产品需求文档、需求池、用户故事、验收标准/AC，或做受控需求变更。"
---

# Requirement.md: single milestone requirement authority

<HARD-GATE>`Goal.md` must exist for an initiated milestone; otherwise return to `write-goal`. If requirement work exposes a changed WhitePaper, ROADMAP, or Goal premise, route to its authority before editing Requirement. Do not prescribe implementation structures in requirements or redefine upstream meaning here.</HARD-GATE>

## Language and contract

Use the Goal locale and the matching
[English](../gmgn/references/en/writing-contract.md) or
[中文](../gmgn/references/zh-CN/writing-contract.md) Requirement template. Keep filename
`Requirement.md`, `type: requirement`, and `nature: normative`.

## Write

- Translate every in-scope Goal slice into numbered requirements `R1`, `R2`, ...
- Give each requirement decidable ACs `R1-AC1`, ... using observable precondition, action,
  and result. This is the qualitative-to-quantitative boundary.
- Separate functional, non-functional, parameter/constraint, non-goal, and open-decision sections.
- Parameterize changeable numbers; name the authority and verification method for values.
- Maintain a Goal ↔ R/AC traceability table. No orphan Goal slice and no unowned AC.
- For a controlled change, record trigger, affected IDs, downstream impact, and version anchor.

## Controlled revision

1. Classify where the changed meaning belongs. Route WhitePaper to `brainstorm`, ROADMAP to
   `roadmap`, and Goal to `write-goal`; resume Requirement work after any required new
   upstream review or approval.
2. For Requirement-owned meaning, start from the old anchor and record the trigger, semantic
   delta, affected R/AC IDs, documents, tests, evidence, and proposed new anchor.
3. Revise only affected requirements, criteria, parameters, constraints, and traceability.
   Do not re-analyze unaffected Goal slices.
4. A delta that changes a decision or reasonable understanding receives independent
   criticism and primary-orchestrator review at a new anchor. Old review remains attached to
   the old anchor.
5. Propagate only to affected Design, Task, implementation, tests, evidence, and state
   representations; review and verify that impact cone only.

Meaning-preserving mechanical changes use same-batch link, hash, ID reference, and status
refresh plus machine checks without reapproval.

## Exit

Reconcile scope coverage and scan every affected AC for decidability. For creation or a
semantic revision, run one independent critic with the locale-matched `critic-brief.md`,
emphasizing upstream consistency and acceptance quality. Resolve findings, obtain
primary-orchestrator review, and commit. Creation then uses **REQUIRED next skill:
`write-design`**. A revision returns to the stage that raised it and continues through the
affected path only.

End every substantive response with **Reflection**: weakest assumption; neglected
counterexample; measured versus inferred.
