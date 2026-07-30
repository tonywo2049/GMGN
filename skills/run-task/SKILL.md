---
name: run-task
description: "Use when one or more approved Task.md rows are confirmed: materialize Card/Log execution contracts, refill the dependency-aware ready set, run isolated writer lanes, review each frozen candidate in at most two rounds, add risk-triggered final verification, integrate required checks, and close. 已确认任务集后创建 Card/Log、滚动并行开发；固定候选最多经过两轮审查，再完成风险验证与共享基线必需检查后关账。"
---

# Run confirmed task cards

<HARD-GATE>Every dispatched task must exist in an accepted `Task.md`, belong to the
confirmed `target_milestone_id` execution set, and have valid Requirement, Design, applicable
Contract, and structural-authority anchors. If preparing or implementing the Card still
requires a product, architecture, interface, data, error, state, recovery, security, or
compatibility decision, do not let the Coder decide it: pause only the impact cone and return
to the owning stage. Never expose an unreviewed or unchecked implementation combination as the
shared baseline.</HARD-GATE>

The primary orchestrator owns scheduling, adjudication, shared state, integration, Task
status, and per-card execution documents. It may serve as one unassigned Coder lane when
capacity remains, but it cannot take over another writer's lane, review its own candidate, or
replace a required Verifier.

## 1. Materialize Card and Log

Before the first Coder dispatch, create exactly two files for every selected task:

1. `execution/<card_id>/Card.md` is the stable normative execution contract. It contains the
   exact Task, Requirement, Design, and applicable Contract anchors; outcome; completion
   criterion; verification contract; and `execution_log: [Log.md](Log.md)`. Add an allowed
   write set, conflict domain, or runtime lock only when it materially bounds a writer or a
   real shared-resource collision. Do not copy the Task dependency graph.
2. `execution/<card_id>/Log.md` is descriptive. It contains the current status, candidate,
   next action, any active blocker or material workspace fact, material decisions, and one
   final evidence summary when closed. Routine dispatch, waiting, unchanged state, and
   successful intermediate checks are not Log entries. Its structural fields and DocStar
   compatibility pointer follow the shared
   writing rules loaded through the registered `gmgn` Skill.
3. In the same checked candidate, replace the Task row's `execution: none` with the Card link
   and set its macro status to `prepared`.

The verification contract selects an executable oracle that fits the change:

- behavior, defect, algorithm, and interface work defines a discriminating RED condition, the
  wrong behavior it detects, and the expected GREEN behavior;
- configuration, migration, build, documentation, and scaffolding work uses an appropriate
  schema check, dry-run, lint, smoke test, or equivalent executable failure/success proof;
- every contract includes the replay command or executable path and final evidence
  destination;
- when a cross-task Contract ID applies, include the smallest provider or consumer
  conformance check that proves the Card's side of the boundary.

Do not fabricate a RED test that cannot distinguish a wrong implementation. The verification
contract refines approved authority; it cannot add behavior or resolve a semantic gap. Return
an unresolved gap to `write-task`, `write-design`, or the owning upstream stage.

Do not create `Verification.md`, `State.md`, a per-role Handoff, or one project-wide execution
log. Run diff, link, and repository-required document checks before advancing the preparation
candidate.

## 2. Build and refill the ready set

A task is ready only when:

- every Task prerequisite is integrated on the shared baseline;
- its approved Contract is sufficient for independent implementation;
- its expected write set, schema, migration, manifest, registry, structural authority, and
  exclusive resources do not conflict with an active lane;
- it can be verified independently; and
- its later merge order cannot change approved semantics.

Recompute the ready set after every material agent return, blocker, integration, or capacity
change. Before waiting or acting as a Coder, scan the entire confirmed execution set and
dispatch every ready, non-conflicting task that fits actual platform, workspace, and exclusive
resource capacity. Never hard-code an agent count.

When capacity cannot fit every ready task, prefer the task whose closure would make the
largest number of currently blocked tasks ready; break ties by stable `card_id`. A blocked
lane does not stop unrelated lanes.

Provider and consumer tasks that share only an approved interface Contract may run in
parallel with contract doubles. A real integration task may depend on their integrated
implementations. If a task cannot be independently tested or still contains separable
outcomes, pause it and its descendants and return it to `write-task`; a Coder cannot split it
ad hoc.

## 3. Prepare the dispatch and runtime tools

Use the dispatch contract loaded through the registered `gmgn` Skill. A run-task brief adds only
the current Card and Log snapshot, exact Design Bundle and Contract anchors, assigned
workspace and write boundary, real conflict domain or lock, verification contract, required
runtime tools, checks, and return evidence. Put resolved workflow decisions directly in the
brief.

Apply these run-task tool requirements from this section only:

- **Ponytail:** every Coder brief requires the registered `ponytail:ponytail` Skill at `full`.
  A Reviewer brief for implementation or test-code changes requires
  `ponytail:ponytail-review`. Resolve availability before the role writes or accepts code.
  Missing Ponytail blocks that code candidate; do not copy its rules or silently continue.
- **CodeGraph:** before a delegated source-discovery role starts in an isolated workspace, if
  indexing is authorized, the CLI is available, and that workspace has no `.codegraph/`, run
  `codegraph init <workspace>` once and confirm a query can use it. Never share an index
  between workspaces. A read-only role does not initialize an index. When an index is usable,
  query it first for source location and relationships and target the exact workspace. If
  initialization fails or the index is absent, stale, unsupported, changed after the query,
  or insufficient, record the reason and use targeted file reads; this does not block the
  task.
- **DocStar:** use a commit-bound brief only when candidate handoff needs it. Treat it as an
  index, not authority, and follow exact pointers or read source when its evidence is
  insufficient.

## 4. Execute, freeze, and monitor writer lanes

Before the first write, confirm the Card scope, preserve existing user changes, and enforce
one writer per workspace. Concurrent writers use isolated workspaces; a sole writer may use
the current workspace. Require baseline/HEAD checks and transferable candidate facts only
when concurrency or handoff makes them material.

A Coder writes only the assigned scope and Card write set. It never edits shared
Design/Contract authority, `Task.md`, Card/Log runtime state, the integration queue, shared
baseline, or remote state. It follows the Card verification contract, loads required tools,
implements the smallest sufficient change without weakening required tests, validation,
error handling, security, accessibility, or the real production path, and runs the prepared
checks.

Discovery does not expand an active Card. Keep a new issue only when leaving it unresolved
prevents the Card outcome or a prepared required check, no accepted effective fallback
contains the impact, and the smallest sufficient correction stays inside existing authority
without adding another independently testable outcome. Otherwise omit a low-value issue,
return a materially valuable separate candidate, or route changed authority upstream.

If implementation evidence contradicts an applicable Contract ID, the Coder does not
negotiate or edit that authority. It returns the observed evidence, smallest proposed semantic
delta, and affected tasks. The existing Log decision is sufficient; do not create a separate
change-request document.

Before Review, commit the complete candidate locally. Handoff and candidate identity follow
the dispatch contract; a correction commit is not a standalone candidate.

Across the confirmed execution set, wait only after ready dispatch, primary-Coder work,
integration, state refresh, and local checks are exhausted. Every Codex `wait_agent` call uses
`agent_wait_timeout_ms = 3600000` (1 hour). Routine progress-update cadence never shortens it.
A timeout has no workflow meaning. If an agent is known to remain `running`, immediately
re-arm the same one-hour wait without inserting `list_agents`, another status query, or a user
update between unchanged timeouts. A timeout alone is not a `list_agents` trigger. Use one
`list_agents` snapshot only when a real scheduling/capacity decision cannot be made from
received lifecycle events or those events conflict; do not query again until a material
lifecycle event or scheduling condition changes. No periodic list interval is configured or
inferred.

Do not interrupt, terminate, or kill an agent merely because it is silent, slow, has not
returned content, or crossed one or more wait timeouts. Stop it only on explicit user
cancellation or concrete evidence that it hard-failed, its scope is invalid, or continuing is
unsafe. While observable state is unchanged, do not report a timeout, heartbeat, agent count,
or `running` status. Report only material progress, a blocker, a decision request, or the
final result.

## 5. Review the candidate at most twice

Apply the code-review contract loaded through the registered `gmgn` Skill. Resolve an
unclean candidate application or judgment-required integration conflict with a fresh Coder
before committing the content that will be reviewed. Freeze that complete candidate while
Review is active.

Create a fresh Reviewer with `review_mode: full` for the complete implementation and test-code
candidate. Collect all active Review returns before editing. The primary orchestrator
adjudicates once, rejects scope expansion, and batches accepted blocker fixes through a fresh
Coder. This first round is the only finding-discovery review.

A fix is mechanical only when it preserves behavior and its exact correction is completely
determined by existing unambiguous authority. The primary orchestrator checks that delta and
reruns affected machine checks without another Reviewer. Mechanical fixes do not consume the
second Review round.

A fix is material when it changes behavior, control flow, data, an interface, a security
boundary, concurrency, persistence, recovery, or the Review impact boundary. Batch all
accepted first-round material fixes into one cumulative fixed candidate. If a material fix is
needed after the full Review, use the one allowed second round: create another fresh Reviewer
with `review_mode: delta`. Never resume or reuse the full Reviewer or the delta Reviewer.
Never dispatch a third Reviewer for the same Task execution.

The delta brief contains the original reviewed candidate, the current fixed candidate,
accepted first-round findings and rulings, the complete cumulative fix delta, its direct
impact boundary, and affected checks. This second round verifies only that accepted
first-round findings are resolved and that the cumulative fix delta introduced no regression
in its direct impact. It does not repeat the full Review, search or report unrelated
pre-existing problems, or broaden the original surface.

The second round returns either explicit no-findings coverage or a blocker limited to an
incomplete accepted fix or a regression caused by the cumulative fix delta. On a blocker,
keep the Task unaccepted and stop this execution; do not apply another material fix and open a
third Review. Non-blocking suggestions do not reopen an acceptable candidate. Record the full
reviewed anchor, the optional delta-reviewed anchor, findings and rulings, exact fix delta,
commands/results, and post-fix checks in final evidence.

## 6. Add a Verifier only for recorded risk

Ordinary deterministic local execution belongs to Review; Coder output remains supporting
evidence. Classify the blocker-resolved final candidate as `not-required` or
`required:<trigger>` through the current assurance policy loaded through the registered
`gmgn` Skill. Record the classification in Log. Do not dispatch a Verifier while a full or
delta Review blocker remains.

When required, dispatch one fresh Verifier against the fixed final candidate. It runs only the
minimum non-transferable or explicitly independent plan and returns exact commands,
environment, exit codes, limitations, and side effects. A failed, skipped, timed-out, or
unavailable required command is not a pass. The Verifier leaves every tracked file unchanged
and does not broaden the plan after the trigger is decided.

Do not run the same verification before and after clean mechanical integration without a
recorded risk reason. If verification fails, record the decision and use a fresh Coder. A
mechanical fix reruns affected checks before a fresh Verifier. A material fix may use the
second Review round if it remains unused; batch the fix, run one fresh delta Reviewer, then a
fresh Verifier. If the second Review round was already used, keep the Task unaccepted and stop
instead of opening a third Review. Route any fix that changes approved authority or scope
upstream.

## 7. Integrate, check the shared baseline, and close

Only the primary orchestrator writes the shared baseline, Task status, Card/Log state, and
traceability. Before integration, confirm through Git that the content matches the last
accepted full or delta-reviewed candidate. A different integration commit is acceptable only
when reviewed source, build inputs, and normative task content are unchanged.

Prepare one final integration candidate before the closing checks. It contains the accepted
implementation plus every tracked closure change:

- write one final evidence summary in `Log.md` and set its current snapshot to closed;
- keep `Card.md` unchanged as the stable contract;
- set only the Task row's macro `status` to `closed` and keep its execution link; and
- refresh affected AC traceability and shared-baseline/integration-queue pointers.

Commit and freeze that complete candidate without advancing the shared baseline.
Before advancing it, confirm that every applicable Contract ID, provider, consumer, caller,
migration, structural authority, and interacting task is inside the checked impact boundary.
Run every project-declared required check against that exact frozen integration candidate
before closing. When CI exists, its evidence must bind to that candidate commit. A skipped,
unavailable, unauthorized, or unexecuted required check is not a pass. If a required check
needs a push and push authority is absent, keep the Task unclosed and record the blocker; never
push without explicit authorization.

After Review, required checks, and any required verification clear, atomically advance the
shared baseline to that exact checked commit. Do not modify tracked content after the final
checks. Candidate-bound evidence produced after the commit remains in its native system keyed
to that commit; do not amend Log only to copy it. If a project requires tracked evidence,
produce it before freezing the candidate and then run the final checks against the frozen
candidate.

A task is complete when its Card contract is satisfied on the checked shared baseline, not
when every nearby issue has been resolved.

## Upstream change and exit

An internal implementation issue stays in the Card. Before local stage routing, any missing
or changed ruling that crosses Milestones or constrains a shared project object returns to
`gmgn` for `write-decision` routing. A Task boundary or completion problem returns to
`write-task`; only a Milestone-local architecture, interface, data, validation, error, state,
recovery, security, compatibility, or resource decision returns to `write-design`; changed
observable behavior or AC returns to `write-requirement`. Follow the GMGN router's
controlled-change rule and pause only affected providers, consumers, integration tasks, and
descendants. Unrelated lanes continue.

A revised authority produces a newly accepted commit. Refresh only affected Task/Card
anchors, tests, and briefs, then resume with fresh Coders. Do not mark a working Contract
`closed` during run-task; `close-milestone` performs final reconciliation and freeze. Do not
invent parallel API versions unless a current coexistence requirement needs them.

Remain in `run-task` while a confirmed task can become ready or a lane/integration entry is
active. When every target-Milestone task is closed on one shared baseline and AC traceability
is full, use **REQUIRED next skill: `close-milestone`**.
