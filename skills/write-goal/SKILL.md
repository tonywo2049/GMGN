---
name: write-goal
description: "Use when an approved ROADMAP exists and the owner explicitly starts or initiates a not-started milestone, phase, or version; create Goal.md with objective decomposition, scope boundary, and slices. Also use for a controlled semantic revision of an existing Goal authority. ROADMAP 已批且负责人点名启动/开工某个 Milestone、版本或阶段时立项，撰写 Goal、目标拆解、范围边界与切片；也用于既有 Goal 权威的受控语义修订。触发词包括启动 M2、开做里程碑、立项。"
---

# Initiate a milestone and write Goal.md

<HARD-GATE>Creation mode requires an approved ROADMAP, a `not-started` milestone row, and explicit owner initiation; otherwise return to `roadmap`. Revision mode requires an existing initiated Goal and its approved ROADMAP anchor, but does not require re-initiation. If the changed meaning belongs to WhitePaper or ROADMAP, return to `brainstorm` or `roadmap` before editing Goal. Work on an uninitiated milestone is out of scope.</HARD-GATE>

## Language and contract

Use the ROADMAP locale unless the owner changes it explicitly. Load the matching layout-free
[English](../gmgn/references/en/writing-contract.md) or
[中文](../gmgn/references/zh-CN/writing-contract.md) contract. Keep filename `Goal.md`,
`type: goal`, and `nature: normative`.

## One change batch

Dispatch an Author to perform one semantic batch:

1. Change the ROADMAP row from `not-started` to `initiated` and record the owner authorization.
2. Create the milestone directory and `Goal.md` as its single entry document. It must answer:
   objective, boundary, slices, non-goals, qualitative completion picture, document map, and
   known gaps. The Author chooses the section structure.
3. Add reciprocal ROADMAP ↔ Goal links and return one anchored candidate.

Do not create Requirement, Design, or Task content early. Mention absent downstream files
as gaps; create each only when its stage starts.

## Author and critic loop

At `ready-to-dispatch`, record the ROADMAP anchor and owner initiation, then dispatch one
Author and retain `author_ref`. The orchestrator does not edit Goal or ROADMAP. After
`author-returned`, send incomplete work to the same Author as `author-rework`; otherwise
enter `candidate-anchored` and dispatch an independent Critic. At `critic-returned`, adjudicate
findings, resume the same Author in `author-revising`, and use the same Critic for blocker
`critic-rechecking`. At `acceptance-ready`, the primary orchestrator reviews the anchored
candidate, then dispatches an Integrator for accepted mechanical propagation and commit
material. Finish only at `node-complete`.

## Controlled revision

1. Start from the old Goal anchor and record the trigger, semantic delta, affected slices,
   documents, and evidence, plus the proposed new anchor.
2. Route WhitePaper-owned meaning to `brainstorm` revision mode and ROADMAP-owned sequencing,
   cross-milestone allocation, dependency, or qualitative milestone-row meaning to `roadmap`
   maintenance mode. Resume here after the required upstream approval; do not patch that
   meaning into Goal.
3. Revise only Goal-owned objectives, boundaries, slices, non-goals, completion pictures, or
   document mapping. Preserve unaffected content.
4. If the delta changes a decision or reasonable understanding, run the independent critic
   and primary-orchestrator review against the affected content and bind it to a new anchor.
   Old review remains attached to the old anchor.
5. Propagate only to affected Requirement, Design, Task, implementation, test, evidence, and
   state representations. Review and verify that impact cone only; do not rerun unrelated
   stages.

Meaning-preserving mechanical changes use same-batch link, hash, and status refresh plus
machine checks without reapproval.

## Exit

Require the Author to self-check the ROADMAP boundary and slices. For creation or a semantic
revision, run the identity-preserving Author/Critic loop using the locale-matched dispatch
contract, obtain primary-orchestrator review, and integrate. Creation then uses **REQUIRED next skill:
`write-requirement`**. A revision returns to the stage that raised it and continues through
the affected path only.

End every substantive response with **Reflection**: weakest assumption; neglected
counterexample; measured versus inferred.
