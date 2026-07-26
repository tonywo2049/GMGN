---
name: write-requirement
description: "Use after milestone initiation and Goal.md to analyze, clarify, create, or change functional/non-functional requirements, PRD/product requirements, requirement pool, user stories, acceptance criteria, or ACs in Requirement.md. Milestone 已立项后写/补需求分析、PRD/产品需求文档、需求池、用户故事、验收标准/AC，或做受控需求变更。"
---

# Requirement.md: single milestone requirement authority

<HARD-GATE>`Goal.md` must exist for an initiated milestone; otherwise return to `write-goal`. If requirement work exposes a changed WhitePaper, ROADMAP, or Goal premise, route to its authority before editing Requirement. Do not prescribe implementation structures in requirements or redefine upstream meaning here.</HARD-GATE>

## Language and contract

Before writing, load the registered `gmgn` Skill through normal discovery and follow its local
writing contract. Use the Goal locale for artifact prose. Keep filename `Requirement.md`,
`type: requirement`, and `nature: normative`.

## Requirement content

- Derive Requirement only from the approved Goal and explicitly sourced external constraints.
  Later documents, implementation, tests, or evidence may expose a needed revision but cannot
  silently define or redefine Requirement.
- Translate every in-scope Goal result slice and Close outcome into the smallest necessary set
  of numbered requirements `R1`, `R2`, ... . Each R states one coherent required behavior,
  capability, or constraint and names its owning Goal result or external constraint.
- Give each R decidable ACs `R1-AC1`, ... using enough observable precondition, action or
  inspection, and result to determine pass or fail. Given/When/Then is optional syntax, not a
  mandatory format. Numeric and static constraints may state their decision rule directly.
  Use unambiguous observable language; terms such as reasonable, complete, sufficient,
  high-performance, or robust require a decidable definition. Include rejection, failure,
  recovery, or unchanged-state conditions only when required by the current outcome or invariant.
- Keep the explicit trace: Goal result or Close outcome → R/AC. No in-scope Goal result or
  Close outcome may disappear, and no R/AC may be unowned.
- Preserve upstream-approved invariants and values without silent weakening. Requirement may
  define quantified parameters it owns; name each value's authority, change boundary, and
  verification method, plus only the measurement conditions needed to make it decidable.
- Include functional, non-functional, parameter/constraint, non-goal, and open-decision content
  only when applicable; do not require fixed sections for absent categories. Resolve every
  Requirement-owned decision before acceptance and route changed upstream meaning upstream.
- Do not invent or prescribe components, modules, interfaces, process structure, code layout,
  data structures, implementation choices, task division, execution order, test commands,
  runtime results, evidence IDs, live status, or closure history. Upstream-defined domain or
  system names may be referenced without making Requirement their design authority.
- Delete any R/AC whose removal would not cause a current Goal outcome or externally imposed
  invariant to fail. Future possibility, speculative reuse or scale, configurability, and
  implementation convenience are not owners.

## Writer and critic loop

Record the Goal commit. The primary session may write directly, or it prepares a complete brief
and creates one fresh Author when the bounded handoff creates real
value. The writer self-checks before return; a delegated Author ends on return, so later
correction uses the primary session or a fresh Author with a new brief. Commit the complete
candidate locally and dispatch one fresh independent Critic from a prepared brief that names
the shortest unambiguous commit reference. Collect all findings before
editing, adjudicate once, and batch accepted blocker fixes. The primary orchestrator checks
each resolution without dispatching a second Critic. When no accepted blocker remains
unresolved, it reviews the candidate, applies accepted mechanical links, mappings, and state,
then runs machine checks.

## Controlled revision

1. Classify where the changed meaning belongs. Route WhitePaper to `brainstorm`, ROADMAP to
   `roadmap`, and Goal to `write-goal`; resume Requirement work after any required new
   upstream review or approval.
2. For Requirement-owned meaning, start from the old commit and record the trigger, semantic
   delta, affected R/AC IDs, documents, tests, evidence, and proposed new commit.
3. Revise only affected requirements, criteria, parameters, constraints, and traceability.
   Do not re-analyze unaffected Goal slices.
4. A delta that changes a decision or reasonable understanding receives independent
   criticism and primary-orchestrator review at a new commit. Old review remains attached to
   the old commit.
Meaning-preserving mechanical changes use same-batch link, ID reference, and status
refresh plus machine checks without reapproval.

## Exit

Require one completion check: every in-scope Goal result and Close outcome is covered; any
proposed exclusion routes to `write-goal`; every R/AC has an upstream owner and passes the
deletion test; every AC has a clear pass/fail decision; every number has an authority, change
boundary, and verification method; every Requirement-owned decision is resolved; and no
technical solution, task, execution information, or actual verification result has leaked
into Requirement. For
creation or a semantic revision, run the fresh-agent writer/Critic loop using the English-only
dispatch contract; tell the Critic to emphasize upstream consistency, acceptance quality, and
deletion of any R/AC that does not serve a current Goal outcome. Obtain primary-orchestrator
review and integrate only when required by workspace topology.

Before every substantive return, perform a task-specific self-check and correct defects. Do
not output a fixed `Reflection` section. Disclose only material unresolved risks that could
change the conclusion, decision, acceptance, or downstream work; otherwise omit the
disclosure. Approval, acceptance, and closure always state remaining material risks or that
none are known.
