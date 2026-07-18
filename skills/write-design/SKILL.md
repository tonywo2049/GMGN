---
name: write-design
description: "Use after Requirement review to create or change Design.md: system design, architecture, interface design, data design, technical/system/implementation solution, and the mapping from requirements to implementation structures. Requirement 已过审后写系统设计、架构设计、接口/数据设计、技术设计/技术方案/实现方案，回答这些需求怎么实现。"
---

# Design.md: requirements → implementation structures

<HARD-GATE>`Requirement.md` must exist and have independent-critic plus primary-orchestrator review. Otherwise return to `write-requirement`.</HARD-GATE>

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

## Exit

Reconcile the mapping in both directions: no orphan design and no unmapped R-AC. Run one
independent critic with `critic-brief.md`, emphasizing feasibility, upstream/downstream
consistency, and overdesign. Resolve findings, obtain primary-orchestrator review, commit,
then **REQUIRED next skill: `write-task`**.

End every substantive response with **Reflection**: weakest assumption; neglected
counterexample; measured versus inferred.
