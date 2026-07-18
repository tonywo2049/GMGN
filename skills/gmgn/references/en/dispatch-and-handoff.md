---
locale: en
purpose: Define dispatch inputs, agent identity, runtime states, role boundaries, and return requirements for independently executed work.
upstream: [GMGN §4](../../../../GMGN.md)
downstream: [GMGN router](../../SKILL.md), [code review](code-review.md)
status: approved
type: task
nature: normative
---

# Dispatch and agent-lifecycle contract

中文版本：[../zh-CN/dispatch-and-handoff.md](../zh-CN/dispatch-and-handoff.md)

This is a content contract, not a fill-in prompt. Preserve the required facts while adapting
wording and order to the task and platform.

## Required dispatch facts

Every dispatch states:

- one independently acceptable objective and `node_id`;
- role: `author | coder | critic | reviewer | verifier | researcher | integrator`;
- whether to start a new agent or resume an existing `agent_ref`;
- current runtime state, baseline anchor, and candidate anchor when one exists;
- in-scope paths/behaviors, explicit exclusions, authority links, and required reading;
- the active stage skill's required content and self-check items;
- workspace permission, effort if the platform supports it, and remote-write prohibition;
- deliverables, exact verification commands or acceptance conditions, and return deadline if any.

The return must contain: artifacts/findings and replayable evidence; deviations and decisions
needed; Reflection. Reject an incomplete return without treating it as reviewed work.

## Runtime record and states

Keep `node_id`, `state`, `baseline_anchor`, `candidate_anchor`, and the relevant identity refs:
`author_ref`, `critic_ref`, `coder_ref`, `reviewer_ref`, `verifier_ref`, `integrator_ref`.
Runtime state is separate from document `status` and work-item status.

- `blocked-prerequisite`: a hard prerequisite is missing.
- `awaiting-owner-input`: an owner ruling, initiation, approval, or acceptance is required.
- `ready-to-dispatch`: inputs and authority are ready.
- `author-active`: the recorded Author is creating the artifact.
- `author-returned`: the Author returned; only completeness and boundary checks have run.
- `author-rework`: the same Author must repair an incomplete or out-of-scope return before review.
- `candidate-anchored`: the exact candidate under review has an immutable anchor.
- `critic-active`: the independent Critic is reviewing the candidate.
- `critic-returned`: findings are back with the primary orchestrator for adjudication.
- `author-revising`: the same Author is applying accepted review findings.
- `critic-rechecking`: the same Critic is checking blocker resolution against the new candidate.
- `upstream-change-pending`: this node is suspended while a controlled authority change runs.
- `acceptance-ready`: required review and checks have no unresolved blocker.
- `accepted`: the responsible gate holder accepted the anchored candidate.
- `integrating`: an Integrator is refreshing links, state, evidence pointers, and commit material.
- `node-complete`: the node's artifact, evidence, and representations agree.
- `agent-unavailable`: a recorded agent cannot be resumed; replacement rules apply.

Implementation and closure add `coder-active`, `coder-returned`, `coder-revising`,
`reviewer-active`, `reviewer-returned`, `reviewer-rechecking`, `verifier-active`, and
`verifier-returned` with the same identity semantics as the corresponding Author/Critic states.

## Identity-preserving review loop

The primary orchestrator dispatches the Author, receives the return, anchors the candidate,
then dispatches an independent Critic. Author and Critic report only to the orchestrator and
do not negotiate or edit each other's work directly.

When the orchestrator accepts a finding, resume the recorded `author_ref`; do not dispatch a
new Author. Send blocker fixes back to the recorded `critic_ref` for targeted recheck. A
non-blocking preference does not force another review round. If work exposes an upstream
problem, preserve the current Author identity in `upstream-change-pending`, complete the
controlled change, then resume that Author with the new authority anchor.

If the platform cannot resume an agent, enter `agent-unavailable` and record the reason.
Replacement is explicit, receives the complete node record, and never masquerades as the old
agent. A replacement Critic performs a full review; targeted recheck is valid only for the
same Critic. The next workflow node starts a new Author/Critic pair by default.

## Role requirements

- **Author** reads the required anchors, writes only the assigned artifact or delta, satisfies
  the stage skill's content contract, chooses its own document structure, self-checks, and
  returns changed files, candidate anchor, checks, deviations, and Reflection.
- **Critic** is read-only and independent. It checks the assigned delta plus minimum context;
  every finding includes location, evidence, impact, required correction, and blocker level.
  It does not edit, expand scope, or become a second author.
- **Coder** implements one approved card with a discriminating failing-first test, the first
  sufficient solution, scoped paths, and replayable real-path evidence.
- **Reviewer** is read-only, reviews the anchored code/combined increment, reports findings,
  and does not repair them.
- **Verifier** independently runs specified tests, startup/E2E, negative paths, and gates at
  the candidate anchor. It reports exact commands, environment, exit codes, and limitations;
  it does not change product meaning or source code.
- **Integrator** performs only accepted mechanical propagation: reciprocal links, mappings,
  state, evidence pointers, and commit preparation. It reports any semantic ambiguity instead
  of deciding it.
- **Researcher** gathers scoped evidence and labels measured facts, source-backed facts, and
  inference; it does not turn a recommendation into authority.

Use low effort for mechanical work, medium for routine execution, and high for judgment-heavy
or high-risk work when the platform exposes that control. Inputs are self-contained; never
assume an agent read the parent conversation. The relevant Reviewer, Verifier, or Integrator
replays commands and persists evidence; the orchestrator checks anchored artifacts, recorded
outputs, and scope without taking over execution. A producing agent's self-report alone is
not acceptance evidence.

## Platform adapters

- **Codex:** the installed Skill carries these role requirements in each dispatch. Project or
  user custom-agent TOML may refine a role, but plugin installation does not make a bundled
  `.codex/agents` directory project-scoped. Record the spawned agent target/thread reference
  and route follow-up instructions to it for revision or recheck.
- **Claude Code:** plugin agents live in the plugin-root `agents/` directory. Record the
  returned agent ID and resume it through the platform's agent messaging control. Do not invoke
  a new plugin agent when the node record requires the same Author, Coder, Critic, or Reviewer.

If a surface lacks steering or resume controls, apply `agent-unavailable`; do not weaken the
identity rule silently.
