---
locale: en
purpose: Define the minimum brief, fresh-agent lifecycle, workspace boundary, role selection, and return contract for delegated GMGN work.
upstream: [GMGN §4](../../../../GMGN.md)
downstream: [GMGN router](../../SKILL.md), [code review](code-review.md)
status: approved
type: task
nature: normative
---

# Dispatch and agent-lifecycle contract

This contract defines required facts, not a fill-in prompt or a separate Handoff document.

## One bounded dispatch

<HARD-GATE>Before creating any delegated agent, the primary orchestrator reads this current
contract, the owning stage's role-selection rules, and the selected platform-specific GMGN
role profile. It maps the dispatch to exactly one of
`adjudicator | author | coder | critic | reviewer | verifier | researcher`; these are the only
GMGN agent roles. It does not create a generic, unnamed, or ad hoc role. A task name or
`dispatch_id` may distinguish instances but does not define another role. If none fits, route
the unresolved semantic case to an Adjudicator instead of inventing a role or deciding it in
the primary session. The brief must carry the selected profile's applicable instructions.</HARD-GATE>

Every delegated agent is created for one bounded dispatch without parent or earlier-agent
conversation history. It remains assigned until that objective completes. An authorization
or missing-information request is an interim pause, not a terminal return: the agent requests
the primary orchestrator, waits without consuming an execution slot when the platform permits,
and resumes the same dispatch when answered. No separate case-state document is required.

An Adjudicator remains assigned through owner questions and every bounded child dispatch for
its semantic case. Its `ask_owner` and `dispatch` actions are interim; only `accept`, explicit
cancellation, invalidation, or hard failure ends the case. The primary orchestrator relays the
owner's answer verbatim to that same Adjudicator. An Author likewise remains assigned through
candidate checkpoints, owner feedback, and accepted fixes while its objective and write
boundary remain unchanged. Do not keep an Author before a candidate is ready to write.

The terminal completion return retires the agent. Never resume, reactivate, repurpose, or send
later work to a retired agent. Explicit cancellation, an invalidated objective, or a hard
platform interruption or failure also ends the dispatch. If an unfinished objective remains
valid, continue with a new agent and brief; treat retained workspace changes as an unverified
draft. A later objective or separately scoped semantic or implementation change likewise
creates another agent from another prepared brief.

An initial implementation candidate has one fresh Reviewer dispatch. Accepted finding fixes do
not create another Critic or Reviewer dispatch; the active Adjudicator rules on their semantic
sufficiency, and the primary orchestrator checks candidate identity and affected machine checks.

The primary orchestrator is the persistent relay and mechanical scheduler, not a delegated
agent. It retains complete session context, associates each case with its active agents,
selects a stage from observable repository state, appends runtime facts to prepared semantic
briefs, schedules capacity, manages workspaces, runs deterministic checks, integrates accepted
candidates, and updates shared state. It does not conduct semantic owner dialogue, plan a
solution, draft a document candidate, decide Critic necessity, adjudicate findings, summarize
or reinterpret semantic messages, or act as a Coder. Those duties belong to an Adjudicator,
Author, or Coder as applicable.

## Select and report the runtime

Immediately before dispatch, the primary orchestrator reads the current `spawn_agent` schema
or equivalent platform surface to confirm that the role's required values remain supported.
On Codex, use this fixed mapping:

| Role | `model` | `reasoning_effort` |
|---|---|---|
| Adjudicator, Author, Critic, Reviewer, Verifier | `gpt-5.6-sol` | `max` |
| Coder | `gpt-5.6-terra` | `max` |
| Researcher | `gpt-5.6-terra` | `max` |

If the required combination is unavailable, report that limitation before dispatch.

Before calling Codex `spawn_agent`, state the selected `model`, `reasoning_effort`, and a
one-sentence reason in user-visible commentary. Then call it with `fork_turns: "none"` and pass
the selected `model` and `reasoning_effort`.

## Authorization and interim questions

A delegated agent requests authorization or missing information from the primary orchestrator,
not from the human owner. The primary orchestrator applies an already explicit authorization
or deterministic rule without reinterpretation. It forwards a semantic question or conflict
unchanged to the active Adjudicator; the Adjudicator either resolves it from authority or
returns `ask_owner`. The primary orchestrator relays that exact question to the owner and the
owner's answer verbatim to the same Adjudicator. A missing external-operation authorization may
be relayed directly when no semantic choice is involved.

One authorization may cover a named set of external operations against an exact target,
including push, tag, release creation, asset upload, deployment, or installation. It remains
valid for those operations and idempotent retries while the target and side-effect boundary are
unchanged. Expanding the operation set, target, or side effects requires another authorization.

An interim answer may provide authorization, missing information, or a proven meaning-
preserving refresh of an authority anchor needed for the same objective and declared write
boundary. It does not create another dispatch. A new objective or materially wider write
boundary requires a new brief and agent. A Critic, Reviewer, or Verifier may resume only while
its fixed candidate, applicable authority, scope, checks, and environment validity inputs
remain unchanged. Otherwise the fixed review surface is invalidated and requires a new brief
and agent.

Create one Adjudicator per bounded semantic case only when judgment or owner dialogue is
needed. Cases with disjoint declared authority and impact cones may run in parallel. Serialize
overlapping cases using those declared anchors and write boundaries; the primary orchestrator
does not infer a semantic dependency graph. Do not keep an Adjudicator pool.

For overlapping shared-baseline or target-Milestone scope, only one primary orchestrator may
mutate shared state and integrate candidates at a time. Other sessions remain read-only or
use an explicitly isolated, non-overlapping scope until ownership is handed over.

Fresh identity is not a reason to dispatch every role. The GMGN router selects roles from the
changed evidence surface; this contract governs only the selected dispatch.

## Prepare the brief before creating the agent

For an initial Adjudicator dispatch, the primary orchestrator copies the owner's request and
observable authority pointers into a bounded case brief without deciding or summarizing them.
For child dispatches, the Adjudicator prepares the semantic fields: objective, authority,
scope, unresolved questions, exact write boundary when applicable, checks, and return gate. A
single `dispatch` action may contain several briefs only when it declares them mutually
independent; the primary orchestrator applies ordinary capacity and workspace rules.
The primary orchestrator appends `dispatch_id`, runtime, repository, workspace, and baseline
facts without paraphrasing the semantic payload. Send one transient brief; do not create
separate semantic, runtime, Handoff, change-order, or next-action documents.

Every brief contains:

1. `dispatch_id`, role, one bounded objective, and required return shape;
2. selected `model`, `reasoning_effort`, and the concise selection reason when the platform
   exposes them;
3. exact authority and scope, plus baseline, candidate, or evidence anchors only when they
   already exist and are needed for this dispatch;
4. required context pointers and the named questions unresolved by that context;
5. repository/workspace facts, write permissions, allowed paths, archive-root exclusions, and
   prohibitions;
6. prior accepted findings or failures only when they affect this dispatch;
7. checks, expected evidence, limitations to report, and the return gate.

The archive-root exclusion applies to every delegated role, including Coder and Researcher.
Generated context and indexes must honor it. No delegated role reads, cites, or uses archived
documents as authority, context, or evidence. If active work depends on archived meaning,
return it to the owning active authority before continuing.

The brief may name registered skills or available tools required for the task. The agent may
load them through normal discovery and follow their own local resources. Put resolved workflow
decisions, including any assurance classification, directly in the brief instead of passing
another Skill's internal resource path.

When preparing a Reviewer brief, use the shared [code-review contract](code-review.md) to
resolve its complete-candidate surface, evidence, and finding gate before dispatch. Put the
applicable resolved rules in the brief; the delegated role does not need another Skill's
internal path.

Do not use an interim answer to expand the prepared objective or write boundary. Do not put
credentials, telemetry instructions, or unrelated project history in a brief.

## Workspace and candidate boundary

Compliance checks are triggered by a real boundary or material state change, not merely by
starting a task. Before the first write, confirm the assigned scope, preservation of existing
user changes, and one writer per workspace. Use an independent worktree or equivalent
workspace for concurrent writers; a single writer may use the current workspace. Require a
resolved baseline and expected HEAD only when a candidate will cross an agent/workspace
boundary or concurrent writing makes that identity necessary.

The primary orchestrator creates or assigns every isolated workspace and records enough
durable Git or platform metadata to prove that GMGN manages it and which unfinished dispatch
uses it. Never infer ownership from a path pattern alone. A workspace remains assigned while
its dispatch is active, under Review or correction, or waiting for owner or Adjudicator input.

When the dispatch becomes terminal, release the workspace and recompute the ready set. Reuse it
only for an already identified next dispatch in the same repository when the previous candidate
is integrated or ended, ordinary tracked and untracked work is clean, and it can move to the
next exact baseline without losing material evidence. Retain ignored build outputs and refresh
any workspace-local source index after rebinding. If the scheduling pass finds no explicit next
consumer, remove the exact GMGN-managed worktree; possible future reuse is not a reason to keep
it. Do not create an idle pool, TTL, LRU, or reuse score.

Never auto-remove the main workspace, a pre-existing or user-created worktree, or a project-
declared persistent workspace. Reconcile interrupted GMGN-managed workspaces on the next entry:
preserve unfinished assignments and reclaim only proven terminal, unassigned workspaces with no
material content. Use Git worktree operations for valid entries, inspect and prove exact
ownership before handling a broken entry, never delete by wildcard, and prune stale Git
metadata only after the managed directory decision. Build outputs and a local index do not
block removal after the candidate and evidence are preserved.

Commit the complete candidate locally before review and identify it in the brief with the
shortest unambiguous commit reference. An isolated handoff also returns changed files,
commands/results, deviations, material unresolved risks, and the complete
original-base-to-candidate commit range; a correction commit is not a standalone candidate.
Never put a full-length commit object ID, diff hash, content hash, archive checksum, or artifact
checksum in the brief or return as a workflow anchor. If the current workspace cannot safely
create the candidate commit, use an isolated worktree. Recheck identity only after an event or
command that could have changed it. Reject wrong-workspace, stale-authority, out-of-scope, or
incomplete transferable content before review or integration. Do not repeat unchanged checks
or create evidence merely to prove that a compliance check ran.

## Commit and hand off review candidates

The writer completes its machine checks before the candidate is committed for independent
review. Freeze the candidate while Review is active. The owning stage and code-review contract
resolve the review mode and surface; this contract requires only one fresh dispatch and one
immutable evidence boundary for each selected role.

Critic and Reviewer are not expected to maximize finding count, and a valid review may return
no findings. Report only concrete material harm with no accepted effective fallback and a
smallest sufficient correction. Omit preference-only, speculative, low-impact, or adequately
contained issues that do not change acceptance or the next action.

## Route returns without a mandatory adjudication hop

The primary orchestrator follows an explicit deterministic transition for routine Coder or
Verifier completion, machine-check results, capacity changes, and implementation Review with
`no findings`. It does not forward every return to an Adjudicator.

Forward Author and Researcher returns, every Critic return, material Reviewer findings, and any
semantic gap, authority conflict, or owner choice unchanged to the active Adjudicator for that
case. The Adjudicator returns `ask_owner`, `dispatch`, or `accept`; the primary orchestrator
executes that action without semantic rewriting. If no active Adjudicator exists for a new
semantic case, create one from the exact return and applicable authority pointers.

## Role completion

- **Adjudicator** returns interim `ask_owner` or `dispatch` actions until one terminal `accept`
  closes its semantic case.
- **Author** returns a bounded candidate checkpoint, self-check evidence, and deviations, then
  waits for owner feedback or adjudication until the objective completes.
- **Critic** and **Reviewer** are read-only and return material findings or `no findings`.
- **Coder** returns its bounded implementation candidate, checks, deviations, and unresolved
  material risk; an isolated handoff also returns the complete candidate range.
- **Verifier** returns exact evidence for its recorded final-candidate trigger and leaves
  tracked files unchanged.
- **Researcher** is an information collector only. It returns source-by-source observations
  and facts with their source, checked version or date, and missing evidence. It does not
  synthesize across sources, compare, infer, recommend, or decide a Design solution. The
  active Adjudicator owns aggregation, analysis, inference, comparison, and conclusions.

A Researcher brief defines one bounded collection question, source and recency requirements,
the facts to collect, the return fields, and the stop condition. It never asks the Researcher
for analysis or a conclusion. When it authorizes candidate discovery, it also states observable
candidate and source inclusion and exclusion conditions and a maximum of three credible
candidates. The Researcher may apply only those conditions to decide whether a candidate or
source enters the collection set. That collection decision is not cross-source comparison,
recommendation, or Design selection.

Every agent self-checks before its terminal completion return and directly corrects defects
inside its scope. An interim authorization or information request states only the blocker,
needed decision, and affected action. The stage Skill and role definition own role-specific
content. Do not emit a fixed `Reflection` section. Report only unresolved material risk that
could change the decision, acceptance, or downstream work.

## Platform notes

- On Codex, read `.codex/agents/<role>.toml`, create the role with no parent-context fork, and
  relay interim decisions to the active agent through the platform message or follow-up
  surface.
- On Claude Code, use a new custom or general-purpose agent for every dispatch. Do not use
  resume or SendMessage to assign later work to a retired role; load `agents/<role>.md` for the
  selected GMGN role. Either surface may continue an active dispatch after an interim request.
  Agent Teams do not provide worktree isolation automatically.

Surface limitations never justify silently reusing an agent, widening write permissions, or
dropping required independent review.
