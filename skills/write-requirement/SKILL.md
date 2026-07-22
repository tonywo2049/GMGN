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
- Carry every ROADMAP acceptance-scenario anchor through its mapped Goal slices into one or
  more R/ACs. Keep the trace explicit as ROADMAP acceptance scenario → Goal slice → R/AC;
  refine the scenario into decidable criteria without copying it as a second AC system.
- Clearly distinguish functional, non-functional, parameter/constraint, non-goal, and
  open-decision content.
- Parameterize changeable numbers; name the authority and verification method for values.
- Maintain the ROADMAP acceptance scenario → Goal slice → R/AC traceability. No acceptance
  scenario may disappear silently, no Goal slice may be orphaned, and no AC may be unowned.
- For a controlled change, record trigger, affected IDs, downstream impact, and version anchor.

Before return, the recorded writer checks that every ROADMAP acceptance scenario is covered
through Goal slices or routed back to `roadmap`/`write-goal`, every Goal slice is covered or
explicitly excluded, every AC is decidable and owned, no requirement prescribes an
implementation structure, and every number has an authority and verification method.

## Writer and critic loop

Record the Goal anchor. The primary session may write directly, or it prepares a complete brief
and creates one fresh Author when the bounded handoff creates real
value. The writer self-checks before return; a delegated Author ends on return, so later
correction uses the primary session or a fresh Author with a new brief. Freeze the candidate
and dispatch one fresh independent Critic from a prepared brief. Collect all findings before
editing, adjudicate once, and batch accepted blocker fixes. A semantic recheck uses a fresh
Critic only for affected scope. When no blocker remains, the primary orchestrator reviews the
candidate, applies accepted mechanical links, mappings, and state, then runs machine checks.

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
decidability. For creation or a semantic revision, run the fresh-agent writer/Critic
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
