---
name: gmgn
description: "Use first to route workflow-driven project work: new projects, product ideas, research, feature development, bug fixes, refactors, WhitePaper, ROADMAP, PRD, requirements, design, task docs, coding delegation, launch, release, acceptance, or closure. 凡要按流程或 workflow 推进研发、调研、功能开发、修 bug、重构、写白皮书/ROADMAP/PRD/需求/设计/任务、派活写代码、上线发布、验收关账，或用户说按 GMGN/按流程办/下一步做什么时使用。"
---

# GMGN router: repository state → next stage

Use this skill to locate the stage, then invoke the specialized skill. The normative method
is [GMGN.md](../../GMGN.md); Chinese is [GMGN.zh-CN.md](../../GMGN.zh-CN.md).

## Language and contract

Infer `en` or `zh-CN` from approved project documents, then the user's language. Keep the
machine contract English. Load the matching layout-free writing contract when writing documents:
[English](references/en/writing-contract.md) | [中文](references/zh-CN/writing-contract.md).

## Route by observable state

| State | Route |
|---|---|
| New idea; no approved WhitePaper | `brainstorm` |
| Approved WhitePaper; ROADMAP absent or being maintained | `roadmap` |
| Owner starts a `not-started` milestone | `write-goal` |
| Goal exists; Requirement absent or changing | `write-requirement` |
| Requirement reviewed; Design absent or changing | `write-design` |
| Design reviewed; Task absent or changing | `write-task` |
| Confirmed task card is ready | `run-task` |
| All cards closed and traceability full | `close-milestone` |

## Runtime and role routing

Use the locale-matched [dispatch and agent-lifecycle contract](references/en/dispatch-and-handoff.md)
or [中文契约](references/zh-CN/dispatch-and-handoff.md). Runtime state is not document or work-item
state. Keep the node record and identity refs until `node-complete`.

- `brainstorm`, `roadmap`, `write-goal`, `write-requirement`, `write-design`, and `write-task`
  dispatch an Author, then an independent Critic. The primary orchestrator does not draft or
  repair the artifact.
- Accepted findings return to the same `author_ref`; blocker rechecks return to the same
  `critic_ref`. Author and Critic communicate only through the orchestrator.
- `run-task` uses the same Coder for fixes, the same Reviewer for targeted recheck, then an
  independent Verifier and an Integrator for mechanical state propagation.
- `close-milestone` dispatches independent verification, a closure Author, a combined
  Critic/Reviewer, and an Integrator after owner acceptance.
- A platform that cannot resume an identity enters `agent-unavailable`; replacement is
  explicit, and replacing a Critic or Reviewer requires a full review.

For document nodes, follow `ready-to-dispatch → author-active → author-returned →
candidate-anchored → critic-active → critic-returned`. Accepted findings loop through
`author-revising` with the same Author and, for blockers, `critic-rechecking` with the same
Critic. Finish through `acceptance-ready → accepted → integrating → node-complete`.

## Controlled-change routing

Workflow nodes are not one-way. Route a change to the single authority for the content:

| Approved authority that needs a semantic change | Route |
|---|---|
| WhitePaper problem, goal, scope, harm order, invariant, or interpretation | `brainstorm` revision mode |
| ROADMAP sequencing, milestone allocation, dependency, or qualitative completion picture | `roadmap` maintenance mode |
| Goal objective, boundary, slice, non-goal, or completion picture | `write-goal` revision mode |
| Requirement, constraint, parameter authority, or acceptance criterion | `write-requirement` revision mode |
| Design structure, interface, data, failure path, or R-AC mapping | `write-design` revision mode |
| Task card, dependency, execution order, test anchor, or traceability mapping | `write-task` revision mode |

Start from the approved old anchor, record the semantic delta and impact cone, update the
authority, then propagate only through affected upstream/downstream representations and
dependent work. Review, approve, and verify only affected content; do not rerun unrelated
stages. Old approval remains attached to the old anchor. The new anchor needs the approval
appropriate to that authority only when the change alters a decision or reasonable
understanding. Meaning-preserving mechanical changes use same-batch refresh and machine
checks without reapproval. An explicit equivalence record may let the new anchor retain the
document approval state by citing the old approved anchor; this is not a new approval.

For a narrow bug or mechanical one-step change, use the controlled bypass: identify scope,
the smallest authority/acceptance condition, implementation, test, independent review, and
same-batch status refresh. Do not fabricate a full chain; do not bypass WhitePaper, ROADMAP,
milestone initiation, scope expansion, or closure authority.

<HARD-GATE>Never route past a missing prerequisite or redefine upstream meaning in a downstream document. The primary orchestrator may decide, dispatch, adjudicate, accept, and gate, but must not silently perform work assigned to Author, Coder, Reviewer, Verifier, or Integrator. Pause dependent work whose premise changed until the semantic revision has the review or approval appropriate to its new version anchor. Agent-to-agent permission does not equal owner authorization. No push, publish, deployment, PR mutation, or external message unless the owner or project rules explicitly authorize it.</HARD-GATE>

End every substantive response with **Reflection**: weakest assumption; neglected
counterexample; measured versus inferred.
