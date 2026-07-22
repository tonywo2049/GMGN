---
name: write-design
description: "Use after Requirement review to create or change Design.md: system design, architecture, interface design, data design, technical/system/implementation solution, and the mapping from requirements to implementation structures. Requirement 已过审后写系统设计、架构设计、接口/数据设计、技术设计/技术方案/实现方案，回答这些需求怎么实现。"
---

# Design.md: requirements → implementation structures

<HARD-GATE>`Requirement.md` must exist and have independent-critic plus primary-orchestrator review. Otherwise return to `write-requirement`. If design work exposes changed upstream meaning, route to the WhitePaper, ROADMAP, Goal, or Requirement authority instead of redefining it in Design.</HARD-GATE>

## Language and contract

Use the Requirement locale for artifact prose and the English-only layout-free
[writing contract](../gmgn/references/en/writing-contract.md). Keep filename `Design.md`,
`type: design`, and `nature: normative`.

## Writer content and self-check

- Inspect the existing repository and real call path before proposing structures. The recorded
  writer chooses the document layout.
- Map every R-AC to modules, interfaces, data, failure paths, and verification points.
- Define trust boundaries, input validation, concurrency/ordering, migration, rollback,
  observability, security, accessibility, and performance only where the requirements demand them.
- Record choices whose alternatives or rollback matter. Give an authoritative decision a
  stable ID, ruling, rationale, conditions, owner, and any superseded decision instead of
  rewriting history.
- For each external input, cache restore, migration import, permission boundary, human entry,
  or model-output acceptance point, record the real source authority, validation, observable
  failure behavior, negative evidence, and owner. “Validated upstream” is not a source.
- Apply the first-sufficient anti-overdesign order from GMGN §7.

Before return, check the mapping in both directions, trust boundaries and negative paths,
existing-call-path feasibility, rollback or failure behavior where required, and whether any
new structure lacks a current R-AC.

## Writer and critic loop

Record the Requirement anchor. The primary session may write directly, or it prepares a
complete brief and creates one fresh Author when the bounded handoff creates
real value. The writer self-checks before return; a delegated Author ends on return, so later
correction uses the primary session or a fresh Author with a new brief. Freeze the candidate
and dispatch one fresh independent Critic from a prepared brief. Collect all findings before
editing, adjudicate once, and batch accepted blocker fixes. The primary orchestrator checks
each resolution without dispatching a second Critic. With no accepted blocker unresolved, it
reviews the anchored candidate, applies accepted mechanical mappings, links, and state, then
runs machine checks.

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

Require the recorded writer to reconcile the affected mapping in both directions: no orphan
design and no unmapped R-AC. For creation or a semantic revision, run the fresh-agent
writer/Critic loop using the English-only dispatch contract; tell the Critic to emphasize
feasibility, upstream/downstream consistency, and overdesign. Obtain primary-orchestrator
review and integrate only when required by workspace topology. Creation then uses **REQUIRED next skill:
`write-task`**. A revision returns to the stage that raised it and continues through the
affected path only.

Before every substantive return, perform a task-specific self-check and correct defects. Do
not output a fixed `Reflection` section. Disclose only material unresolved risks that could
change the conclusion, decision, acceptance, or downstream work; otherwise omit the
disclosure. Approval, acceptance, and closure always state remaining material risks or that
none are known.
