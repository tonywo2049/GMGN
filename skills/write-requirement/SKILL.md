---
name: write-requirement
description: "Use after milestone initiation and Goal.md to analyze, clarify, create, or change functional/non-functional requirements, PRD/product requirements, requirement pool, user stories, acceptance criteria, or ACs in Requirement.md. Milestone 已立项后写/补需求分析、PRD/产品需求文档、需求池、用户故事、验收标准/AC，或做受控需求变更。"
---

# Requirement.md: single milestone requirement authority

<HARD-GATE>`Goal.md` must exist for an initiated milestone; otherwise return to `write-goal`. If requirement work exposes a changed WhitePaper, ROADMAP, or Goal premise, route to its authority before editing Requirement. Do not prescribe implementation structures in requirements or redefine upstream meaning here.</HARD-GATE>

## Language and contract

Use the Goal locale and the matching layout-free
[English](../gmgn/references/en/writing-contract.md) or
[中文](../gmgn/references/zh-CN/writing-contract.md) contract. Keep filename
`Requirement.md`, `type: requirement`, and `nature: normative`.

## Writer content and self-check

- Translate every in-scope Goal slice into numbered requirements `R1`, `R2`, ...; the recorded
  writer chooses the document structure.
- Give each requirement decidable ACs `R1-AC1`, ... using observable precondition, action,
  and result. This is the qualitative-to-quantitative boundary.
- Separate functional, non-functional, parameter/constraint, non-goal, and open-decision sections.
- Parameterize changeable numbers; name the authority and verification method for values.
- Maintain a Goal ↔ R/AC traceability table. No orphan Goal slice and no unowned AC.
- For a controlled change, record trigger, affected IDs, downstream impact, and version anchor.

Before return, the recorded writer checks that every Goal slice is covered or explicitly
excluded, every AC is decidable and owned, no requirement prescribes an implementation
structure, and every number has an authority and verification method.

## Writer and critic loop

At `ready-to-dispatch`, record the Goal anchor, select the actual writer, and bind `author_ref`.
The primary session may write directly, or an Author may be delegated with the content and
self-check above when the bounded handoff creates real value. At `author-returned`, send
incomplete or out-of-scope work to the same recorded writer as `author-rework`; otherwise enter
`candidate-anchored` and dispatch an independent Critic. At `critic-returned`, adjudicate
findings, resume the same recorded writer in `author-revising`, and send blocker fixes to the
same Critic in `critic-rechecking`. When no blocker remains, the primary orchestrator
reviews the candidate. The primary orchestrator applies accepted mechanical links, mappings,
state, and commit material, including across an integration boundary, and runs machine checks. Finish at
`node-complete`.

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

Require the recorded writer to reconcile scope coverage and scan every affected AC for
decidability. For creation or a semantic revision, run the identity-preserving writer/Critic
loop using the locale-matched dispatch contract; tell the Critic to emphasize upstream
consistency and acceptance quality. Obtain primary-orchestrator review and integrate only
when required by workspace topology. Creation then uses **REQUIRED next skill:
`write-design`**. A revision returns to the stage that raised it and continues through the
affected path only.

Before every substantive return, perform a task-specific self-check and correct defects. Do
not output a fixed `Reflection` section. Disclose only material unresolved risks that could
change the conclusion, decision, acceptance, or downstream work; otherwise omit the
disclosure. Approval, acceptance, and closure always state remaining material risks or that
none are known.
