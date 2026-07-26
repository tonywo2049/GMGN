---
name: write-design
description: "Use after Requirement review to create or change the Design-stage bundle: root Design.md, conditional module design, and design/Contract.md only for independently developed boundaries. Requirement 已过审后确定可直接实现的架构、模块职责与按需的跨单元接口契约。"
---

# Design stage: requirements → architecture and executable boundaries

<HARD-GATE>`Requirement.md` must exist and have independent-critic plus primary-orchestrator review. Otherwise return to `write-requirement`. If design work exposes changed upstream meaning, route to the WhitePaper, ROADMAP, Goal, or Requirement authority instead of redefining it in Design.</HARD-GATE>

## Language, bundle, and authority

Before writing, load the registered `gmgn` Skill through normal discovery and follow its local
writing contract. Use the Requirement locale for artifact prose. Every Design-stage artifact
is normative.

`Design.md` always exists and owns global architecture, module boundaries, the Bundle index,
and the complete R/AC mapping. Add only the files current work needs:

```text
Design.md
design/
├── <module-id>.md
├── Contract.md
├── contracts/<contract-id>.md
└── schemas/<structural-authority>
```

- `design/<module-id>.md` owns one module's private design when size, specialization, or
  parallel authoring makes a separate authority useful.
- `design/Contract.md` is required only when current work crosses an independently developed
  module, task, team, process, or repository boundary. It owns the cross-unit interface index
  and shared contract rules.
- Keep a small interface directly in `design/Contract.md`; split
  `design/contracts/<contract-id>.md` only when independent review or size requires it.
- Put an exact machine-readable or compilable interface authority under `design/schemas/`
  only when correctness depends on it. Do not pre-create format subdirectories.

Do not create an empty file or directory, split a normal in-process module merely to justify a
contract, or copy one definition into several artifacts. Every child links to `Design.md`;
every cross-unit contract links its provider, consumers, applicable module documents, and
structural authority. `Design.md` indexes those links without duplicating their owned meaning.

The Design-stage candidate is `Design.md` plus every linked Design-stage artifact at one Git
commit. Design acceptance marks that complete Bundle `approved`.

## Design content and completion

Design determines how to implement the reviewed Requirement. Specify every choice that can
change an R/AC, public or cross-unit data, authority source, validation order, observable
error, atomicity, recovery, security, compatibility, or resource behavior. Local replaceable
expressions that cannot change another unit's result need no Design content. If the approved
Bundle permits incompatible implementations of a shared boundary, it is incomplete.

The following are applicability checks, not required headings or a document template:

- Derive every decision from reviewed R/ACs or an explicitly sourced external constraint.
  Inspect the repository and real call paths for feasibility without redefining upstream
  meaning.
- Determine the smallest sufficient technical stack, dependency and build choices, source
  locations, components, responsibilities, owned data, dependency direction, and trust
  boundaries.
- Determine required call and data flows, state transitions, non-trivial algorithms, storage
  keys and indexes, transaction boundaries, migrations, concurrency, ordering, idempotency,
  failure recovery, rollback, security, performance, resource, and observability behavior
  whenever the current R/AC or real call path makes them implementation-significant.
- Map each R/AC once in root `Design.md` to the owning design structure, necessary data,
  applicable failure behavior, interface authority, and verification point. Child artifacts
  link their applicable R/ACs without copying the complete map.
- Give each retained design element one owner and the current R/AC or sourced invariant that
  would fail if it were removed. Future reuse, possible scale, flexibility, or implementation
  convenience is not an owner.

Every applicable cross-unit boundary must close the whole path from authoritative producer,
through specified derivation or conversion, to consumer validation and state effect. Define
legal object phases and conversions; every invariant's single validation authority and every
required production call site; success, observable failures, and state effects; and applicable
atomicity, concurrency, ordering, retry, cancellation, idempotency, recovery, compatibility,
authentication, authorization, and resource behavior. Define one-to-many completeness,
uniqueness, and zero-effect semantics when present. When several checks can fail and first
error changes compatibility, safety, or retry behavior, define one authoritative error order.
Naming a validator without binding every required entry point does not close the boundary.

For each cross-unit interface, assign a stable Contract ID, provider, consumers, interaction
form, exact request, success, error, preconditions, postconditions, invariants, state effects,
and conformance point. When compatibility or correctness depends on exact fields, presence,
types, widths, tags, encoding, byte order, canonicalization, hash preimage, signature domain,
state key, error enum, or method signature, link one machine-readable or compilable authority
such as OpenAPI, Protobuf, JSON Schema, an event schema, or code-native trait/types. Markdown
explains semantics and does not copy the complete signature. Add the smallest reducer, golden
vector, or conformance specification only when the structural authority cannot express a
required derivation, ordering, or byte result. Design defines these authorities; it does not
implement production I/O, storage, or providers.

Keep the Bundle `draft` while any implementation-significant decision remains unresolved.

Record alternatives only when they explain a current decision or live rollback path. Do not
include commands, full results, candidate chronology, work status, execution history, or
closure records. Do not add formal API versions unless a current external or
coexisting-version compatibility requirement needs them.

Before return, apply this Design Ready gate:

1. No implementation-significant question, hidden default, or unapproved parameter remains.
2. Every applicable boundary has one structure authority and a closed producer-to-state path.
3. Every R/AC and retained design element has one resolvable owner, implementation result, and
   verification point without duplicated authority.
4. Applicable schema compiles or lints, and required vectors or conformance checks reproduce.
5. Removing, reusing, making native, or directly replacing any retained structure would lose a
   current accepted outcome or safeguard.

## Writer and critic loop

Record the Requirement commit. For a small Bundle, the primary session writes it directly.
For useful parallelism, it first creates root `Design.md` with the global architecture, module
boundaries, dependency direction, planned artifacts, and ownership; root remains the primary
session's write surface. Dispatch fresh Authors by bounded semantic module, not mechanically by
file count. Each Author writes only its declared child artifacts and self-checks their links
and local closure.

The primary session integrates provider/consumer seams, shared state, error order, and schema
references, then commits one complete immutable Bundle candidate and identifies it by the
shortest unambiguous commit reference. Run one Critic round after that integration. A small
Bundle uses one fresh Critic; a large Bundle may use parallel fresh Critics on bounded module
scopes plus one Bundle-seam scope in the same round. Every Critic reads the same candidate
commit, all returns are collected before editing, and physical file count never determines
the number of Critics.

Critics find any implementation-significant decision still unspecified. Reject any public or
cross-unit decision, authority, validation entry, state effect, failure, recovery, or
parameter left ambiguous. Check provider and consumer feasibility, object-phase legality,
structural authority consistency, global-versus-local rule conflicts, R/AC traceability, and
whether each separate artifact can be deleted.

Adjudicate once and batch accepted blocker fixes. A fix is mechanical only when it makes a
duplicate representation conform to an already unambiguous reviewed authority without changing
meaning. The primary orchestrator checks those resolutions and affected machine checks without
another Critic. If the fix must invent or change Design-owned meaning, it is a new semantic
batch under Controlled revision, not a recheck of the old batch. Accept only the complete
Bundle at one commit as the shared Design baseline.

## Controlled revision

1. Classify the authority before editing. Route WhitePaper to `brainstorm`, ROADMAP to
   `roadmap`, Goal to `write-goal`, and Requirement or R-AC meaning to `write-requirement`.
   Resume after any required new upstream review or approval.
2. A meaning-preserving clarification only aligns a duplicate representation with an existing
   unambiguous authority. It uses the smallest same-batch edit, affected pointer refresh, and
   machine checks without semantic reapproval.
3. For Design- or Contract-owned meaning, start from the old Bundle commit and record the
   trigger, smallest semantic delta, affected Contract IDs, R-AC mappings, structures,
   providers, consumers, and proposed new commit.
4. Adding or changing a public type or Port, authority source, required validation call site,
   error priority, state or durability order, or provider/consumer obligation is a semantic
   delta. Narrow it back to the reviewed authority or open a new batch.
5. Revise only the affected design, contract, schema, and links; do not redesign unrelated
   structures. A semantic delta receives one fresh independent Critic round scoped to that
   delta and its direct impact surface, plus primary-orchestrator review at the new Bundle
   commit. Old review remains attached to the old commit.

Meaning-preserving mechanical changes use same-batch link, mapping pointer, and status
refresh plus machine checks without reapproval.

## Exit

Require the recorded writer to reconcile the Bundle links: no orphan child, unmapped R/AC,
unresolved structure authority, or cross-unit boundary with competing definitions. For
creation or a semantic revision, run the writer/Critic loop above using the English-only
dispatch contract. Obtain primary-orchestrator review and integrate only when required by
workspace topology. Design acceptance marks the complete Bundle `approved`, not `closed`.

Before every substantive return, perform a task-specific self-check and correct defects. Do
not output a fixed `Reflection` section. Disclose only material unresolved risks that could
change the conclusion, decision, acceptance, or downstream work; otherwise omit the
disclosure. Approval, acceptance, and closure always state remaining material risks or that
none are known.
