---
name: run-task
description: "Use when an initiated Milestone has accepted Task.md rows: materialize Card/Log execution contracts, run every ready row without separate execution-set confirmation, have the active Adjudicator directly review each fixed candidate, add risk-triggered final verification, integrate required checks, and close. Milestone 已启动且 Task.md 已接受后，无需另行确认执行集，直接调度所有 ready Task；同一 active Adjudicator 直接审查固定候选，再完成风险验证与共享基线必需检查后关账。"
---

# Run target-milestone task cards

<HARD-GATE>Every dispatched task must exist in an accepted `Task.md`, belong to the
initiated `target_milestone_id`, and have valid Requirement, Design, applicable
Contract, and structural-authority anchors. If preparing or implementing the Card still
requires a product, architecture, interface, data, error, state, recovery, security, or
compatibility decision, do not let the Coder decide it: pause only the impact cone and return
to the owning stage. Never expose an unreviewed or unchecked implementation combination as the
shared baseline. For RED-gated work, the Coder must record a valid test-only RED checkpoint
against unchanged production behavior before writing production implementation; no separate
primary-orchestrator or Adjudicator approval is required.</HARD-GATE>

The primary orchestrator owns deterministic ready-set scheduling, runtime state, workspace
management, integration, and the shared baseline. The active Adjudicator owns execution
semantics, authority gaps, direct review of fixed implementation/test candidates,
judgment-dependent assurance classification, and findings. One assigned Author writes the
Card/Log and task-state candidates for a Card,
and every implementation lane
uses a delegated Coder. The primary orchestrator does not write those candidates, act as a
Coder, take over another writer's lane, review its own candidate, or replace a required
Verifier.

Every accepted Task row for the initiated Milestone enters execution when ready. Do not ask
the owner to confirm an execution set. Ask only when excluding or deferring a ready Task would
change the accepted plan, or when an external operation lacks the shared authorization defined
by the dispatch contract.

## 1. Materialize or reopen Card and Log

Creating the Task Card and Log from an accepted Task row requires no separate human
confirmation. The Adjudicator derives the exact completion and verification meaning from
accepted authority and prepares one bounded Author brief. The primary orchestrator appends
runtime and workspace facts and dispatches the Author, which remains assigned through the
Card's preparation and closing document candidates while that objective stays unchanged.

Before the first Coder dispatch, create exactly two files for every newly materialized task:

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
3. In the same checked candidate, replace the new Task row's `execution: none` with the Card
   link and set its macro status to `prepared`.

For a reopened Task, the assigned Author reuses its existing Card and Log, keeps the execution
link, sets the macro status to `prepared`, and updates the Log current snapshot with the
unfinished work. Keep the
Card unchanged unless an owning-stage revision changed its anchors or completion contract.

The verification contract selects an executable oracle that fits the change:

- behavior, defect, algorithm, and interface work records the smallest set of authority-derived
  test cases. Each case identifies its exact approved Requirement, AC, Design, Contract, or
  Task completion-criterion anchor; scenario or input; observable expected result; and the
  wrong behavior it detects. One case may cover multiple anchors, and existing-behavior cases
  may already pass, but every changed behavior must have discriminating pre-implementation
  failure coverage;
- pure refactoring first establishes the applicable tests as GREEN, preserves their behavior
  through the refactor, and does not fabricate RED;
- configuration, migration, build, documentation, and scaffolding work uses an appropriate
  schema check, dry-run, lint, smoke test, or equivalent executable failure/success proof;
- every contract includes the replay command or executable path and final evidence
  destination;
- when a cross-task Contract ID applies, include the smallest provider or consumer
  conformance check that proves the Card's side of the boundary.

The Coder encodes those approved criteria; it does not define acceptance meaning. A behavior
test is valid only when it reaches the approved behavior or Contract boundary and distinguishes
a wrong implementation. An unrelated missing file, fixture, dependency, environment, import,
or syntax failure; an oracle copied from implementation or changed rule text; a tautological
mock; a post-hoc mutation; or mere path or text presence is not behavior RED evidence. Absence
or compile/load failure counts only when the missing public artifact is itself an approved
Contract outcome; mere path presence remains a structural check. A check whose oracle is
copied from the changed rule is structural regression, not behavior TDD evidence.

The verification contract refines approved authority; it cannot add behavior or resolve a
semantic gap. Return an unresolved gap to `write-task`, `write-design`, or the owning
upstream stage.

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

Treat safe lane saturation as a scheduling invariant. At run-task entry, after Card
preparation, and immediately after every material agent return, blocker, Review or integration
completion, authority or state refresh, or capacity change, scan the entire target-Milestone
Task set and recompute readiness. Inspect every Task, not only the lane or descendants involved
in the event. While actual platform, workspace, and exclusive-resource capacity is available,
dispatch every ready, non-conflicting task that fits it before deferrable local checks or
waiting; do not leave capacity idle. If required Review or integration
must complete before more Tasks can become ready, complete that boundary, then recompute and
refill immediately. This detection is event-driven and does not authorize lifecycle polling.
Never hard-code an agent count.

When capacity cannot fit every ready task, prefer the task whose closure would make the
largest number of currently blocked tasks ready; break ties by stable `card_id`. A blocked
lane does not stop unrelated lanes.

Provider and consumer tasks that share only an approved interface Contract may run in
parallel with contract doubles. A real integration task may depend on their integrated
implementations. If a task cannot be independently tested or still contains separable
outcomes, pause it and its descendants and return it to `write-task`; a Coder cannot split it
ad hoc.

## 3. Prepare the dispatch and runtime tools

Use the dispatch contract loaded through the registered `gmgn` Skill. The Adjudicator supplies
the current Card and Log meaning, exact Design Bundle and Contract anchors, objective, write
boundary, verification contract, checks, and return gate. The primary orchestrator adds only
the assigned workspace, baseline, real conflict domain or lock, runtime tools, and dispatch
identity. Put resolved workflow decisions directly in that single transient brief.

For RED-gated work, the initial Coder brief authorizes the complete test and production write
boundary. Require the Coder to create and record the test-only RED checkpoint before production
work, then continue directly to GREEN in the same dispatch. The Coder does not request or wait
for a separate RED approval from the primary orchestrator or Adjudicator.

Authorization and missing-information pauses follow the dispatch contract.

Apply these run-task tool requirements from this section only:

- **Ponytail:** every Coder brief requires the registered `ponytail:ponytail` Skill at `full`.
  The active Adjudicator reviewing an implementation or test-code candidate requires
  `ponytail:ponytail-review`. The primary orchestrator confirms availability before code is
  written or accepted and runs the prepared deterministic commands. Missing Ponytail blocks
  that code candidate; do not copy its rules or silently continue.
- **CodeGraph:** before the first delegated source-discovery role starts in a source
  workspace, the primary orchestrator checks that exact workspace. If the CLI is available and
  `.codegraph/` is absent, automatically run `codegraph init <workspace>` once and confirm a
  query can use it; do not ask the owner. Never share an index between workspaces, and refresh
  the local index after a reused workspace moves to a new baseline. A delegated read-only role
  does not initialize or refresh an index itself. When an index is usable, query it first for
  source location and relationships and target the exact workspace. If initialization fails
  or the index is absent, stale, unsupported, changed after the query, or insufficient, record
  the reason and use targeted file reads; this does not block the task.
- **DocStar:** use a commit-bound brief only when candidate handoff needs it. Treat it as an
  index, not authority, and follow exact pointers or read source when its evidence is
  insufficient.

## 4. Execute, freeze, and monitor writer lanes

Before the first write, confirm the Card scope, preserve existing user changes, and enforce
one writer per workspace. Concurrent writers use isolated workspaces; a sole writer may use
the current workspace. Require baseline/HEAD checks and transferable candidate facts only
when concurrency or handoff makes them material.

For RED-gated work, the Coder first changes only tests and test-only support, commits that
test-only checkpoint locally, runs the prepared target command against unchanged production
behavior, and confirms that it reaches the approved boundary and fails for the expected reason.
The RED run must expose the prepared failing coverage for every changed behavior; use targeted
cases when an earlier failure would mask a later one. If the test or failure is invalid, the
Coder corrects only test scope and repeats RED before production work. If it exposes an
authority gap, send an interim semantic decision request through the primary orchestrator to
the active Adjudicator and wait. Otherwise record the checkpoint reference, replay command,
exit code, and target failure and continue without a separate review or authorization step.

After recording RED, freeze the target tests and every helper that can affect their verdict.
The Coder implements the smallest sufficient production change and obtains GREEN with the same
target command before running required regression checks. Any result-affecting target-test
change invalidates its RED evidence. Stop production work, recreate the test-only checkpoint
against the original production baseline, record valid RED again, and then continue; never
delete, skip, weaken, bypass, or move production logic into a test to obtain GREEN.

After the first GREEN, refactor only to correct a concrete structure problem. When refactoring,
retain a pre-refactor GREEN checkpoint and rerun the same target and required regression checks;
otherwise skip refactoring without creating another checkpoint.

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
negotiate or edit that authority. It sends the primary orchestrator an interim decision request
with the observed evidence, smallest proposed semantic delta, and affected tasks. The primary
orchestrator forwards it unchanged to the active Adjudicator. Resume the same Coder only when
the adjudication preserves its objective and write boundary; otherwise
the objective is invalidated and a new brief and agent are required. The existing Log decision
is sufficient; do not create a separate change-request document.

Before Review, commit the complete candidate locally. Handoff and candidate identity follow
the dispatch contract; a correction commit is not a standalone candidate.

Across the target-Milestone Task set, wait only after ready dispatch, integration, state
refresh, and local checks are exhausted. Every Codex `wait_agent` call uses
the actual tool argument `{"timeout_ms": 600000}` (10 minutes) as a maximum wait. An agent
completion or attention event returns early and the primary session handles it immediately
without calling `list_agents`.

If the full ten minutes expires without an event, call `list_agents` once. Handle any completed or
attention-needed dispatch immediately. If the snapshot reports `running`, finish any unrelated
ready scheduling work and return to the same maximum ten-minute `wait_agent` call. Do not call
`list_agents` more than once for the same timeout.

Between lifecycle events and timeout boundaries, do not poll `list_agents`, send a message to
the agent, inspect its workspace or logs, or issue another status query merely to learn
progress. A message to an active agent must carry authorization, requested information, or
another decision permitted by the dispatch contract. Do not infer a shorter polling interval.

A running dispatch remains unfinished primary-session work. While any dispatched agent is
`running`, do not call `interrupt_agent`, end the orchestration, or return a final task result.
Call `interrupt_agent` only after explicit user cancellation or concrete evidence that the
agent hard-failed, its assigned scope became invalid, or continuing is unsafe. Silence,
slowness, missing content, wait timeouts, agent count, capacity pressure, and a primary-
session time or token budget are not such evidence. The primary session does not create or send
heartbeat, unchanged `running`, timeout, agent-count, or progress data to the user, Log,
telemetry, or another agent. Platform-native lifecycle telemetry, if any, remains out of band.
Report only material progress, a blocker, a decision request, or the final result.

## 5. Review the fixed candidate

Apply the code-review contract loaded through the registered `gmgn` Skill. Resolve an unclean
candidate application or judgment-required integration conflict before freezing the complete
candidate. The Coder commits that candidate checkpoint and waits for acceptance or an in-scope
finding; it does not retire at the checkpoint.

The primary orchestrator verifies candidate identity and, in a disposable copy or declared
generated paths, runs the prepared RED/GREEN replay, targeted checks, and required regression
commands. For a RED-gated candidate, bind the evidence to the original baseline, recorded RED
checkpoint, final candidate, authority-derived cases, target command, and any pre-refactor
GREEN checkpoint. Replay the target command at the RED checkpoint and final candidate to
confirm the expected failure and GREEN. Forward the exact command, environment, exit code,
limitation, side effect, and candidate-identity result without interpretation.

The same active Adjudicator directly reviews the complete fixed implementation/test candidate
and machine evidence under the code-review contract. It checks that the tests can reject wrong
behavior and that no result-affecting test or helper change weakened the recorded oracle. It
returns `accept` or `dispatch` containing the minimum repair brief for a material finding with
no accepted effective fallback.

Send an in-scope finding to the same still-active Coder. The Coder commits a new complete
candidate checkpoint. The primary orchestrator reruns only checks affected by the finding or
fix, and the same Adjudicator inspects the exact fix delta and affected surfaces without
rechecking unchanged work. Do not dispatch another assessment agent or a fresh Coder for that
same objective and write boundary.

If a fix changes approved behavior, scope, interface authority, objective, write boundary, or
another upstream meaning, route it to the owning stage or create a new dispatch instead of
treating it as an in-scope repair. If the Adjudicator cannot determine from existing authority
that every accepted finding is resolved, keep the Task unaccepted. Non-blocking suggestions do
not reopen an acceptable candidate. Record the reviewed anchor, finding and ruling, exact fix
delta, commands/results, and post-fix checks in final evidence.

## 6. Add a Verifier only for recorded risk

Ordinary deterministic local execution belongs to the primary orchestrator; Coder output
remains supporting evidence. The primary orchestrator applies `not-required` or
`required:<trigger>` mechanically
when the current assurance policy and recorded facts make the classification explicit. Route
only a judgment-dependent trigger to the active Adjudicator. Record the classification in Log.
Do not dispatch a Verifier before the active Adjudicator accepts the review surface.

When required, dispatch one fresh Verifier against the fixed final candidate. It runs only the
minimum non-transferable or explicitly independent plan and returns exact commands,
environment, exit codes, limitations, and side effects. A failed, skipped, timed-out, or
unavailable required command is not a pass. The Verifier leaves every tracked file unchanged
and does not broaden the plan after the trigger is decided.

Do not run the same verification before and after clean mechanical integration without a
recorded risk reason. If verification fails, record the evidence and route it through the
owning stage and dispatch contract. Any resulting repair reruns affected checks before a fresh
Verifier when the recorded trigger still applies. Route any fix that changes approved
authority or scope upstream.

## 7. Integrate, check the shared baseline, and close

Only the primary orchestrator advances the shared baseline and integrates accepted candidates.
The assigned Author writes Task status, Card/Log state, traceability, and final evidence as a
bounded document candidate from exact accepted returns; the primary orchestrator does not
draft that content. Before integration, confirm through Git that the content matches the last
reviewed candidate plus the exact adjudicated fix delta. No other source, build-input, or
normative task-content change is allowed.

The same assigned Author prepares one final integration candidate before the closing checks.
It contains the accepted implementation plus every tracked closure change:

- write one final evidence summary in `Log.md` and set its current snapshot to closed;
- keep `Card.md` unchanged as the stable contract;
- set only the Task row's macro `status` to `closed` and keep its execution link; and
- refresh affected AC traceability and shared-baseline/integration-queue pointers.

For RED-gated work, that final evidence summary records the recorded RED checkpoint, command,
exit code, and target failure; the final GREEN candidate and same-command result; and either
the pre-refactor GREEN checkpoint plus post-refactor result or that refactoring was skipped for
lack of a concrete need. Keep the RED checkpoint addressable through Review; do not create a
separate RED, GREEN, or verification document.

Commit and freeze that complete candidate without advancing the shared baseline.
Before advancing it, confirm that every applicable Contract ID, provider, consumer, caller,
migration, structural authority, and interacting task is inside the checked impact boundary.
Run every project-declared required check against that exact frozen integration candidate
before closing. When CI exists, its evidence must bind to that candidate commit. A skipped,
unavailable, unauthorized, or unexecuted required check is not a pass. If a required check
needs a push not covered by the shared external-operation authorization, keep the Task
unclosed and request it through the primary orchestrator.

After Review, required checks, and any required verification clear, atomically advance the
shared baseline to that exact checked commit. Do not modify tracked content after the final
checks. Candidate-bound evidence produced after the commit remains in its native system keyed
to that commit; do not amend Log only to copy it. If a project requires tracked evidence,
produce it before freezing the candidate and then run the final checks against the frozen
candidate.

A task is complete when its Card contract is satisfied on the checked shared baseline, not
when every nearby issue has been resolved.

After closure makes the Card's writer dispatches terminal, the primary orchestrator releases
their GMGN-managed workspaces under the shared dispatch contract. It may rebind one to an
already ready compatible task; after the refill pass, reclaim any released workspace with no
explicit next consumer.

## Upstream change and exit

An internal implementation issue stays in the Card. Before local stage routing, any changed
D-ID or new ruling selected for Decision returns to `gmgn` for `write-decision` routing,
regardless of its scope. A Task boundary or completion problem returns to `write-task`; a
design decision not recorded in Decision returns to `write-design`; changed observable
behavior or AC not recorded in Decision returns to `write-requirement`. Follow the GMGN
router's controlled-change rule and pause only affected providers, consumers, integration
tasks, and descendants. Unrelated lanes continue.

A revised authority produces a newly accepted commit. Refresh only affected Task/Card
anchors, tests, and briefs, then resume eligible active Coders under the dispatch contract. Do
not mark a working Contract `closed` during run-task; `close-milestone` performs final
reconciliation and freeze. Do not invent parallel API versions unless a current coexistence
requirement needs them.

Remain in `run-task` while a target-Milestone task can become ready or a lane/integration
entry is active. When every target-Milestone task is closed on one shared baseline and AC
traceability is full, use **REQUIRED next skill: `close-milestone`**.
