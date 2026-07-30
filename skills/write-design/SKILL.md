---
name: write-design
description: "Use after Requirement review to create or change the Design-stage bundle: required implementation decisions in root Design.md, conditional module design, and design/Contract.md only for independently developed boundaries. Requirement 已过审后确定必要实现决定与按需的模块或跨单元接口权威。"
---

# Design stage: requirements → implementation decisions

<HARD-GATE>`Requirement.md` and the current approved Decision must exist. Requirement must have passed the Critic necessity gate and any required Critic review plus primary-orchestrator review. If either authority is missing or design work exposes changed upstream meaning, stop and return the issue to `gmgn` for routing instead of redefining it in Design.</HARD-GATE>

## Language, bundle, and authority

Before writing, load the registered `gmgn` Skill through normal discovery and follow its local
writing rules. Use the Requirement locale for artifact prose. Every Design-stage artifact
is normative.

`Design.md` always exists as the root Design authority and complete R/AC mapping entry. Add
architecture and module boundaries only when current R/ACs need them, and add a Bundle index
only when linked child artifacts exist. Add only the files current work needs:

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
structural authority. When children exist, `Design.md` indexes those links without duplicating
their owned meaning.

The Design-stage candidate is `Design.md` plus every linked Design-stage artifact at one Git
commit. Design acceptance marks that complete Bundle `approved`.

## Design content and completion

Design determines how to implement the reviewed Requirement. Specify every choice that can
change an R/AC, public or cross-unit data, authority source, validation order, observable
error, atomicity, recovery, security, compatibility, or resource behavior. Local replaceable
expressions that cannot change another unit's result need no Design content. If the approved
Bundle permits incompatible implementations of a shared boundary, it is incomplete.

## External solution research

For initial Design creation, derive one bounded research scope from reviewed R/ACs, applicable
D-IDs, external constraints, and the known integration environment before drafting any
Design-stage artifact. State the technical problem, hard constraints and exclusions,
comparison dimensions, evidence needed to treat a solution as mature or validated, and the
Design decision the research will support. Do not preselect architecture, modules,
interfaces, data structures, or a technical stack beyond choices already fixed by approved
authority or observed integration facts. Repository inspection may supply constraints and
later feasibility evidence, but it does not count as external research.

For a controlled revision, repeat only the affected external research when the delta changes
the researched problem, a selection constraint, the selected solution, or a time-sensitive
fact on which that selection depends. A meaning-preserving clarification does not repeat
research.

If the Owner has not already named external solutions to include or exclude, ask one plain,
self-contained question that summarizes the research scope and says that current internet
sources will be searched when none are specified. Include any Owner-named candidate in the
research without assuming that it will be selected. When the Owner names none, proceed with
internet research without further questions.

Research one to three relevant external solutions before drafting Design. Keep one when it is
the only credible candidate, compare two when a real tradeoff exists, and add a third only
when it is a distinct credible path; do not pad the set. Use primary evidence such as an
official standard, specification, documentation, reference implementation, maintainer source
and release record, production case, audit, or paper. Search snippets, rankings, stars, and
popularity alone do not prove maturity or fit. Record the checked version or date for facts
that can change.

Compare only what can change the decision: current R/AC and constraint coverage,
compatibility, security boundaries, maintenance, licensing, and adoption cost. The primary
session selects the Design-owned solution. Route a tradeoff that changes upstream meaning to
`gmgn`. If no credible external solution fits, record the search boundary and the material
reason, then design the smallest new solution instead of inventing candidates.

Carry into the owning Design artifact the selected solution or no-fit result, checked version
or date, primary evidence, and key fit or gap. Retain a rejected candidate only when omitting
it would make the current choice unclear or remove a live rollback path. Do not create
`Research.md` or store the working scope, search terms, full research report, or candidate
chronology in the Design Bundle.

The following are applicability checks, not required headings or a document template:

- Derive every decision from reviewed R/ACs, applicable D-IDs, or an explicitly sourced
  external constraint. Implement the local consequence of a project ruling without
  redefining it. Inspect the repository and real call paths for feasibility without
  redefining upstream meaning.
- Determine the smallest sufficient technical stack, dependency and build choices, source
  locations, components, responsibilities, owned data, dependency direction, and trust
  boundaries.
- Determine required call and data flows, state transitions, non-trivial algorithms, storage
  keys and indexes, transaction boundaries, migrations, concurrency, ordering, idempotency,
  failure recovery, rollback, security, performance, resource, and observability behavior
  whenever the current R/AC or real call path makes them implementation-significant.
- Map each R/AC once in root `Design.md` to the owning design structure, necessary data,
  applicable failure behavior, interface authority, and verification point. Link an
  applicable D-ID where it directly constrains that implementation result. Child artifacts
  link their applicable R/ACs without copying the complete map.
- Give each retained design element one owner and the current R/AC, D-ID, or sourced invariant
  that would fail if it were removed. Future reuse, possible scale, flexibility, or
  implementation convenience is not an owner.

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

Do not include commands, full results, candidate chronology, work status, execution history,
or closure records. Do not add formal API versions unless a current external or
coexisting-version compatibility requirement needs them.

Before return, apply this Design Ready gate:

1. The bounded external research is complete, and Design records the selected solution or
   no-fit result with primary evidence.
2. No implementation-significant question, hidden default, or unapproved parameter remains.
3. Every applicable boundary has one structure authority and a closed producer-to-state path.
4. Every R/AC and retained design element has one resolvable owner, implementation result, and
   verification point without duplicated authority.
5. Applicable schema compiles or lints, and required vectors or conformance checks reproduce.
6. Removing, reusing, making native, or directly replacing any retained structure would lose a
   current accepted outcome or safeguard.

## Writer and review-selection loop

Use the registered `gmgn` Skill's shared document-candidate and dispatch rules, and record the
Decision and Requirement commits. For a small Bundle, the primary session writes it directly.
For useful parallelism, it first creates root `Design.md` with the global architecture, module
boundaries, dependency direction, planned artifacts, and ownership; root remains the primary
session's write surface. Dispatch fresh Authors by bounded semantic module, not mechanically by
file count. Each Author writes only its declared child artifacts and self-checks their links
and local closure.

The primary session integrates provider/consumer seams, shared state, error order, and schema
references into one complete immutable Bundle candidate. When the shared necessity gate
selects Critic, a small Bundle uses one fresh Critic; a
large Bundle may use parallel fresh Critics on bounded module scopes plus one Bundle-seam
scope in the same round. Every Critic reads the same candidate commit, all returns are
collected before editing, and physical file count never determines the number of Critics.

When dispatched, Critics find any implementation-significant decision still unspecified.
Reject any public or cross-unit decision, authority, validation entry, state effect, failure,
recovery, or parameter left ambiguous. Check provider and consumer feasibility, object-phase
legality, structural authority consistency, global-versus-local rule conflicts, R/AC
traceability, and whether each separate artifact can be deleted.

Resolve accepted findings through the shared document-candidate loop. If a fix must invent or
change Design-owned meaning, it is a new semantic batch under Controlled revision, not a
recheck of the old batch. Accept only the complete Bundle at one commit as the shared Design
baseline.

## Controlled revision

1. Return meaning outside Design authority, including a changed D-ID, to `gmgn` for routing before editing.
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
   structures. A semantic delta applies the Critic necessity gate and receives any required
   fresh independent Critic round scoped to that delta and its direct impact surface, plus
   primary-orchestrator review at the new Bundle commit. Old review remains attached to the
   old commit.

Meaning-preserving mechanical changes use same-batch link, mapping pointer, and status
refresh plus machine checks without reapproval.

## Exit

Require the recorded writer to reconcile the Bundle links: no orphan child, unmapped R/AC,
unapplied implementation-relevant D-ID, unresolved structure authority, or cross-unit
boundary with competing definitions. For
creation or a semantic revision, run the writer/review-selection loop above using the
English-only dispatch contract. Obtain primary-orchestrator review and integrate only when
required by workspace topology. Design acceptance marks the complete Bundle `approved`, not `closed`.
