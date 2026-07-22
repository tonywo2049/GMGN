---
locale: en
purpose: Define the minimum brief, fresh-agent lifecycle, workspace boundary, role selection, and return contract for delegated GMGN work.
upstream: [GMGN §4](../../../../GMGN.md)
downstream: [GMGN router](../../SKILL.md), [code review](code-review.md)
status: approved
type: task
nature: normative
assurance_policy: gmgn-assurance-v1
---

# Dispatch and fresh-agent contract

This contract defines required facts, not a fill-in prompt or a separate Handoff document.

## One dispatch, one fresh agent

Every delegated `author | coder | critic | reviewer | verifier | researcher` is created for
one bounded dispatch without parent or earlier-agent conversation history. One return ends the
agent. Never resume, reactivate, repurpose, or send later work to a returned agent. A later
authoring or coding attempt, separately scoped semantic or implementation change, or later
verification creates another agent from another prepared brief. Critic and Reviewer are not
redispatched to recheck fixes from their completed round.

The primary orchestrator is persistent coordination authority, not a delegated agent. It may
write specification documents directly when it holds the clearest context and may act as one
Coder only under the explicit no-parallelism rule. Those choices do not remove independent
review or required verification.

Fresh identity is not a reason to dispatch every role. Select a role only when its evidence
surface changed:

- semantic document change → Critic;
- implementation or test-code diff, including deterministic local execution → Reviewer;
- recorded trigger from the [assurance policy](assurance-policy.json) → Verifier after review
  clears;
- equivalent mechanical links, formatting, pointers, and status → machine checks.

## Prepare the brief before creating the agent

Every brief contains:

1. `dispatch_id`, role, one bounded objective, and required return shape;
2. exact authority, baseline, candidate, and relevant evidence anchors;
3. required context pointers and the named questions unresolved by that context;
4. repository/workspace facts, write permissions, allowed paths, and prohibitions;
5. prior accepted findings or failures only when they affect this dispatch;
6. checks, expected evidence, limitations to report, and the return gate.

Do not create an agent and then expand its scope through follow-up messages. A clarification may
only explain an existing brief fact; a new objective or changed candidate needs a new brief and
new agent. Do not put credentials, telemetry instructions, or unrelated project history in a
brief.

For a run-task Coder, the exact `Card.md`, current `Log.md` snapshot, and authority anchors are
the static execution input. Attach a commit-bound DocStar brief when available and verified
against the exact baseline. It is an index, not authority. Follow omitted pointers or use
targeted reads when needed; do not ingest all Task or Log history by default. Use CodeGraph only
as a locator and confirm claims against the checked-out source, diff, and tests.

## Workspace and candidate boundary

Before repository writing, require:

- `git rev-parse --show-toplevel` equals the absolute assigned workspace;
- `baseline_anchor` and `expected_head_anchor` resolve as commits;
- `HEAD` equals the expected initial or revision anchor;
- the dispatch has one write owner and explicit allowed paths.

Use an independent worktree for concurrent writers. A worktree isolates files and the index;
it does not solve semantic, interface, merge, or shared-resource conflicts. In a shared
workspace, parallel agents return proposals only and one recorded writer applies them.

A writing return identifies one immutable `candidate_anchor`, changed files, commands/results,
deviations, and material unresolved risks. Recheck the workspace and candidate on return.
Reject an unanchored, wrong-workspace, stale-authority, or out-of-scope candidate before review.

## Freeze and the single review round

The writer completes its self-check and machine checks before the candidate is frozen for
independent review. Each semantic change batch or task execution uses
`review_policy: single-pass`: at most one Critic/Reviewer round; both roles may run in that
round when both evidence surfaces changed. Once review starts, collect every active return
before editing. The primary orchestrator
adjudicates once, batches accepted blocker fixes, checks each resolution against its finding,
and runs the affected machine checks. Do not send fixes from that round to another Critic or
Reviewer. If a fix expands authority, scope, or behavior beyond the accepted findings, split
it into a separately scoped change instead of treating it as a recheck. Non-blocking
suggestions do not reopen a candidate. The final anchor records the reviewed anchor, complete
findings and rulings, exact fix delta, and post-fix checks.

The Reviewer runs the prepared deterministic local checks and returns exact commands,
environment, exit codes, limitations, and side effects together with code findings. After
accepted fixes, the primary orchestrator checks the exact fix delta and reruns affected machine
checks without another independent round.

A fresh Verifier is exceptional, not default. Classify the final candidate from the assurance
policy as `not-required` or `required:<trigger>`. Do not dispatch it while relevant Critic or
Reviewer blockers remain. When required, bind its evidence to the blocker-resolved final
candidate. Repeating identical tests at another boundary is not additional evidence.

## Role returns

- **Author** returns the assigned document candidate, self-check evidence, and deviations.
- **Critic** is read-only. Every finding gives location, evidence, impact, required correction,
  and blocker level; it does not become a second author.
- **Coder** implements one Card attempt, stays inside its write set, produces discriminating
  tests, and returns one local candidate commit. A later fix uses a fresh Coder but does not
  trigger another Reviewer in the same task execution.
- **Reviewer** does not intentionally edit workspace files. It checks the anchored
  implementation diff, spec fit, untested paths, assertion discrimination, side effects, and
  avoidable complexity, then runs the prepared deterministic local checks. It prefers a
  disposable copy for commands that write and proves HEAD, frozen diff/content hash, and
  tracked status are unchanged before returning.
- **Verifier** is a risk-triggered final-candidate role. It does not edit product meaning or
  source and returns exact evidence for the non-transferable or explicitly independent plan.
- **Researcher** distinguishes direct observation, sourced fact, and inference. Research does
  not become authority without orchestrator adjudication.

Every agent self-checks before its single return and directly corrects defects inside its
scope. Do not emit a fixed `Reflection` section. Report only unresolved material risk that
could change the decision, acceptance, or downstream work.

## Platform notes

- On Codex, create each role with no parent-context fork. Agent progress remains local; only
  blockers, rulings, candidates, findings, verification results, and completion are material
  orchestrator events.
- On Claude Code, use a new custom or general-purpose agent for every dispatch. Do not use
  resume or SendMessage to assign later work to a returned role. Agent Teams do not provide
  worktree isolation automatically.
- Wait only after useful dispatch, local checks, state refresh, and integration work are
  exhausted. Use one longest-safe event wait. A timeout is a liveness checkpoint, not a reason
  to start a list/status/wait polling loop.
- On Codex, use one `list_agents` snapshot only when a scheduling/capacity decision needs
  current state, a wait timed out without an unambiguous agent state, or received lifecycle
  events conflict. Do not query again until a material lifecycle event, candidate, blocker, or
  scheduling condition changes. `path_prefix` scopes the snapshot; it is not an interval.
  There is no periodic list interval.

Surface limitations never justify silently reusing an agent, widening write permissions, or
dropping independent review.
