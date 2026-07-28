---
name: run-task
description: "Use when one or more approved Task.md rows are confirmed: materialize per-card execution contracts, run every ready implementation task through bounded writer lanes, review code and deterministic local execution once, add separate final-candidate verification only for explicit risk triggers, integrate, and close. 已确认任务集后创建单卡 Card/Log、滚动并行开发、由 Reviewer 一轮完成代码审查与确定性本地检查，仅在风险触发时单独验证最终候选并关账。"
---

# Run confirmed task cards

<HARD-GATE>Every dispatched task must exist in an independently reviewed and primary-orchestrator-accepted `Task.md`, belong to the confirmed `target_milestone_id` execution set, and have valid Requirement plus Design-stage authority, including the applicable `design/Contract.md`, split contract, and structural-authority anchors when they exist. A task is ready only when its Task prerequisites are closed on the shared baseline and any declared shared-resource constraint is available. If implementation changes upstream meaning, stop only its impact cone and revise that authority.</HARD-GATE>

The primary orchestrator owns scheduling, adjudication, shared state, integration, Task status,
and per-card execution documents. It may be the Coder for one task only when no useful
implementation work can run in parallel with orchestration; it cannot replace the independent
Reviewer or any risk-triggered Verifier.

## 1. Materialize execution documents

Before the first Coder dispatch, the primary orchestrator creates exactly two files for each
confirmed task selected for this run:

1. `execution/<card_id>/Card.md` first. It is normative and contains the stable task execution
   contract: exact Task/Requirement/Design and applicable interface-Contract anchors, outcome,
   completion criterion, TDD contract, and `execution_log: [Log.md](Log.md)`. Add scope
   exclusions or an allowed path/write set only when they materially bound a delegated writer.
   Add conflict domains or runtime locks only for a real shared-resource collision. Do not copy
   the Task dependency DAG into Card.
2. `execution/<card_id>/Log.md` second. It is descriptive and contains a replaceable current
   snapshot—status, current candidate when one exists, next action, and only an active blocker
   or material workspace fact—followed by material decisions only. On closure it contains one
   final evidence summary. Routine dispatch, waiting, unchanged status, and successful
   intermediate checks are not Log entries. Keep one DocStar compatibility pointer:
   `latest_event: [Current](#current)` while active, changed to
   `[Final Evidence](#final-evidence)` when closed. It does not require generated event IDs.
3. After both files resolve, replace the Task row's `execution: none` with a real link to
   `Card.md` and set its macro status to `prepared`. Do this in the same checked candidate so
   no published Task pointer dangles.

The TDD contract states the RED test or test location, the wrong behavior it discriminates,
expected GREEN behavior, replay command or executable path, and final verification/evidence
destination. When a cross-task Contract ID applies, include the smallest provider or consumer
conformance check that proves the Card's side of the boundary. This is an implementation
refinement of approved authority, not permission to add scope. An unresolved semantic gap
returns to `write-task`, `write-design`, or the appropriate upstream skill.

Do not create `Verification.md`, `State.md`, a per-role Handoff, or one project-wide execution
log. On retries, start from the current snapshot and only the material decisions relevant to
the unresolved issue.

Run diff, link, and repository-required document checks before advancing the shared baseline
with this preparation candidate.

## 2. Build and refill the ready set

Read the compact Task rows for the confirmed execution set and the selected tasks' Card current
contracts. A ready task has every prerequisite integrated and no collision with a declared
shared-resource constraint. Recompute after every material agent return, block, integration,
or resource-capacity change. Before waiting or acting as a Coder, the primary orchestrator
scans every task in the confirmed execution set, not only the current card or active lane, and
dispatches every ready, non-conflicting task that fits currently available capacity.
Concurrency is the minimum of platform capacity, ready tasks, available writer workspaces, and
any real exclusive-resource capacity; never hard-code a count. When capacity cannot fit every
ready task, prefer the task whose closure would make the largest number of currently blocked
tasks ready; break ties by stable `card_id`. A blocked lane does not stop unrelated lanes.

The current approved interface contract is a shared working authority, not an implementation
prerequisite or a final frozen artifact. Provider and consumer tasks that share only that
Contract anchor may run in parallel with contract doubles; a real integration task may depend
on their integrated implementations.

If a task still contains separable responsibilities or cannot be independently tested, pause
it and its descendants and return it to `write-task`; a Coder cannot split authority ad hoc.

## 3. Prepare every agent dispatch

Every delegated Author, Coder, Critic, Reviewer, Verifier, or Researcher is single-use. Before
creating it, prepare a complete brief containing:

- `dispatch_id`, role, one bounded objective, and return format;
- authority and scope, plus baseline/candidate commit references only when they already exist
  and are needed for handoff, review, or integration;
- exact workspace, allowed write scope, permissions, and prohibitions;
- only the required Card/current Log context, exact applicable interface-Contract anchor, and
  relevant accepted findings or failures;
- checks to run and evidence required for return.

The brief may name registered skills or available tools required for the task. The agent may
load them through normal discovery and follow their own local resources. Put resolved workflow
decisions, including any assurance classification, directly in the brief instead of passing
another Skill's internal resource path.

Every Coder brief must require the registered `ponytail:ponytail` Skill at `full`. A Reviewer
brief must require `ponytail:ponytail-review` when its candidate contains implementation or
test-code changes. Resolve availability before the role writes or accepts that code. A missing
required Skill is a dependency blocker for that code task, not permission to copy its rules,
silently continue, or accept the code candidate.

Create a new agent without parent or earlier-agent conversation history. One return ends that
agent. A later writing attempt, separately scoped semantic or implementation change, or later
verification gets a new agent and a new brief. Critic and Reviewer are not redispatched to
recheck fixes from their completed round. Fresh identity does not mean every role is dispatched
after every change.

Before creating a delegated role that will discover source in an isolated workspace, the
primary orchestrator prepares that exact workspace. When CodeGraph indexing is
authorized, the CLI is available, and the workspace has no `.codegraph/`, it must
run `codegraph init <workspace>`
once before source discovery and confirm that a query can use the index.
A read-only role, including Reviewer, never initializes the index. Do not share an index between
workspaces. If initialization fails, record the reason and targeted-read fallback in the brief;
the failure does not block the task.

Use a commit-bound DocStar brief only when candidate handoff needs it; treat it as an index,
not authority. When the workspace has a usable CodeGraph index, use it first for source
location and code relationships, target the exact assigned workspace in every query, and treat
returned source as already read. Read checked-out files directly when the index is absent,
stale, unsupported, changed after the query, or insufficient for the decision.

## 4. Protect one writer boundary per task

Compliance checks are triggered by a real boundary or material state change, not merely by
starting a task. Before the first write, confirm Card scope, preservation of existing user
changes, and one writer per workspace. Use an isolated workspace for each concurrent writing
lane; a sole writer may use the current workspace. Require baseline/HEAD checks and record
candidate transfer facts only for concurrent work or handoff. Do not repeat an unchanged check
or create evidence for the check itself.

A Coder writes only the prepared brief's allowed scope and any Card `write_set`, never shared
Design/Contract authority, `Task.md`, Card/Log runtime state, the integration queue, or remote
state. It first establishes a discriminating RED test, loads `ponytail:ponytail` through normal
discovery at `full`, implements the smallest sufficient change without removing required
safeguards, and runs the Card checks. It does not make a check pass by removing a required
test, weakening an assertion, swallowing an error, or bypassing the real production path.
Discovery does not expand an active Card. A newly found issue belongs to it only when leaving
the issue unresolved prevents the Card outcome or a prepared required check, no accepted
effective fallback contains the impact, and the smallest sufficient correction stays inside
existing authority without adding another independently testable outcome. Otherwise omit a
low-value issue, return a materially valuable separate candidate to the primary orchestrator,
or route an authority change upstream; do not keep the Card open.

If implementation evidence contradicts an applicable interface contract, the Coder does not
negotiate or edit that authority. It returns one contract blocker containing only the observed
evidence, the smallest proposed semantic delta, and affected tasks. This existing Log decision
is sufficient; do not create a separate change-request document. Several Coders may provide
evidence, but the primary orchestrator remains the one contract authority.

Before review, a sole writer commits the complete candidate locally and returns its shortest
unambiguous commit reference. An isolated Coder handoff also returns changed files,
commands/results, deviations, material unresolved risks, and the complete
original-base-to-candidate commit range. A correction commit is not a standalone candidate.
A later correction uses a fresh Coder. Full-length commit object IDs, diff/content hashes, and
checksums are not workflow anchors.

Across the confirmed execution set, wait only after ready dispatch, primary-Coder work,
integration, state refresh, and local checks are exhausted.
Every Codex `wait_agent` call uses `agent_wait_timeout_ms = 3600000` (1 hour). Routine
progress-update cadence never shortens it. A timeout has no workflow meaning. If an agent is
known to remain `running`, immediately re-arm the same one-hour wait without inserting
`list_agents`, another status query, or a user update between unchanged timeouts. A timeout
alone is not a `list_agents` trigger. Use one
`list_agents` snapshot only when a real scheduling/capacity decision cannot be made from
received lifecycle events or those events conflict; do not query again until a material
lifecycle event or scheduling condition changes. No periodic list interval is configured or
inferred.

The primary orchestrator must not interrupt, terminate, or kill an agent merely because it has
not returned content, is silent or slow, or crossed one or more wait timeouts. Stop it only on
explicit user cancellation or concrete evidence that it has hard-failed, its scope is invalid,
or continuing is unsafe. While observable state is unchanged, do not report a wait timeout,
silence, absence of content, agent count, or `running` status. Report only material progress, a
blocker, a decision request, or the final result.

## 5. Review the final useful candidate once

Before independent review, the writer completes its self-check and required machine checks.
The primary orchestrator applies the complete isolated handoff before review; never apply only
its last correction commit. A sole-writer candidate needs no temporary copy. Resolve an
unclean application or judgment-required conflict with a fresh Coder before committing the
review content. Once review begins, do not edit that content while review roles are active.

Before integration, confirm through Git that the content being integrated matches the reviewed
commit. A different integration commit is acceptable only when the reviewed source, build
inputs, and normative task content are unchanged. Recheck identity only after an event or
command that could have changed it.

Select roles by impact:

| changed surface | required independent role |
|---|---|
| specification or document meaning | fresh Critic |
| implementation diff or test code, including deterministic local execution | fresh Reviewer |
| recorded `required:<trigger>` classification | fresh Verifier, but only after review blockers clear |
| formatting, links, pointers, or equivalent mechanical state | machine checks only |

The Critic/Reviewer rows above are evaluated only once, immediately before the task
execution's review round. An accepted finding fix remains part of that reviewed execution and
does not re-enter role selection.

Critic and Reviewer may run together when both surfaces changed. Collect every active review
return before editing. The primary orchestrator adjudicates once, rejects scope expansion,
and batches accepted blocker fixes into one revision. Each task execution uses
`review_policy: single-pass` and has at most this one Critic/Reviewer round. The primary
orchestrator checks each resolution and runs affected machine checks. This bounded resolution
check does not search for new findings; do not resume or create a Critic/Reviewer for the
fixes when they only align implementation with an existing unambiguous authority. A fix that
must invent or change authority, scope, public behavior, interface obligation, error priority,
or state order becomes a separately scoped semantic change. Put the reviewed anchor, complete
findings and rulings, exact fix delta, and post-fix checks in the final evidence summary.
Non-blocking suggestions do not reopen the candidate.
Do not keep a task open to perfect a non-blocking issue when its Card outcome works and an
effective fallback keeps the remaining impact within accepted bounds.

Critic and Reviewer do not maximize finding count; a valid review may return no findings.
Before reporting an issue, determine its concrete material harm if left unresolved, whether an
accepted effective fallback already contains that harm, and the smallest sufficient
correction. Omit preference-only, speculative, low-impact, cleanup, refactoring,
broader-coverage, or adequately contained observations that do not change acceptance or the
next action. This filter does not discard Ponytail findings: code minimality is an explicit
acceptance condition, and code that
`ponytail:ponytail-review` can delete while preserving current requirements and safeguards
violates it.

For a candidate containing implementation or test-code changes, the Reviewer loads
`ponytail:ponytail-review` through normal discovery and applies it inside this same review round
alongside correctness, regression, safety, data, and acceptance review.
The Reviewer also runs the prepared deterministic local targeted, negative, integration, and
project checks that fit its environment and checks conformance to every applicable Contract
ID. Add exploratory checks only for a concrete risk. It returns
exact commands, environment, exit codes,
limitations, and side effects together with its findings. A skipped or unavailable required
Reviewer command is not a pass. If no accepted blocker changes the candidate, this execution
evidence belongs to the final candidate. After accepted fixes, the primary orchestrator checks
the exact fix delta and reruns every affected machine check without another independent round.

## 6. Add a separate Verifier only for risk triggers

Ordinary deterministic local execution belongs to the Reviewer; Coder test output remains
supporting implementation evidence. A fresh Verifier is exceptional, not default. Classify the
final candidate as `not-required` or `required:<trigger>` using the current assurance policy
loaded through the registered `gmgn` Skill. Record the classification in Log; add the reason
and minimum verification plan only when verification is required, and include them in any
Verifier brief.

Do not dispatch a Verifier while relevant Critic or Reviewer blockers remain. When a trigger
exists, dispatch one fresh Verifier against the fixed final candidate. It runs only the
non-transferable or explicitly independent plan and returns exact
commands, environment, exit codes, limitations, and side effects. A failed, skipped,
timed-out, or unavailable required command is not a pass. It does not broaden the verification
plan after the recorded
risk is decided and applies the same materiality/fallback filter to incidental observations.
An accepted fallback satisfies verification only when it is itself the required and
successfully verified path. The Verifier must leave every tracked file unchanged on both pass
and failure. A command that generates or refreshes oracle, evidence, or attempt files is run
beforehand by the Coder or primary orchestrator, not by the Verifier.

Do not separately verify the lane candidate and then repeat the same verification after clean
mechanical integration. An additional pre-integration Verifier is allowed only when the
integration decision itself needs independent runtime evidence, an external mutable resource
or environment makes evidence non-transferable, the baseline/test inputs changed materially,
or project policy explicitly requires dual verification. Record the reason.

If risk-triggered verification fails, record it as a material decision in Log, create a fresh
Coder for the fix, check the resolution and affected machine checks without another Reviewer,
then dispatch a fresh Verifier because the required final-candidate evidence was invalidated.
If the fix expands authority, scope, or behavior beyond the reviewed task, route it as a
separately scoped change.

## 7. Integrate and close

Only the primary orchestrator writes the shared baseline, Task status, Card/Log state, and
traceability. Integration conflicts are resolved before the task's one review round. A
post-review fix uses a fresh Coder when needed, then runs affected machine
checks and any risk-triggered verification without another Reviewer.

After the final candidate clears required review and any required verification:

- write one final evidence summary in `Log.md` and set its current snapshot to closed;
- keep `Card.md` unchanged as the stable contract;
- set only the Task row's macro `status` to `closed` and keep its `execution` link;
- refresh affected AC traceability and shared-baseline/integration-queue pointers;
- run diff, links, repository checks, and then atomically advance the shared baseline.

Before advancing it, confirm that every applicable Contract ID, provider, consumer, caller,
migration, structural authority, and interacting task is inside the checked impact boundary
and that the integrated content still matches the reviewed candidate.

Material blockers and decisions plus final commit references, commands, review, and required evidence
stay in Log and are never copied back into Task. Release the lane only after the integrated
anchor and closure evidence are durable. A task is complete when its Card contract is satisfied,
not when every nearby issue discovered during the work has been resolved. Do not push unless
explicitly authorized.

## Upstream change and exit

When evidence challenges an interface contract, the primary orchestrator classifies it before
changing shared authority:

- an internal implementation issue stays in the Card and does not change Contract;
- a meaning-preserving clarification only aligns a duplicate representation with an existing
  unambiguous Contract authority, using the smallest same-batch pointer refresh and machine
  checks;
- a semantic Design/Contract change pauses only affected providers, consumers, integration
  tasks, and descendants, records the blocker in Log, and returns to `write-design`.

The Design revision produces one newly reviewed bundle commit. Refresh only affected Task/Card
anchors and tests, then resume with fresh Coders; unrelated lanes continue. Use the normal
Git commit rather than a parallel `v1`/`v2` workflow unless a current
external or coexisting-version requirement needs formal API versions. Any other evidence that
contradicts approved authority follows the same impact-cone rule and routes to its owner.
Do not mark the working Contract `closed` during run-task; `close-milestone` performs the final
implementation-to-contract reconciliation and freeze.

Remain in `run-task` while a confirmed task can become ready or a lane/integration entry is
active. When every target-Milestone task is closed on one shared baseline and AC traceability
is full, use **REQUIRED next skill: `close-milestone`**. Before every substantive return,
perform a task-specific self-check and correct defects. Do not output a fixed `Reflection`
section; disclose only unresolved material risk.
