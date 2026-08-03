---
name: run-task
description: "Use when an initiated Milestone has accepted Task.md rows: let one Commander compute ready work and prepare one Runner per Task, execute complete Card/Log and implementation candidates, review in each Runner, add risk-triggered verification, and let a Commander integrate the checked candidate. Milestone 已启动且 Task.md 已接受后，由 Commander 计算 ready set 并为每个 Task 准备一个 Runner；Runner 完成执行与审查，Commander 按门禁集成。"
---

# Run target-milestone task cards

<HARD-GATE>Every executed Task must exist in an accepted `Task.md`, belong to the initiated
`target_milestone_id`, and have valid Requirement, Design, applicable Contract, and structural-
authority anchors. If preparing or implementing it still requires a product, architecture,
interface, data, error, state, recovery, security, or compatibility decision, do not let a
Runner or Coder decide it: pause only the impact cone and send the evidence through a
Commander, which invokes the owning Skill inside the same bounded matter. Never expose an
unreviewed or unchecked implementation combination as the shared baseline. For RED-gated work,
the Coder records a valid production-unchanged RED checkpoint against unchanged behavior
before production implementation; no separate approval of that checkpoint is required.</HARD-GATE>

This stage requires the Commander-and-Runner hub-and-spoke flow. When instructed to advance
`run-task`, the primary orchestrator does not first read and analyze the ready set. It creates
one Commander with the Owner instruction, repository, and observable entry points. The
Commander reads current authority and state, computes the dependency-aware ready set, and
returns the number of Runners to create plus each complete Runner brief. The primary
orchestrator mechanically creates those Runners without rewriting their briefs.

A Commander may directly create any defined named Agent that the current workflow assigns to
it. The normal ready-set path still leaves Runner creation and resumption to the primary
orchestrator. When an active matter needs an upstream semantic change, the same Commander
invokes the owning Skill, creates the roles that Skill requires, and returns to run-task after
the upstream candidate is accepted and integrated. Commander use in another stage follows that
stage's owning workflow; Runner-based execution remains specific to this Skill.

One Runner owns one Task and its assigned repository workspace set end to end. It directly
creates any needed Coder, Researcher, and risk-triggered Verifier. It normally reviews the
Coder candidate itself under the code-review contract. It creates an independent Critic or
Reviewer only when the Owner, applicable authority, this Skill, or the Commander brief
explicitly requires that role. The Runner never creates a Commander, Author, another Runner,
or an unnamed role.

Normal Task execution does not use an Author. The Coder creates or resumes Card/Log,
mechanically updates only its accepted Task row's execution pointer and macro status, writes
the verification contract, records applicable RED/GREEN checkpoints, implements the change,
and produces related evidence. The Runner owns Review, finding adjudication, assurance
classification, and Verifier decisions, then returns those exact closure facts to the same
Coder for Task-local recording. Neither decides upstream meaning or updates the shared
baseline.

Every accepted Task row for the initiated Milestone enters execution when ready. Do not ask
the Owner to confirm an execution set. Ask only when excluding or deferring a ready Task would
change the accepted plan, or when an external operation lacks the shared authorization defined
by the dispatch contract.

## 1. Materialize or reopen Card, Log, and Task execution state

Creating the Task Card and Log from an accepted Task row requires no separate Owner
confirmation. The Commander resolves the bounded Task objective and authority in the complete
Runner brief. The Runner prepares an exact Coder brief; the Coder creates or resumes the Card,
Log, exact Task-row execution state, verification contract, tests, implementation, and related
execution evidence in one active dispatch.

Before production implementation, create exactly two files for every newly materialized Task:

1. `execution/<card_id>/Card.md` is the stable normative execution contract. It contains the
   exact Task, Requirement, Design, and applicable Contract anchors; outcome; completion
   criterion; verification contract; and `execution_log: [Log.md](Log.md)`. Add an allowed
   write set, conflict domain, or runtime lock only when it materially bounds a writer or a
   real shared-resource collision. Do not copy the Task dependency graph.
2. `execution/<card_id>/Log.md` is descriptive. It contains the current status, candidate,
   next action, any active blocker or material workspace fact, material decisions, and one
   final evidence summary when closed. Routine dispatch, waiting, unchanged state, and
   successful intermediate checks are not Log entries. Its structural fields and DocStar
   compatibility pointer follow the writing rules loaded through the registered `gmgn` Skill.
3. The Coder replaces only the accepted Task row's `execution: none` with the Card link and
   sets its macro status to `prepared`. It does not change that row's Task meaning, spec anchor,
   or prerequisite, or any other row. This setup has no standalone preparation checkpoint,
   return, pause, or Runner confirmation. Include it in the first applicable committed
   checkpoint and continue the same dispatch.

For a reopened Task, the Coder reuses the existing Card and Log and updates the Log current
snapshot with the unfinished work, keeps the execution link, and sets only that Task row's
macro status to `prepared`. Keep Card unchanged unless an owning-stage revision changed its
anchors or completion contract.

The verification contract selects an executable oracle that fits the change:

- behavior, defect, algorithm, and interface work records the smallest set of authority-derived
  test cases. Each case identifies its exact approved Requirement, AC, Design, Contract, or
  Task completion-criterion anchor; scenario or input; observable expected result; and the
  wrong behavior it detects. One case may cover multiple anchors, and existing-behavior cases
  may already pass, but every changed behavior needs discriminating pre-implementation failure
  coverage;
- pure refactoring first establishes applicable tests as GREEN, preserves their behavior, and
  does not fabricate RED;
- configuration, migration, build, documentation, and scaffolding work uses an appropriate
  schema check, dry-run, lint, smoke test, or equivalent executable failure/success proof;
- every contract includes the replay command or executable path and final evidence destination;
  and
- when a cross-Task Contract ID applies, include the smallest provider or consumer conformance
  check that proves this Task's side of the boundary.

The Coder encodes the accepted criteria; it does not define acceptance meaning. A behavior
test is valid only when it reaches the approved behavior or Contract boundary and distinguishes
a wrong implementation. An unrelated missing file, fixture, dependency, environment, import,
or syntax failure; an oracle copied from implementation or changed rule text; a tautological
mock; a post-hoc mutation; or mere path or text presence is not behavior RED evidence. Absence
or compile/load failure counts only when the missing public artifact is itself an approved
Contract outcome. A check whose oracle is copied from the changed rule is structural
regression, not behavior TDD evidence.

The verification contract refines approved authority; it cannot add behavior or resolve a
semantic gap. Return an unresolved gap as `needs_commander` for routing to `write-task`,
`write-design`, or the owning upstream stage.

Do not create `Verification.md`, `State.md`, a per-role Handoff, or one project-wide execution
log. Run diff, link, and repository-required document checks before production work without
returning a separate preparation candidate.

## 2. Compute and refill the ready set

A Task is ready only when:

- every Task prerequisite is integrated on the shared baseline;
- its approved Contract is sufficient for independent implementation;
- its expected write set, schema, migration, manifest, registry, structural authority, and
  exclusive resources do not conflict with an active lane;
- it can be verified independently; and
- its later merge order cannot change approved semantics.

At initial entry and after a material Runner return, blocker, integration completion, authority
or state refresh, or capacity change that can affect global readiness, the primary orchestrator
creates or resumes the Commander for that bounded matter. The Commander scans the entire
target-Milestone Task set, computes readiness, resolves conflicts and priority, and returns
complete Runner briefs. The primary orchestrator performs only the requested mechanical
creation or resumption. When that bounded matter is applied, its Commander retires; an
unfinished `ask_owner`, Runner repair, or required-check wait keeps the same Commander active.

Treat safe lane saturation as a scheduling invariant. While actual platform, workspace, and
exclusive-resource capacity is available, the Commander selects every ready, non-conflicting
Task that fits before deferrable checks or waiting. If Review or integration must complete
before more Tasks can become ready, complete that boundary and recompute. Never hard-code an
agent count.

When capacity cannot fit every ready Task, prefer the Task whose closure would make the largest
number of currently blocked Tasks ready; break ties by stable `card_id`. A blocked Runner does
not stop unrelated Runners.

Provider and consumer Tasks that share only an approved interface Contract may run in parallel
with contract doubles. A real integration Task may depend on their integrated implementations.
If a Task cannot be independently tested or still contains separable outcomes, pause it and
its descendants through `needs_commander` and return it to `write-task`; a Coder cannot split
it ad hoc.

## 3. Prepare child dispatches and runtime tools

Use the dispatch contract loaded through the registered `gmgn` Skill. A Commander return
separates any caller-only mechanical workspace preparation from each complete Runner brief.
The primary orchestrator applies that preparation before dispatch. If preparation fails, it
returns the exact failure facts to the same Commander and does not start the Runner. After
success, it creates the Runner with the Commander's brief unchanged.

The Runner brief contains only this Task's changing facts and resolved selections: Task and
Card anchors when they exist, exact Design Bundle and Contract anchors, objective, every
changed repository and assigned workspace, accepted bases, stable Task branch names, shared-
remote policy, authorization, allowed write boundary, known conflict and lock facts, required
checks, expected evidence, and return gates. It may record an explicit independent-review
requirement or assurance classification, but does not copy stable Runner/Coder, RED/GREEN,
monitoring, Review, assurance-execution, or completion procedures. The Runner adds only Task-
local facts learned inside its workspace and prepares exact child briefs.

The initial Coder brief names the exact accepted Task row and limits its `Task.md` write to
`execution` and macro `status`. For RED-gated work, it authorizes the complete Task-local
document, test, and production write boundary. Require the Coder to create and record the
production-unchanged RED checkpoint before production work, then continue directly to GREEN
in the same dispatch. The Coder does not request or wait for separate RED approval from the
Runner, Commander, or primary orchestrator, and does not return an interim RED checkpoint for
confirmation.

Authorization and missing-information pauses follow the dispatch contract. The Runner resolves
Task-local facts; it returns a structured `needs_commander` event for cross-Task or shared-
authority conflict, an upstream return, an Owner decision, or anything outside its brief.

Apply these run-task tool requirements from this section only:

- **Ponytail:** every Coder brief requires the registered `ponytail:ponytail` Skill at `full`.
  The Runner reviewing an implementation or test candidate requires
  `ponytail:ponytail-review`; an explicitly required independent Reviewer uses it as well. The
  Runner confirms availability before code is written or accepted. Missing Ponytail blocks
  that code candidate; do not copy its rules or silently continue.
- **CodeGraph:** before the first child source-discovery role starts, the Runner checks its
  exact workspace. If the CLI is available and `.codegraph/` is absent, automatically run
  `codegraph init <workspace>` once and confirm a query can use it; do not ask the Owner. Never
  share an index between workspaces, and refresh it after the workspace moves to a new
  baseline. A read-only child does not initialize or refresh an index itself. When usable,
  query it first for source locations and relationships against the exact workspace. If
  initialization fails or the index is absent, stale, unsupported, changed after the query, or
  insufficient, record the reason and use targeted file reads; this does not block the Task.
- **DocStar:** use a commit-bound brief only when candidate handoff needs it. Treat it as an
  index, not authority, and follow exact pointers or read source when its evidence is
  insufficient.

## 4. Execute, freeze, and monitor writer lanes

Before the first write, confirm Task scope, preserve existing user changes, and enforce one
writer per workspace. Concurrent Runners use isolated workspaces; a sole Runner may use the
current workspace. Require baseline/HEAD checks and transferable-candidate facts only when
concurrency or handoff makes them material. Within one Runner workspace, the Runner and its
Coder write only in separate turns.

Apply the dispatch contract's Git boundary to every changed repository. The primary
orchestrator provisions or assigns the Task-named branch and writable worktree; the Runner is
their only remote writer and the Coder never pushes. Under existing shared authorization, the
Runner publishes the first coherent checkpoint and pushes later coherent checkpoints before
any pause, handoff, or pull-request update. A replacement Runner resumes the same branch and
pull request. Do not create per-Coder, per-review, per-repair, or per-commit branches or pull
requests.

For RED-gated work, the Coder first changes only Task-local execution documents, tests, and
test-only support, commits that production-unchanged checkpoint locally, runs the prepared
target command against unchanged production behavior, and confirms that it reaches the
approved boundary and fails for the expected reason. The checkpoint may include Card, Log,
and the exact Task-row execution/status update, but no production implementation.
The RED run must expose prepared failing coverage for every changed behavior; use targeted
cases when an earlier failure would mask a later one. If the test or failure is invalid, the
Coder corrects only test scope and repeats RED before production work. If it exposes an
authority gap, return exact evidence to the Runner, which emits `needs_commander` and waits.
Otherwise record the checkpoint reference, replay command, exit code, and target failure,
without pausing or returning it to the Runner, and continue directly to GREEN.

After recording RED, freeze target tests and every helper that can affect their verdict. The
Coder implements the smallest sufficient production change and obtains GREEN with the same
target command before required regression checks. Any result-affecting target-test change
invalidates RED evidence. Stop production work, recreate the production-unchanged checkpoint
against the original production baseline, record valid RED again, and then continue. Never
delete, skip, weaken, bypass, or move production logic into a test to obtain GREEN.

After the first GREEN, refactor only to correct a concrete structure problem. When
refactoring, retain a pre-refactor GREEN checkpoint and rerun the same target and required
regression checks; otherwise skip refactoring without creating another checkpoint.

A Coder writes only assigned scope and the Card write set. It may create or update Card/Log and
change only its exact accepted Task row's execution pointer and macro status. It never changes
that row's Task meaning, spec anchor, prerequisite, or any other Task row, and never edits
shared Design/Contract authority, the integration queue, shared baseline, or remote state. It
follows the Card verification contract, loads required tools, implements the smallest
sufficient change without weakening required tests, validation, error handling, security,
accessibility, or the real production path, and runs prepared checks.

Discovery does not expand an active Card. Keep a new issue only when leaving it unresolved
prevents the Card outcome or a prepared required check, no accepted effective fallback contains
the impact, and the smallest sufficient correction stays inside existing authority without
adding another independently testable outcome. Otherwise omit a low-value issue, return a
materially valuable separate candidate, or route changed authority upstream.

If implementation evidence contradicts an applicable Contract ID, the Coder does not negotiate
or edit that authority. It returns observed evidence, the smallest proposed semantic delta,
and affected Tasks to the Runner. The Runner sends that exact substantive state to the primary
orchestrator as `needs_commander`; the primary orchestrator creates or resumes the applicable
Commander. Resume the same Runner and Coder only when the result preserves objective and write
boundary. The existing Log decision is sufficient; do not create a change-request document.

Before Review, commit the complete candidate locally. Handoff and candidate identity follow
the dispatch contract; a correction commit is not a standalone candidate.

Each caller monitors only its direct agents: the Runner monitors its children, a Commander
monitors the agents it creates, and the primary orchestrator monitors Commanders and Runners.
Child invocation and routine progress never pass through the primary orchestrator. Wait only
after available substantive work at that level is exhausted. Every Codex `wait_agent` call uses
the actual tool argument `{"timeout_ms": 600000}` (10 minutes) as a maximum. An agent
completion or attention event returns early and the caller handles it immediately without
calling `list_agents` first.

If the full ten minutes expires without an event, the caller calls `list_agents` once. Handle
any completed or attention-needed dispatch immediately. If the snapshot reports `running`,
finish unrelated ready work at that level and return to the same maximum ten-minute
`wait_agent` call. Do not call `list_agents` more than once for the same timeout.

Between lifecycle events and timeout boundaries, do not poll `list_agents`, send a message,
inspect an agent workspace or logs, or issue another status query merely to learn progress. A
message to an active agent must carry authorization, requested information, or a decision
permitted by the dispatch contract. Do not infer a shorter polling interval.

A running dispatch remains unfinished work. Do not call `interrupt_agent`, end orchestration,
or return a final Task result while a required direct agent is `running`. Call
`interrupt_agent` only after explicit Owner cancellation or concrete evidence that the agent
hard-failed, its assigned scope became invalid, or continuing is unsafe. Silence, slowness,
timeouts, agent count, capacity pressure, and a session time or token budget are not such
evidence. Do not send heartbeat, unchanged `running`, timeout, agent-count, or routine progress
data to the Owner, Log, telemetry, or another agent. Platform lifecycle telemetry remains out
of band. Report only material progress, a blocker, a decision request, or the final result.

## 5. Review the fixed candidate

Apply the code-review contract loaded through the registered `gmgn` Skill. Resolve a dirty or
incomplete Task-local candidate before freezing it. The Coder commits that complete checkpoint
and waits for the Runner's acceptance or an in-scope finding; it does not retire at the
checkpoint.

The Runner verifies candidate identity and, in a disposable copy or declared generated paths,
runs the prepared RED/GREEN replay, targeted checks, and required regression commands. For a
RED-gated candidate, bind evidence to the original baseline, recorded RED checkpoint, final
candidate, authority-derived cases, target command, and any pre-refactor GREEN checkpoint.
Replay the target command at the RED checkpoint and final candidate to confirm the expected
failure and GREEN. Preserve exact command, environment, exit code, limitation, side effect,
and identity result.

The Runner directly reviews the complete fixed implementation and test candidate under the
code-review contract. It checks that tests reject wrong behavior and no result-affecting test
or helper change weakened the recorded oracle. It applies the material-harm, effective-
fallback, and smallest-sufficient-correction finding gate. Create an independent Reviewer only
when the Owner, applicable authority, this Skill, or Commander brief explicitly requires it;
the Runner adjudicates that return.

Send an accepted in-scope finding to the same still-active Coder. The Coder commits a new
complete candidate checkpoint. The Runner inspects the exact fix delta and reruns only checks
affected by the finding or fix without automatically creating another Reviewer or Coder.

If a fix changes approved behavior, scope, interface authority, Task objective, write boundary,
or other upstream meaning, the Runner returns `needs_commander` instead of treating it as an
in-scope repair. Non-blocking suggestions do not reopen an acceptable candidate. The Runner
retains the reviewed anchor, finding and ruling, exact fix delta, commands/results, and post-
fix checks as closure facts for the same Coder.

## 6. Add a Verifier only for recorded risk

Ordinary deterministic local execution belongs to the Runner; Coder output remains supporting
evidence. The Runner applies `not-required` or `required:<trigger>` mechanically when the
current assurance policy and recorded facts make classification explicit. It resolves a
Task-local judgment and returns any cross-Task, shared-authority, or Owner decision as
`needs_commander`. Keep the classification as a closure fact for the same Coder to record in
Log. Do not dispatch a Verifier before relevant Review blockers clear.

When required, the Runner creates one fresh Verifier against the fixed final candidate. It
runs only the minimum non-transferable or explicitly independent plan and returns exact
commands, environment, exit codes, limitations, and side effects to the Runner. A failed,
skipped, timed-out, or unavailable required command is not a pass. The Verifier leaves every
tracked file unchanged and does not broaden the plan after the trigger is decided.

Do not run the same verification before and after content-preserving integration without a
recorded risk reason. If verification fails, the Runner records evidence and returns the
smallest in-scope repair to the same Coder or emits `needs_commander` for changed authority or
scope. Any repair reruns affected checks before a fresh Verifier when the recorded trigger
still applies.

## 7. Prepare and integrate the final candidate

After Review blockers and any required Verifier clear, the Runner sends the exact Review,
finding, assurance, Verifier, and affected-check results to the same still-active Coder with
one closure instruction. The Coder prepares one complete final candidate containing the
accepted implementation plus every tracked Task-execution closure change:

- write one final evidence summary in `Log.md` and set its current snapshot to closed;
- keep `Card.md` unchanged as the stable contract;
- set only the Task row's macro `status` to `closed` and keep its execution link; and
- refresh only affected Task-local AC traceability and existing integration pointers allowed by
  the brief.

For RED-gated work, final evidence records the RED checkpoint, command, exit code, and target
failure; the final GREEN candidate and same-command result; and either the pre-refactor GREEN
checkpoint plus post-refactor result or that refactoring was skipped for lack of concrete need.
Keep RED addressable through Review; do not create a separate RED, GREEN, Review,
verification, or integration document.

When final evidence and the candidate are committed together, record the last addressable
implementation or verification checkpoint rather than attempting to write that commit's own
reference into `Log.md`. The pull-request head, host checks, and Commander integration return
bind the final frozen commit outside that commit's content.

The Coder commits that closure candidate locally and returns it to the Runner. The Runner
checks the exact closure delta and affected document checks. If it changes implementation,
tests, verdict-affecting helpers, Card meaning, or any Task field other than the authorized
status/execution fields, invalidate and rerun the affected evidence instead of accepting it as
closure-only. The Runner then freezes the complete candidate without updating the shared
baseline. For a repository with an authorized shared pull-request remote, it pushes the frozen
Task branch and creates or marks ready the single pull request for that repository. An earlier
Draft pull request is allowed only when required host checks or requested early collaboration
need it; continue with that same pull request. Its head must identify the frozen candidate.
For a multi-repository Task, use one branch and pull request per changed repository and return
the complete set together; do not designate one repository's pull request as a synthetic Task
closure record.

The Runner then returns one transient `ready_for_integration` event directly to the primary
orchestrator with each repository's branch, pull request when present, candidate anchor,
original baseline, complete isolated range, changed files, and workspace, plus Review and
Verifier evidence, required gates, deviations, and material risks. If a required remote
operation is not authorized, request that authorization before this event. Do not persist
`ready_for_integration` as a Task, Card, Log, or workflow state.

The primary orchestrator creates one Commander with the complete integration brief. It does
not check or integrate the candidate first. The same Commander remains assigned through any
Runner repair required by this bounded integration matter. The Commander executes exactly:

1. acquire the existing integration lock;
2. synchronize the latest shared baseline;
3. form the final candidate on that latest baseline;
4. use existing Git commit/tree mechanisms to confirm candidate identity;
5. run or verify every required gate bound to that exact candidate;
6. update the shared baseline through the repository's declared merge policy; and
7. release the integration lock.

Use a native merge queue as the existing integration lock when it provides the required
serialization; protected-branch rules and required checks remain gates rather than a lock. Do
not add a parallel lock or integration branch when the native queue already covers that
boundary. A multi-repository Task follows only its approved compatibility order and remains
incomplete until every required repository candidate is integrated and cross-repository gates
pass. Git does not make those repository updates atomic.

The Commander may inspect and modify content within the current stage, brief, authority, and
write boundary. A rebase, conflict resolution, or Commander edit that changes candidate
content invalidates the affected RED/GREEN, Review, Verifier, and upstream evidence. In that
case it releases the lock without updating the baseline, returns the exact repair and
invalidated gates to the primary orchestrator, and waits. The primary orchestrator resumes the
applicable Runner, then returns its new checkpoint to the same Commander, which restarts the
integration sequence. Only a merge commit that leaves candidate content unchanged may reuse
the original evidence.

Before updating the shared baseline, the Commander confirms that every applicable Contract ID,
provider, consumer, caller, migration, structural authority, and interacting Task is inside
the checked impact boundary. Every project-declared required check must pass against the exact
frozen integration candidate. When CI exists, its evidence binds to that candidate commit. A
skipped, unavailable, unauthorized, or unexecuted required check is not a pass. If a required
check needs a push not covered by shared external-operation authorization, keep the Task
unclosed and return the authorization request through the primary orchestrator.

After all gates clear for one repository, the Commander atomically updates that repository's
shared-baseline entry to the exact checked commit and releases the lock. Do not modify tracked
content after final checks.
Candidate-bound evidence produced after the commit remains in its native system keyed to that
commit; do not amend Log only to copy it. If tracked evidence is required, produce it before
freezing and run final checks against that frozen candidate.

The Commander returns the integrated candidate, shared-baseline anchor, exact gate results,
released-lock evidence, deviations, and unresolved material risk. The primary orchestrator
records that result mechanically and does not perform another integration or semantic review.
A Task is complete when its Card contract is satisfied on the checked shared baseline, not
when every nearby issue has been resolved.

After integration makes the Runner and Coder dispatches terminal, the primary orchestrator
releases their GMGN-managed workspace under the dispatch contract. It may rebind it only to an
already ready compatible Task named by a subsequent Commander brief; otherwise reclaim the
released workspace.

## Upstream change and exit

An internal implementation issue stays in the Card. A cross-Task or shared-authority conflict,
changed D-ID, newly selected Decision ruling, Task boundary problem, missing Design decision,
changed observable behavior or AC, Owner decision, or issue outside the Runner brief becomes
one transient `needs_commander` event with exact evidence, impact cone, requested decision,
and paused action. The primary orchestrator creates or resumes the applicable Commander and
does not decide the run-task matter itself.

The Commander identifies the owning route: changed D-ID or new Decision ruling uses
`write-decision`; Task boundary or completion meaning uses `write-task`; Design meaning not
recorded in Decision uses `write-design`; changed observable behavior or AC not recorded in
Decision uses `write-requirement`. It invokes that owning Skill inside the same Commander
dispatch, applies the stage's decision, Author, Critic, approval, and integration rules, and
directly creates every named Agent that rule selects. Upstream semantic document candidates
remain Author work. The Commander may make mechanical or other changes allowed by the active
Skill; any content change invalidates the evidence and gates that depend on it.

The primary orchestrator remains the exact Owner relay and may mechanically provision a
document workspace from the Commander's complete instruction. It does not take over planning,
finding adjudication, or integration. An Owner decision returns as `ask_owner`; the primary
orchestrator relays the question and answer unchanged to the same Commander. Pause only
affected providers, consumers, integration Tasks, and descendants; unrelated Runners continue.

With a shared pull-request remote, the Commander uses one separate authority-stage branch,
writable worktree, and pull request for the upstream candidate. The Author writes and commits
the candidate locally; the Commander publishes and integrates the accepted candidate under the
owning Skill and repository policy. Do not mix it into an affected Runner branch or pull
request. Integrate and approve that authority candidate first; then direct the primary
orchestrator to refresh the affected Runner's accepted base and resume it mechanically. Rerun
only gates invalidated by the semantic change. Task-local execution evidence and meaning-
preserving documentation remain in the Runner candidate.

A revised authority produces a newly accepted commit. Refresh only affected Task/Card anchors,
tests, and briefs, then resume an eligible existing Runner and Coder when objective and write
boundary remain unchanged; otherwise create a new dispatch. Do not mark a working Contract
`closed` during `run-task`; `close-milestone` performs final reconciliation and freeze. Do not
invent parallel API versions unless a current coexistence requirement needs them.

Remain in `run-task` while a target-Milestone Task can become ready or a Runner or integration
matter is active. When every target-Milestone Task is closed on one shared baseline and AC
traceability is full, use **REQUIRED next skill: `close-milestone`**.
