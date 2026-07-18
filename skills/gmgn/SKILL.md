---
name: gmgn
description: "Use first to route workflow-driven project work: new projects, product ideas, research, feature development, bug fixes, refactors, WhitePaper, ROADMAP, PRD, requirements, design, task docs, coding delegation, launch, release, acceptance, or closure. 凡要按流程或 workflow 推进研发、调研、功能开发、修 bug、重构、写白皮书/ROADMAP/PRD/需求/设计/任务、派活写代码、上线发布、验收关账，或用户说按 GMGN/按流程办/下一步做什么时使用。"
---

# GMGN router: repository state → next stage

Use this skill to locate the stage, then invoke the specialized skill. The normative method
is [GMGN.md](../../GMGN.md); Chinese is [GMGN.zh-CN.md](../../GMGN.zh-CN.md).

## Language and contract

Infer `en` or `zh-CN` from approved project documents, then the user's language. Keep the
machine contract English. Load the matching writing contract only when writing documents:
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

For a narrow bug or mechanical one-step change, use the controlled bypass: identify scope,
the smallest authority/acceptance condition, implementation, test, independent review, and
same-batch status refresh. Do not fabricate a full chain; do not bypass WhitePaper, ROADMAP,
milestone initiation, scope expansion, or closure authority.

<HARD-GATE>Never route past a missing prerequisite. Agent-to-agent permission does not equal owner authorization. No push, publish, deployment, PR mutation, or external message unless the owner or project rules explicitly authorize it.</HARD-GATE>

End every substantive response with **Reflection**: weakest assumption; neglected
counterexample; measured versus inferred.
