---
name: write-design
description: "Use after Requirement review to create or semantically revise the Design-stage bundle. Every creation or semantic revision first completes bounded external-solution research; root Design.md owns required implementation decisions, with module design and design/Contract.md only when needed. Requirement 已过审后创建或语义修订 Design Bundle；每次均先完成有边界的外部方案调研，再确定必要实现决定与按需的模块或跨单元接口权威。"
---

# Design stage: requirements → implementation decisions

<HARD-GATE>`Requirement.md` and the current approved Decision must exist. Requirement must have been directly reviewed and accepted by its active Adjudicator. If either authority is missing or design work exposes changed upstream meaning, stop and return the issue to `gmgn` for routing instead of redefining it in Design.</HARD-GATE>

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

<HARD-GATE>Initial Design creation and every semantic revision of the Design-stage Bundle require
the bounded external-solution research below before drafting or editing any Design-stage artifact.
For a revision, limit the research to the semantic delta and its direct impact surface; neither
delta size nor an already-clear problem waives it.</HARD-GATE>

The assigned Adjudicator derives one bounded research scope from reviewed R/ACs, applicable
D-IDs, external constraints, and the known integration environment. State the technical
problem, hard constraints and exclusions, comparison dimensions, and evidence needed to treat
a solution as mature or validated. State
observable candidate and source inclusion and exclusion conditions, and the Design decision
the research will support. Do not preselect architecture, modules,
interfaces, data structures, or a technical stack beyond choices already fixed by approved
authority or observed integration facts. Repository inspection may supply constraints and later
feasibility evidence, but it does not count as external research.

A meaning-preserving correction or mechanical change does not alter Design-owned meaning and is
outside this trigger.

If the Owner has not already named external solutions to include or exclude, the Adjudicator
asks one plain, self-contained question through the primary orchestrator's exact relay that
summarizes the research scope and says that current internet sources will be searched when
none are specified. Include any Owner-named candidate in the research without assuming that
it will be selected. When the Owner names none, proceed with authorized Researcher discovery
without further questions.

After the scope and any Owner-named candidates are fixed, the Adjudicator returns one
Researcher dispatch and the primary orchestrator adds runtime facts and sends it. The
Adjudicator does not search external sources itself. When the Owner names none, the brief
authorizes the Researcher to discover up to three credible candidates and collect source-by-source
evidence by applying the stated observable inclusion and exclusion conditions. The Researcher
may decide whether a candidate or source enters the collection set only by those conditions. The research
covers one to three relevant external solutions before Design drafting: keep one when it is the
only credible candidate, collect two when a real tradeoff exists, and add a third only when it
is a distinct credible path; do not pad the set. Use primary evidence such as an official
standard, specification, documentation, reference implementation, maintainer source and release
record, production case, audit, or paper. Search snippets, rankings, stars, and popularity alone
do not prove maturity or fit. Record the checked version or date for facts that can change.
For a software candidate, inspect source code and tests relevant to the current problem at an
explicitly checked upstream release, version, or commit; documentation, rankings, or the project
name alone are insufficient.

The same Adjudicator aggregates the returned evidence, compares only what can change the
decision, and selects the Design-owned solution: current R/AC and constraint coverage,
compatibility, security boundaries, maintenance, and adoption cost. Route a tradeoff
that changes upstream meaning to `gmgn`. If no credible external solution fits, record the
search boundary and material reason instead of inventing candidates. Choose direct new
implementation or reference-only reimplementation only when the research establishes a
material no-fit against current R/ACs or constraints.

When reusing source, keep the smallest closed code slice. Every retained upstream file, module,
symbol, helper, type, or test must be directly required by a current R/AC or be a necessary
dependency for another retained item to work correctly. Keep necessary validation, invariants,
error handling, recovery and security safeguards, unavoidable helpers and types, and the minimum
relevant tests. Exclude unrelated features, CLIs, UIs, examples, plugins, configuration,
extensibility, and future abstractions.

Carry into the owning Design artifact the selected solution or no-fit result, checked version
or date, primary evidence, and key fit or gap. Retain a rejected candidate only when omitting
it would make the current choice unclear or remove a live rollback path. Do not create
`Research.md` or store the working scope, search terms, full research report, or candidate
chronology in the Design Bundle.

When source is reused or adapted, Design records the upstream identity, checked revision, and
exact reuse boundary at the smallest stable and useful file, module, or symbol granularity,
unavoidable transitive items, local destination and adaptations, explicit exclusions, primary
source and test evidence, and verification point. Select the file, module, or symbol level that
matches the current reuse shape; all three are not required. This does not require a whole-
repository inventory or a line-by-line list. For copied, ported, or adapted source, the checked
upstream revision is the source authority. For an ordinary package dependency, Design records
the evaluated version; the manifest or lockfile owns the exact production pin.

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

Treat a known-answer test (KAT) or other vector that defines expected results as Design
authority regardless of its path or executable form. Validate its creation or revision with
the applicable reproduction or conformance check, not RED/GREEN. Use an approved, unchanged
vector as an implementation RED/GREEN oracle only under `run-task`.

Keep the Bundle `draft` while any implementation-significant decision remains unresolved.

Do not include commands, full results, candidate chronology, work status, execution history,
or closure records. Do not add formal API versions unless a current external or
coexisting-version compatibility requirement needs them.

Before return, apply this Design Ready gate:

1. The bounded external research for the initial creation or current semantic revision is
   complete, and Design records the selected solution or material no-fit plus the applicable
   evidence, revision, reuse boundary, exclusions, and verification point.
2. No implementation-significant question, hidden default, or unapproved parameter remains.
3. Every applicable boundary has one structure authority and a closed producer-to-state path.
4. Every R/AC and retained design element has one resolvable owner, implementation result, and
   verification point without duplicated authority.
5. Applicable schema compiles or lints, and required vectors or conformance checks reproduce.
6. Removing, reusing, making native, or directly replacing any retained structure would lose a
   current accepted outcome or safeguard.

## Writer and review loop

Use the registered `gmgn` Skill's shared document-candidate and dispatch rules, and record the
Decision and Requirement commits. The Adjudicator first resolves the root R/AC mapping and
selects only child artifacts justified by current R/ACs. It then dispatches one primary Author
for root `Design.md` and complete Bundle reconciliation. Add shared architecture, module
boundaries, dependency direction, and ownership only when those R/ACs require them. The Author
integrates provider/consumer seams, shared state, error order, and schema references into one
complete immutable Bundle candidate, commits it, and waits.

The primary orchestrator checks candidate identity and runs prepared deterministic checks,
then forwards the fixed complete Bundle and exact evidence to the same active Adjudicator.
That Adjudicator directly checks for any implementation-significant decision still
unspecified: public or cross-unit decisions, authority, validation entry points, state
effects, failures, recovery, and parameters; provider and consumer compatibility; object-
phase legality; structural-authority consistency; global-versus-local rule conflicts; R/AC
traceability; and whether each separate artifact can be deleted.

The Adjudicator sends an accepted in-scope finding to the same primary Author. A Design-owned
decision omitted from the fixed candidate but required by that finding remains a repair by that
Author and the same active Adjudicator while accepted or upstream authority, the prepared
objective, and the write boundary remain unchanged. Adding or changing Design-owned meaning alone
does not create a new semantic case or batch and does not restart the current research cycle. Only
a change to accepted or upstream authority or a material expansion of the prepared objective or
write boundary enters Controlled revision as a new semantic case. Accept only the complete Bundle
at one commit as the shared Design baseline.

## Controlled revision

1. Return meaning outside Design authority, including a changed D-ID, to `gmgn` for routing before editing.
2. A meaning-preserving clarification only aligns a duplicate representation with an existing
   unambiguous authority. It uses the smallest same-batch edit, affected pointer refresh, and
   machine checks without semantic reapproval.
3. For Design-stage Bundle meaning, start from the old Bundle commit and record the trigger,
   smallest semantic delta, affected Contract IDs, R-AC mappings, structures, providers,
   consumers, and proposed new commit.
4. Before editing that semantic delta, complete its bounded external research under External
   solution research.
5. Adding or changing a public type or Port, authority source, required validation call site,
   error priority, state or durability order, or provider/consumer obligation is a semantic
   delta. It opens a new batch only when it changes accepted or upstream authority or materially
   expands the prepared objective or write boundary. Otherwise keep it in the current batch,
   including when an accepted in-scope finding requires an omitted Design-owned decision; when
   that boundary is crossed, narrow the delta back to reviewed authority or open the new batch.
6. Revise only the affected design, contract, schema, and links; do not redesign unrelated
   structures. The same active Adjudicator directly reviews the fixed semantic delta and its
   direct impact surface and accepts it at the new Bundle commit or returns a minimum finding
   to the same primary Author. Old review remains attached to the old commit.
7. A compatible update is mechanical only when it does not affect behavior, security, or an
   interface; otherwise route it back through `write-design`.

Meaning-preserving mechanical changes use same-batch link, mapping pointer, and status
refresh plus machine checks without reapproval.

## Exit

Require the recorded writer to reconcile the Bundle links: no orphan child, unmapped R/AC,
unapplied implementation-relevant D-ID, unresolved structure authority, or cross-unit
boundary with competing definitions. For
creation or a semantic revision, run the writer/review loop above using the
English-only dispatch contract. Obtain Adjudicator acceptance and let the primary orchestrator
integrate only when required by workspace topology. Design acceptance marks the complete
Bundle `approved`, not `closed`.
