---
name: write-design
description: "Use after Requirement review to create or change Design.md: system design, architecture, interface design, data design, technical/system/implementation solution, and the mapping from requirements to implementation structures. Requirement 已过审后写系统设计、架构设计、接口/数据设计、技术设计/技术方案/实现方案，回答这些需求怎么实现。"
---

# Design.md: requirements → implementation structures

<HARD-GATE>`Requirement.md` must exist and have independent-critic plus primary-orchestrator review. Otherwise return to `write-requirement`. If design work exposes changed upstream meaning, route to the WhitePaper, ROADMAP, Goal, or Requirement authority instead of redefining it in Design.</HARD-GATE>

## Language and contract

Use the Requirement locale and the matching
[English](../gmgn/references/en/writing-contract.md) or
[中文](../gmgn/references/zh-CN/writing-contract.md) Design template. Keep filename
`Design.md`, `type: design`, and `nature: normative`.

## Write

- Inspect the existing repository and real call path before proposing structures.
- Map every R-AC to modules, interfaces, data, failure paths, and verification points.
- Define trust boundaries, input validation, concurrency/ordering, migration, rollback,
  observability, security, accessibility, and performance only where the requirements demand them.
- Record important choices and rejected alternatives; use the locale-matched `decision-log.md`
  when a ruling must become an append-only authority.
- Use the trust-surface register for state-changing input acceptance points.
- Apply the first-sufficient anti-overdesign order from GMGN §7.

## Controlled revision

1. Classify the authority before editing. Route WhitePaper to `brainstorm`, ROADMAP to
   `roadmap`, Goal to `write-goal`, and Requirement or R-AC meaning to `write-requirement`.
   Resume after any required new upstream review or approval.
2. For Design-owned meaning, start from the old anchor and record the trigger, semantic delta,
   affected R-AC mappings, structures, interfaces, data, documents, tests, evidence, and
   proposed new anchor.
3. Revise only the affected design and bidirectional mapping; do not redesign unrelated
   structures.
4. A delta that changes a decision or reasonable understanding receives independent
   criticism and primary-orchestrator review at a new anchor. Old review remains attached to
   the old anchor.
5. Propagate only to affected Task cards, implementation, tests, evidence, and state
   representations; review and verify that impact cone only.

Meaning-preserving mechanical changes use same-batch link, hash, mapping pointer, and status
refresh plus machine checks without reapproval.

## Exit

Reconcile the affected mapping in both directions: no orphan design and no unmapped R-AC.
For creation or a semantic revision, run one independent critic with `critic-brief.md`,
emphasizing feasibility, upstream/downstream consistency, and overdesign. Resolve findings,
obtain primary-orchestrator review, and commit. Creation then uses **REQUIRED next skill:
`write-task`**. A revision returns to the stage that raised it and continues through the
affected path only.

End every substantive response with **Reflection**: weakest assumption; neglected
counterexample; measured versus inferred.
