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

## Design content

- Derive Design from the reviewed Requirement and explicitly sourced external constraints.
  Inspect the existing repository and real call paths for feasibility, but Design, Task,
  implementation, tests, or evidence cannot silently redefine upstream meaning. The recorded
  writer chooses the document layout.
- State the smallest implementation structure needed to satisfy the current R/ACs:
  architecture, responsibilities, owned data, composition, implementation constraints,
  required failure or recovery behavior, and verification points.
- Map each R/AC as: R/AC → design structure and data → applicable failure behavior →
  verification point. Every retained design element must name the current R/AC or sourced
  external invariant that would fail if it were removed.
- Split responsibilities by behavior and authority, not mechanically by existing library,
  process, repository, or deployment boundary. Keep every required responsibility, give each
  data or security responsibility one authority, and allow one implementation to own multiple
  responsibilities.
- Add trust boundaries, validation, concurrency, ordering, idempotency, resource limits,
  migration, rollback, observability, security, accessibility, and performance behavior only
  when required by a current R/AC or real call path. Do not require fixed sections for absent
  concerns.
- Requirement owns observable targets, constraints, acceptance values, and decision methods.
  Design may own implementation-specific choices, configuration, and derived values that do
  not change Requirement meaning. Task executes approved values and reports evidence; a needed
  change returns to the authority that owns the value.
- When the current Milestone outcome is research or selection, or a concrete uncertainty blocks
  a design decision, record only the uncertainty, required evidence, decision conditions, and
  controlled revision point. Task performs research, spikes, and experiments. Do not mandate a
  fixed research funnel or test sequence for every Design.
- When `Contract.md` is needed, give each retained cross-unit boundary a stable Contract ID and
  record its provider, consumers, interaction form, input/output semantics, invariants,
  observable failures, and conformance point. Keep an interface in Design when one
  implementation unit owns it; never create an empty Contract.
- Link an applicable OpenAPI, Protobuf, JSON Schema, code interface, event schema, command, or
  file format as the structural authority instead of copying it into Markdown. An interface
  contract does not imply HTTP or a network service.
- Record an authoritative decision only when its alternatives, conditions, or rollback matter.
  Retain rejected alternatives only when they explain a current decision or live rollback path.
- Implementation evidence may trigger a controlled Design revision. Keep the final adopted
  structure, decisions, Design-owned parameter boundaries, and only necessary evidence pointers
  in Design. Keep commands, full results, candidate chronology, task status, execution history,
  and closure records downstream.
- Apply the first-sufficient anti-overdesign order from GMGN §7. Delete any module, interface,
  state, configuration item, dependency, document, or failure mechanism whose removal would not
  cause a current R/AC or sourced external invariant to fail. Future reuse, possible scale,
  flexibility, and implementation convenience are not owners.
- Use the Design Bundle's Git commit. Do not add a parallel `v1`/`v2` workflow or formal API
  version unless a current external or coexisting-version compatibility requirement needs it.

Before return, check that every R/AC maps to structure, necessary data, applicable failure
behavior, and a verification point; every design element has a current R/AC or sourced external
constraint; Requirement meaning and owned values are unchanged; every independent boundary has
one interface authority and no empty Contract; research steps, test commands, results, and task
status remain downstream; and no retained structure can be deleted, reused, made native, or
replaced by a direct solution without losing a current accepted outcome.

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
