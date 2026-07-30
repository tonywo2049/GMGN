---
locale: en
purpose: Define the minimum brief, fresh-agent lifecycle, workspace boundary, role selection, and return contract for delegated GMGN work.
upstream: [GMGN §4](../../../../GMGN.md)
downstream: [GMGN router](../../SKILL.md), [code review](code-review.md)
status: approved
type: task
nature: normative
---

# Dispatch and fresh-agent contract

This contract defines required facts, not a fill-in prompt or a separate Handoff document.

## One dispatch, one fresh agent

Every delegated `author | coder | critic | reviewer | verifier | researcher` is created for
one bounded dispatch without parent or earlier-agent conversation history. One return ends the
agent. Never resume, reactivate, repurpose, or send later work to a returned agent. A later
authoring or coding attempt, separately scoped semantic or implementation change, or later
verification creates another agent from another prepared brief. An initial implementation
candidate has one fresh Reviewer dispatch. Accepted finding fixes do not create another
Critic or Reviewer dispatch; the primary orchestrator checks them and runs affected machine
checks.

A platform-interrupted or hard-failed delegated agent is also retired. If the objective
remains valid, continue with a fresh agent and a new prepared brief. Treat retained workspace
changes as an unverified draft until the primary orchestrator checks the candidate boundary;
never resume the interrupted conversation.

The primary orchestrator is persistent coordination authority, not a delegated agent. It may
write specification documents directly when it holds the clearest context and may act as one
Coder only under the explicit no-parallelism rule. Those choices do not remove independent
review when required or required verification.

For overlapping shared-baseline or target-Milestone scope, only one primary orchestrator may
mutate shared state and integrate candidates at a time. Other sessions remain read-only or
use an explicitly isolated, non-overlapping scope until ownership is handed over.

Fresh identity is not a reason to dispatch every role. The GMGN router selects roles from the
changed evidence surface; this contract governs only the selected dispatch.

## Prepare the brief before creating the agent

Every brief contains:

1. `dispatch_id`, role, one bounded objective, and required return shape;
2. exact authority and scope, plus baseline, candidate, or evidence anchors only when they
   already exist and are needed for this dispatch;
3. required context pointers and the named questions unresolved by that context;
4. repository/workspace facts, write permissions, allowed paths, archive-root exclusions, and
   prohibitions;
5. prior accepted findings or failures only when they affect this dispatch;
6. checks, expected evidence, limitations to report, and the return gate.

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

Do not create an agent and then expand its scope through follow-up messages. A clarification may
only explain an existing brief fact; a new objective or changed candidate needs a new brief and
new agent. Do not put credentials, telemetry instructions, or unrelated project history in a
brief.

## Workspace and candidate boundary

Compliance checks are triggered by a real boundary or material state change, not merely by
starting a task. Before the first write, confirm the assigned scope, preservation of existing
user changes, and one writer per workspace. Use an independent worktree or equivalent
workspace for concurrent writers; a single writer may use the current workspace. Require a
resolved baseline and expected HEAD only when a candidate will cross an agent/workspace
boundary or concurrent writing makes that identity necessary.

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

## Role returns

- **Author** returns its bounded candidate, self-check evidence, and deviations.
- **Critic** and **Reviewer** are read-only and return material findings or `no findings`.
- **Coder** returns its bounded implementation candidate, checks, deviations, and unresolved
  material risk; an isolated handoff also returns the complete candidate range.
- **Verifier** returns exact evidence for its recorded final-candidate trigger and leaves
  tracked files unchanged.
- **Researcher** distinguishes direct observation, sourced fact, and inference.

Every agent self-checks before its single return and directly corrects defects inside its
scope. The stage Skill and role definition own role-specific content. Do not emit a fixed
`Reflection` section. Report only unresolved material risk that could change the decision,
acceptance, or downstream work.

## Platform notes

- On Codex, create each role with no parent-context fork.
- On Claude Code, use a new custom or general-purpose agent for every dispatch. Do not use
  resume or SendMessage to assign later work to a returned role. Agent Teams do not provide
  worktree isolation automatically.

Surface limitations never justify silently reusing an agent, widening write permissions, or
dropping required independent review.
