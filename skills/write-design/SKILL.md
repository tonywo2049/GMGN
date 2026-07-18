---
name: write-design
description: "Use after Requirement review to create or change Design.md: system design, architecture, interface design, data design, technical/system/implementation solution, and the mapping from requirements to implementation structures. Requirement 已过审后写系统设计、架构设计、接口/数据设计、技术设计/技术方案/实现方案，回答这些需求怎么实现。"
---

# Design.md: requirements → implementation structures

<HARD-GATE>`Requirement.md` must exist and have independent-critic plus primary-orchestrator review. Otherwise return to `write-requirement`. If design work exposes changed upstream meaning, route to the WhitePaper, ROADMAP, Goal, or Requirement authority instead of redefining it in Design.</HARD-GATE>

## Language and contract

Use the Requirement locale and the matching layout-free
[English](../gmgn/references/en/writing-contract.md) or
[中文](../gmgn/references/zh-CN/writing-contract.md) contract. Keep filename
`Design.md`, `type: design`, and `nature: normative`.

## Author content and self-check

- Dispatch an Author to inspect the existing repository and real call path before proposing
  structures. The Author chooses the document layout.
- Map every R-AC to modules, interfaces, data, failure paths, and verification points.
- Define trust boundaries, input validation, concurrency/ordering, migration, rollback,
  observability, security, accessibility, and performance only where the requirements demand them.
- Record important choices and rejected alternatives. An authoritative decision must include
  a stable ID, trigger and old anchor, ruling, rationale, conditions, owner, propagation
  targets, and new version anchor; superseding decisions cite the old ID instead of rewriting it.
- For each external input, cache restore, migration import, permission boundary, human entry,
  or model-output acceptance point, record the real source authority, validation, observable
  failure behavior, negative evidence, and owner. “Validated upstream” is not a source.
- Apply the first-sufficient anti-overdesign order from GMGN §7.

Before return, check the mapping in both directions, trust boundaries and negative paths,
existing-call-path feasibility, rollback or failure behavior where required, and whether any
new structure lacks a current R-AC.

## Author and critic loop

At `ready-to-dispatch`, record the Requirement anchor and dispatch one Author with the content
and self-check above; retain `author_ref`. The orchestrator does not draft Design. At
`author-returned`, return missing or out-of-scope work to the same Author as `author-rework`;
otherwise enter `candidate-anchored` and dispatch an independent Critic. At `critic-returned`,
adjudicate findings, resume the same Author in `author-revising`, and send blocker fixes to
the same Critic in `critic-rechecking`. With no blocker, the primary orchestrator reviews the
anchored candidate and dispatches an Integrator for accepted mechanical mappings, links,
state, and commit material. Finish at `node-complete`.

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

Require the Author to reconcile the affected mapping in both directions: no orphan design and
no unmapped R-AC. For creation or a semantic revision, run the identity-preserving
Author/Critic loop using the locale-matched dispatch contract; tell the Critic to emphasize
feasibility, upstream/downstream consistency, and overdesign. Obtain primary-orchestrator
review and integrate. Creation then uses **REQUIRED next skill:
`write-task`**. A revision returns to the stage that raised it and continues through the
affected path only.

End every substantive response with **Reflection**: weakest assumption; neglected
counterexample; measured versus inferred.
