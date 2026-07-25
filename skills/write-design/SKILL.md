---
name: write-design
description: "Use after Requirement review to create or change the Design-stage bundle: Design.md plus Contract.md only when independently developed boundaries need a separate interface authority. Requirement 已过审后确定架构、模块职责与按需的跨任务接口契约。"
---

# Design stage: requirements → architecture and executable boundaries

<HARD-GATE>`Requirement.md` must exist and have independent-critic plus primary-orchestrator review. Otherwise return to `write-requirement`. If design work exposes changed upstream meaning, route to the WhitePaper, ROADMAP, Goal, or Requirement authority instead of redefining it in Design.</HARD-GATE>

## Language and contract

Before writing, load the registered `gmgn` Skill through normal discovery and follow its local
writing contract. Use the Requirement locale for artifact prose. `Design.md` uses `type:
design`; an independently needed `Contract.md` uses `type: contract`; both are normative.

The Design-stage candidate is:

- `Design.md` alone when there is no cross-unit interface; or
- one Design Bundle—`Design.md` plus required `Contract.md` at the same Git commit—when
  current work crosses independently developed module, task, or team boundaries.

The contract itself is mandatory for every such boundary; only the separate file is
conditional on that boundary existing. Do not create an empty `Contract.md`. Do not split a
normal in-process module into services merely to justify a contract artifact.
Design acceptance makes the bundle an `approved` working baseline for implementation, not the
final frozen contract. Controlled coding evidence may produce a newly reviewed working commit;
`close-milestone` freezes the final implementation-matching Contract as `closed`.

## Writer content and self-check

- Inspect the existing repository and real call path before proposing structures. The recorded
  writer chooses the document layout.
- `Design.md` owns architecture, module responsibilities, owned data, composition, internal
  implementation constraints, failure paths, and the mapping from R-ACs to those structures.
- When `Contract.md` is needed, give each retained cross-task boundary a stable Contract ID and
  record its provider, consumers, entry or interaction form, input/output semantics,
  invariants, observable failures, and conformance point. Add authentication, idempotency,
  timeout, retry, ordering, concurrency, compatibility, or migration behavior only when a
  current R/AC or real call path needs it.
- Link an applicable OpenAPI, Protobuf, JSON Schema, code interface, event schema, command, or
  file format as the structural authority instead of copying it into Markdown. An interface
  contract does not imply HTTP or a network service.
- Map every R-AC to modules, applicable Contract IDs, data, failure paths, and verification
  points. Partition technical responsibility so a provider and its consumers can implement
  against the approved contract without waiting for each other's code.
- Define trust boundaries, input validation, concurrency/ordering, migration, rollback,
  observability, security, accessibility, and performance only where the requirements demand them.
- Record choices whose alternatives or rollback matter. Give an authoritative decision a
  stable ID, ruling, rationale, conditions, owner, and any superseded decision instead of
  rewriting history.
- For each external input, cache restore, migration import, permission boundary, human entry,
  or model-output acceptance point, record the real source authority, validation, observable
  failure behavior, negative evidence, and owner. “Validated upstream” is not a source.
- Apply the first-sufficient anti-overdesign order from GMGN §7. For every new module,
  interface, state, configuration item, dependency, or failure mechanism, name the current
  R/AC that would fail if it were removed. Future reuse or possible scale is not sufficient.
- Run a bounded feasibility spike before accepting a boundary only when a concrete uncertainty
  in a library, protocol, serialization path, legacy integration, or required quality cannot
  be resolved from the repository and direct evidence. The spike is evidence, not a mandatory
  production task.
- Use the Design Bundle's Git commit. Do not add a parallel
  `v1`/`v2` workflow or formal API version unless a current external or coexisting-version
  compatibility requirement needs it.

Before return, check the mapping in both directions, trust boundaries and negative paths,
existing-call-path feasibility, provider/consumer agreement on each retained Contract ID,
rollback or failure behavior where required, and whether any new document or structure lacks a
current R-AC or can be deleted, reused, made native, or replaced by a direct solution without
losing a current accepted outcome.

## Writer and critic loop

Record the Requirement commit. The primary session may write directly, or it prepares a
complete brief and creates one fresh Author when the bounded handoff creates
real value. The writer self-checks before return; a delegated Author ends on return, so later
correction uses the primary session or a fresh Author with a new brief. Commit the whole
Design-stage candidate locally and dispatch one fresh independent Critic from a prepared brief
that names the shortest unambiguous commit reference. When
`Contract.md` exists, the Critic checks both provider and consumer feasibility, the
Design-to-Contract mapping, and whether the separate artifact can be deleted. Collect all
findings before editing, adjudicate once, and batch accepted blocker fixes. The primary
orchestrator checks each resolution without dispatching a second Critic. With no accepted
blocker unresolved, it reviews and accepts the Design Bundle at one commit, applies accepted
mechanical mappings, links, and state, then runs machine checks. This commit is the shared
working baseline for Task creation and Coder dispatch.

## Controlled revision

1. Classify the authority before editing. Route WhitePaper to `brainstorm`, ROADMAP to
   `roadmap`, Goal to `write-goal`, and Requirement or R-AC meaning to `write-requirement`.
   Resume after any required new upstream review or approval.
2. A Coder may challenge an interface contract with implementation evidence but cannot change
   the shared contract in its Card. The primary orchestrator classifies the return as an
   internal implementation issue, a meaning-preserving clarification, or a semantic
   Design/Contract change.
3. A meaning-preserving clarification uses the smallest same-batch edit, affected pointer
   refresh, and machine checks. It does not trigger semantic reapproval.
4. For Design- or Contract-owned meaning, start from the old bundle commit and record the
   trigger, smallest semantic delta, affected Contract IDs, R-AC mappings, structures,
   providers, consumers, tasks, code, tests, evidence, and proposed new commit. Pause only that
   impact cone.
5. Revise only the affected design, contract, and bidirectional mapping; do not redesign
   unrelated structures. A semantic delta receives one fresh independent Critic round and
   primary-orchestrator review at the new bundle commit. Old review remains attached to the
   old commit.
6. Propagate only to affected Task cards, implementation, tests, evidence, and state
   representations. Unaffected lanes continue.

Meaning-preserving mechanical changes use same-batch link, mapping pointer, and status
refresh plus machine checks without reapproval.

## Exit

Require the recorded writer to reconcile the affected mapping in both directions: no orphan
design or contract, no unmapped R-AC, and no cross-task boundary with multiple competing
authorities. For creation or a semantic revision, run the fresh-agent writer/Critic loop using
the English-only dispatch contract; tell the Critic to emphasize provider/consumer feasibility,
upstream/downstream consistency, and a deletion-first overdesign check against the smallest
sufficient Design Bundle. Obtain primary-orchestrator review and integrate only when required
by workspace topology. Creation then uses **REQUIRED next skill: `write-task`**. A revision
returns to the stage that raised it and continues through the affected path only.
Do not mark the Design-stage Contract `closed` here; final freezing belongs to accepted
Milestone closure after implementation and contract evidence agree.

Before every substantive return, perform a task-specific self-check and correct defects. Do
not output a fixed `Reflection` section. Disclose only material unresolved risks that could
change the conclusion, decision, acceptance, or downstream work; otherwise omit the
disclosure. Approval, acceptance, and closure always state remaining material risks or that
none are known.
