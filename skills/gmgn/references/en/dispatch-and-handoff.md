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
2. exact authority and scope, plus baseline, candidate, or evidence anchors only when they
   already exist and are needed for this dispatch;
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

Compliance checks are triggered by a real boundary or material state change, not merely by
starting a task. Before the first write, confirm the assigned scope, preservation of existing
user changes, and one writer per workspace. Use an independent worktree or equivalent
workspace for concurrent writers; a single writer may use the current workspace. Require a
resolved baseline and expected HEAD only when a candidate will cross an agent/workspace
boundary or concurrent writing makes that identity necessary.

Freeze the simplest sufficient exact identity before review. A sole writer may use a captured
diff or content hash. An isolated handoff returns changed files, commands/results, deviations,
material unresolved risks, and the complete original-base-to-current-tip diff or ordered
commit chain; a correction commit is not a standalone candidate. Recheck an identity only
after an event or command that could have changed it. Reject wrong-workspace, stale-authority,
out-of-scope, or incomplete transferable content before review or integration. Do not repeat
unchanged checks or create evidence merely to prove that a compliance check ran.

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

Critic and Reviewer are not expected to maximize finding count, and a valid review may return
no findings. Before reporting an issue, they consider its concrete material harm if left
unresolved, whether an effective fallback already keeps the impact within accepted bounds,
and the smallest sufficient correction. Omit preference-only, speculative, low-impact, or
adequately contained issues when they do not change acceptance or the next action. Do not
propose a broader redesign when a smaller correction or effective fallback is sufficient.

The Reviewer runs the prepared deterministic local checks and returns exact commands,
environment, exit codes, limitations, and side effects together with code findings. After
accepted fixes, the primary orchestrator checks the exact fix delta and reruns affected machine
checks without another independent round.

A fresh Verifier is exceptional, not default. Classify the final candidate from the assurance
policy as `not-required` or `required:<trigger>`. Do not dispatch it while relevant Critic or
Reviewer blockers remain. When required, bind its evidence to the blocker-resolved final
candidate. It runs only the checks needed to decide the recorded trigger and stops once that
decision is established. Apply the same materiality and fallback filter to incidental
observations, but never waive a failed, skipped, timed-out, or unavailable required check
unless an accepted fallback is itself the required and successfully verified path. Repeating
identical tests at another boundary is not additional evidence.

## Role returns

- **Author** returns the assigned document candidate, self-check evidence, and deviations.
- **Critic** is read-only. It reports only contradictions or omissions that could materially
  change the decision, scope, invariants, acceptance, or downstream work; wording preferences
  and hypothetical completeness are omitted.
- **Coder** implements one Card attempt, stays inside its write set, produces discriminating
  tests, and does not absorb adjacent work. A discovered issue stays in the Card only when it
  blocks the Card outcome or a prepared required check, has no accepted effective fallback,
  and its smallest sufficient correction fits the existing authority. An isolated handoff
  returns its complete candidate range. A later fix uses a fresh Coder but does not trigger
  another Reviewer in the same task execution.
- **Reviewer** does not intentionally edit workspace files. It checks the anchored
  implementation diff for concrete correctness, regression, safety, data, or acceptance
  impact, then runs the prepared deterministic local checks. Cleanup, refactoring, and broader
  coverage are not blockers unless required to contain a material risk. It compares the frozen
  content identity after commands that could change it.
- **Verifier** is a risk-triggered final-candidate role. It leaves every tracked file unchanged
  on both pass and failure, does not broaden the assigned risk after it is decided, and returns
  exact evidence for the non-transferable or explicitly independent plan. Evidence generation
  or refresh runs before this independent check.
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
- Before waiting or acting as a Coder, the primary orchestrator scans every task in the
  confirmed execution set, not only the current card or active lane, and dispatches every
  ready, non-conflicting task that fits currently available capacity. Wait only after useful
  dispatch, local checks, state refresh, and integration work are exhausted. Use one
  longest-safe event wait. A timeout is a liveness checkpoint, not a reason to start a
  list/status/wait polling loop.
- A long-running primary session sends no heartbeat when observable state is unchanged. It
  updates only for material progress, a blocker, a decision request, or the final result.
- On Codex, use one `list_agents` snapshot only when a scheduling/capacity decision needs
  current state, a wait timed out without an unambiguous agent state, or received lifecycle
  events conflict. Do not query again until a material lifecycle event, candidate, blocker, or
  scheduling condition changes. `path_prefix` scopes the snapshot; it is not an interval.
  There is no periodic list interval.

Surface limitations never justify silently reusing an agent, widening write permissions, or
dropping independent review.
