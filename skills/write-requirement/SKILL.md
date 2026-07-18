---
name: write-requirement
description: "Use after milestone initiation and Goal.md to analyze, clarify, create, or change functional/non-functional requirements, PRD/product requirements, requirement pool, user stories, acceptance criteria, or ACs in Requirement.md. Milestone 已立项后写/补需求分析、PRD/产品需求文档、需求池、用户故事、验收标准/AC，或做受控需求变更。"
---

# Requirement.md: single milestone requirement authority

<HARD-GATE>`Goal.md` must exist for an initiated milestone; otherwise return to `write-goal`. Do not prescribe implementation structures in requirements.</HARD-GATE>

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

## Exit

Reconcile scope coverage and scan every AC for decidability. Run one independent critic
with the locale-matched `critic-brief.md`, emphasizing upstream consistency and acceptance
quality. Resolve findings, obtain primary-orchestrator review, commit, then
**REQUIRED next skill: `write-design`**.

End every substantive response with **Reflection**: weakest assumption; neglected
counterexample; measured versus inferred.
