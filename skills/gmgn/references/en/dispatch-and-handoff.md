---
locale: en
purpose: Define the minimum brief, agent lifecycle, workspace boundary, role selection, and return contract for delegated GMGN work.
upstream: [GMGN §4](../../../../GMGN.md)
downstream: [GMGN router](../../SKILL.md), [code review](code-review.md)
status: approved
type: task
nature: normative
---

# Dispatch and agent-lifecycle contract

This contract defines required facts, not a fill-in prompt or a separate Handoff document.

## One bounded dispatch

<HARD-GATE>Before creating an agent, its authorized caller reads this contract, the owning
stage's role-selection rules, and the selected platform-specific GMGN role profile. Map the
dispatch to exactly one of `commander | runner | author | coder | critic | reviewer | verifier |
researcher`. These are the only GMGN agent roles. A task name or `dispatch_id` distinguishes
instances but never creates a role variant. If no role fits, keep the work in the primary
session or route it to the owning stage. The brief carries the selected profile's applicable
instructions.</HARD-GATE>

Create every agent for one bounded dispatch without parent or earlier-agent conversation
history. It remains assigned until its objective completes. An authorization request,
missing-information request, Owner question, candidate checkpoint, or required wait is
interim when the objective and write boundary remain unchanged. Resume that same agent with
the exact answer or next action instead of retiring and recreating it.

The authorized caller records the platform Agent ID together with `dispatch_id`, role,
objective, and workspace assignment in existing runtime state. Follow-up messages and waits
target that exact active Agent ID. A Runner records IDs for its children; the primary
orchestrator records IDs for agents it creates. Do not replace Agent IDs with task names or
persist a new identity ledger.

A terminal completion retires the agent. Explicit cancellation, invalidation, or hard
platform failure also ends the dispatch. Never resume, repurpose, or send later work to a
retired agent. If an unfinished objective remains valid after a hard end, create a new agent
and treat retained workspace content as an unverified draft. A later objective or materially
wider write boundary requires another brief and agent.

The primary orchestrator retains the complete session context. Outside `run-task`, it routes
stages, conducts semantic Owner dialogue, analyzes evidence, makes workflow and semantic
decisions, prepares briefs, schedules agents, adjudicates Critic and Reviewer findings,
integrates accepted candidates, and updates shared state. It may perform meaning-preserving
mechanical edits. It must delegate creation or semantic revision of WhitePaper, Decision,
ROADMAP, Goal, Requirement, Design, Task, and other upstream authority, plan, or design
candidates to an independent Author. Do not create an Author when no such candidate is needed.

Only `run-task` uses the Commander-and-Runner hub-and-spoke flow defined below. Commander is
not a general stage decision-maker. The primary orchestrator does not draft a run-task
implementation candidate, and no Integrator role exists.

## Creation authority and lifecycle

Outside `run-task`, the primary orchestrator creates any needed Author, Researcher, Critic,
Reviewer, or Verifier and receives its return directly. The primary orchestrator analyzes a
Researcher return and adjudicates Critic or Reviewer findings.

Inside `run-task`:

- only the primary orchestrator creates, resumes, and retires a Commander;
- only the primary orchestrator mechanically creates or resumes a Runner from a Commander's
  complete brief;
- a Commander creates no agent;
- one Runner owns one Task and its repository workspace set end to end;
- a Runner may directly create its Coder, Researcher, and risk-triggered Verifier; and
- a Runner may create a Critic or Reviewer only when the Owner, applicable authority, current
  workflow rule, or Commander brief explicitly requires that independent role.

A Runner never creates a Commander, Author, another Runner, or any unnamed role. Parallel
Runners do not communicate directly. Their child-agent calls and routine lifecycle handling
stay inside the Runner; only structured substantive state or results go directly to the
primary orchestrator.

One Commander owns one bounded global run-task matter. `ask_owner` and waiting for a Runner
repair or required check are interim. Resume the same Commander until that matter is applied,
cancelled, invalidated, or hard-fails. A later matter gets a new Commander. Do not keep a
Commander pool or assign role variants by scheduling, conflict, or integration use.

An Author or Coder remains assigned after a candidate checkpoint when an in-scope finding may
return. Use that same writer while objective and write boundary remain unchanged. Critic,
Reviewer, and Verifier returns are terminal for their selected fixed surface; dispatch them
again only when the owning workflow requires a new fixed-candidate check.

## Select and report the runtime

Immediately before dispatch, the authorized caller reads the current `spawn_agent` schema or
equivalent platform surface to confirm that the role's required values remain supported. On
Codex, use this fixed mapping:

| Role | `model` | `reasoning_effort` |
|---|---|---|
| Commander, Runner, Author, Critic, Reviewer, Verifier | `gpt-5.6-sol` | `max` |
| Coder, Researcher | `gpt-5.6-terra` | `max` |

If the required combination is unavailable, report that limitation before dispatch.

Before calling Codex `spawn_agent`, state the selected `model`, `reasoning_effort`, and a
one-sentence reason in user-visible commentary. Then call it with `fork_turns: "none"` and
pass the selected `model` and `reasoning_effort`.

## Authorization and interim questions

A delegated agent requests authorization or missing information from its authorized caller,
not directly from the human Owner. Outside `run-task`, the primary orchestrator decides within
existing authority or obtains Owner input. Inside `run-task`, a child returns to its Runner;
the Runner resolves in-Task facts or sends a structured `needs_commander` event to the primary
orchestrator for a cross-Task conflict, upstream return, Owner decision, or issue outside its
brief.

When a Commander returns `ask_owner`, the primary orchestrator relays that question unchanged
and returns the Owner's answer verbatim to the same Commander. A missing external-operation
authorization may be asked directly when no semantic choice is involved.

One authorization may cover a named set of external operations against an exact target,
including push, tag, release creation, asset upload, deployment, or installation. It remains
valid for those operations and idempotent retries while the target and side-effect boundary
are unchanged. Expanding the operation set, target, or side effects requires another
authorization.

An interim answer may provide authorization, missing information, or a proven meaning-
preserving authority-anchor refresh needed for the same objective and declared write
boundary. It does not create another dispatch. A Critic, Reviewer, or Verifier may resume only
while its fixed candidate, applicable authority, scope, checks, and environment-validity
inputs remain unchanged. Otherwise the surface is invalid and needs a new brief and agent.

For overlapping shared-baseline or target-Milestone scope, only one primary orchestrator owns
shared-state mutation at a time. Outside `run-task`, that primary orchestrator integrates.
Inside `run-task`, only its current Commander holding the existing integration lock may change
the shared baseline. Other sessions and Runners stay read-only toward that baseline or use
their assigned isolated, non-overlapping workspaces.

Fresh identity is not a reason to dispatch every role. The router and owning stage select only
roles needed by the changed evidence surface.

## Prepare the brief before creating the agent

Every brief contains:

1. `dispatch_id`, role, one bounded objective, and required return shape; the caller records
   the returned platform Agent ID after creation;
2. selected `model`, `reasoning_effort`, and the concise selection reason when exposed;
3. exact authority and scope, plus baseline, candidate, or evidence anchors only when they
   exist and matter;
4. required context pointers and named questions unresolved by that context;
5. repository and workspace facts, write permissions, allowed paths, archive-root exclusions,
   and prohibitions;
6. prior accepted findings or failures only when they affect this dispatch;
7. checks, expected evidence, limitations to report, and the return gate.

The archive-root exclusion applies to every role. Generated context and indexes honor it. No
agent reads, cites, or uses archived documents as active authority, context, or evidence. If
current work needs archived meaning, return it to the owning active authority first.

The brief may name registered skills or available tools required for the task. Put resolved
workflow decisions, including an assurance classification, directly in the brief instead of
passing another Skill's internal resource path. Do not put credentials, telemetry
instructions, unrelated history, or another protocol document in the brief.

For an upstream semantic document candidate, the primary orchestrator resolves the objective,
authority, accepted Owner meaning, exact write boundary, checks, and return gate before
creating the Author. The Author does not decide unresolved meaning.

For initial `run-task` entry, the primary orchestrator does not read the Task set to compute
readiness first. It creates one Commander with the Owner instruction, repository, and
observable entry points. The Commander reads current authority and state, computes the full
ready set, and returns the number of Runners plus each complete Runner brief. The primary
orchestrator creates exactly those Runners without summarizing, rewriting, or semantically
augmenting the briefs. The Commander, not the primary orchestrator, owns this ready-set
analysis.

For implementation and test work, resolve the complete-candidate surface, verification
contract, deterministic commands, evidence, and finding gate under the shared
[code-review contract](code-review.md) before Coder dispatch. A Runner prepares that Coder
brief and receives its checkpoint directly.

## Workspace and candidate boundary

Compliance checks are triggered by a real boundary or material state change, not merely by
starting a task. Before the first write, confirm assigned scope, preservation of user changes,
and one writer per workspace. Use an independent worktree or equivalent workspace for
concurrent writers; a single writer may use the current workspace. Require a resolved
baseline and expected HEAD only when concurrency or candidate handoff makes identity material.

The primary orchestrator mechanically creates or assigns each isolated Runner or document
workspace from the accepted brief and records enough durable Git or platform metadata to
prove which unfinished dispatch owns it. Never infer ownership from a path pattern. A Runner
owns its Task workspace while its dispatch is active, under Review or correction, waiting on
a Commander, or queued for integration. Its child writers use that same assignment one at a
time.

For each repository that a Git-backed Task changes, keep one Task-named branch, at most one
active pull request, and at most one writable worktree. The branch and pull request belong to
the Task-repository change, not to an agent identity. The current Runner owns them and is the
only remote writer; its Coder changes the same workspace in separate turns and never writes
remote state. If a Runner hard-fails or is replaced, its successor treats retained content as
unverified and resumes the same branch and pull request instead of creating another pair. Name
the branch with a stable Task or Card ID, never a transient Agent ID.

For a multi-repository Task, `shared baseline` means the recorded set containing one current
integrated commit per participating repository. Each repository update is atomic by itself;
the set is not a cross-repository transaction.

When shared external-operation authorization covers the exact repository and Task branch,
the Runner publishes the first coherent checkpoint and pushes later coherent checkpoints
before pausing, handing off, or updating a pull request. Do not leave a reported recoverable
checkpoint only in local storage. A pull request is one integration surface for the complete
Task-repository candidate, not one surface per commit or repair. `run-task` owns its exact
creation and ready timing.

Do not create a branch or writable worktree merely because a role is independent. A no-edit
Critic, Researcher, Reviewer, or Verifier reads the fixed Git object or existing frozen
workspace when that is sufficient. If an assigned command requires an isolated checkout, use
a disposable detached worktree or copy without a branch, keep tracked content unchanged, and
remove it after the check.

When a dispatch becomes terminal, release its workspace. Reuse it only for an already
identified next dispatch in the same repository when the previous candidate is integrated or
ended, ordinary tracked and untracked work is clean, and it can move to the next exact
baseline without losing material evidence. Retain ignored build outputs and refresh a local
source index after rebinding. If the scheduling pass finds no explicit next consumer, remove
the exact GMGN-managed worktree. Possible future reuse does not justify an idle pool, TTL,
LRU, or reuse score.

After verified integration, remove the managed worktree and delete its no-longer-needed local
Task branch only after native Git or host evidence proves the candidate integrated. Let the
host close the merged pull request; delete its remote branch only when the repository policy
and shared authorization permit it. For cancellation, preserve every material checkpoint
first and close or retain the pull request according to the explicit disposition; never delete
an unmerged branch with material work merely to release a workspace.

Never auto-remove the main workspace, a pre-existing or user-created worktree, or a project-
declared persistent workspace. On the next entry, preserve unfinished assignments and reclaim
only proven terminal, unassigned managed workspaces with no material content. Use Git
worktree operations for valid entries, prove exact ownership before handling a broken entry,
never delete by wildcard, and prune stale Git metadata only after the managed-directory
decision. Build outputs and a local index do not block removal after candidate and evidence
preservation.

Commit the complete candidate locally before independent review or cross-workspace handoff and
identify it with the shortest unambiguous commit reference. An isolated handoff also returns
changed files, commands and results, deviations, material unresolved risks, and the complete
original-base-to-candidate commit range; a correction commit is not a standalone candidate.
Never use a full-length commit object ID, diff hash, content hash, archive checksum, or
artifact checksum as a workflow anchor. If the current workspace cannot safely create the
candidate commit, use an isolated worktree.

Recheck identity only after an event or command that could change it. Reject a wrong
workspace, stale authority, out-of-scope content, or incomplete transferable candidate before
review or integration. Do not repeat unchanged checks or create evidence merely to prove that
a compliance check ran.

## Review candidate boundaries

The writer completes self-checks before committing a fixed candidate. Self-checks, tests, and
the writer's explanation are evidence, not review or acceptance. Freeze the candidate while a
selected independent Critic or Reviewer works.

For upstream semantic documents, the primary orchestrator applies the router's Critic
necessity gate. Meaning-preserving mechanical edits require machine checks, not a Critic. Each
selected Critic receives one immutable semantic surface and returns to the primary
orchestrator, which adjudicates findings and sends an accepted in-scope repair to the same
Author. A semantic batch has at most one Critic round; after a fix, the primary orchestrator
checks the exact repair and affected machine evidence.

For implementation and test candidates, the Runner normally performs the code-review
contract itself. An independent Reviewer is used only when explicitly required by the Owner,
authority, current workflow, or Commander brief. In either path, an accepted in-scope finding
returns to the same Coder, which commits a new complete candidate. The Runner checks the exact
repair and reruns affected commands without automatically creating another Reviewer.

Critic and Reviewer do not maximize finding count. A valid return may contain no findings.
Report an issue only when leaving it unresolved creates concrete material harm, no accepted
effective fallback contains that harm, and the smallest sufficient correction can be stated.

## Run-task returns and integration

A Runner sends only substantive structured status and results to the primary orchestrator.
`needs_commander` and `ready_for_integration` are transient events, not Task, Card, Log, or
workflow states. The primary orchestrator forwards a `needs_commander` payload unchanged to
the applicable active Commander or creates a new Commander for the bounded matter. It does
not adjudicate the run-task issue itself.

When a Runner reports `ready_for_integration`, the primary orchestrator creates one Commander
with the complete integration brief. That Commander directly checks the candidate, makes any
permitted change, verifies it, and updates the shared baseline under `run-task`. If it requires
a Runner repair, the primary orchestrator resumes the applicable Runner and later returns the
new checkpoint to that same still-active Commander. After Commander completion, the primary
orchestrator records the result mechanically; it does not perform a second integration or
semantic review.

## Role completion

- **Commander** returns complete Runner briefs, an interim Owner or Runner action, or one
  applied bounded result. Interim waits keep the same Commander active.
- **Runner** returns substantive Task state, `needs_commander`, `ready_for_integration`, or its
  integrated completion result; child dispatch detail stays inside the Runner.
- **Author** returns its committed candidate checkpoint, self-check evidence, deviations, and
  material risk, then remains available for an in-scope fix until the objective ends.
- **Coder** returns its committed complete candidate checkpoint and evidence to its Runner,
  then remains available for an in-scope fix until the Task candidate is accepted or invalid.
- **Critic** and **Reviewer** are read-only and return material findings or explicit no-
  findings coverage for their fixed surface.
- **Verifier** returns exact evidence for its recorded fixed-candidate trigger and leaves
  tracked files unchanged.
- **Researcher** returns source-by-source observations, checked versions or dates, missing
  evidence, and limitations. It does not synthesize, compare, infer, recommend, or select.
  Its caller owns analysis and conclusions.

A Researcher brief defines one bounded collection question, source and recency requirements,
facts to collect, return fields, and a stop condition. Candidate discovery also needs
observable source and candidate inclusion/exclusion conditions and at most three credible
candidates. Applying those conditions to the collection set is not cross-source comparison or
solution selection.

Every agent self-checks before a terminal completion and directly corrects defects inside its
scope. An interim request states only the blocker, needed decision, and affected action. Do
not emit a fixed `Reflection` section. Report only unresolved material risk that could change
the decision, acceptance, or downstream work.

## Platform notes

- On Codex, read `.codex/agents/<role>.toml` when that profile exists, create the role without
  a parent-context fork, and continue an unfinished dispatch through the platform message or
  follow-up surface.
- On Claude Code, use a new custom or general-purpose agent for every new dispatch. Do not use
  resume or SendMessage for later work after a role retires; load `agents/<role>.md` for the
  selected role. Either surface may continue an active dispatch after an interim request.
  Agent Teams do not provide worktree isolation automatically.

Surface limitations never justify silently reusing a retired agent, widening write
permissions, inventing a role variant, or dropping a required independent check.
